import json

from aiokafka import AIOKafkaProducer
from loguru import logger
from pydantic import BaseModel
from shared_config import config


class BaseKafkaProducer:
    def __init__(self):
        self._producer = AIOKafkaProducer(
            bootstrap_servers=config.kafka.bootstrap_servers
        )

    async def start(self):
        await self._producer.start()
        logger.debug("Kafka producer started")

    async def stop(self):
        await self._producer.stop()
        logger.debug("Kafka producer stopped")

    async def send_json(self, topic: str, payload: BaseModel):
        if not self._producer._sender:  # продюсер не запущен
            raise RuntimeError("Kafka producer not started")

        data = json.dumps(payload.model_dump()).encode("utf-8")
        logger.debug(f"Producing to {topic}: {payload}")
        await self._producer.send_and_wait(topic=topic, value=data)

    async def __aenter__(self):
        await self.start()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.stop()
