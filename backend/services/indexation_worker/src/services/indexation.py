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
from src.config import config as local_config
from src.models.core import LineSignature
from src.services.embed import BatchEmbedder
from src.services.extract import FitzService
from src.services.segmentation import SegmentationResult, SegmentationService
from src.services.summarization import SummarizationService


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
        self.summarization_service = SummarizationService()

    async def run(
        self, pdf_bytes: bytes, ctx: WorkerRequestContext
    ) -> IndexationWorkerResult:
        indexed_chunks: list[IndexedChunk] = []
        total_llm_usage = Usage()

        # 0) Извлечение строк батчами
        line_batches = list(FitzService.batch_lines(pdf_bytes))
        await ProgressService.send_progress(ctx=ctx, progress=0.05)
        logger.info(f"🧾 Извлечено батчей страниц: {len(line_batches)}")

        # 1) LLM-сегментация → leaves (чанкинг)
        async for partial_results, frac in self._segment_batches(line_batches):
            for lines, res, usage in partial_results:
                total_llm_usage += usage
                leaves = self._process_segmented_chunks(lines, res)
                indexed_chunks.extend(leaves)
            await ProgressService.send_progress(ctx, 0.05 + 0.55 * frac)

        logger.info(
            f"🌿 Сформировано leaves: {len([c for c in indexed_chunks if c.level == 'leaves'])}"
        )
        await ProgressService.send_progress(ctx, 0.60)

        # 2) Sections/document через оверлап-окна по страницам
        # Материализуем все линии, чтобы построить окна по страницам
        all_lines: list[LineSignature] = []
        for batch in line_batches:
            all_lines.extend(batch)
        sections, doc_chunk, usage_sum = await self._build_hierarchy(all_lines)
        total_llm_usage += usage_sum

        indexed_chunks.extend(sections)
        if doc_chunk:
            indexed_chunks.append(doc_chunk)

        logger.info(f"📚 Секции: {len(sections)}, документ: {1 if doc_chunk else 0}")
        await ProgressService.send_progress(ctx, 0.80)

        # 3) Эмбеддинги
        embeddings = await self.batch_embedder.compute()

        if len(embeddings) != len(indexed_chunks):
            logger.error(
                "❌ Embedding count mismatch: chunks=%d embeddings=%d",
                len(indexed_chunks),
                len(embeddings),
            )
            raise RuntimeError("Embedding count mismatch")

        for chunk, emb in zip(indexed_chunks, embeddings):
            chunk.embedding = emb

        await ProgressService.send_progress(ctx, 1.00)
        logger.info(f"✅ Индексация завершена. Чанков всего: {len(indexed_chunks)}")
        logger.debug(f"✅ total_llm_usage: {total_llm_usage}")
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
                logger.debug(
                    f"⚠️ Пустой контент в чанке [{chunk.start_line}-{chunk.end_line}] — пропуск"
                )
                continue

            first_page = min(l.position.page for l in chunk_lines)
            last_page = max(l.position.page for l in chunk_lines)

            embed_mode = local_config.embed_mode  # "content" | "summary" | "hybrid"
            to_embed = content
            if embed_mode == "summary" and chunk.local_summary:
                to_embed = f"{chunk.title}\n\n{chunk.local_summary}"
            elif embed_mode == "hybrid" and chunk.local_summary:
                to_embed = f"{chunk.title}\n\n{chunk.local_summary}\n\n{content[: local_config.embed_hybrid_prefix_chars]}"

            self.batch_embedder.append(to_embed)

            result_chunks.append(
                IndexedChunk(
                    content=content,
                    embedding=[],
                    positions=[line.position for line in chunk_lines],
                    title=chunk.title or None,
                    keyphrases=chunk.keyphrases or [],
                    local_summary=chunk.local_summary or None,
                    level="leaves",
                    start_line=chunk.start_line,
                    end_line=chunk.end_line,
                    page_span=[first_page, last_page],
                )
            )

            logger.info(
                f"🧩 Leaf [{chunk.start_line}-{chunk.end_line}] "
                f"p{first_page}…p{last_page} ({len(content)} ch) "
                f"title='{(chunk.title or '').strip()[:60]}' "
                f"keys={len(chunk.keyphrases)}"
            )

        return result_chunks

    async def _segment_batches(
        self, batches: list[list[LineSignature]]
    ) -> AsyncIterator[
        tuple[list[tuple[list[LineSignature], SegmentationResult, Usage]], float]
    ]:
        total = len(batches) or 1
        max_in_flight = local_config.max_concurrent_segments
        it = iter(batches)
        in_flight: set[asyncio.Task] = set()
        done = 0
        buffer: list[tuple[list[LineSignature], SegmentationResult, Usage]] = []

        async def run_with_batch(batch: list[LineSignature]):
            res, usage = await self.segmentation_service.limited_segment(batch)
            return batch, res, usage

        # первичная загрузка
        for _ in range(min(max_in_flight, total)):
            try:
                b = next(it)
            except StopIteration:
                break
            in_flight.add(asyncio.create_task(run_with_batch(b)))

        while in_flight:
            done_task = await asyncio.wait(
                in_flight, return_when=asyncio.FIRST_COMPLETED
            )
            finished = list(done_task[0])
            in_flight -= set(finished)
            for fut in finished:
                batch, res, usage = await fut
                buffer.append((batch, res, usage))
                done += 1
                # подкидываем новые
                try:
                    b = next(it)
                    in_flight.add(asyncio.create_task(run_with_batch(b)))
                except StopIteration:
                    pass
            if buffer and (len(buffer) >= 4 or done == total):
                yield buffer, done / total
                buffer.clear()

    async def _build_hierarchy(
        self, all_lines: list[LineSignature]
    ) -> tuple[list[IndexedChunk], IndexedChunk | None, Usage]:
        """Sections + document слои. Возвращает (sections, document, суммарный usage)."""
        total_usage = Usage()
        sections: list[IndexedChunk] = []

        materialized = self.summarization_service.materialize_windows(all_lines)
        if not materialized:
            logger.warning("⚠️ Окна для секций не построены — пропуск уровня sections")
            return sections, None, total_usage

        # параллельно саммаризируем окна
        async def run_window(ws: tuple[tuple[int, int], list[LineSignature]]):
            (start_page, end_page), window_lines = ws
            summary, usage = await self.summarization_service.limited_summarize_section(
                window_lines
            )
            content = summary.strip()
            return start_page, end_page, window_lines, content, usage

        tasks = [asyncio.create_task(run_window(w)) for w in materialized]
        logger.info(f"🪟 Всего окон для секций: {len(tasks)}")

        for fut in asyncio.as_completed(tasks):
            start_page, end_page, window_lines, content, usage = await fut
            total_usage += usage

            if not content:
                logger.debug(f"⚠️ Пустое секционное саммари p{start_page}…p{end_page}")
                continue

            # эмбеддим секционное саммари
            self.batch_embedder.append(content)

            sections.append(
                IndexedChunk(
                    content=content,
                    embedding=[],
                    positions=[ln.position for ln in window_lines],
                    level="sections",
                    start_line=min(ln.index for ln in window_lines)
                    if window_lines
                    else None,
                    end_line=max(ln.index for ln in window_lines)
                    if window_lines
                    else None,
                    page_span=[start_page, end_page],
                )
            )
            logger.info(f"📦 Section p{start_page}…p{end_page} ({len(content)} ch)")
            logger.debug(f"📦 {content}")

        # документное саммари — по секционным саммари
        doc_chunk: IndexedChunk | None = None
        if sections:
            section_texts = [
                s.content
                for s in sorted(sections, key=lambda x: (x.page_span or (0, 0))[0])
            ]
            doc_summary, usage = await self.summarization_service.summarize_document(
                section_texts
            )
            total_usage += usage
            doc_content = doc_summary.strip()
            if doc_content:
                self.batch_embedder.append(doc_content)
                first_page = min((s.page_span or (1, 1))[0] for s in sections)
                last_page = max((s.page_span or (1, 1))[1] for s in sections)
                # positions для документа берём "реперные": первая и последняя линии
                first_pos = sections[0].positions[0] if sections[0].positions else None
                last_pos = (
                    sections[-1].positions[-1] if sections[-1].positions else None
                )
                positions = []
                if first_pos:
                    positions.append(first_pos)
                if last_pos and last_pos != first_pos:
                    positions.append(last_pos)

                doc_chunk = IndexedChunk(
                    content=doc_content,
                    embedding=[],
                    positions=positions,
                    level="document",
                    start_line=None,
                    end_line=None,
                    page_span=[first_page, last_page],
                )
                logger.info(
                    f"🗂️ Document summary ({len(doc_content)} ch) p{first_page}…p{last_page}"
                )
                logger.info(f"🗂️ {doc_content}")
            else:
                logger.warning("⚠️ Пустое документное саммари")

        return sections, doc_chunk, total_usage
