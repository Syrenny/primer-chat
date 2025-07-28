import asyncio
from uuid import UUID

from loguru import logger
from shared_models.indexation.core import IndexedChunk
from sqlalchemy.ext.asyncio import AsyncSession
from src.config import config as local_config
from src.db.dao.history_meta import DaoHistoryMeta
from src.services.chunks import ChunkService


class RetrieveService:
    @classmethod
    async def retrieve(
        cls, session: AsyncSession, user_id: UUID, history_id: UUID, query: str
    ) -> list[IndexedChunk]:
        history_meta = await DaoHistoryMeta.get_history_meta(
            session=session, user_id=user_id, history_id=history_id
        )
        if not history_meta:
            raise ValueError(
                f"HistoryMeta not found for user {user_id} and history {history_id}"
            )

        retrieved_chunks_tasks = [
            ChunkService.find_chunks(
                file_id=db_file_meta.file_id,
                user_id=user_id,
                session=session,
                query=query,
                limit=local_config.retriever.max_chunks_per_file,
            )
            for db_file_meta in history_meta.files
        ]

        results = await asyncio.gather(*retrieved_chunks_tasks, return_exceptions=True)

        chunks: list[IndexedChunk] = []
        for file_meta, result in zip(history_meta.files, results):
            if isinstance(result, Exception):
                logger.warning(
                    f"[Retriever] ⚠️ Failed to retrieve chunks from file {file_meta.file_id}: {result}"
                )
                continue
            result.sort(key=lambda c: (c.position.start_line, c.position.end_line))
            chunks.extend(result)

        logger.debug(
            f"[Retriever] Retrieved {len(chunks)} chunks for query '{query}' in history {history_id}"
        )
        return chunks
