from typing import Literal

from pydantic import BaseModel, ConfigDict


class UserPersona(BaseModel):
    model_config = ConfigDict(strict=True)

    tone: Literal["formal", "friendly", "neutral"] = "neutral"
    verbosity: Literal["short", "normal", "detailed"] = "normal"
    language: Literal["ru", "en"] = "ru"
    suggestions: list[str] = []
