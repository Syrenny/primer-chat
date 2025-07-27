from typing import Any, Literal

from pydantic import BaseModel, ConfigDict

from shared_models.openai.completions import ChatCompletionResponse, ChatMessage
from shared_models.user.persona import UserPersona
from shared_models.worker.context import WorkerRequestContext


class GenerationWorkerRequest(BaseModel):
    model_config = ConfigDict(strict=True)

    context: WorkerRequestContext

    history: list[ChatMessage]
    query: str
    chunks: Any
    summary: Any
    persona: UserPersona


class GenerationWorkerChunkResponse(BaseModel):
    model_config = ConfigDict(strict=True)

    context: WorkerRequestContext

    type: Literal["default", "error"] = "default"
    chunk: ChatCompletionResponse
    is_final: bool = False
