import asyncio
import json
from abc import ABC, abstractmethod

from aiokafka import AIOKafkaConsumer, AIOKafkaProducer
from loguru import logger
from pydantic import BaseModel
from shared_config import config


class BaseKafkaProducer(ABC):
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

        data = json.dumps(payload.model_dump_json()).encode("utf-8")
        logger.debug(f"Producing to {topic}: {payload}")
        await self._producer.send_and_wait(topic=topic, value=data)

    async def __aenter__(self):
        await self.start()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.stop()


class BaseKafkaConsumer(ABC):
    def __init__(self, topic: str, group_id: str):
        self.topic = topic
        self.group_id = group_id

        self._consumer = AIOKafkaConsumer(
            topic,
            bootstrap_servers=config.kafka.bootstrap_servers,
            group_id=group_id,
            auto_offset_reset=config.kafka.auto_offset_reset,
            enable_auto_commit=config.kafka.enable_auto_commit,
            max_poll_records=config.kafka.max_poll_records,
            session_timeout_ms=config.kafka.session_timeout_ms,
        )

        self._task: asyncio.Task | None = None
        self._stopped = asyncio.Event()

    async def start(self):
        logger.debug(f"Starting Kafka consumer for topic: {self.topic}")
        await self._consumer.start()
        self._task = asyncio.create_task(self._consume_loop())

    async def stop(self):
        self._stopped.set()
        if self._task:
            await self._task
        await self._consumer.stop()
        logger.debug(f"Kafka consumer for topic {self.topic} stopped")

    async def wait_until_stopped(self):
        await self._stopped.wait()

    async def _consume_loop(self):
        try:
            while not self._stopped.is_set():
                result = await self._consumer.getmany(timeout_ms=1000)
                for tp, messages in result.items():
                    for msg in messages:
                        try:
                            payload = json.loads(msg.value)
                            await self.handle_message(payload)
                        except Exception:
                            logger.exception("Failed to process Kafka message")
        except asyncio.CancelledError:
            logger.warning("Kafka consumer task cancelled")
        except Exception:
            logger.exception("Unexpected error in Kafka consumer")

    @abstractmethod
    async def handle_message(self, payload: dict):
        """Process one message from Kafka"""
        raise NotImplementedError

    async def __aenter__(self):
        await self.start()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.stop()
