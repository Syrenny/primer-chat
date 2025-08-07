import asyncio

from loguru import logger
from shared_models.indexation.core import IndexationResult, IndexedChunk
from shared_models.openai.completions import Usage
from src.services.embed import BatchEmbedder
from src.services.extract import FitzService
from src.services.segmentation import (
    LineSignature,
    SegmentationResult,
    SegmentationService,
)


class IndexationService:
    def __init__(self) -> None:
        self.segmentation_service = SegmentationService()
        self.batch_embedder = BatchEmbedder()

    async def run(self, pdf_bytes: bytes) -> IndexationResult:
        indexed_chunks: list[IndexedChunk] = []
        total_llm_usage = Usage()

        line_batches = list(FitzService.batch_lines(pdf_bytes))
        segmentation_results = await self._segment_batches(line_batches)

        for lines, (result, usage) in zip(line_batches, segmentation_results):
            total_llm_usage += usage
            indexed_chunks += self._process_segmented_chunks(lines, result)

        embeddings = await self.batch_embedder.compute()
        for chunk, emb in zip(indexed_chunks, embeddings):
            chunk.embedding = emb

        return IndexationResult(
            chunks=indexed_chunks,
            llm_usage=total_llm_usage,
            embeddings_usage=self.batch_embedder.embeddings_usage,
        )

    def _process_segmented_chunks(
        self, lines: list[LineSignature], result: SegmentationResult
    ) -> list[IndexedChunk]:
        result_chunks = []

        for chunk in result.chunks:
            chunk_lines = lines[chunk.start_line : chunk.end_line + 1]
            content = FitzService.get_content(chunk_lines)
            self.batch_embedder.append(content)

            result_chunks.append(
                IndexedChunk(
                    content=content,
                    embedding=[],
                    html_tag=chunk.html_tag,
                    position=[line.position for line in chunk_lines],
                )
            )

            logger.info(
                f"Chunk [{chunk.start_line}-{chunk.end_line}] → <{chunk.html_tag}>"
            )

        return result_chunks

    async def _segment_batches(self, batches: list[list[LineSignature]]):
        tasks = [self.segmentation_service.limited_segment(batch) for batch in batches]
        return await asyncio.gather(*tasks)
