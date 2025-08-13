from functools import lru_cache
from uuid import UUID

from loguru import logger
from shared_adapters.openai import Embeddings
from shared_models.indexation.core import ExtendedIndexedChunk
from sqlalchemy.ext.asyncio import AsyncSession
from src.config import config as local_config
from src.db.dao import DaoChunks
from src.db.models import DBChunk
from src.services.chunks import ChunkService
from src.services.request import RequestService


@lru_cache
def get_embeddings() -> Embeddings:
    return Embeddings()


class RetrieveService:
    @classmethod
    async def find_chunks(
        cls,
        user_id: UUID,
        history_id: UUID,
        session: AsyncSession,
        query: str,
    ) -> list[DBChunk]:
        embeddings_client = get_embeddings()

        embeddings_response = await embeddings_client.embed_one(query)

        return await DaoChunks.find_history_chunks(
            session=session,
            user_id=user_id,
            history_id=history_id,
            query_embedding=embeddings_response.data[0].embedding,
            limit=local_config.retriever.limit,
        )

    @classmethod
    async def retrieve_and_save(
        cls,
        session: AsyncSession,
        user_id: UUID,
        history_id: UUID,
        request_id: UUID,
        query: str,
    ) -> list[ExtendedIndexedChunk]:
        db_chunks = await cls.find_chunks(
            history_id=history_id,
            user_id=user_id,
            session=session,
            query=query,
        )

        await RequestService.update_request(
            user_id=user_id, request_id=request_id, session=session, chunks=db_chunks
        )

        chunks = ChunkService.from_db_chunks(db_chunks)

        logger.debug(
            f"[Retriever] Retrieved {len(chunks)} chunks for query '{query}' in history {history_id}"
        )
        return chunks
