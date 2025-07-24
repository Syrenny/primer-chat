from pydantic import BaseModel
from shared_models.openai.completions import ChatMessage, Usage

from .core import ParsedSummaryResponse


class SummarizationWorkerRequest(BaseModel):
    request_id: str
    history: list[ChatMessage]


class SummarizationWorkerResponse(BaseModel):
    request_id: str
    summary: ParsedSummaryResponse | None = None
    usage: Usage | None = None
    error: str | None = None
