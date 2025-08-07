from datetime import datetime
from uuid import UUID

from pydantic import BaseModel
from shared_models.indexation.core import IndexedChunk
from src.db.models import DBGenerationRequest
from src.models.dto.messages import ChatHistoryMessage
from src.services.chunks import ChunkService


class GenerationRequest(BaseModel):
    request_id: UUID
    history_id: UUID
    timestamp: datetime
    chunks: list[IndexedChunk]
    user_message: ChatHistoryMessage
    assistant_message: ChatHistoryMessage

    @classmethod
    def from_orm(cls, db_request: DBGenerationRequest) -> "GenerationRequest":
        return cls(
            request_id=db_request.id,
            history_id=db_request.history_id,
            timestamp=db_request.timestamp,
            chunks=ChunkService.from_db_chunks(db_request.retrieved_chunks),
            user_message=ChatHistoryMessage.from_orm(db_request.user_message),
            assistant_message=ChatHistoryMessage.from_orm(db_request.assistant_message),
        )

    @classmethod
    def from_orm_list(
        cls, db_request: list[DBGenerationRequest]
    ) -> list["GenerationRequest"]:
        return [cls.from_orm(req) for req in db_request]


class CreateHistoryMetaRequest(BaseModel):
    file_ids: list[UUID] = []


class UpdateHistoryMetaRequest(BaseModel):
    file_ids: list[UUID] = []
