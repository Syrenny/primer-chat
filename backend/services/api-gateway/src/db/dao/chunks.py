from uuid import UUID

import sqlalchemy as db
from shared_models.indexation.core import IndexedChunk
from sqlalchemy.ext.asyncio import AsyncSession
from src.db.models import DBChunk
from src.db.wrap import transactional


class DaoChunks:
    @classmethod
    @transactional
    async def save_file_chunks(
        cls,
        session: AsyncSession,
        user_id: UUID,
        file_id: UUID,
        embeddings: list[list[float]],
        chunks: list[IndexedChunk],
    ) -> None:
        """Сохраняет чанки в БД."""
        chunk_objects = [
            DBChunk(
                user_id=user_id,
                file_id=file_id,
                content=chunk.content,
                embedding=embedding,
                html_tag=chunk.html_tag,
                xyxy=chunk.position.xyxy,
                start_line=chunk.position.start_line,
                end_line=chunk.position.end_line,
            )
            for chunk, embedding in zip(chunks, embeddings)
        ]
        session.add_all(chunk_objects)

    @classmethod
    @transactional
    async def find_file_chunks(
        cls,
        session: AsyncSession,
        user_id: UUID,
        file_id: UUID,
        query_embedding: list[float],
        limit: int = 5,
    ) -> list[DBChunk]:
        """Ищет чанки с помощью pgvector."""
        result = await session.execute(
            db.select(DBChunk)
            .filter(DBChunk.user_id == user_id, DBChunk.file_id == file_id)
            .order_by(DBChunk.embedding.l2_distance(query_embedding))
            .limit(limit)
        )
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
