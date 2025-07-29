from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field
from src.db.models import DBFileMeta


class FileMeta(BaseModel):
    file_id: UUID
    filename: str = Field(description="The name of the file.")
    is_indexed: bool

    @classmethod
    def from_orm(cls, db_file_meta: DBFileMeta) -> "FileMeta":
        return cls(
            file_id=db_file_meta.id,
            filename=db_file_meta.filename,
            is_indexed=db_file_meta.is_indexed,
        )

    @classmethod
    def from_orm_list(cls, db_files: list[DBFileMeta]) -> list["FileMeta"]:
        return [cls.from_orm(db_file_meta) for db_file_meta in db_files]

    model_config = ConfigDict(json_encoders={UUID: str})


class FileStatus(BaseModel):
    file_id: UUID
    is_indexed: bool


class SignedUrl(BaseModel):
    url: str
