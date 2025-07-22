from typing import Literal

from pydantic import BaseModel

TagType = Literal["h1", "h2", "h3", "p"]


class StyleKey(BaseModel):
    index: int
    font: str
    size: float
    flags: int


class ClassifierResponse(BaseModel):
    mapping: dict[int, TagType]
