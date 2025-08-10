from pydantic import BaseModel, ConfigDict

from shared_models.worker.context import WorkerRequestContext


class IndexationWorkerRequest(BaseModel):
    model_config = ConfigDict(strict=True)

    context: WorkerRequestContext
    s3_link: str


class IndexationWorkerResponse(BaseModel):
    model_config = ConfigDict(strict=True)

    context: WorkerRequestContext
    error: str | None = None
