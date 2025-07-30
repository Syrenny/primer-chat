from datetime import UTC, datetime
from typing import AsyncIterator
from uuid import UUID

import redis.asyncio as redis
from shared_config import config


# TODO make _key_template = "{key_prefix}:{user_id}:{history}"
class RedisGenerationBuffer:
    _client: redis.Redis | None = None
    _chunk_key_template = "generation_buffer:{user_id}:chunks"
    _meta_key_template = "generation_buffer:{user_id}:meta"

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
    def _chunk_key(cls, user_id: UUID) -> str:
        return cls._chunk_key_template.format(user_id=user_id)

    @classmethod
    def _meta_key(cls, user_id: UUID) -> str:
        return cls._meta_key_template.format(user_id=user_id)

    @classmethod
    async def init(cls, user_id: UUID, request_id: UUID, history_id: UUID) -> None:
        client = await cls.get_client()
        meta_key = cls._meta_key(user_id)

        await client.hset(
            meta_key,
            mapping={
                "request_id": str(request_id),
                "history_id": str(history_id),
                "started_at": datetime.now(UTC),
            },
        )
        await client.expire(meta_key, config.redis.buffer.ttl_seconds)

    @classmethod
    async def load_chunks(cls, user_id: UUID) -> list[str]:
        client = await cls.get_client()
        return await client.lrange(cls._chunk_key(user_id), 0, -1)

    @classmethod
    async def append_chunk(cls, user_id: UUID, chunk: str) -> None:
        client = await cls.get_client()
        chunk_key = cls._chunk_key(user_id)
        channel = f"generation:{user_id}"

        await client.rpush(chunk_key, chunk)
        await client.expire(chunk_key, config.redis.buffer.ttl_seconds)
        await client.publish(channel, chunk)

    @classmethod
    async def get_request_id(cls, user_id: UUID) -> UUID | None:
        client = await cls.get_client()
        meta = await client.hget(cls._meta_key(user_id), "request_id")
        return UUID(meta) if meta else None

    @classmethod
    async def clear_all(cls, user_id: UUID) -> None:
        client = await cls.get_client()
        await client.delete(cls._chunk_key(user_id))
        await client.delete(cls._meta_key(user_id))

    @classmethod
    async def exists(cls, user_id: UUID) -> bool:
        client = await cls.get_client()
        return (await client.exists(cls._chunk_key(user_id)) == 1) and (
            await client.exists(cls._meta_key(user_id)) == 1
        )

    @classmethod
    async def listen(cls, user_id: UUID) -> AsyncIterator[str]:
        client = await cls.get_client()

        pubsub = client.pubsub()
        channel = f"generation:{user_id}"
        await pubsub.subscribe(channel)

        try:
            while True:
                message = await pubsub.get_message(
                    ignore_subscribe_messages=True, timeout=1
                )
                if message:
                    yield message["data"]
        finally:
            await pubsub.unsubscribe(channel)
            await pubsub.close()
