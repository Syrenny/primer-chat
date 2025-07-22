from typing import Annotated, Literal, Union

from pydantic import BaseModel, Field

from .chunks import Chunks


class ResponseError(BaseModel):
    type: Literal["error"]
    message: str


class ResponseDefault(BaseModel):
    type: Literal["default"]
    chunks: Chunks


WorkerResponse = Annotated[
    Union[ResponseError, ResponseDefault], Field(discriminator="type")
]
