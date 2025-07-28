from typing import AsyncIterator
from uuid import UUID

import redis.asyncio as redis
from loguru import logger
from shared_config import config


# TODO make _key_template = "{key_prefix}:{user_id}:{history}"
class RedisActiveHistory:
    _client: redis.Redis | None = None
    _key_template = "{key_prefix}:{user_id}"

    @classmethod
    async def get_client(cls) -> redis.Redis:
        if cls._client is None:
            cls._client = redis.Redis(
                host=config.redis.connection.host,
                port=config.redis.connection.port,
                db=config.redis.connection.db,
                decode_responses=True,
            )
        return cls._client

    @classmethod
    def _make_key(cls, user_id: UUID) -> str:
        return cls._key_template.format(
            key_prefix=config.redis.active_history.key_prefix, user_id=str(user_id)
        )

    @classmethod
    async def acquire(cls, user_id: UUID, history_id: UUID) -> bool:
        client = await cls.get_client()
        result = await client.set(
            name=cls._make_key(user_id),
            value=str(history_id),
            ex=config.redis.active_history.ttl_seconds,
            nx=True,  # Только если ключ НЕ существует
        )
        return result is not None  # True, если удалось захватить

    @classmethod
    async def release(cls, user_id: UUID) -> None:
        client = await cls.get_client()
        await client.delete(cls._make_key(user_id))

    @classmethod
    async def get_active(cls, user_id: UUID) -> UUID | None:
        client = await cls.get_client()
        value = await client.get(cls._make_key(user_id))
        return UUID(value) if value else None


class RedisStreamClient:
    _client: redis.Redis | None = None
    _group_name = "generation-workers"
    _consumer_name = "consumer-1"

    @classmethod
    async def get_client(cls) -> redis.Redis:
        if cls._client is None:
            cls._client = redis.Redis(
                host=config.redis.connection.host,
                port=config.redis.connection.port,
                db=config.redis.connection.db,
                decode_responses=True,
            )
            await cls._client.ping()
        return cls._client

    @classmethod
    async def ensure_stream_and_group(cls):
        """Создаёт стрим и группу, если не существует"""
        client = await cls.get_client()

        # Попытка создать стрим и группу (safe)
        try:
            await client.xgroup_create(
                name=config.redis.stream.key,
                groupname=cls._group_name,
                id="0",
                mkstream=True,  # если стрим не существует — создать
            )
            logger.info(
                f"Redis group '{cls._group_name}' created on stream '{config.redis.stream.key}'"
            )
        except redis.exceptions.ResponseError as e:
            if "BUSYGROUP" in str(e):
                pass  # группа уже существует
            else:
                raise

    @classmethod
    async def publish(cls, data: str) -> None:
        client = await cls.get_client()
        await client.xadd(config.redis.stream.key, {"data": data})

    @classmethod
    async def listen(cls) -> AsyncIterator[str]:
        client = await cls.get_client()
        await cls.ensure_stream_and_group()

        while True:
            response = await client.xreadgroup(
                groupname=cls._group_name,
                consumername=cls._consumer_name,
                streams={config.redis.stream.key: ">"},
                count=1,
                block=5000,
            )

            if response:
                stream_name, messages = response[0]
                for msg_id, fields in messages:
                    try:
                        yield fields["data"]
                        # подтвердить обработку
                        await client.xack(
                            config.redis.stream.key, cls._group_name, msg_id
                        )
                    except Exception as e:
                        logger.exception(f"Redis: Ошибка обработки сообщения: {e}")
