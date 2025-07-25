from uuid import UUID

from pydantic import BaseModel, Field


class FileMeta(BaseModel):
    file_id: UUID
    filename: str = Field(description="The name of the file.")
    is_indexed: bool
    s3_link: str


class FileStatus(BaseModel):
    file_id: UUID
    is_indexed: bool


class SignedUrl(BaseModel):
    url: str
