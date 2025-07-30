from loguru import logger
from pydantic import ValidationError
from shared_adapters.openai import OpenAIFullCompletions
from shared_models.openai.completions import ChatMessage
from src.models.validator import ValidatorResponse
from src.prompts.render import render_prompt


class ValidationService:
    def __init__(self) -> None:
        self.completions = OpenAIFullCompletions()

    def _parse_response(self, response: str) -> ValidatorResponse | None:
        try:
            return ValidatorResponse.model_validate_json(response)
        except ValidationError:
            logger.error(f"Invalid validator response: {response}")
            return None

    def _build_validator_system_prompt(self, query: str) -> str:
        return render_prompt(name="validator_system.j2", context={"query": query})

    async def validate(self, query: str) -> ValidatorResponse | None:
        system_prompt = ChatMessage(
            role="system", content=self._build_validator_system_prompt(query=query)
        )
        params = {
            "system_prompt": system_prompt,
            "query": None,
            "history": None,
        }
        response, _ = await self.completions.create(**params)
        return self._parse_response(response)
