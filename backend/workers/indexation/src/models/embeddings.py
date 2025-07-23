from typing import List, Literal

from pydantic import BaseModel, field_validator
from src.config import config


class EmbeddingsData(BaseModel):
    index: int
    embedding: List[float]
    object: Literal["embedding"] = "embedding"

    @field_validator("embedding")
    @classmethod
    def validate_dimension(cls, values: List[float]) -> List[float]:
        if len(values) != config.embeddings_dimensions:
            raise ValueError(
                f"Invalid embeddings dimension. Expected {config.embeddings_dimensions}, got {len(values)}"
            )
        return values


class EmbeddingsUsage(BaseModel):
    prompt_tokens: int = 0
    total_tokens: int = 0

    def __iadd__(self, other: "EmbeddingsUsage") -> "EmbeddingsUsage":
        self.prompt_tokens += other.prompt_tokens
        self.total_tokens += other.total_tokens
        return self


class EmbeddingsResponse(BaseModel):
    object: Literal["list"] = "list"
    data: List[EmbeddingsData]
    model: str
    usage: EmbeddingsUsage

    @property
    def embeddings(self) -> List[List[float]]:
        return [item.embedding for item in self.data]
