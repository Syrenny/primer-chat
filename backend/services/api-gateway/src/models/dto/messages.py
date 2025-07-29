from datetime import datetime
from uuid import UUID

from pydantic import BaseModel
from shared_models.openai.completions import ChatMessage
from src.db.models import DBMessage


class ChatHistoryMessage(BaseModel):
    index: UUID
    data: ChatMessage
    timestamp: datetime

    @classmethod
    def from_orm(cls, db_message: DBMessage) -> "ChatHistoryMessage":
        return cls(
            index=db_message.id,
            data=ChatMessage.model_validate(db_message.data),
            timestamp=db_message.timestamp,
        )

    @classmethod
    def from_orm_list(cls, db_messages: list[DBMessage]) -> list["ChatHistoryMessage"]:
        return [cls.from_orm(db_message) for db_message in db_messages]

    @classmethod
    def to_chat_messages(
        cls, chat_history_messages: list["ChatHistoryMessage"]
    ) -> list[ChatMessage]:
        return [chm.data for chm in chat_history_messages]
