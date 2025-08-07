from uuid import UUID

from loguru import logger
from pydantic import ValidationError
from shared_adapters.redis import RedisGenerationBuffer
from shared_models.generation.interface import GenerationWorkerChunkResponse
from shared_models.openai.completions import ChatMessage
from sqlalchemy.ext.asyncio import AsyncSession
from src.db.dao import DaoMessages
from src.db.models import DBChunk


class MessageService:
    @classmethod
    async def add_user_message(
        cls,
        user_id: UUID,
        history_id: UUID,
        session: AsyncSession,
        query: str,
        request_id: UUID,
    ) -> None:
        chat_message = ChatMessage(role="user", content=query)

        await DaoMessages.add_message(
            session=session,
            user_id=user_id,
            history_id=history_id,
            data=chat_message,
            request_id=request_id,
            chunks=[],
        )

    @classmethod
    async def create_assistant_message(
        cls,
        user_id: UUID,
        history_id: UUID,
        session: AsyncSession,
        request_id: UUID,
        content: str,
        chunks: list[DBChunk],
    ) -> None:
        chat_message = ChatMessage(role="assistant", content=content)

        await DaoMessages.add_message(
            session=session,
            user_id=user_id,
            history_id=history_id,
            request_id=request_id,
            data=chat_message,
            chunks=chunks,
        )

    @classmethod
    async def get_buffer(
        cls,
        user_id: UUID,
    ) -> str:
        raw_chunks = await RedisGenerationBuffer.load_chunks(user_id=user_id)

        chunks = []

        for raw_chunk in raw_chunks:
            try:
                chunk = GenerationWorkerChunkResponse.model_validate_json(raw_chunk)
            except ValidationError as err:
                logger.error(f"Invalid chunk from Redis: {str(err)}")
                continue

            if chunk.type == "default":
                chunks.append(chunk.chunk)

        return "".join(chunks)

    @classmethod
    async def clear_buffer(
        cls,
        user_id: UUID,
    ) -> None:
        await RedisGenerationBuffer.clear_all(user_id=user_id)
