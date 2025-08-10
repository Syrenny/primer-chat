import asyncio
from asyncio import TimeoutError as AsyncTimeoutError
from contextlib import AsyncExitStack, aclosing, asynccontextmanager
from typing import AsyncGenerator
from uuid import UUID

import async_timeout
from loguru import logger
from pydantic import ValidationError
from shared_adapters.redis import RedisGenerationBuffer, RedisGenerationRequestStore
from shared_models.generation.interface import (
    GenerationWorkerChunkResponse,
    GenerationWorkerRequest,
)
from shared_models.indexation.core import ExtendedIndexedChunk
from shared_models.worker.context import WorkerRequestContext
from sqlalchemy.ext.asyncio import AsyncSession
from src.config import config as local_config
from src.exceptions.generation import GenerationWorkerError
from src.kafka.generation.producer import GenerationProducer
from src.models.dto.completions import ErrorChunk, ResponseChunk, RetrievedChunk
from src.services.history import HistoryMessagesService
from src.services.request import RequestService
from src.services.retriever import RetrieveService
from src.services.user import UserPersonaService


@asynccontextmanager
async def init_generation_context(
    user_id: UUID, history_id: UUID, session: AsyncSession, query: str
) -> AsyncGenerator[UUID, None]:
    generation_request = await RequestService.create_request(
        user_id=user_id, history_id=history_id, session=session, user_message=query
    )
    await RedisGenerationBuffer.init(
        user_id=user_id, history_id=history_id, request_id=generation_request.request_id
    )

    try:
        yield generation_request.request_id
    except Exception as err:
        logger.exception(
            f"❌ Error during generation publish ({user_id=}, {history_id=}): {err}"
        )
        await RedisGenerationBuffer.clear_all(user_id=user_id)


class GenerationService:
    @classmethod
    async def publish(
        cls, user_id: UUID, history_id: UUID, session: AsyncSession, query: str
    ) -> UUID:
        async with init_generation_context(
            user_id=user_id, history_id=history_id, session=session, query=query
        ) as request_id:
            history_messages_with_summary = (
                await HistoryMessagesService.get_history_messages(
                    user_id=user_id, history_id=history_id, session=session
                )
            )

            extended_chunks = await RetrieveService.retrieve_and_save(
                session=session,
                user_id=user_id,
                history_id=history_id,
                request_id=request_id,
                query=query,
            )

            persona = await UserPersonaService.get_persona(
                session=session, user_id=user_id
            )

            context = WorkerRequestContext(
                request_id=request_id,
                user_id=user_id,
                history_id=history_id,
            )

            request = GenerationWorkerRequest(
                context=context,
                history=history_messages_with_summary,
                query=query,
                chunks=extended_chunks,
                persona=persona,
            )

            await RedisGenerationRequestStore.put(
                user_id=user_id, request_id=request_id, request=request
            )

            async with GenerationProducer() as producer:
                await producer.send(context)

            logger.info(
                f"🛰️ Sent generation request {request_id} for history {history_id}"
            )
            return request_id

    @classmethod
    async def stream_model_chunks(
        cls, user_id: UUID, history_id: UUID, request_id: UUID
    ) -> AsyncGenerator[str, None]:
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
    ) -> AsyncGenerator[GenerationWorkerChunkResponse, None]:
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
    async def stream_retrieved_chunks(
        cls, user_id: UUID, request_id: UUID
    ) -> AsyncGenerator[ExtendedIndexedChunk, None]:
        try:
            request = await RedisGenerationRequestStore.get(
                user_id=user_id, request_id=request_id
            )
            if request is None:
                raise
        except Exception as err:
            logger.error(f"💥 Failed to fetch request from Redis: {err}")
            return

        for chunk in request.chunks:
            yield (
                RetrievedChunk(
                    type="retrieved",
                    positions=chunk.positions,
                    file_id=chunk.file_id,
                    filename=chunk.filename,
                ).model_dump_json()
                + "\n\n"
            )

    @classmethod
    async def stream_api_chunks(
        cls, user_id: UUID, history_id: UUID, request_id: UUID
    ) -> AsyncGenerator[str, None]:
        retrieved_generator = cls.stream_retrieved_chunks(
            user_id=user_id, request_id=request_id
        )

        model_generator = cls.stream_model_chunks(
            user_id=user_id,
            history_id=history_id,
            request_id=request_id,
        )

        try:
            async with AsyncExitStack() as stack:
                r = await stack.enter_async_context(aclosing(retrieved_generator))
                m = await stack.enter_async_context(aclosing(model_generator))
                try:
                    async for chunk in r:
                        yield chunk
                    async for chunk in m:
                        yield (
                            ResponseChunk(type="response", text=chunk).model_dump_json()
                            + "\n\n"
                        )
                except asyncio.CancelledError:
                    logger.info(
                        f"🚫 Client disconnected (user={user_id}, history={history_id})"
                    )
                except Exception as err:
                    logger.exception(f"💥 Unhandled exception in stream: {err}")
                    error_response = ErrorChunk(
                        type="error", text="Internal server error"
                    )
                    yield error_response.model_dump_json() + "\n\n"
        finally:
            await RedisGenerationRequestStore.delete(
                user_id=user_id, request_id=request_id
            )
