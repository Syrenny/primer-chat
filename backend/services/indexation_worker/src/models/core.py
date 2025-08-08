from pydantic import BaseModel
from shared_models.indexation.core import HTMLTag, PdfLinePosition


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
