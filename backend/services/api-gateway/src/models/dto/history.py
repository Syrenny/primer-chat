from uuid import UUID

from pydantic import BaseModel
from src.db.models import DBHistoryMeta
from src.models.dto.files import FileMeta
from src.models.dto.requests import GenerationRequest


class HistoryMetaSummary(BaseModel):
    summary_message_index: int = 0
    content: str = ""


class HistoryMeta(BaseModel):
    history_id: UUID
    summary: HistoryMetaSummary
    files: list[FileMeta]
    requests: list[GenerationRequest]

    @classmethod
    def from_orm(cls, db_history_meta: DBHistoryMeta) -> "HistoryMeta":
        return cls(
            history_id=db_history_meta.id,
            summary=HistoryMetaSummary.model_validate(db_history_meta.summary),
            files=FileMeta.from_orm_list(db_history_meta.files),
            requests=GenerationRequest.from_orm_list(db_history_meta.requests),
        )

    @classmethod
    def from_orm_list(cls, db_history_meta: list[DBHistoryMeta]) -> list["HistoryMeta"]:
        return [cls.from_orm(meta) for meta in db_history_meta]


class CreateHistoryMetaRequest(BaseModel):
    file_ids: list[UUID] = []


class UpdateHistoryMetaRequest(BaseModel):
    file_ids: list[UUID] = []
