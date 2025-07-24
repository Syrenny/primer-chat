from typing import Literal

from pydantic import BaseModel


class UserPersona(BaseModel):
    tone: Literal["formal", "friendly", "neutral"] = "neutral"
    verbosity: Literal["short", "normal", "detailed"] = "normal"
    language: Literal["ru", "en"] = "ru"
    suggestions: str = ""
