from typing import Annotated, Literal, Union

from pydantic import BaseModel, Field

from .indexation import IndexationResult


class ResponseError(BaseModel):
    type: Literal["error"]
    message: str


class ResponseDefault(BaseModel):
    type: Literal["default"]
    result: IndexationResult


WorkerResponse = Annotated[
    Union[ResponseError, ResponseDefault], Field(discriminator="type")
]
