from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from src.db.models import DBFileMeta
from src.db.wrap import transactional


class DaoFileMeta:
    @classmethod
    @transactional
    async def list_file_meta(
        cls, session: AsyncSession, user_id: UUID
    ) -> list[DBFileMeta]:
        stmt = select(DBFileMeta).filter(
            DBFileMeta.user_id == user_id,
        )

        result = await session.execute(stmt)

        return result.scalars().all()

    @classmethod
    @transactional
    async def add_file_meta(
        cls, session: AsyncSession, user_id: UUID, filename: str
    ) -> DBFileMeta:
        file_meta = DBFileMeta(
            user_id=user_id,
            filename=filename,
        )
        session.add(file_meta)

        return file_meta

    @classmethod
    @transactional
    async def get_file_meta(
        cls, session: AsyncSession, user_id: UUID, file_id: UUID
    ) -> None | DBFileMeta:
        stmt = select(DBFileMeta).filter(
            DBFileMeta.user_id == user_id, DBFileMeta.file_id == file_id
        )

        result = await session.execute(stmt)

        return result.scalars().first()

    @classmethod
    @transactional
    async def delete_file_meta(
        cls,
        session: AsyncSession,
        user_id: UUID,
        file_id: UUID,
    ) -> None | DBFileMeta:
        db_file_meta = await cls.get_file_meta(session, user_id, file_id)

        if db_file_meta:
            await session.delete(db_file_meta)

        return db_file_meta

    @classmethod
    @transactional
    async def get_is_indexed(
        cls, session: AsyncSession, user_id: UUID, file_id: UUID
    ) -> bool | None:
        db_file_meta = await cls.get_file_meta(
            session=session,
            user_id=user_id,
            file_id=file_id,
        )

        if db_file_meta is None:
            return None

        return db_file_meta.is_indexed

    @classmethod
    @transactional
    async def set_is_indexed(
        cls, session: AsyncSession, user_id: UUID, file_id: UUID, value: bool
    ) -> bool | None:
        db_file_meta = await cls.get_file_meta(
            session=session,
            user_id=user_id,
            file_id=file_id,
        )

        if db_file_meta is None:
            return None

        db_file_meta.is_indexed = value
        return value
