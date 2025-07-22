from typing import Literal, List

from pydantic import BaseModel, field_validator
from src.config import config


class EmbeddingData(BaseModel):
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


class EmbeddingUsage(BaseModel):
    prompt_tokens: int
    total_tokens: int


class EmbeddingsResponse(BaseModel):
    object: Literal["list"] = "list"
    data: List[EmbeddingData]
    model: str
    usage: EmbeddingUsage
