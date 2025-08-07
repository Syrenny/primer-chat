from typing import Literal, Union
from uuid import UUID

from pydantic import BaseModel
from shared_models.indexation.core import IndexedChunk


class ApiBufferResponse(BaseModel):
    buffer: str


class CompletionsRequest(BaseModel):
    history_id: UUID
    query: str


class ErrorChunk(BaseModel):
    type: Literal["error"]
    chunk: str


class DefaultChunk(BaseModel):
    type: Literal["default"]
    chunk: str


class RetrievedChunk(BaseModel):
    type: Literal["retrieved"]
    chunk: IndexedChunk


ApiChunkCompletionsResponse = Union[
    ErrorChunk,
    DefaultChunk,
    RetrievedChunk,
]
