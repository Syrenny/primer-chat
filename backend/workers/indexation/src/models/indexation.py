from typing import List

from pydantic import BaseModel

from .segmentation import HTMLTag
from .openai import Usage

class ChunkPosition(BaseModel):
    xyxy: tuple[float, float, float, float]
    start_line: int
    end_line: int


class IndexedChunk(BaseModel):
    content: str
    html_tag: HTMLTag
    position: ChunkPosition


class IndexationResult(BaseModel):
    chunks: List[IndexedChunk]
    usage: Usage
