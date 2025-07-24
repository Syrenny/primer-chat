from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from src.db.models import DBToken
from src.db.wrap import transactional


class DaoToken:
    @classmethod
    @transactional
    async def create_token(
        cls, session: AsyncSession, user_id: UUID, token: str
    ) -> DBToken:
        """Создает токен для пользователя."""
        result = await session.execute(
            select(DBToken).filter(DBToken.user_id == user_id)
        )
        existing_token = result.scalar_one_or_none()

        if existing_token:
            existing_token.token = token
        else:
            existing_token = DBToken(user_id=user_id, token=token)
            session.add(existing_token)

        return existing_token
