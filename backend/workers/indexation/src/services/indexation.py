import asyncio
from typing import List

import fitz
from loguru import logger
from src.models.indexation import ChunkPosition, IndexationResult, IndexedChunk
from src.models.openai import Usage
from src.services.segmentation import SegmentationService


class FitzUtils:
    @classmethod
    def get_line_bbox(cls, line: dict) -> fitz.Rect:
        """Получить объединённый bbox всех спанов одной строки"""
        rect = None
        for span in line.get("spans", []):
            span_rect = fitz.Rect(span["bbox"]).normalize()
            rect = span_rect if rect is None else rect | span_rect
        return rect

    @classmethod
    def get_lines_bbox(cls, lines: List[dict]) -> tuple[int, int, int, int]:
        """Получить объединённый bbox для нескольких строк"""
        full_bbox = None
        for line in lines:
            line_bbox = cls.get_line_bbox(line)
            if line_bbox is not None:
                full_bbox = line_bbox if full_bbox is None else full_bbox | line_bbox
        if full_bbox is None:
            full_bbox = fitz.Rect(0, 0, 0, 0)
        return tuple(full_bbox.normalize())

    @classmethod
    def get_content(cls, lines: List[dict]) -> str:
        """Вернуть текст по индексам"""
        text = "\n".join(
            " ".join(span["text"] for span in line.get("spans", []) if span.get("text"))
            for line in lines
        )
        return text.strip()

    @classmethod
    def rect_to_tuple(cls, rect: fitz.Rect) -> tuple[float, float, float, float]:
        """Преобразовать bbox в кортеж (x0, y0, x1, y1)"""
        return tuple(rect)


class IndexationService:
    def __init__(self) -> None:
        self.segmentation_service = SegmentationService()

    async def run(self, pdf_bytes: bytes) -> IndexationResult:
        chunks: list[IndexedChunk] = []
        usage: Usage = Usage(prompt_tokens=0, completion_tokens=0, total_tokens=0)

        with fitz.open(stream=pdf_bytes, filetype="pdf") as doc:
            pages = list(doc.pages())

            # 👇 Запускаем параллельно сегментацию по страницам
            segmentation_tasks = [
                self.segmentation_service.segment([page]) for page in pages
            ]
            segmentation_results = await asyncio.gather(*segmentation_tasks)

            for page_num, (page, (result, current_usage)) in enumerate(
                zip(pages, segmentation_results)
            ):
                usage.prompt_tokens += current_usage.prompt_tokens
                usage.completion_tokens += current_usage.completion_tokens
                usage.total_tokens += current_usage.total_tokens

                text_dict = page.get_text("dict")
                lines = []

                for block in text_dict.get("blocks", []):
                    if block.get("type") != 0:
                        continue
                    lines.extend(block.get("lines", []))

                for chunk in result.chunks:
                    chunk_lines = lines[chunk.start_line : chunk.end_line + 1]

                    position = ChunkPosition(
                        xyxy=FitzUtils.get_lines_bbox(chunk_lines),
                        start_line=chunk.start_line,
                        end_line=chunk.end_line,
                    )

                    content = FitzUtils.get_content(chunk_lines)

                    chunks.append(
                        IndexedChunk(
                            content=content, html_tag=chunk.html_tag, position=position
                        )
                    )
                    logger.info(
                        f"Page {page_num}: Chunk [{chunk.start_line}-{chunk.end_line}] → <{chunk.html_tag}>"
                    )

        return IndexationResult(chunks=chunks, usage=usage)
