from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from src.db.models import DBFileMeta, DBHistoryMeta
from src.db.wrap import transactional
from src.models.dto.history import HistoryMetaSummary


class DaoHistoryMeta:
    @classmethod
    @transactional
    async def list_history_meta(
        cls, session: AsyncSession, user_id: UUID
    ) -> list[DBHistoryMeta]:
        stmt = (
            select(DBHistoryMeta)
            .filter(
                DBHistoryMeta.user_id == user_id,
            )
            .options(
                selectinload(DBHistoryMeta.messages),
                selectinload(DBHistoryMeta.files),
            )
        )

        result = await session.execute(stmt)

        return result.scalars().all()

    @classmethod
    @transactional
    async def count_user_histories(cls, session: AsyncSession, user_id: UUID) -> int:
        stmt = select(DBHistoryMeta).filter(DBHistoryMeta.user_id == user_id)
        result = await session.execute(stmt)
        return result.scalars().unique().count()

    @classmethod
    @transactional
    async def add_history_meta(
        cls,
        session: AsyncSession,
        user_id: UUID,
        summary: HistoryMetaSummary,
        files: list[DBFileMeta] | None = None,
    ) -> DBHistoryMeta:
        db_history_meta = DBHistoryMeta(user_id=user_id, summary=summary.model_dump())
        if files:
            db_history_meta.files = files
        session.add(db_history_meta)

        return db_history_meta

    @classmethod
    @transactional
    async def get_history_meta(
        cls,
        session: AsyncSession,
        user_id: UUID,
        history_id: UUID,
    ) -> DBHistoryMeta | None:
        stmt = (
            select(DBHistoryMeta)
            .filter(DBHistoryMeta.user_id == user_id, DBHistoryMeta.id == history_id)
            .options(
                selectinload(DBHistoryMeta.messages),
                selectinload(DBHistoryMeta.files),
            )
        )

        result = await session.execute(stmt)

        return result.scalars().first()

    @classmethod
    @transactional
    async def delete_history_meta(
        cls,
        session: AsyncSession,
        user_id: UUID,
        history_id: UUID,
    ) -> None | DBHistoryMeta:
        db_file_meta = await cls.get_history_meta(
            session=session, user_id=user_id, history_id=history_id
        )

        if db_file_meta:
            await session.delete(db_file_meta)

        return db_file_meta

    @classmethod
    @transactional
    async def update_history_meta(
        cls,
        session: AsyncSession,
        user_id: UUID,
        history_id: UUID,
        summary: HistoryMetaSummary | None = None,
        files: list[DBFileMeta] | None = None,
    ) -> DBHistoryMeta | None:
        db_history_meta = await cls.get_history_meta(
            session=session, user_id=user_id, history_id=history_id
        )

        if not db_history_meta:
            return None

        if summary is not None:
            db_history_meta.summary = summary.model_dump()

        if files:
            db_history_meta.files = files

        return db_history_meta
