from shared_config import config as global_config
from shared_kafka.base import BaseKafkaProducer
from shared_models.generation.interface import GenerationWorkerRequest


class GenerationProducer(BaseKafkaProducer):
    async def send(self, payload: GenerationWorkerRequest):
        await self.send_json(
            topic=global_config.kafka.generation.request.topic, payload=payload
        )
