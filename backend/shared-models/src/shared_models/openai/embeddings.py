from typing import List, Literal

from pydantic import BaseModel, ConfigDict


class EmbeddingsData(BaseModel):
    model_config = ConfigDict(strict=True)

    index: int
    embedding: List[float]
    object: Literal["embedding"] = "embedding"


class EmbeddingsUsage(BaseModel):
    model_config = ConfigDict(strict=True)

    prompt_tokens: int = 0
    total_tokens: int = 0

    def __iadd__(self, other: "EmbeddingsUsage") -> "EmbeddingsUsage":
        self.prompt_tokens += other.prompt_tokens
        self.total_tokens += other.total_tokens
        return self


class EmbeddingsResponse(BaseModel):
    model_config = ConfigDict(strict=True)

    object: Literal["list"] = "list"
    data: List[EmbeddingsData]
    model: str
    usage: EmbeddingsUsage

    @property
    def embeddings(self) -> List[List[float]]:
        return [item.embedding for item in self.data]
