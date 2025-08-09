from shared_adapters.kafka import BaseKafkaProducer
from shared_config import config
from shared_models.indexation.interface import IndexationWorkerRequest


class IndexationProducer(BaseKafkaProducer):
    async def send(self, payload: IndexationWorkerRequest):
        await self.send_json(
            topic=config.kafka.indexation.request.topic, payload=payload
        )
