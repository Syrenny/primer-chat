from uuid import UUID, uuid4

from pydantic import BaseModel, ConfigDict, Field


class UserContext(BaseModel):
    user_id: UUID

    model_config = ConfigDict(json_encoders={UUID: str})


class CookieData(BaseModel):
    id: UUID
    user_id: UUID = Field(default_factory=uuid4)

    model_config = ConfigDict(json_encoders={UUID: str})
