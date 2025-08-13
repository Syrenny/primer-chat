from typing import List, Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from shared_models.openai.completions import Usage
from shared_models.openai.embeddings import EmbeddingsUsage


class PdfLinePosition(BaseModel):
    model_config = ConfigDict(strict=True)

    page: int
    xyxy: list[float] = Field(min_length=4, max_length=4)


HTMLTag = Literal["h1", "h2", "h3", "p"]


class IndexedChunk(BaseModel):
    model_config = ConfigDict(strict=True)

    content: str
    embedding: list[float]
    positions: list[PdfLinePosition]

    html_tag: HTMLTag | None = None

    title: str | None = None
    keyphrases: list[str] = Field(default_factory=list)
    local_summary: str | None = None
    level: Literal["leaves", "sections", "document"] = "leaves"

    start_line: int | None = None
    end_line: int | None = None
    page_span: list[int] | None = Field(min_length=2, max_length=2, default=None)


class IndexationWorkerResult(BaseModel):
    model_config = ConfigDict(strict=True)

    chunks: List[IndexedChunk]
    llm_usage: Usage
    embeddings_usage: EmbeddingsUsage


class ExtendedIndexedChunk(IndexedChunk):
    model_config = ConfigDict(strict=True)

    file_id: UUID
    filename: str

    @classmethod
    def to_indexed_chunk(cls, dto: "ExtendedIndexedChunk") -> IndexedChunk:
        return IndexedChunk(
            content=dto.content,
            embedding=dto.embedding,
            positions=dto.positions,
            html_tag=dto.html_tag,
            title=dto.title,
            keyphrases=list(dto.keyphrases or []),
            local_summary=dto.local_summary,
            level=dto.level,
            start_line=dto.start_line,
            end_line=dto.end_line,
            page_span=dto.page_span,
        )

    @classmethod
    def to_indexed_chunks(
        cls, chunks: list["ExtendedIndexedChunk"]
    ) -> list[IndexedChunk]:
        return [cls.to_indexed_chunk(chunk) for chunk in chunks]
