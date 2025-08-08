from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from src.db.models import DBChunk, DBGenerationRequest
from src.db.wrap import transactional


class DaoRequest:
    @classmethod
    @transactional
    async def list_requests(
        cls, session: AsyncSession, user_id: UUID, history_id: UUID
    ) -> list[DBGenerationRequest]:
        stmt = (
            select(DBGenerationRequest)
            .filter(
                DBGenerationRequest.user_id == user_id,
                DBGenerationRequest.history_id == history_id,
            )
            .options(
                selectinload(DBGenerationRequest.retrieved_chunks),
            )
        )

        result = await session.execute(stmt)

        return result.scalars().all()

    @classmethod
    @transactional
    async def add_request(
        cls,
        session: AsyncSession,
        user_id: UUID,
        history_id: UUID,
        user_message: str,
        assistant_message: str | None = None,
        chunks: list[DBChunk] | None = None,
    ) -> DBGenerationRequest:
        db_request = DBGenerationRequest(
            user_id=user_id,
            history_id=history_id,
            user_message=user_message,
        )

        if assistant_message:
            db_request.assistant_message = assistant_message

        if chunks:
            db_request.retrieved_chunks = chunks

        session.add(db_request)

        return db_request

    @classmethod
    @transactional
    async def get_request(
        cls, session: AsyncSession, user_id: UUID, request_id: UUID
    ) -> None | DBGenerationRequest:
        stmt = (
            select(DBGenerationRequest)
            .filter(
                DBGenerationRequest.user_id == user_id,
                DBGenerationRequest.id == request_id,
            )
            .options(
                selectinload(DBGenerationRequest.retrieved_chunks),
            )
        )

        result = await session.execute(stmt)

        return result.scalars().first()

    @classmethod
    @transactional
    async def update_request(
        cls,
        session: AsyncSession,
        user_id: UUID,
        request_id: UUID,
        user_message: str | None = None,
        assistant_message: str | None = None,
        chunks: list[DBChunk] | None = None,
    ) -> DBGenerationRequest | None:
        db_request = await cls.get_request(
            session=session, user_id=user_id, request_id=request_id
        )
        if not db_request:
            return None

        if chunks:
            db_request.retrieved_chunks = chunks

        if user_message:
            db_request.user_message = user_message

        if assistant_message:
            db_request.assistant_message = assistant_message

        return db_request

    @classmethod
    @transactional
    async def delete_request(
        cls, session: AsyncSession, user_id: UUID, request_id: UUID
    ) -> None | DBGenerationRequest:
        db_request = await cls.get_request(
            session=session,
            user_id=user_id,
            request_id=request_id,
        )

        if db_request:
            await session.delete(db_request)

        return db_request
