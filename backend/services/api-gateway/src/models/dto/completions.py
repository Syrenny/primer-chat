from typing import Annotated, Literal, Union
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class BaseEvent(BaseModel):
    type: str

    model_config = ConfigDict(json_encoders={UUID: str})


class CompletionsRequestEvent(BaseEvent):
    type: Literal["request"]
    history_id: UUID
    query: str


class ResumeRequestEvent(BaseEvent):
    type: Literal["resume"]
    history_id: UUID


CompletionsEvent = Annotated[
    Union[CompletionsRequestEvent, ResumeRequestEvent], Field(discriminator="type")
]


class BaseResponse(BaseModel):
    type: str


class ErrorResponse(BaseResponse):
    type: Literal["error"]
    text: str


class BufferResponse(BaseResponse):
    type: Literal["buffer"]
    text: str


class ChunkResponse(BaseResponse):
    type: Literal["chunk"]
    text: str
