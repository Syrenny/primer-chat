from shared_models.indexation.interface import IndexationWorkerRequest
from src.config import config
from src.consumers.base import BaseKafkaProducer


class IndexationProducer(BaseKafkaProducer):
    async def send(self, payload: IndexationWorkerRequest):
        await self.send_json(
            topic=config.kafka.indexation.request.topic, payload=payload
        )
