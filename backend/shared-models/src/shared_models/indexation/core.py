from typing import List, Literal

from pydantic import BaseModel, ConfigDict

from shared_models.openai.completions import Usage
from shared_models.openai.embeddings import EmbeddingsUsage


class PdfLinePosition(BaseModel):
    model_config = ConfigDict(strict=True)

    page: int
    xyxy: list[float, float, float, float]


HTMLTag = Literal["h1", "h2", "h3", "p"]


class IndexedChunk(BaseModel):
    model_config = ConfigDict(strict=True)

    content: str
    embedding: list[float]
    html_tag: HTMLTag
    position: list[PdfLinePosition]


class IndexationResult(BaseModel):
    model_config = ConfigDict(strict=True)

    chunks: List[IndexedChunk]
    llm_usage: Usage
    embeddings_usage: EmbeddingsUsage


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
    html_tag: HTMLTag


class SegmentationResult(BaseModel):
    chunks: list[ResultChunk]
