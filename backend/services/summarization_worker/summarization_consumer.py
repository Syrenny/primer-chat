import asyncio
import json
from functools import lru_cache

from aiokafka import AIOKafkaConsumer, AIOKafkaProducer
from loguru import logger
from shared_models.summarization.interface import (
    SummarizationWorkerRequest,
    SummarizationWorkerResponse,
)
from src.config import config
from src.services.summarization import SummaryService


@lru_cache
def get_summary_service() -> SummaryService:
    return SummaryService()


async def consume():
    consumer = AIOKafkaConsumer(
        config.kafka_request_topic,
        bootstrap_servers=config.kafka_bootstrap_servers,
        group_id=config.kafka_group_id,
        value_deserializer=lambda m: json.loads(m.decode("utf-8")),
        enable_auto_commit=True,
    )

    producer = AIOKafkaProducer(
        bootstrap_servers=config.kafka_bootstrap_servers,
        value_serializer=lambda m: json.dumps(m).encode("utf-8"),
    )

    async with consumer, producer:
        async for msg in consumer:
            request = SummarizationWorkerRequest.model_validate(msg.value)

            logger.info(f"Handling request {request.request_id}")

            service = get_summary_service()

            worker_response = SummarizationWorkerResponse(request_id=request.request_id)

            try:
                (
                    worker_response.summary,
                    worker_response.usage,
                ) = await service.summarize(request.history)
            except Exception as err:
                worker_response.error = str(err)
                logger.exception(f"Ошибка во время саммаризации: {err}")

            await producer.send_and_wait(
                topic=config.kafka_response_topic,
                value=worker_response.model_dump(mode="json"),
            )


if __name__ == "__main__":
    asyncio.run(consume())
