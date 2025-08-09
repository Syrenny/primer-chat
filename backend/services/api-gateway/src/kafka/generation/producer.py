from shared_adapters.kafka import BaseKafkaProducer
from shared_config import config as global_config
from shared_models.worker.context import WorkerRequestContext


class GenerationProducer(BaseKafkaProducer):
    async def send(self, payload: WorkerRequestContext):
        await self.send_json(
            topic=global_config.kafka.generation.request.topic, payload=payload
        )
