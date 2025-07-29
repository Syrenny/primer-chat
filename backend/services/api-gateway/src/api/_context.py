from uuid import UUID
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from src.context.user_context import SessionContext
from src.db.session import get_db


class RequestContext:
    def __init__(
        self,
        session: AsyncSession = Depends(get_db),
        user_id: UUID = Depends(SessionContext.get_user_id),
    ):
        self.session = session
        self.user_id = user_id
