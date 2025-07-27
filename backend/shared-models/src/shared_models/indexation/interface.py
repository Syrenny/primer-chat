from pydantic import BaseModel, ConfigDict

from shared_models.indexation.core import IndexationResult
from shared_models.worker.context import WorkerRequestContext


class IndexationWorkerRequest(BaseModel):
    model_config = ConfigDict(strict=True)

    context: WorkerRequestContext
    s3_link: str


class IndexationWorkerResponse(BaseModel):
    model_config = ConfigDict(strict=True)

    context: WorkerRequestContext
    result: IndexationResult | None = None
    error: str | None = None
