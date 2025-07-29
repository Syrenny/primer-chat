from uuid import UUID

from pydantic import BaseModel, ConfigDict
from src.db.models import DBCookie


class UserContext(BaseModel):
    user_id: UUID

    model_config = ConfigDict(json_encoders={UUID: str})


class CookieData(BaseModel):
    cookie_id: UUID

    model_config = ConfigDict(json_encoders={UUID: str})

    @classmethod
    def from_orm(cls, db_cookie: DBCookie) -> "CookieData":
        return cls(cookie_id=db_cookie.id)
