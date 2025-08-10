from uuid import UUID

from pydantic import BaseModel


class WorkerRequestContext(BaseModel):
    request_id: UUID
    user_id: UUID
    file_id: UUID | None = None
    history_id: UUID | None = None
