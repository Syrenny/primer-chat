from pydantic import BaseModel

from shared_models.worker.context import WorkerRequestContext


class IndexationWorkerRequest(BaseModel):
    context: WorkerRequestContext
    s3_link: str


class IndexationWorkerResponse(BaseModel):
    request_id: str
    context: WorkerRequestContext
    result: str | None = None
    error: str | None = None
