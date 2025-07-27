from typing import AsyncIterator, List

import backoff
import openai
from asyncio_throttle import Throttler
from shared_config import config, secrets
from shared_models.openai.completions import ChatCompletionResponse, ChatMessage
from shared_models.openai.embeddings import EmbeddingsResponse


class Embeddings:
    def __init__(
        self,
    ) -> None:
        self.throttler = Throttler(
            rate_limit=config.embeddings.throttle_rate_limit,
            period=config.embeddings.throttle_period,
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
                model=config.embeddings.model,
                input=texts,
                dimensions=config.embeddings.dimensions,
            )
        return EmbeddingsResponse.model_validate(response.model_dump())

    async def embed_one(self, text: str) -> EmbeddingsResponse:
        return await self.embed([text])


class OpenAICompletionsGenerator:
    def __init__(self) -> None:
        self.throttler = Throttler(
            rate_limit=config.openai.throttle_rate_limit,
            period=config.openai.throttle_period,
        )
        self.client = openai.AsyncOpenAI(
            api_key=secrets.openai_key.get_secret_value(),
            base_url=config.openai.base_url,
        )

    @backoff.on_exception(
        backoff.expo, (openai.APIError,), jitter=backoff.full_jitter, max_tries=5
    )
    async def generate(
        self, query: ChatMessage, history: list[ChatMessage], system_prompt: ChatMessage
    ) -> AsyncIterator[ChatCompletionResponse]:
        async with self.throttler:
            generator = await self.client.chat.completions.create(
                model=config.openai.model,
                messages=[system_prompt] + history + [query],
                stream=True,
                temperature=config.openai.temperature,
                max_tokens=config.openai.max_tokens,
            )

            async for chunk in generator:
                yield ChatCompletionResponse.model_validate(chunk.model_dump())


class OpenAIFullCompletions:
    def __init__(self) -> None:
        self.throttler = Throttler(
            rate_limit=config.openai.throttle_rate_limit,
            period=config.openai.throttle_period,
        )
        self.client = openai.AsyncOpenAI(
            api_key=secrets.openai_key.get_secret_value(),
            base_url=config.openai.base_url,
        )

    @backoff.on_exception(
        backoff.expo, (openai.APIError,), jitter=backoff.full_jitter, max_tries=5
    )
    async def create(
        self,
        system_prompt: ChatMessage,
        history: list[ChatMessage] | None,
        query: ChatMessage | None,
    ) -> ChatCompletionResponse:
        async with self.throttler:
            response = await self.client.chat.completions.create(
                model=config.openai.model,
                messages=[system_prompt] + (history or []) + ([query] if query else []),
                stream=False,
                temperature=config.openai.temperature,
                max_tokens=config.openai.max_tokens,
            )

        return ChatCompletionResponse.model_validate(response.model_dump())
