from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from src.db.models import DBCookie
from src.db.wrap import transactional


class DaoCookie:
    @classmethod
    @transactional
    async def get_cookie(
        cls, session: AsyncSession, cookie_id: UUID
    ) -> None | DBCookie:
        stmt = select(DBCookie).filter(DBCookie.id == cookie_id)

        result = await session.execute(stmt)

        return result.scalars().first()

    @classmethod
    @transactional
    async def create_cookie(cls, session: AsyncSession, user_id: UUID) -> DBCookie:
        db_cookie = DBCookie(user_id=user_id)
        session.add(db_cookie)

        return db_cookie
