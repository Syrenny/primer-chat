from loguru import logger
from pydantic import ValidationError
from shared_config import config
from shared_kafka.base import BaseKafkaConsumer
from shared_models.indexation.interface import IndexationWorkerResponse
from src.db.session import session_manager
from src.services.chunks import ChunkService
from src.services.files import FileProcessor, FileService


class IndexationResultConsumer(BaseKafkaConsumer):
    def __init__(self):
        super().__init__(
            topic=config.kafka.indexation.response.topic,
            group_id=config.kafka.indexation.response.group_id,
        )

    async def handle_message(self, payload: dict):
        try:
            data = IndexationWorkerResponse.model_validate_json(payload)
        except ValidationError as err:
            logger.error(
                logger.error(f"[indexation] ❌ Ошибка валидации ответа воркера: {err}")
            )
            return

        if data.error:
            logger.warning(f"[indexation] ⚠️ Ошибка индексации: {data.error}")
            async with session_manager.session() as session:
                await FileProcessor.delete(
                    user_id=data.context.user_id,
                    session=session,
                    file_id=data.context.file_id,
                )
            return

        try:
            async with session_manager.session() as session:
                await ChunkService.save_chunks(
                    file_id=data.context.file_id,
                    user_id=data.context.user_id,
                    chunks=data.result.chunks,
                    session=session,
                )

                await FileService.set_is_indexed(
                    file_id=data.context.file_id,
                    user_id=data.context.user_id,
                    session=session,
                    value=True,
                )
                logger.info(
                    f"[indexation] ✅ Успешно проиндексирован файл {data.context.file_id}"
                )

        except Exception as err:
            logger.exception(f"[indexation] ❌ Ошибка при сохранении чанков: {err}")

            async with session_manager.session() as session:
                user_context = data.context
                await FileProcessor.delete(
                    user_id=user_context.user_id,
                    session=session,
                    file_id=user_context.file_id,
                )
