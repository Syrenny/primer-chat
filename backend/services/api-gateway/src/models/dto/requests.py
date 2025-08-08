from datetime import datetime
from uuid import UUID

from pydantic import BaseModel
from shared_models.generation.interface import ChatMessage
from shared_models.indexation.interface import ExtendedIndexedChunk
from src.db.models import DBGenerationRequest
from src.services.chunks import ChunkService


class GenerationRequest(BaseModel):
    request_id: UUID
    history_id: UUID
    timestamp: datetime
    chunks: list[ExtendedIndexedChunk]
    user_message: ChatMessage
    assistant_message: ChatMessage | None

    @classmethod
    def from_orm(cls, db_request: DBGenerationRequest) -> "GenerationRequest":
        user = ChatMessage(role="user", content=db_request.user_message)

        assistant = None
        if db_request.assistant_message:
            assistant = ChatMessage(
                role="assistant", content=db_request.assistant_message
            )

        return cls(
            request_id=db_request.id,
            history_id=db_request.history_id,
            timestamp=db_request.timestamp,
            chunks=ChunkService.from_db_chunks(db_request.retrieved_chunks),
            user_message=user,
            assistant_message=assistant,
        )

    @classmethod
    def from_orm_list(
        cls, db_request: list[DBGenerationRequest]
    ) -> list["GenerationRequest"]:
        return [cls.from_orm(req) for req in db_request]

    @classmethod
    def to_chm(cls, requests: list["GenerationRequest"]) -> list[ChatMessage]:
        messages: list[ChatMessage] = []
        for req in requests:
            messages.append(req.user_message)
            if req.assistant_message:
                messages.append(req.assistant_message)
        return messages


class CreateHistoryMetaRequest(BaseModel):
    file_ids: list[UUID] = []


class UpdateHistoryMetaRequest(BaseModel):
    file_ids: list[UUID] = []
