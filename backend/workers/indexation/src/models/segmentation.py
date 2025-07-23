from typing import Literal

from pydantic import BaseModel

HTMLTag = Literal["h1", "h2", "h3", "p"]


class StyleKey(BaseModel):
    font: str
    size: float
    flags: int


class LineSignature(BaseModel):
    index: int
    content: str
    style: StyleKey


class SegmentationRequest(BaseModel):
    lines: list[LineSignature]


class ResultChunk(BaseModel):
    start_line: int
    end_line: int
    html_tag: HTMLTag


class SegmentationResult(BaseModel):
    chunks: list[ResultChunk]
