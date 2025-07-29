from uuid import UUID

from shared_models.user.persona import UserPersona
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from src.db.models import DBUser
from src.db.wrap import transactional


class DaoUser:
    @classmethod
    @transactional
    async def get_user_by_id(
        cls, session: AsyncSession, user_id: UUID
    ) -> DBUser | None:
        stmt = (
            select(DBUser)
            .filter(DBUser.id == user_id)
            .options(
                selectinload(DBUser.cookie),
                selectinload(DBUser.files),
                selectinload(DBUser.histories),
            )
        )
        result = await session.execute(stmt)
        return result.scalar_one_or_none()

    @classmethod
    @transactional
    async def update_user(
        cls, session: AsyncSession, user_id: UUID, persona: UserPersona
    ) -> DBUser | None:
        db_user = await cls.get_user_by_id(session=session, user_id=user_id)
        if not db_user:
            return None
        db_user.persona = persona.model_dump()
        return db_user

    @classmethod
    @transactional
    async def create_user(cls, session: AsyncSession, persona: UserPersona) -> DBUser:
        user = DBUser(persona=persona.model_dump())
        session.add(user)
        return user

    @classmethod
    @transactional
    async def delete_user(cls, session: AsyncSession, user_id: UUID) -> None:
        user = await cls.get_user_by_id(session=session, user_id=user_id)
        if user:
            await session.delete(user)
