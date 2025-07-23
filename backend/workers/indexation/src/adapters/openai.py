from asyncio_throttle import Throttler
from openai import AsyncOpenAI
from src.config import config, secrets
from src.models.openai import ChatCompletionResponse, ChatMessage

throttler = Throttler(
    rate_limit=config.openai_throttle_rate_limit, period=config.openai_throttle_period
)


class FullCompletions:
    def __init__(self) -> None:
        self.client = AsyncOpenAI(
            api_key=secrets.openai_key.get_secret_value(),
            base_url=config.openai_base_url,
        )

    async def create(self, system_prompt: ChatMessage) -> ChatCompletionResponse:
        response = await self.client.chat.completions.create(
            model=config.openai_model,
            messages=[system_prompt],
            stream=False,
            temperature=config.openai_temperature,
            max_tokens=config.openai_max_tokens,
        )

        return ChatCompletionResponse.model_validate(response.model_dump())
