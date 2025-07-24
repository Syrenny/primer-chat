from uuid import UUID

import sqlalchemy as db
from sqlalchemy.ext.asyncio import AsyncSession
from src.db.models import DBChunk
from src.db.wrap import transactional


class DaoChunks:
    @classmethod
    @transactional
    async def save_file_chunks(
        cls, session: AsyncSession, user_id: UUID, meta: FileMeta, chunks: list[str]
    ) -> None:
        """Сохраняет чанки в БД."""
        embeddings = get_langchain_embeddings()
        chunk_objects = [
            DBChunk(
                user_id=user_id,
                filename=meta.filename,
                file_id=meta.file_id,
                chunk_text=chunk,
                embedding=embeddings.embed_query(chunk),
            )
            for chunk in chunks
        ]
        session.add_all(chunk_objects)

    @classmethod
    @transactional
    async def find_file_chunks(
        cls,
        session: AsyncSession,
        query: str,
        user_id: UUID,
        file_id: UUID,
        limit: int = 5,
    ) -> list[DBChunk]:
        """Ищет чанки с помощью pgvector."""
        embeddings = get_langchain_embeddings()
        query_vector = embeddings.embed_query(query)

        result = await session.execute(
            db.select(DBChunk)
            .filter(DBChunk.user_id == user_id, DBChunk.file_id == file_id)
            .order_by(DBChunk.embedding.l2_distance(query_vector))
            .limit(limit)
        )
        return result.scalars().all()

    @classmethod
    @transactional
    async def delete_file_chunks(
        cls, session: AsyncSession, user_id: UUID, filename: str, file_id: UUID
    ) -> None:
        """Удаляет чанки, связанные с файлом пользователя."""
        await session.execute(
            db.delete(DBChunk).filter_by(
                user_id=user_id, filename=filename, file_id=file_id
            )
        )
