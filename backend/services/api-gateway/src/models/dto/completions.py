from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict
from shared_models.generation.interface import GenerationWorkerChunkResponse


class APICompletionsRequest(BaseModel):
    history_id: UUID
    query: str

    model_config = ConfigDict(json_encoders={UUID: str})


class APICompletionsChunkResponse(BaseModel):
    type: Literal["error", "default"] = "default"
    text: str

    @classmethod
    def from_worker_response(cls, raw: str) -> "APICompletionsChunkResponse":
        response = GenerationWorkerChunkResponse.model_validate_json(raw)

        return cls(type=response.type, text=response.chunk.choices[0].message.content)
