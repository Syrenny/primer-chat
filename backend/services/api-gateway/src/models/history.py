from uuid import UUID

from pydantic import BaseModel
from src.db.models import DBHistoryMeta
from src.models.files import FileMeta


class HistoryMeta(BaseModel):
    history_id: UUID
    summary: str
    files: list[FileMeta]

    @classmethod
    def from_db(cls, db_history_meta: list[DBHistoryMeta]) -> list["HistoryMeta"]:
        return [
            cls(
                history_id=meta.id,
                summary=meta.summary,
                files=FileMeta.from_db(meta.files),
            )
            for meta in db_history_meta
        ]


class CreateHistoryMetaRequest(BaseModel):
    summary: list[str] | None = None
    file_ids: list[UUID] | None = None


class UpdateHistoryMetaRequest(BaseModel):
    summary: list[str] | None = None
    file_ids: list[UUID] | None = None
