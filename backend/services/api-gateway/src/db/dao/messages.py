from uuid import UUID

import sqlalchemy as db
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from src.db.models import DBChunk, DBMessage
from src.db.wrap import transactional


class DaoMessages:
    @classmethod
    @transactional
    async def add_message(
        cls,
        session: AsyncSession,
        user_id: UUID,
        history_id: UUID,
        content: str,
        is_user: bool,
        context: list[DBChunk] | None = None,
        snippet: str | None = None,
    ) -> DBMessage:
        context = context or []
        new_message = DBMessage(
            user_id=user_id,
            history_id=history_id,
            content=content,
            context=context,
            is_user_message=is_user,
            snippet=snippet,
        )

        session.add(new_message)
        await session.flush()

        return new_message

    @classmethod
    @transactional
    async def get_messages(
        cls, session: AsyncSession, user_id: UUID, history_id: UUID
    ) -> list[DBMessage]:
        result = await session.execute(
            db.select(DBMessage)
            .filter(DBMessage.user_id == user_id, DBMessage.history_id == history_id)
            .options(selectinload(DBMessage.context))
            .order_by(DBMessage.timestamp)
        )
        return result.scalars().all()
