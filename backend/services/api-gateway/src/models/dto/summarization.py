from pydantic import BaseModel


class ParsedSummaryResponse(BaseModel):
    summary: str
    new_notes: str  # Новые предпочтения пользователя, выявленные по истории сообщений и старому саммари
