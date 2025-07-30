from uuid import UUID

import sqlalchemy as db
from shared_models.openai.completions import ChatMessage
from sqlalchemy.ext.asyncio import AsyncSession
from src.db.models import DBMessage
from src.db.wrap import transactional


class DaoMessages:
    @classmethod
    @transactional
    async def get_message_by_id(
        cls, session: AsyncSession, user_id: UUID, history_id: UUID, message_id: UUID
    ) -> DBMessage | None:
        stmt = (
            db.select(DBMessage)
            .filter(
                DBMessage.user_id == user_id,
                DBMessage.history_id == history_id,
                DBMessage.id == message_id,
            )
            .order_by(DBMessage.timestamp)
        )
        result = await session.execute(stmt)
        return result.scalars().first()

    @classmethod
    @transactional
    async def add_message(
        cls,
        session: AsyncSession,
        user_id: UUID,
        history_id: UUID,
        data: ChatMessage,
        request_id: UUID,
    ) -> DBMessage:
        db_message = DBMessage(
            user_id=user_id,
            history_id=history_id,
            data=data.model_dump(),
            request_id=request_id,
        )

        session.add(db_message)

        return db_message

    @classmethod
    @transactional
    async def list_messages(
        cls, session: AsyncSession, user_id: UUID, history_id: UUID
    ) -> list[DBMessage]:
        stmt = (
            db.select(DBMessage)
            .filter(DBMessage.user_id == user_id, DBMessage.history_id == history_id)
            .order_by(DBMessage.timestamp)
        )
        result = await session.execute(stmt)
        return result.scalars().all()
