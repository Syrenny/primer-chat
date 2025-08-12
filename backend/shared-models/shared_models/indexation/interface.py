from typing import Annotated, Literal, Union

from pydantic import BaseModel, ConfigDict, Field, TypeAdapter

from shared_models.worker.context import WorkerRequestContext


class IndexationWorkerRequest(BaseModel):
    model_config = ConfigDict(strict=True)

    context: WorkerRequestContext
    s3_link: str


class IndexationWorkerResponse(BaseModel):
    model_config = ConfigDict(strict=True)

    context: WorkerRequestContext
    error: str | None = None


class IndexationProgressError(BaseModel):
    model_config = ConfigDict(strict=True)

    type: Literal["error"] = "error"


class IndexationProgressResponse(BaseModel):
    model_config = ConfigDict(strict=True)

    type: Literal["response"] = "response"

    context: WorkerRequestContext
    progress: float  # [0:1]


IndexationProgress = Annotated[
    Union[IndexationProgressError, IndexationProgressResponse],
    Field(discriminator="type"),
]

IndexationProgressAdapter = TypeAdapter(IndexationProgress)
