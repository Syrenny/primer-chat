from typing import Annotated, Literal, Union
from uuid import UUID

from pydantic import BaseModel, Field
from shared_models.indexation.core import PdfLinePosition


class ApiBufferResponse(BaseModel):
    buffer: str


class CompletionsRequest(BaseModel):
    history_id: UUID
    query: str


class ErrorChunk(BaseModel):
    type: Literal["error"]
    text: str


class ResponseChunk(BaseModel):
    type: Literal["response"]
    text: str


class RetrievedChunk(BaseModel):
    type: Literal["retrieved"]
    positions: list[PdfLinePosition]
    file_id: UUID
    filename: str


ApiChunkCompletionsResponse = Annotated[
    Union[ErrorChunk, ResponseChunk, RetrievedChunk],
    Field(discriminator="type"),
]
