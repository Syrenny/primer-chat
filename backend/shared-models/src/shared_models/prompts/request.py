from pydantic import BaseModel
from shared_models.user.persona import UserPersona

from .actions import Action


class PromptRequest(BaseModel):
    action: Action
    query: str
    persona: UserPersona
    history: list[...]
