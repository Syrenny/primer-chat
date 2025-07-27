from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field
from src.db.models import DBFileMeta


class FileMeta(BaseModel):
    file_id: UUID
    filename: str = Field(description="The name of the file.")
    is_indexed: bool

    @classmethod
    def from_db(cls, files: list[DBFileMeta]) -> list["FileMeta"]:
        return [
            cls(
                file_id=file.file_id, filename=file.filename, is_indexed=file.is_indexed
            )
            for file in files
        ]

    model_config = ConfigDict(json_encoders={UUID: str})


class FileStatus(BaseModel):
    file_id: UUID
    is_indexed: bool


class SignedUrl(BaseModel):
    url: str
