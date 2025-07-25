from loguru import logger
from pydantic import ValidationError
from shared_adapters.openai import OpenAIFullCompletions
from shared_models.openai.completions import ChatCompletionResponse, ChatMessage, Usage
from shared_models.summarization.core import ParsedSummaryResponse
from src.prompts.render import render_prompt


class SummaryService:
    def __init__(self) -> None:
        self.summarizer = OpenAIFullCompletions()
        self.index = 0

    async def _make_summary(self, history: list[ChatMessage]) -> ChatCompletionResponse:
        system_prompt = render_prompt(name="summarization_system.j2", context={})
        summarizer_params = {
            "system_prompt": ChatMessage(role="system", content=system_prompt),
            "history": history,
        }

        return await self.summarizer.create(**summarizer_params)

    async def summarize(
        self, history: list[ChatMessage]
    ) -> tuple[ParsedSummaryResponse, Usage]:
        response: ChatCompletionResponse = await self._make_summary(history)
        try:
            raw = response.choices[0].message
            summary = ParsedSummaryResponse.model_validate_json(raw)
        except ValidationError as err:
            logger.error(f"Summary response validation error: {raw}")
            raise err

        return summary, response.usage
