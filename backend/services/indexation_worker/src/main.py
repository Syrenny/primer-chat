import asyncio
import json
from functools import lru_cache

from aiokafka import AIOKafkaConsumer, AIOKafkaProducer
from loguru import logger
from shared_adapters.s3 import S3Storage
from shared_config import config
from shared_models.indexation.interface import (
    IndexationWorkerRequest,
    IndexationWorkerResponse,
)
from src.services.indexation import IndexationService


@lru_cache
def get_indexation_service() -> IndexationService:
    return IndexationService()


async def consume_indexation() -> None:
    consumer = AIOKafkaConsumer(
        config.kafka.indexation.request.topic,
        bootstrap_servers=config.kafka.bootstrap_servers,
        group_id=config.kafka.indexation.request.group_id,
        value_deserializer=lambda v: json.loads(v.decode("utf-8")),
    )

    producer = AIOKafkaProducer(
        bootstrap_servers=config.kafka.bootstrap_servers,
        value_serializer=lambda v: json.dumps(v).encode("utf-8"),
    )

    async with consumer, producer:
        async for msg in consumer:
            request = IndexationWorkerRequest.model_validate(msg.value)

            worker_response = IndexationWorkerResponse(
                request_id=request.request_id, context=request.context
            )

            try:
                pdf_bytes = await S3Storage.get_pdf_bytes_from_url(request.s3_link)

                service = get_indexation_service()
                worker_response.result = await service.run(pdf_bytes)
            except Exception as err:
                worker_response.error = str(err)
                logger.exception(f"Ошибка во время индексации: {err}")

            await producer.send_and_wait(
                topic=config.kafka.indexation.response.topic,
                value=worker_response.model_dump(mode="json"),
            )


if __name__ == "__main__":
    asyncio.run(consume_indexation())
