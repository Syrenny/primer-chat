from typing import AsyncIterator

from shared_adapters.openai import OpenAICompletionsGenerator
from shared_models.indexation.core import IndexedChunk
from shared_models.openai.completions import ChatMessage, Usage
from shared_models.user.persona import UserPersona
from src.models.validator import ValidatorResponse
from src.prompts.render import render_prompt
from src.services.validation import ValidationService


class PromptBuilder:
    def __init__(self) -> None:
        self.validator = ValidationService()

    def system(self, persona: UserPersona, chunks: list[IndexedChunk]) -> ChatMessage:
        prompt = render_prompt(
            name="generation_system.j2", context={"persona": persona, "chunks": chunks}
        )
        return ChatMessage(role="system", content=prompt)

    async def user(self, query: str) -> ChatMessage:
        response: ValidatorResponse | None = await self.validator.validate(query)

        if not response or not response.verdict:
            content = query
        else:
            content = render_prompt(
                name="validator_user_wrapper.j2",
                context={"query": query, "reason": response.reason},
            )

        return ChatMessage(role="user", content=content)


class GenerationService:
    def __init__(self) -> None:
        self.completions = OpenAICompletionsGenerator()
        self.prompt_builder = PromptBuilder()

    async def stream(
        self,
        query: str,
        history: list[ChatMessage],
        persona: UserPersona,
        chunks: list[IndexedChunk],
    ) -> AsyncIterator[tuple[str, Usage | None, bool]]:
        params: dict[str, ChatMessage | list[ChatMessage]] = {
            "query": await self.prompt_builder.user(query),
            "history": history,
            "system_prompt": self.prompt_builder.system(persona=persona, chunks=chunks),
        }

        async for chunk, usage, is_final in self.completions.generate(**params):
            yield chunk, usage, is_final
