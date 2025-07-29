from datetime import datetime
from uuid import UUID

from pydantic import BaseModel
from shared_models.user.persona import UserPersona
from src.db.models import DBUser
from src.models.dto.files import FileMeta
from src.models.dto.history import HistoryMeta
from src.models.dto.session import CookieData


class UserDTO(BaseModel):
    user_id: UUID
    persona: UserPersona = UserPersona()
    created_at: datetime

    cookie: CookieData
    histories: list[HistoryMeta]
    files: list[FileMeta]

    @classmethod
    def from_orm(cls, db_user: DBUser) -> "UserDTO":
        return cls(
            user_id=db_user.id,
            persona=UserPersona.model_validate(db_user.persona),
            created_at=db_user.created_at,
            cookie=CookieData.from_orm(db_user.cookie),
            histories=HistoryMeta.from_orm_list(db_user.histories),
            files=FileMeta.from_orm_list(db_user.files),
        )
