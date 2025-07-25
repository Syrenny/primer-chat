from shared_models.generation.interface import GenerationWorkerRequest
from src.config import config
from src.consumers.base import BaseKafkaProducer


class GenerationProducer(BaseKafkaProducer):
    async def send(self, payload: GenerationWorkerRequest):
        await self.send_json(
            topic=config.kafka.indexation.request.topic, payload=payload
        )
