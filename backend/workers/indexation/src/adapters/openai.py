from openai import AsyncOpenAI
from src.config import config, secrets
from src.models.openai import ChatCompletionResponse, ChatMessage


class FullCompletions:
    def __init__(self) -> None:
        self.client = AsyncOpenAI(
            api_key=secrets.openai_validator_key.get_secret_value(),
            base_url=config.openai_validator_base_url,
        )

    async def create(
        self, history: list[ChatMessage], system_prompt: ChatMessage
    ) -> ChatCompletionResponse:
        response = await self.client.chat.completions.create(
            model=config.openai_validator_model,
            messages=[system_prompt] + history,
            stream=False,
            temperature=config.openai_validator_temperature,
            max_tokens=config.openai_validator_max_tokens,
        )

        return response.choices[0].message.content
