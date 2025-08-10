import asyncio
import json
from abc import ABC, abstractmethod
from types import TracebackType
from typing import Optional, Self

from aiokafka import AIOKafkaConsumer, AIOKafkaProducer
from loguru import logger
from pydantic import BaseModel
from shared_config import config


class BaseKafkaProducer(ABC):
    def __init__(self) -> None:
        self._producer = AIOKafkaProducer(
            bootstrap_servers=config.kafka.bootstrap_servers
        )
        self._started = False

    async def start(self) -> None:
        await self._producer.start()
        self._started = True
        logger.debug("Kafka producer started")

    async def stop(self) -> None:
        try:
            await self._producer.stop()
        finally:
            self._started = False
            logger.debug("Kafka producer stopped")

    async def send_json(
        self,
        *,
        topic: str,
        payload: BaseModel,
        key: Optional[bytes] = None,
        headers: Optional[list[tuple[str, bytes]]] = None,
    ) -> None:
        """Отправляет Pydantic-модель как JSON (bytes)."""
        if not self._started:
            raise RuntimeError("Kafka producer not started")

        body_dict = payload.model_dump(mode="json")
        data = json.dumps(body_dict, ensure_ascii=False).encode("utf-8")

        logger.debug(f"Producing to {topic}: {type(payload).__name__}")
        await self._producer.send_and_wait(
            topic=topic, value=data, key=key, headers=headers
        )

    async def __aenter__(self) -> Self:
        await self.start()
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None:
        await self.stop()


class BaseKafkaConsumer(ABC):
    def __init__(self, topic: str, group_id: str) -> None:
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

    async def start(self) -> None:
        logger.debug(f"Starting Kafka consumer for topic: {self.topic}")
        await self._consumer.start()
        self._task = asyncio.create_task(self._consume_loop())

    async def stop(self) -> None:
        self._stopped.set()
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
        await self._consumer.stop()
        logger.debug(f"Kafka consumer for topic {self.topic} stopped")

    async def wait_until_stopped(self) -> None:
        await self._stopped.wait()

    async def _consume_loop(self) -> None:
        try:
            while not self._stopped.is_set():
                result = await self._consumer.getmany(timeout_ms=1000)
                if not result:
                    continue
                for _tp, messages in result.items():
                    for msg in messages:
                        try:
                            raw = msg.value  # bytes
                            payload = json.loads(raw.decode("utf-8"))
                            await self.handle_message(payload)  # dict
                        except Exception:
                            logger.exception("Failed to process Kafka message")
        except asyncio.CancelledError:
            logger.warning("Kafka consumer task cancelled")
        except Exception:
            logger.exception("Unexpected error in Kafka consumer")

    @abstractmethod
    async def handle_message(self, payload: dict) -> None:
        """Обработать одно сообщение (payload уже dict)."""
        raise NotImplementedError

    async def __aenter__(self) -> Self:
        await self.start()
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None:
        await self.stop()
