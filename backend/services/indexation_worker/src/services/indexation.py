import asyncio
from typing import AsyncIterator

from loguru import logger
from shared_adapters.redis import RedisIndexationProgressBuffer
from shared_models.indexation.core import IndexationWorkerResult, IndexedChunk
from shared_models.indexation.interface import (
    IndexationProgressError,
    IndexationProgressResponse,
)
from shared_models.openai.completions import Usage
from shared_models.worker.context import WorkerRequestContext
from src.services.embed import BatchEmbedder
from src.services.extract import FitzService
from src.services.segmentation import (
    LineSignature,
    SegmentationResult,
    SegmentationService,
)


class ProgressService:
    @classmethod
    async def send_progress(cls, ctx: WorkerRequestContext, progress: float) -> None:
        # Защита от вылета за пределы
        p = max(0.0, min(1.0, float(progress)))
        msg = IndexationProgressResponse(
            type="response",
            context=ctx,
            progress=p,
        )
        await RedisIndexationProgressBuffer.commit_progress(
            user_id=ctx.user_id,
            file_id=ctx.file_id,
            progress=msg,
        )

    @classmethod
    async def send_error(cls, ctx: WorkerRequestContext) -> None:
        msg = IndexationProgressError(type="error")

        await RedisIndexationProgressBuffer.commit_progress(
            user_id=ctx.user_id,
            file_id=ctx.file_id,
            progress=msg,
        )


class IndexationService:
    def __init__(self) -> None:
        self.segmentation_service = SegmentationService()
        self.batch_embedder = BatchEmbedder()

    async def run(
        self, pdf_bytes: bytes, ctx: WorkerRequestContext
    ) -> IndexationWorkerResult:
        indexed_chunks: list[IndexedChunk] = []
        total_llm_usage = Usage()

        line_batches = list(FitzService.batch_lines(pdf_bytes))
        await ProgressService.send_progress(ctx=ctx, progress=0.05)

        async for partial_results, frac in self._segment_batches(line_batches):
            for lines, res, usage in partial_results:
                total_llm_usage += usage
                indexed_chunks.extend(self._process_segmented_chunks(lines, res))
            await ProgressService.send_progress(ctx, 0.05 + 0.65 * frac)

        await ProgressService.send_progress(ctx, 0.80)

        embeddings = await self.batch_embedder.compute()

        for chunk, emb in zip(indexed_chunks, embeddings):
            chunk.embedding = emb

        await ProgressService.send_progress(ctx, 1.00)

        return IndexationWorkerResult(
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
            content = FitzService.get_content(chunk_lines).strip()
            if not content:
                continue

            self.batch_embedder.append(content)

            result_chunks.append(
                IndexedChunk(
                    content=content,
                    embedding=[],
                    html_tag=chunk.html_tag,
                    positions=[line.position for line in chunk_lines],
                )
            )

            logger.info(
                f"Chunk [{chunk.start_line}-{chunk.end_line}] → <{chunk.html_tag}>"
            )

        return result_chunks

    async def _segment_batches(
        self, batches: list[list[LineSignature]]
    ) -> AsyncIterator[
        tuple[list[tuple[list[LineSignature], SegmentationResult, Usage]], float]
    ]:
        total = len(batches) or 1

        async def run_with_batch(batch: list[LineSignature]):
            res, usage = await self.segmentation_service.limited_segment(batch)
            return batch, res, usage

        tasks = [asyncio.create_task(run_with_batch(batch)) for batch in batches]

        done = 0
        buffer: list[tuple[list[LineSignature], SegmentationResult, Usage]] = []

        for fut in asyncio.as_completed(tasks):
            batch, res, usage = await fut
            buffer.append((batch, res, usage))
            done += 1

            if len(buffer) >= 4 or done == total:
                yield buffer, done / total
                buffer.clear()
