import json

import redis.asyncio as redis
from shared_config import config


class RedisStreamClient:
    _client: redis.Redis | None = None

    @classmethod
    async def get_client(cls) -> redis.Redis:
        if cls._client is None:
            cls._client = redis.Redis(
                host=config.redis.host,
                port=config.redis.port,
                db=config.redis.db,
                decode_responses=True,
            )
            await cls._client.ping()
        return cls._client

    @classmethod
    async def publish(cls, data: dict):
        client = await cls.get_client()
        await client.xadd(config.redis.stream_key, {"data": json.dumps(data)})

    @classmethod
    async def listen(cls):
        client = await cls.get_client()
        last_id = "$"
        while True:
            response = await client.xread(
                {config.redis.stream_key: last_id},
                block=0,
                count=1,
            )
            if response:
                stream, messages = response[0]
                for msg_id, fields in messages:
                    try:
                        yield json.loads(fields["data"])
                    except Exception as e:
                        print("Ошибка обработки:", e)
                    last_id = msg_id
