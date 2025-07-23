import backoff
import openai
from asyncio_throttle import Throttler
from src.config import config, secrets
from src.models.openai import ChatCompletionResponse, ChatMessage


class FullCompletions:
    def __init__(self) -> None:
        self.throttler = Throttler(
            rate_limit=config.openai_throttle_rate_limit,
            period=config.openai_throttle_period,
        )
        self.client = openai.AsyncOpenAI(
            api_key=secrets.openai_key.get_secret_value(),
            base_url=config.openai_base_url,
        )

    @backoff.on_exception(
        backoff.expo, (openai.APIError,), jitter=backoff.full_jitter, max_tries=5
    )
    async def create(self, system_prompt: ChatMessage) -> ChatCompletionResponse:
        async with self.throttler:
            response = await self.client.chat.completions.create(
                model=config.openai_model,
                messages=[system_prompt],
                stream=False,
                temperature=config.openai_temperature,
                max_tokens=config.openai_max_tokens,
            )

        return ChatCompletionResponse.model_validate(response.model_dump())
