from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class APICompletionsRequest(BaseModel):
    history_id: UUID
    query: str

    model_config = ConfigDict(json_encoders={UUID: str})


class APICompletionsChunkResponse(BaseModel):
    type: Literal["error", "default"] = "default"
    text: str
