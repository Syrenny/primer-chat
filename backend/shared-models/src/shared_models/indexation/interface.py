from pydantic import BaseModel


class IndexationWorkerRequest(BaseModel):
    s3_link: str


class IndexationWorkerResponse(BaseModel):
    request_id: str
    result: str | None = None
    error: str | None = None
