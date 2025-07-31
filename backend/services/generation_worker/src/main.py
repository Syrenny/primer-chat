import asyncio
import signal
from functools import lru_cache

from loguru import logger
from pydantic import ValidationError
from shared_adapters.redis import RedisGenerationBuffer
from shared_config import config
from shared_kafka.base import BaseKafkaConsumer, BaseKafkaProducer
from shared_models.generation.interface import (
    GenerationWorkerChunkResponse,
    GenerationWorkerRequest,
    GenerationWorkerResponse,
)
from src.services.generation import GenerationService


@lru_cache
def get_generation_service() -> GenerationService:
    return GenerationService()


class WorkerGenerationResultProducer(BaseKafkaProducer):
    async def send(self, payload: GenerationWorkerResponse) -> None:
        await self.send_json(
            topic=config.kafka.generation.response.topic, payload=payload
        )


class WorkerGenerationRequestConsumer(BaseKafkaConsumer):
    def __init__(self) -> None:
        super().__init__(
            topic=config.kafka.generation.request.topic,
            group_id=config.kafka.generation.request.group_id,
        )

    async def handle_message(self, payload: dict) -> None:
        try:
            request = GenerationWorkerRequest.model_validate_json(payload)
        except ValidationError as err:
            logger.exception(f"[generation worker] ❌ Validation error: {err}")
            return
        try:
            service = get_generation_service()
            params = {
                "query": request.query,
                "history": request.history,
                "persona": request.persona,
                "chunks": request.chunks,
            }
            async for chunk, usage, is_final in service.stream(**params):
                chunk_response = GenerationWorkerChunkResponse(
                    context=request.context, chunk=chunk, usage=usage, is_final=is_final
                )
                logger.debug(f"Streaming message...   {chunk}")
                await RedisGenerationBuffer.append_chunk(
                    user_id=request.context.user_id,
                    chunk=chunk_response.model_dump_json(),
                )
        except Exception as err:
            text = f"[generation worker] 🧨 Streaming error {err}"
            chunk_response = GenerationWorkerChunkResponse(
                type="error", context=request.context, chunk=text, is_final=True
            )
            await RedisGenerationBuffer.append_chunk(
                user_id=request.context.user_id,
                chunk=chunk_response.model_dump_json(),
            )
            logger.exception(text)
        finally:
            logger.info(
                f"[generation worker] ✅ Generation completed: user_id={request.context.user_id}"
            )

            worker_response = GenerationWorkerResponse(context=request.context)
            async with WorkerGenerationResultProducer() as producer:
                await producer.send(worker_response)


async def main() -> None:
    loop = asyncio.get_running_loop()
    stop_event = asyncio.Event()

    for sig in (signal.SIGINT, signal.SIGTERM):
        loop.add_signal_handler(sig, stop_event.set)

    async with WorkerGenerationRequestConsumer():
        await stop_event.wait()
        logger.info("[generation worker] 🧹 Graceful shutdown")


if __name__ == "__main__":
    asyncio.run(main())
