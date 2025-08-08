from uuid import UUID

from shared_models.indexation.core import (
    ExtendedIndexedChunk,
    IndexedChunk,
    PdfLinePosition,
)
from sqlalchemy.ext.asyncio import AsyncSession
from src.db.dao import DaoChunks
from src.db.models import DBChunk


class ChunkService:
    @classmethod
    async def save_chunks(
        cls,
        user_id: UUID,
        file_id: UUID,
        session: AsyncSession,
        chunks: list[IndexedChunk],
    ) -> None:
        await DaoChunks.save_file_chunks(
            session=session,
            user_id=user_id,
            file_id=file_id,
            chunks=chunks,
        )

    @classmethod
    async def delete_chunks(
        cls, user_id: UUID, file_id: UUID, session: AsyncSession
    ) -> None:
        await DaoChunks.delete_file_chunks(
            session=session, user_id=user_id, file_id=file_id
        )

    @classmethod
    async def from_ids(
        cls, user_id: UUID, session: AsyncSession, ids: list[UUID]
    ) -> list[DBChunk]:
        return await DaoChunks.get_chunks_by_ids(
            session=session, user_id=user_id, chunk_ids=ids
        )

    @classmethod
    def from_db_chunks(cls, db_chunks: list[DBChunk]) -> list[ExtendedIndexedChunk]:
        return [
            ExtendedIndexedChunk(
                file_id=db_chunk.file_id,
                content=db_chunk.content,
                embedding=db_chunk.embedding.tolist(),
                html_tag=db_chunk.html_tag,
                positions=[
                    PdfLinePosition.model_validate(pos) for pos in db_chunk.positions
                ],
            )
            for db_chunk in db_chunks
        ]
