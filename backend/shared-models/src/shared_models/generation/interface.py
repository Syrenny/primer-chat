from typing import Literal

from pydantic import BaseModel, ConfigDict

from shared_models.indexation.core import IndexedChunk
from shared_models.openai.completions import ChatMessage, Usage
from shared_models.user.persona import UserPersona
from shared_models.worker.context import WorkerRequestContext


class GenerationWorkerRequest(BaseModel):
    model_config = ConfigDict(strict=True)

    context: WorkerRequestContext

    history: list[ChatMessage]
    query: str
    chunks: list[IndexedChunk]
    persona: UserPersona


class GenerationWorkerChunkResponse(BaseModel):
    model_config = ConfigDict(strict=True)

    context: WorkerRequestContext

    type: Literal["default", "error"] = "default"
    chunk: str
    usage: Usage | None = None
    is_final: bool = False


class GenerationWorkerResponse(BaseModel):
    model_config = ConfigDict(strict=True)

    context: WorkerRequestContext

    stopped: bool = True
