from loguru import logger
from pydantic import ValidationError
from shared_config import config
from shared_kafka.base import BaseKafkaConsumer
from shared_models.generation.interface import GenerationWorkerResponse
from src.db.session import session_manager
from src.services.messages import GenerationBufferService
from src.services.request import RequestService


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

        buffer = await GenerationBufferService.get_buffer(user_id=data.context.user_id)

        if not buffer:
            logger.warning(
                f"[generation] Пустой буфер для user_id={data.context.user_id}"
            )
            return

        async with session_manager.session() as session:
            await RequestService.update_request(
                user_id=data.context.user_id,
                request_id=data.context.request_id,
                session=session,
                assistant_message=buffer,
            )

        await GenerationBufferService.clear_buffer(user_id=data.context.user_id)
