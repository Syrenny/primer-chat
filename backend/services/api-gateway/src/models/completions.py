from typing import Literal
from uuid import UUID

from pydantic import BaseModel


class APICompletionsRequest(BaseModel):
    history_id: UUID
    query: str


class APICompletionsChunkResponse(BaseModel):
    type: Literal["error", "default"] = "default"
    text: str
