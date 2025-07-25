from uuid import UUID, uuid4

from pydantic import BaseModel, Field


class UserContext(BaseModel):
    user_id: UUID


class CookieData(BaseModel):
    user_id: UUID = Field(default_factory=uuid4)
