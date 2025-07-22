from typing import List

import backoff
import openai
from src.config import config, secrets
from src.models.embeddings import EmbeddingsResponse


class Embeddings:
    def __init__(
        self,
    ) -> None:
        self.client = openai.AsyncOpenAI(api_key=secrets.embeddings_key)

    @backoff.on_exception(backoff.expo, (openai.APIError), max_tries=3)
    async def embed(self, texts: List[str]) -> EmbeddingsResponse:
        response = await self.client.embeddings.create(
            model=config.embeddings_model,
            input=texts,
            dimensions=config.embeddings_dimensions,
        )
        return EmbeddingsResponse.model_validate(response)

    async def embed_one(self, text: str) -> EmbeddingsResponse:
        return await self.embed([text])
