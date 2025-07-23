from typing import List

import backoff
import openai
from asyncio_throttle import Throttler
from src.config import config, secrets
from src.models.embeddings import EmbeddingsResponse


class Embeddings:
    def __init__(
        self,
    ) -> None:
        self.throttler = Throttler(
            rate_limit=config.embeddings_throttle_rate_limit,
            period=config.embeddings_throttle_period,
        )
        self.client = openai.AsyncOpenAI(
            api_key=secrets.embeddings_key.get_secret_value()
        )

    @backoff.on_exception(
        backoff.expo, (openai.APIError,), jitter=backoff.full_jitter, max_tries=5
    )
    async def embed(self, texts: List[str]) -> EmbeddingsResponse:
        async with self.throttler:
            response = await self.client.embeddings.create(
                model=config.embeddings_model,
                input=texts,
                dimensions=config.embeddings_dimensions,
            )
        return EmbeddingsResponse.model_validate(response.model_dump())

    async def embed_one(self, text: str) -> EmbeddingsResponse:
        return await self.embed([text])
