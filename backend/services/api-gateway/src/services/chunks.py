from functools import lru_cache
from uuid import UUID

from shared_adapters.openai import Embeddings
from shared_models.indexation.core import IndexedChunk, PdfLinePosition
from sqlalchemy.ext.asyncio import AsyncSession
from src.db.dao import DaoChunks
from src.db.models import DBChunk


@lru_cache
def get_embeddings() -> Embeddings:
    return Embeddings()


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
    def from_db_chunks(cls, db_chunks: list[DBChunk]) -> list[IndexedChunk]:
        return [
            IndexedChunk(
                content=db_chunk.content,
                embedding=db_chunk.embedding.tolist(),
                html_tag=db_chunk.html_tag,
                position=[
                    PdfLinePosition.model_validate(pos) for pos in db_chunk.position
                ],
            )
            for db_chunk in db_chunks
        ]

    @classmethod
    async def find_chunks(
        cls, user_id: UUID, file_id: UUID, session: AsyncSession, query: str, limit: int
    ) -> list[IndexedChunk]:
        embeddings_client = get_embeddings()

        embeddings_response = await embeddings_client.embed_one(query)

        db_chunks = await DaoChunks.find_file_chunks(
            session=session,
            user_id=user_id,
            file_id=file_id,
            query_embedding=embeddings_response.data[0].embedding,
            limit=limit,
        )

        return cls.from_db_chunks(db_chunks)

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
