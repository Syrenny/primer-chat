import asyncio
import json
from functools import lru_cache

from aiokafka import AIOKafkaConsumer, AIOKafkaProducer
from shared_models.generation.interface import (
    GenerationWorkerChunkResponse,
    GenerationWorkerRequest,
)
from src.config import config
from src.services.generation import GenerationService


@lru_cache
def get_generation_service() -> GenerationService:
    return GenerationService()


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
            request = GenerationWorkerRequest.model_validate(msg.value)

            service = get_generation_service()
            async for chunk in service.stream(
                request.query, request.history, request.persona
            ):
                response = GenerationWorkerChunkResponse(
                    request_id=request.request_id, chunk=chunk
                )
                await producer.send_and_wait(
                    topic=config.kafka_response_topic,
                    value=response.model_dump(mode="json"),
                )


if __name__ == "__main__":
    asyncio.run(consume())
