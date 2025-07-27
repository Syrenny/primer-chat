from uuid import UUID

from pydantic import BaseModel, ConfigDict


class WorkerRequestContext(BaseModel):
    request_id: UUID
    user_id: UUID
    file_id: UUID | None = None
    history_id: UUID | None = None

    model_config = ConfigDict(strict=True, json_encoders={UUID: str})
