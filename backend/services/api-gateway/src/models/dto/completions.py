from typing import Literal
from uuid import UUID

from pydantic import BaseModel
from shared_models.generation.interface import GenerationWorkerChunkResponse


class CompletionsRequest(BaseModel):
    history_id: UUID
    query: str


class ApiBufferResponse(BaseModel):
    buffer: str


class ApiChunkResponse(BaseModel):
    type: Literal["error", "default"] = "default"
    text: str

    @classmethod
    def from_worker_response(cls, raw: str) -> "ApiChunkResponse":
        response = GenerationWorkerChunkResponse.model_validate_json(raw)

        return cls(type=response.type, text=response.chunk)
