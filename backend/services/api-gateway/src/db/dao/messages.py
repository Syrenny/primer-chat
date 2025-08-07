from uuid import UUID

import sqlalchemy as db
from shared_models.openai.completions import ChatMessage
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from src.db.models import DBChunk, DBGenerationRequest, DBMessage
from src.db.wrap import transactional


class DaoMessages:
    @classmethod
    @transactional
    async def add_message(
        cls,
        session: AsyncSession,
        user_id: UUID,
        history_id: UUID,
        data: ChatMessage,
        request_id: UUID,
        chunks: list[DBChunk],
    ) -> DBMessage:
        db_message = DBMessage(
            user_id=user_id,
            history_id=history_id,
            data=data.model_dump(),
            request_id=request_id,
            chunks=chunks,
        )

        session.add(db_message)

        return db_message

    @classmethod
    @transactional
    async def list_messages(
        cls, session: AsyncSession, user_id: UUID, history_id: UUID
    ) -> list[DBMessage]:
        stmt = (
            db.select(DBGenerationRequest)
            .filter(
                DBGenerationRequest.user_id == user_id,
                DBGenerationRequest.history_id == history_id,
            )
            .order_by(DBGenerationRequest.timestamp)
            .options(
                selectinload(DBGenerationRequest.user_message),
                selectinload(DBGenerationRequest.assistant_message),
            )
        )

        result = await session.execute(stmt)
        requests = result.scalars().all()

        messages: list[DBMessage] = []
        for req in requests:
            if req.user_message:
                messages.append(req.user_message)
            if req.assistant_message:
                messages.append(req.assistant_message)
        return messages
