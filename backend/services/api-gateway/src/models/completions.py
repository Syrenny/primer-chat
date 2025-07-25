from typing import Literal

from pydantic import BaseModel


class APICompletionsRequest(BaseModel):
    query: str


class APICompletionsChunkResponse(BaseModel):
    type: Literal["error", "default"] = "default"
    text: str
