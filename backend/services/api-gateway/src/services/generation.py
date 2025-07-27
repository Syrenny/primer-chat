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
from src.services.chunks import ChunkService
from src.services.history import HistoryService


class GenerationService:
    @classmethod
    async def publish(
        cls, user_id: UUID, history_id: UUID, session: AsyncSession, query: str
    ) -> UUID:
        history_meta = await DaoHistoryMeta.get_history_meta(
            session=session, user_id=user_id, history_id=history_id
        )
        history = await HistoryService.get_history(
            user_id=user_id, history_id=history_id, session=session
        )
        chunks = await ChunkService.find_chunks(
            user_id=user_id, history_id=history_id, session=session, query=query
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
            logger.warning("AsyncTimeoutError")
            return

    @classmethod
    async def _listen_stream(
        cls,
        user_id: UUID,
        history_id: UUID,
    ) -> AsyncIterator[GenerationWorkerChunkResponse]:
        """Фильтрует сообщения из Redis по user_id и history_id"""

        while True:
            raw: dict = await wait_for(
                anext(RedisStreamClient.listen()),
                timeout=local_config.generation.wait_for_stream_timeout,
            )
            response = GenerationWorkerChunkResponse.model_validate(raw)

            if str(response.context.user_id) == str(user_id) and str(
                response.context.history_id
            ) == str(history_id):
                yield response
