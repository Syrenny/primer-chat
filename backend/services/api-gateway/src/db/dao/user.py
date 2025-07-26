from uuid import UUID

from shared_models.user.persona import UserPersona
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from src.db.models import DBUser
from src.db.wrap import transactional


class DaoUser:
    @classmethod
    @transactional
    async def get_user_by_id(
        cls, session: AsyncSession, user_id: UUID
    ) -> DBUser | None:
        result = await session.execute(select(DBUser).filter(DBUser.id == user_id))
        return result.scalar_one_or_none()

    @classmethod
    @transactional
    async def get_user_by_token(
        cls, session: AsyncSession, token: str
    ) -> DBUser | None:
        stmt = select(DBUser).join(DBUser.token).filter(DBUser.token.has(token=token))
        result = await session.execute(stmt)
        return result.scalar_one_or_none()

    @classmethod
    @transactional
    async def update_persona(
        cls, session: AsyncSession, user_id: UUID, persona: UserPersona
    ) -> None:
        user = await cls.get_user_by_id(session=session, user_id=user_id)
        if user is not None:
            user.persona = persona.model_dump()

    @classmethod
    @transactional
    async def get_persona(
        cls, session: AsyncSession, user_id: UUID
    ) -> UserPersona | None:
        user = await cls.get_user_by_id(session=session, user_id=user_id)
        if user and user.persona:
            return UserPersona(**user.persona)
        return None

    @classmethod
    @transactional
    async def create_user(
        cls, session: AsyncSession, persona: UserPersona | None = None
    ) -> DBUser:
        user = DBUser(
            persona=(persona or UserPersona()).model_dump(),
        )
        session.add(user)
        return user

    @classmethod
    @transactional
    async def delete_user(cls, session: AsyncSession, user_id: UUID) -> None:
        user = await cls.get_user_by_id(session=session, user_id=user_id)
        if user:
            await session.delete(user)
