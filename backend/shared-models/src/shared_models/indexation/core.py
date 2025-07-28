from typing import List

from pydantic import BaseModel, ConfigDict

from shared_models.openai.completions import Usage
from shared_models.openai.embeddings import EmbeddingsUsage

from .segmentation import HTMLTag


class ChunkPosition(BaseModel):
    model_config = ConfigDict(strict=True)

    xyxy: list[float, float, float, float]
    start_line: int
    end_line: int


class IndexedChunk(BaseModel):
    model_config = ConfigDict(strict=True)

    content: str
    embedding: list[float]
    html_tag: HTMLTag
    position: ChunkPosition


class IndexationResult(BaseModel):
    model_config = ConfigDict(strict=True)

    chunks: List[IndexedChunk]
    llm_usage: Usage
    embeddings_usage: EmbeddingsUsage
