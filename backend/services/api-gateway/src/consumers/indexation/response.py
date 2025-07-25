import json

from aiokafka import AIOKafkaConsumer
from loguru import logger
from shared_config import config
from src.schemas.indexing import IndexedResultPayload  # Pydantic-модель
from src.services.chunk_service import ChunkService


async def consume_indexing_results():
    consumer = AIOKafkaConsumer(
        config.kafka.indexation.response.topic,
        bootstrap_servers=config.kafka.bootstrap_servers,
        group_id=config.kafka.indexation.response.group_id,
        auto_offset_reset=config.kafka.auto_offset_reset,
        enable_auto_commit=config.kafka.enable_auto_commit,
    )

    async with consumer:
        async for msg in consumer:
            try:
                data = json.loads(msg.value)
                payload = IndexedResultPayload(**data)

                await ChunkService.save_chunks(
                    file_id=payload.file_id,
                    user_id=payload.user_id,
                    chunks=payload.chunks,
                )
            except Exception:
                logger.exception("Failed to process indexing result")
