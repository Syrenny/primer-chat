from loguru import logger
from pydantic import ValidationError
from shared_adapters.openai import OpenAIFullCompletions
from shared_models.openai.completions import ChatMessage, Usage
from src.models.dto.summarization import ParsedSummaryResponse
from src.prompts.render import render_prompt


class SummaryService:
    def __init__(self) -> None:
        self.summarizer = OpenAIFullCompletions()
        self.index = 0

    async def _make_summary(self, history: list[ChatMessage]) -> tuple[str, Usage]:
        system_prompt = render_prompt(
            name="summarization_system.j2", context={"messages": history}
        )
        summarizer_params = {
            "query": None,
            "system_prompt": ChatMessage(role="system", content=system_prompt),
            "history": None,
        }

        return await self.summarizer.create(**summarizer_params)

    async def summarize(
        self, history: list[ChatMessage]
    ) -> tuple[ParsedSummaryResponse, Usage]:
        raw, usage = await self._make_summary(history)
        try:
            summary_response = ParsedSummaryResponse.model_validate_json(raw)
        except ValidationError as err:
            logger.error(f"Summary response validation error: {raw}")
            logger.error(f"History: {history}")
            raise err

        return summary_response, usage
