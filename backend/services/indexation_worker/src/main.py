import asyncio
import signal
from functools import lru_cache

from loguru import logger
from pydantic import ValidationError
from shared_adapters.s3 import S3Storage
from shared_config import config
from shared_kafka.base import BaseKafkaConsumer, BaseKafkaProducer
from shared_models.indexation.interface import (
    IndexationWorkerRequest,
    IndexationWorkerResponse,
)
from src.services.indexation import IndexationService


@lru_cache
def get_indexation_service() -> IndexationService:
    return IndexationService()


class WorkerIndexationResultProducer(BaseKafkaProducer):
    async def send(self, payload: IndexationWorkerResponse):
        await self.send_json(
            topic=config.kafka.indexation.response.topic, payload=payload
        )


class WorkerIndexationRequestConsumer(BaseKafkaConsumer):
    def __init__(self):
        super().__init__(
            topic=config.kafka.indexation.request.topic,
            group_id=config.kafka.indexation.request.group_id,
        )

    async def handle_message(self, payload: dict):
        try:
            request = IndexationWorkerRequest.model_validate_json(payload)
        except ValidationError as err:
            logger.error(f"[indexation worker] ❌ Validation error: {err}")
            return

        worker_response = IndexationWorkerResponse(context=request.context)

        try:
            pdf_bytes = await S3Storage.get_pdf_bytes_from_url(request.s3_link)

            service = get_indexation_service()
            worker_response.result = await service.run(pdf_bytes)
        except Exception as err:
            worker_response.error = str(err)
            logger.exception(f"[indexation worker] 🧨 Indexation error: {err}")

        async with WorkerIndexationResultProducer() as producer:
            await producer.send(worker_response)


async def main():
    consumer = WorkerIndexationRequestConsumer()
    await consumer.start()

    loop = asyncio.get_running_loop()
    stop_event = asyncio.Event()

    for sig in (signal.SIGINT, signal.SIGTERM):
        loop.add_signal_handler(sig, stop_event.set)
    try:
        await stop_event.wait()
    finally:
        logger.info("[indexation worker] 🧹 Graceful shutdown")
        await consumer.stop()


if __name__ == "__main__":
    asyncio.run(main())
