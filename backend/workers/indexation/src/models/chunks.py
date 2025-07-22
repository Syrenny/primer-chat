from uuid import UUID, uuid4

from pydantic import BaseModel, Field


class Chunks(BaseModel):
    index: UUID = Field(default_factory=uuid4)
    content: str
    title: str | None = None
    children: list["Chunks"] | None = None

    def is_leaf(self) -> bool:
        return not self.children
