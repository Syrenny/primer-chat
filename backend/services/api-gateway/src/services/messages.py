from uuid import UUID

from loguru import logger
from pydantic import ValidationError
from shared_adapters.redis import RedisGenerationBuffer
from shared_models.generation.interface import GenerationWorkerChunkResponse


class GenerationBufferService:
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
