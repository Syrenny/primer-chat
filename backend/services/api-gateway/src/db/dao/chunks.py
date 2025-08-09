from uuid import UUID

import sqlalchemy as db
from shared_models.indexation.core import IndexedChunk
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from src.db.models import DBChunk, history_file_association
from src.db.wrap import transactional


class DaoChunks:
    @classmethod
    @transactional
    async def list_chunks(
        cls, session: AsyncSession, user_id: UUID, file_id: UUID
    ) -> list[DBChunk]:
        stmt = select(DBChunk).filter(
            DBChunk.user_id == user_id, DBChunk.file_id == file_id
        )

        result = await session.execute(stmt)

        return result.scalars().all()

    @classmethod
    @transactional
    async def save_file_chunks(
        cls,
        session: AsyncSession,
        user_id: UUID,
        file_id: UUID,
        filename: str,
        chunks: list[IndexedChunk],
    ) -> None:
        """Сохраняет чанки в БД."""
        chunk_objects = [
            DBChunk(
                user_id=user_id,
                file_id=file_id,
                filename=filename,
                content=chunk.content,
                embedding=chunk.embedding,
                html_tag=chunk.html_tag,
                positions=[pos.model_dump() for pos in chunk.positions],
            )
            for chunk in chunks
        ]
        session.add_all(chunk_objects)

    @classmethod
    @transactional
    async def find_history_chunks(
        cls,
        session: AsyncSession,
        user_id: UUID,
        history_id: UUID,
        query_embedding: list[float],
        limit: int,
    ) -> list[DBChunk]:
        """Ищет чанки среди всех файлов, привязанных к истории."""

        exists_q = (
            db.select(db.literal(1))
            .select_from(history_file_association)
            .where(
                history_file_association.c.history_id == history_id,
                history_file_association.c.file_id == DBChunk.file_id,
            )
        )

        stmt = (
            db.select(DBChunk)
            .where(DBChunk.user_id == user_id, db.exists(exists_q).correlate(DBChunk))
            .order_by(DBChunk.embedding.l2_distance(query_embedding))
            .limit(limit)
        )

        result = await session.execute(stmt)
        return result.scalars().all()

    @classmethod
    @transactional
    async def delete_file_chunks(
        cls, session: AsyncSession, user_id: UUID, file_id: UUID
    ) -> None:
        """Удаляет чанки, связанные с файлом пользователя."""
        await session.execute(
            db.delete(DBChunk).filter_by(user_id=user_id, file_id=file_id)
        )

    @classmethod
    @transactional
    async def get_chunks_by_ids(
        cls,
        session: AsyncSession,
        user_id: UUID,
        chunk_ids: list[UUID],
    ) -> list[DBChunk]:
        """Возвращает принадлежащие пользователю чанки по их ID."""
        if not chunk_ids:
            return []

        result = await session.execute(
            db.select(DBChunk).filter(
                DBChunk.user_id == user_id, DBChunk.id.in_(chunk_ids)
            )
        )
        return result.scalars().all()
