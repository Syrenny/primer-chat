from shared_config import config
from shared_models.indexation.interface import IndexationWorkerResponse
from src.consumers.base import BaseKafkaConsumer
from src.db.session import session_manager
from src.services.chunks import ChunkService
from src.services.files import FileService


class IndexationResultConsumer(BaseKafkaConsumer):
    def __init__(self):
        super().__init__(
            topic=config.kafka.indexation.response.topic,
            group_id=config.kafka.indexation.response.group_id,
        )

    async def handle_message(self, payload: dict):
        data = IndexationWorkerResponse.model_validate(payload)

        async with session_manager.session() as session:
            await ChunkService.save_chunks(
                file_id=data.context.file_id,
                user_id=data.context.user_id,
                chunks=data.chunks,
                session=session,
            )

            await FileService.set_is_indexed(
                file_id=data.context.file_id,
                user_id=data.context.user_id,
                session=session,
                value=True,
            )
