from typing import List

from pydantic import field_validator
from shared_models.openai.embeddings import EmbeddingsData, EmbeddingsResponse
from src.config import config


class ValidatedEmbeddingsData(EmbeddingsData):
    @field_validator("embedding")
    @classmethod
    def validate_dimension(cls, values: List[float]) -> List[float]:
        if len(values) != config.embeddings_dimensions:
            raise ValueError(
                f"Invalid embeddings dimension. Expected {config.embeddings_dimensions}, got {len(values)}"
            )
        return values


class ValidatedEmbeddingsResponse(EmbeddingsResponse):
    data: List[ValidatedEmbeddingsData]
