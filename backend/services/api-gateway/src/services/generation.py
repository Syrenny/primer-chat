from asyncio import TimeoutError as AsyncTimeoutError
from asyncio import wait_for
from builtins import anext
from typing import AsyncIterator
from uuid import UUID, uuid4

from loguru import logger
from shared_adapters.redis import RedisStreamClient
from shared_models.generation.interface import (
    GenerationWorkerChunkResponse,
    GenerationWorkerRequest,
)
from shared_models.worker.context import WorkerRequestContext
from sqlalchemy.ext.asyncio import AsyncSession
from src.config import config as local_config
from src.consumers.generation.request import GenerationProducer
from src.db.dao import DaoUser
from src.db.dao.history_meta import DaoHistoryMeta
from src.models.completions import APICompletionsChunkResponse
from src.services.history import HistoryService
from src.services.retriever import RetrieveService


class GenerationService:
    @classmethod
    async def publish(
        cls, user_id: UUID, history_id: UUID, session: AsyncSession, query: str
    ) -> UUID:
        history_meta = await DaoHistoryMeta.get_history_meta(
            session=session, user_id=user_id, history_id=history_id
        )

        if not history_meta:
            raise ValueError(f"HistoryMeta not found: {history_id=}, {user_id=}")

        history = await HistoryService.get_history(
            user_id=user_id, history_id=history_id, session=session
        )

        chunks = await RetrieveService.retrieve(
            session=session, user_id=user_id, history_id=history_id, query=query
        )

        persona = await DaoUser.get_persona(session=session, user_id=user_id)

        request_id = uuid4()
        request = GenerationWorkerRequest(
            context=WorkerRequestContext(
                request_id=request_id,
                user_id=user_id,
                history_id=history_id,
            ),
            history=history,
            query=query,
            chunks=chunks,
            summary=history_meta.summary,
            persona=persona,
        )

        async with GenerationProducer() as producer:
            await producer.send(request)

        logger.info(f"🛰️ Sent generation request {request_id} for history {history_id}")
        return request_id

    @classmethod
    async def listen(
        cls,
        user_id: UUID,
        history_id: UUID,
    ) -> AsyncIterator[APICompletionsChunkResponse]:
        try:
            async for response in cls._listen_stream(user_id, history_id):
                yield APICompletionsChunkResponse(
                    type=response.type, text=response.chunk.choices[0].message.content
                )
                if response.is_final:
                    break
        except AsyncTimeoutError:
            logger.warning(f"⏱️ Listen timed out for {user_id=} {history_id=}")
            return

    @classmethod
    async def _listen_stream(
        cls,
        user_id: UUID,
        history_id: UUID,
    ) -> AsyncIterator[GenerationWorkerChunkResponse]:
        for attempt in range(local_config.generation.listen_max_attempts):
            try:
                raw = await wait_for(
                    anext(RedisStreamClient.listen()),
                    timeout=local_config.generation.listen_timeout_seconds,
                )
                response = GenerationWorkerChunkResponse.model_validate(raw)

                if cls._is_valid_response(response, user_id, history_id):
                    yield response
            except AsyncTimeoutError:
                logger.warning(
                    f"⏱️ Timeout while waiting for Redis stream. Attempt {attempt + 1}/{local_config.generation.listen_max_attempts}"
                )
            except Exception as err:
                logger.exception(f"❌ Error in Redis stream listening: {err}")
        logger.warning(f"❗ Max attempts exceeded for {user_id=} {history_id=}")

    @staticmethod
    def _is_valid_response(
        response: GenerationWorkerChunkResponse, user_id: UUID, history_id: UUID
    ) -> bool:
        return (
            response.context.user_id == user_id
            and response.context.history_id == history_id
        )
