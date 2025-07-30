from typing import Literal

from pydantic import BaseModel, ConfigDict


class ChatMessage(BaseModel):
    model_config = ConfigDict(strict=True)

    role: Literal["system", "user", "assistant", "function"]
    content: str
    name: str | None = None


class Usage(BaseModel):
    model_config = ConfigDict(strict=True)

    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0

    def __iadd__(self, other: "Usage") -> "Usage":
        self.prompt_tokens += other.prompt_tokens
        self.completion_tokens += other.completion_tokens
        self.total_tokens += other.total_tokens
        return self
