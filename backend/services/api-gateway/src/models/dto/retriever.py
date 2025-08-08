from uuid import UUID

from pydantic import BaseModel
from shared_models.indexation.interface import ExtendedIndexedChunk


class ApiRetrieverRequest(BaseModel):
    history_id: UUID
    query: str


class ApiRetrieverResponse(BaseModel):
    chunks: list[ExtendedIndexedChunk]
