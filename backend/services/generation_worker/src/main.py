import asyncio
import signal
from functools import lru_cache

from loguru import logger
from pydantic import ValidationError
from shared_adapters.redis import RedisStreamClient
from shared_config import config
from shared_kafka.base import BaseKafkaConsumer
from shared_models.generation.interface import (
    GenerationWorkerChunkResponse,
    GenerationWorkerRequest,
)
from src.services.generation import GenerationService


@lru_cache
def get_generation_service() -> GenerationService:
    return GenerationService()


class WorkerGenerationRequestConsumer(BaseKafkaConsumer):
    def __init__(self):
        super().__init__(
            topic=config.kafka.generation.topic,
            group_id=config.kafka.generation.group_id,
        )

    async def handle_message(self, payload: dict):
        try:
            request = GenerationWorkerRequest.model_validate_json(payload)
        except ValidationError as err:
            logger.error(f"[generation worker] ❌ Validation error: {err}")
            return
        try:
            service = get_generation_service()
            async for chunk in service.stream(
                request.query, request.history, request.persona
            ):
                response = GenerationWorkerChunkResponse(
                    context=request.context, chunk=chunk
                )
                await RedisStreamClient.publish(response.model_dump_json())
        except Exception as err:
            logger.exception(f"[generation worker] 🧨 Streaming error {err}")


async def main():
    loop = asyncio.get_running_loop()
    stop_event = asyncio.Event()

    for sig in (signal.SIGINT, signal.SIGTERM):
        loop.add_signal_handler(sig, stop_event.set)

    async with WorkerGenerationRequestConsumer():
        await stop_event.wait()
        logger.info("[generation worker] 🧹 Graceful shutdown")


if __name__ == "__main__":
    asyncio.run(main())
