from loguru import logger
from pydantic import ValidationError
from shared_config import config
from shared_kafka.base import BaseKafkaConsumer
from shared_models.generation.interface import GenerationWorkerResponse
from src.db.session import session_manager
from src.services.messages import MessageService


class GenerationResultConsumer(BaseKafkaConsumer):
    def __init__(self) -> None:
        super().__init__(
            topic=config.kafka.generation.response.topic,
            group_id=config.kafka.generation.response.group_id,
        )

    async def handle_message(self, payload: dict) -> None:
        try:
            data = GenerationWorkerResponse.model_validate_json(payload)
        except ValidationError as err:
            logger.error(f"[generation] ❌ Ошибка валидации ответа воркера: {err}")
            return

        buffer = await MessageService.get_buffer(user_id=data.context.user_id)

        if not buffer:
            logger.warning(
                f"[generation] Пустой буфер для user_id={data.context.user_id}"
            )
            return

        async with session_manager.session() as session:
            await MessageService.create_assistant_message(
                session=session,
                user_id=data.context.user_id,
                history_id=data.context.history_id,
                request_id=data.context.request_id,
                content=buffer,
            )

        await MessageService.clear_buffer(user_id=data.context.user_id)
