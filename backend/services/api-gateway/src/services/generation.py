import asyncio
from asyncio import TimeoutError as AsyncTimeoutError
from contextlib import aclosing, asynccontextmanager
from typing import AsyncGenerator, AsyncIterator
from uuid import UUID, uuid4

import async_timeout
from loguru import logger
from pydantic import ValidationError
from shared_adapters.redis import RedisGenerationBuffer
from shared_models.generation.interface import (
    GenerationWorkerChunkResponse,
    GenerationWorkerRequest,
)
from shared_models.worker.context import WorkerRequestContext
from sqlalchemy.ext.asyncio import AsyncSession
from src.config import config as local_config
from src.consumers.generation.request import GenerationProducer
from src.exceptions.generation import GenerationWorkerError
from src.models.dto.completions import ApiChunkResponse
from src.services.history import HistoryMessagesService
from src.services.messages import MessageService
from src.services.retriever import RetrieveService
from src.services.user import UserPersonaService


@asynccontextmanager
async def init_generation_context(
    user_id: UUID, history_id: UUID
) -> AsyncGenerator[UUID, None]:
    request_id = uuid4()
    await RedisGenerationBuffer.init(
        user_id=user_id, history_id=history_id, request_id=request_id
    )

    try:
        yield request_id
    except Exception as err:
        logger.error(
            f"❌ Error during generation publish ({user_id=}, {history_id=}): {err}"
        )
        await RedisGenerationBuffer.clear_all(user_id=user_id)


class GenerationService:
    @classmethod
    async def publish(
        cls, user_id: UUID, history_id: UUID, session: AsyncSession, query: str
    ) -> UUID:
        async with init_generation_context(
            user_id=user_id, history_id=history_id
        ) as request_id:
            await MessageService.add_user_message(
                session=session,
                user_id=user_id,
                history_id=history_id,
                request_id=request_id,
                query=query,
            )

            history_messages_with_summary = (
                await HistoryMessagesService.get_history_messages(
                    user_id=user_id, history_id=history_id, session=session
                )
            )

            chunks = await RetrieveService.retrieve(
                session=session, user_id=user_id, history_id=history_id, query=query
            )

            persona = await UserPersonaService.get_persona(
                session=session, user_id=user_id
            )

            request = GenerationWorkerRequest(
                context=WorkerRequestContext(
                    request_id=request_id,
                    user_id=user_id,
                    history_id=history_id,
                ),
                history=history_messages_with_summary,
                query=query,
                chunks=chunks,
                persona=persona,
            )

            async with GenerationProducer() as producer:
                await producer.send(request)

            logger.info(
                f"🛰️ Sent generation request {request_id} for history {history_id}"
            )
            return request_id

    @classmethod
    async def listen(
        cls, user_id: UUID, history_id: UUID, request_id: UUID
    ) -> AsyncIterator[str]:
        try:
            async with async_timeout.timeout(
                local_config.generation.listen_timeout_seconds
            ):
                async for response in cls._listen_filtered_stream(
                    user_id=user_id, history_id=history_id, request_id=request_id
                ):
                    if response.type == "error":
                        raise GenerationWorkerError(message=response.chunk)
                    yield response.chunk
                    if response.is_final:
                        break
        except AsyncTimeoutError:
            logger.warning(f"⏱️ Listen timed out for {user_id=} {history_id=}")
            return

    @classmethod
    async def _listen_filtered_stream(
        cls,
        user_id: UUID,
        history_id: UUID,
        request_id: UUID,
    ) -> AsyncIterator[GenerationWorkerChunkResponse]:
        async for raw in RedisGenerationBuffer.listen(user_id=user_id):
            try:
                response = GenerationWorkerChunkResponse.model_validate_json(raw)
            except ValidationError as err:
                logger.exception(f"❌ Error validating response: {err}")
                continue

            if (
                response.context.user_id == user_id
                and response.context.history_id == history_id
                and response.context.request_id == request_id
            ):
                yield response

    @classmethod
    async def stream_api_chunks(
        cls, user_id: UUID, history_id: UUID, request_id: UUID
    ) -> AsyncGenerator[str, None]:
        generator = cls.listen(
            user_id=user_id,
            history_id=history_id,
            request_id=request_id,
        )

        async with aclosing(generator) as _generator:
            try:
                async for chunk in _generator:
                    yield ApiChunkResponse(text=chunk).model_dump_json() + "\n\n"
            except asyncio.CancelledError:
                logger.info(
                    f"🚫 Client disconnected (user={user_id}, history={history_id})"
                )
            except Exception as err:
                logger.exception(f"💥 Unhandled exception in stream: {err}")
                error_response = ApiChunkResponse(
                    type="error", text="Internal server error"
                )
                yield error_response.model_dump_json() + "\n\n"
