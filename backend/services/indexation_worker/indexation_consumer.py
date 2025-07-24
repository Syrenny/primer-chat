import json
from functools import lru_cache

from aiokafka import AIOKafkaConsumer, AIOKafkaProducer
from loguru import logger
from shared_models.indexation.interface import (
    IndexationWorkerRequest,
    IndexationWorkerResponse,
)
from src.adapters.s3 import get_pdf_bytes
from src.config import config
from src.services.indexation import IndexationService


@lru_cache
def get_indexation_service() -> IndexationService:
    return IndexationService()


async def consume_indexation():
    consumer = AIOKafkaConsumer(
        config.kafka_request_topic,
        bootstrap_servers=config.kafka_bootstrap_servers,
        group_id=config.kafka_group_id,
        value_deserializer=lambda v: json.loads(v.decode("utf-8")),
    )

    producer = AIOKafkaProducer(
        bootstrap_servers=config.kafka_bootstrap_servers,
        value_serializer=lambda v: json.dumps(v).encode("utf-8"),
    )

    async with consumer, producer:
        async for msg in consumer:
            request = IndexationWorkerRequest.model_validate(msg.value)

            worker_response = IndexationWorkerResponse(request_id=request.request_id)

            try:
                pdf_bytes = await get_pdf_bytes(request.s3_link)

                service = get_indexation_service()
                worker_response.result = await service.run(pdf_bytes)
            except Exception as err:
                worker_response.error = str(err)
                logger.exception(f"Ошибка во время индексации: {err}")

            await producer.send_and_wait(
                topic=config.kafka_response_topic,
                value=worker_response.model_dump(mode="json"),
            )
