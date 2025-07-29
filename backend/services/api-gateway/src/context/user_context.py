from contextvars import ContextVar
from uuid import UUID

from src.models.dto.session import UserContext


class SessionContext:
    _user_context: ContextVar[UserContext] = ContextVar("user_context", default=None)

    @classmethod
    def set_user_context(cls, context: UserContext) -> None:
        cls._user_context.set(context)

    @classmethod
    def get_user_context(cls) -> UserContext | None:
        return cls._user_context.get()

    @classmethod
    def get_user_id(cls) -> UUID:
        context = cls._user_context.get()
        if not context:
            raise ValueError("Session context unavailable")
        return context.user_id
