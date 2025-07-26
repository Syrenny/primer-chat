import asyncio
from itertools import islice
from typing import Iterable, List

import fitz
from loguru import logger
from pydantic import ValidationError
from shared_models.indexation.core import ChunkPosition, IndexationResult, IndexedChunk
from shared_models.indexation.segmentation import LineSignature, StyleKey
from shared_models.openai.completions import Usage
from shared_models.openai.embeddings import EmbeddingsResponse, EmbeddingsUsage
from shared_adapters.openai import Embeddings
from src.config import config
from src.services.segmentation import SegmentationService


class FitzUtils:
    @classmethod
    def get_chunk_xyxy(
        cls, lines: List[LineSignature]
    ) -> tuple[float, float, float, float]:
        """Получить объединённый bbox для нескольких строк"""
        full_bbox = None
        for line in lines:
            line_bbox = fitz.Rect(line.style.bbox)
            if line_bbox is not None:
                full_bbox = line_bbox if full_bbox is None else full_bbox | line_bbox
        if full_bbox is None:
            full_bbox = fitz.Rect(0, 0, 0, 0)
        return tuple(full_bbox)

    @classmethod
    def get_content(cls, lines: List[LineSignature]) -> str:
        text = " ".join([line.content for line in lines])
        return text.strip()

    @classmethod
    def style_key(cls, span: dict) -> StyleKey:
        return StyleKey(
            font=span["font"],
            size=round(span["size"], 2),
            flags=span.get("flags", 0),
            bbox=span.get("bbox"),
        )

    @classmethod
    def extract_lines(cls, pages: List[fitz.Page]) -> List[LineSignature]:
        result = []
        line_index = 0

        for page in pages:
            text = page.get_text("dict")
            for block in text.get("blocks", []):
                if block.get("type") != 0:
                    continue

                for line in block.get("lines", []):
                    line_content = " ".join(
                        span["text"]
                        for span in line.get("spans", [])
                        if span.get("text")
                    )
                    if not line_content.strip():
                        continue

                    main_span = line["spans"][0]
                    result.append(
                        LineSignature(
                            index=line_index,
                            content=line_content,
                            style=cls.style_key(main_span),
                        )
                    )
                    line_index += 1

        return result


class BatchEmbedder:
    def __init__(self) -> None:
        self._buffered_texts: list[str] = []
        self.embeddings = Embeddings()
        self.embeddings_usage = EmbeddingsUsage()

    def append(self, content: str) -> None:
        self._buffered_texts.append(content)

    def _validate_embeddings(self, response: EmbeddingsResponse) -> None:
        length = len(response.embeddings)
        if length != config.embeddings_dimensions:
            raise ValidationError(
                f"Invalid embeddings dimension. Expected {config.embeddings_dimensions}, got {length}"
            )

    def _batch_chunks(self) -> Iterable[list[str]]:
        it = iter(self._buffered_texts)
        while True:
            batch = list(islice(it, config.embeddings_batch_size))
            if not batch:
                break
            yield batch

    async def compute(self) -> list[list[float]]:
        self.flush()
        batches = list(self._batch_chunks())

        tasks = [self.embeddings.embed(batch) for batch in batches]

        result: list[list[float]] = []
        for embeddings_result in await asyncio.gather(*tasks):
            self._validate_embeddings(embeddings_result)
            result += embeddings_result.embeddings
            self.embeddings_usage += embeddings_result.usage

        return result

    def flush(self) -> None:
        self._buffered_texts = []
        self.embeddings_usage = EmbeddingsUsage()


class IndexationService:
    def __init__(self) -> None:
        self.segmentation_service = SegmentationService()
        self.embedder = BatchEmbedder()

    def batch_pages(self, pages: list[fitz.Page]) -> Iterable[list[LineSignature]]:
        it = iter(pages)
        while True:
            batch = list(islice(it, config.pages_batch_size))
            if not batch:
                break
            yield FitzUtils.extract_lines(batch)

    async def run(self, pdf_bytes: bytes) -> IndexationResult:
        chunks: list[IndexedChunk] = []
        llm_usage = Usage()

        with fitz.open(stream=pdf_bytes, filetype="pdf") as doc:
            batches = list(self.batch_pages(doc.pages()))
            segmentation_tasks = [
                self.segmentation_service.limited_segment(batch) for batch in batches
            ]
            segmentation_results = await asyncio.gather(*segmentation_tasks)

            for batch_num, (batch, (result, current_usage)) in enumerate(
                zip(batches, segmentation_results)
            ):
                llm_usage += current_usage

                for chunk in result.chunks:
                    chunk_lines = batch[chunk.start_line : chunk.end_line + 1]

                    screen_position = ChunkPosition(
                        xyxy=FitzUtils.get_chunk_xyxy(chunk_lines),
                        start_line=chunk.start_line,
                        end_line=chunk.end_line,
                    )

                    content = FitzUtils.get_content(chunk_lines)

                    self.embedder.append(content)

                    chunks.append(
                        IndexedChunk(
                            content=content,
                            embedding=[],
                            html_tag=chunk.html_tag,
                            position=screen_position,
                        )
                    )
                    logger.info(
                        f"Batch {batch_num}: Chunk [{chunk.start_line}-{chunk.end_line}] → <{chunk.html_tag}>"
                    )

        chunks_embeddings = await self.embedder.compute()
        for i, embedding in enumerate(chunks_embeddings):
            chunks[i].embedding = embedding

        return IndexationResult(
            chunks=chunks,
            llm_usage=llm_usage,
            embeddings_usage=self.embedder.embeddings_usage,
        )
