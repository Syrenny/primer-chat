from uuid import UUID

from pydantic import BaseModel


class WorkerRequestContext(BaseModel):
    user_id: UUID
    file_id: UUID | None = None
    history_id: UUID | None = None
