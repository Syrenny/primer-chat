from pydantic import BaseModel


class ValidatorResponse(BaseModel):
    verdict: bool  # True - OK, False - Violates
    reason: str | None = None
