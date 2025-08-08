from typing import List, Literal
from uuid import UUID

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
    positions: list[PdfLinePosition]


class IndexationWorkerResult(BaseModel):
    model_config = ConfigDict(strict=True)

    chunks: List[IndexedChunk]
    llm_usage: Usage
    embeddings_usage: EmbeddingsUsage


class ExtendedIndexedChunk(IndexedChunk):
    model_config = ConfigDict(strict=True)
    file_id: UUID

    @classmethod
    def to_indexed_chunk(cls, dto_chunk: "ExtendedIndexedChunk") -> IndexedChunk:
        return IndexedChunk(
            content=dto_chunk.content,
            embedding=dto_chunk.embedding,
            html_tag=dto_chunk.html_tag,
            positions=dto_chunk.positions,
        )

    @classmethod
    def to_indexed_chunks(
        cls, chunks: list["ExtendedIndexedChunk"]
    ) -> list[IndexedChunk]:
        return [chunk.to_indexed_chunk() for chunk in chunks]
