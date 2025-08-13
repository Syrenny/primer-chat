from pydantic import BaseModel
from shared_models.indexation.core import PdfLinePosition


class StyleKey(BaseModel):
    font: str
    size: float
    flags: int


class LineSignature(BaseModel):
    index: int
    content: str
    style: StyleKey
    position: PdfLinePosition


class SegmentationRequest(BaseModel):
    lines: list[LineSignature]


class ResultChunk(BaseModel):
    start_line: int
    end_line: int

    title: str  # синтетическое короткое название чанка
    keyphrases: list[str]  # ключевые фразы (лемматизируй где возможно)
    local_summary: str  # краткое саммари чанка (2–4 предложения)


class SegmentationResult(BaseModel):
    chunks: list[ResultChunk]
