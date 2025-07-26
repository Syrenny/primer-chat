from functools import lru_cache
from uuid import UUID

from shared_adapters.openai import Embeddings
from shared_models.indexation.core import ChunkPosition, IndexedChunk
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
        embeddings_client = get_embeddings()

        contents = [chunk.content for chunk in chunks]
        embeddings = embeddings_client.embed(contents)

        await DaoChunks.save_file_chunks(
            session=session,
            user_id=user_id,
            file_id=file_id,
            chunks=chunks,
            embeddings=embeddings,
        )

    @classmethod
    def from_db_chunks(cls, db_chunks: list[DBChunk]) -> list[IndexedChunk]:
        return [
            IndexedChunk(
                content=db_chunk.content,
                embedding=db_chunk.embedding,
                html_tag=db_chunk.html_tag,
                position=ChunkPosition(
                    xyxy=db_chunk.xyxy,
                    start_line=db_chunk.start_line,
                    end_line=db_chunk.end_line,
                ),
            )
            for db_chunk in db_chunks
        ]

    @classmethod
    async def find_chunks(
        cls, user_id: UUID, file_id: UUID, session: AsyncSession, query: str
    ) -> list[IndexedChunk]:
        embeddings_client = get_embeddings()

        query_embedding = await embeddings_client.embed_one(query)

        db_chunks = await DaoChunks.find_file_chunks(
            session=session,
            user_id=user_id,
            file_id=file_id,
            query_embedding=query_embedding,
        )

        return cls.from_db_chunks(db_chunks)

    @classmethod
    async def delete_chunks(
        cls, user_id: UUID, file_id: UUID, session: AsyncSession
    ) -> None:
        await DaoChunks.delete_file_chunks(
            session=session, user_id=user_id, file_id=file_id
        )
