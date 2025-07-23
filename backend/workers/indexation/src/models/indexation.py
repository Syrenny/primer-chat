from typing import List

from pydantic import BaseModel

from .embeddings import EmbeddingsUsage
from .openai import Usage
from .segmentation import HTMLTag


class ChunkPosition(BaseModel):
    xyxy: tuple[float, float, float, float]
    start_line: int
    end_line: int


class IndexedChunk(BaseModel):
    content: str
    embedding: list[float]
    html_tag: HTMLTag
    position: ChunkPosition


class IndexationResult(BaseModel):
    chunks: List[IndexedChunk]
    llm_usage: Usage
    embeddings_usage: EmbeddingsUsage
