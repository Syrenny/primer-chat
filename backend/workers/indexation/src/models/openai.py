from typing import Literal

from pydantic import BaseModel, Field


class ChatMessage(BaseModel):
    role: Literal["system", "user", "assistant", "function"]
    content: str
    name: str | None = None


class Choice(BaseModel):
    index: int
    message: ChatMessage
    finish_reason: str | None


class Usage(BaseModel):
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int


class ChatCompletionResponse(BaseModel):
    index: str = Field(alias="id")
    object: str
    created: int
    model: str
    choices: list[Choice]
    usage: Usage | None
