import asyncio
from itertools import islice
from typing import Iterable

from loguru import logger
from shared_adapters.openai import Embeddings
from shared_config import config as global_config
from shared_models.openai.embeddings import EmbeddingsResponse, EmbeddingsUsage
from src.config import config as local_config


class BatchEmbedder:
    def __init__(self) -> None:
        self._buffered_texts: list[str] = []
        self.embeddings = Embeddings()
        self.embeddings_usage = EmbeddingsUsage()

    def append(self, content: str) -> None:
        text = (content or "").strip()

        if text:
            self._buffered_texts.append(text)
        else:
            logger.debug("Skipped empty text in BatchEmbedder.append()")

    def _validate_embeddings(self, response: EmbeddingsResponse) -> None:
        for emb in response.embeddings:
            if len(emb) != global_config.embeddings.dimensions:
                raise ValueError(
                    f"Embedding has invalid dimension. Expected {global_config.embeddings.dimensions}, got {len(emb)}"
                )

    def _batch_chunks(self) -> Iterable[list[str]]:
        it = iter(self._buffered_texts)
        while True:
            batch = list(islice(it, local_config.embeddings_batch_size))
            if not batch:
                break
            yield batch

    async def compute(self) -> list[list[float]]:
        batches = list(self._batch_chunks())

        self.flush()

        if not batches:
            return []

        tasks = [self.embeddings.embed(batch) for batch in batches]

        result: list[list[float]] = []
        responses = await asyncio.gather(*tasks, return_exceptions=True)

        for batch, response in zip(batches, responses):
            if isinstance(response, Exception):
                logger.error(f"❌ Ошибка при эмбеддинге. Batch: {batch}")
                raise RuntimeError(f"Embedding failed: {response}")
            self._validate_embeddings(response)
            result.extend(response.embeddings)
            self.embeddings_usage += response.usage

        return result

    def flush(self) -> None:
        self._buffered_texts = []
        self.embeddings_usage = EmbeddingsUsage()
