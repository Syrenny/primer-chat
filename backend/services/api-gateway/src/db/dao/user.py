from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import joinedload
from src.db.models import DBFileMeta, DBUser
from src.db.wrap import transactional


class DaoUser:
    @classmethod
    @transactional
    async def find_user(cls, session: AsyncSession, file_id: UUID) -> None | DBUser:
        stmt = (
            select(DBFileMeta)
            .options(joinedload(DBFileMeta.user))
            .filter(DBFileMeta.file_id == file_id)
        )

        result = await session.execute(stmt)

        return result.scalars().first().user

    @classmethod
    @transactional
    async def create_user(
        cls, session: AsyncSession, email: str, password: str
    ) -> DBUser | None:
        """Создает нового пользователя."""
        user = DBUser(email=email, password=password)
        session.add(user)
        return user

    @classmethod
    @transactional
    async def get_user_by_email(
        cls, session: AsyncSession, email: str
    ) -> DBUser | None:
        """Возвращает пользователя по email, или None, если пользователь не найден."""
        result = await session.execute(select(DBUser).filter(DBUser.email == email))
        return result.scalar_one_or_none()

    @classmethod
    @transactional
    async def get_user_by_id(
        cls, session: AsyncSession, user_id: UUID
    ) -> DBUser | None:
        result = await session.execute(select(DBUser).filter(DBUser.id == user_id))
        return result.scalar_one_or_none()
