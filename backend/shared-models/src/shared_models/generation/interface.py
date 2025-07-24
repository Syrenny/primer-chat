from typing import Any

from pydantic import BaseModel

from shared_models.openai.completions import ChatCompletionResponse, ChatMessage
from shared_models.user.persona import UserPersona


class GenerationWorkerRequest(BaseModel):
    request_id: str
    history: list[ChatMessage]
    query: str
    context: Any
    summary: Any
    persona: UserPersona


class GenerationWorkerChunkResponse(BaseModel):
    request_id: str
    chunk: ChatCompletionResponse
