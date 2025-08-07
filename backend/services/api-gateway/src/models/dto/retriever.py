from uuid import UUID

from pydantic import BaseModel
from shared_models.indexation.core import IndexedChunk


class ApiRetrieverRequest(BaseModel):
    history_id: UUID
    query: str


class ApiRetrieverResponse(BaseModel):
    chunks: list[IndexedChunk]
