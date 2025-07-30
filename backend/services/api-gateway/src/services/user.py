from uuid import UUID

from shared_models.user.persona import UserPersona
from sqlalchemy.ext.asyncio import AsyncSession
from src.db.dao import DaoCookie, DaoUser
from src.exceptions.user import CookieNotFoundError, UserNotFoundError
from src.models.dto.session import CookieData
from src.models.dto.user import UserDTO


class UserService:
    @classmethod
    async def get_user_by_id(cls, session: AsyncSession, user_id: UUID) -> UserDTO:
        db_user = await DaoUser.get_user_by_id(session=session, user_id=user_id)
        if db_user is None:
            raise UserNotFoundError(user_id=user_id)
        return UserDTO.from_orm(db_user)

    @classmethod
    async def get_user_by_cookie(
        cls, session: AsyncSession, cookie: CookieData
    ) -> UserDTO:
        db_cookie = await DaoCookie.get_cookie(
            session=session, cookie_id=cookie.cookie_id
        )
        if db_cookie is None:
            raise CookieNotFoundError(cookie_id=cookie.cookie_id)

        user = await cls.get_user_by_id(session=session, user_id=db_cookie.user_id)
        return user

    @classmethod
    async def create_user(cls, session: AsyncSession) -> UserDTO:
        persona = UserPersona()

        db_user = await DaoUser.create_user(session=session, persona=persona)
        _ = await DaoCookie.create_cookie(session=session, user_id=db_user.id)
        db_user = await DaoUser.get_user_by_id(session=session, user_id=db_user.id)

        return UserDTO.from_orm(db_user)

    @classmethod
    async def update_user(
        cls, session: AsyncSession, user_id: UUID, persona: UserPersona
    ) -> UserDTO:
        _db_user = await DaoUser.update_user(
            session=session, user_id=user_id, persona=persona
        )
        if _db_user is None:
            raise UserNotFoundError(user_id)

        db_user = await cls.get_user_by_id(session=session, user_id=_db_user.id)

        return UserDTO.from_orm(db_user)


class UserPersonaService:
    @classmethod
    async def get_persona(cls, session: AsyncSession, user_id: UUID) -> UserPersona:
        user = await UserService.get_user_by_id(session=session, user_id=user_id)
        return user.persona

    @classmethod
    async def append_suggestions(
        cls, session: AsyncSession, user_id: UUID, suggestion: str
    ) -> None:
        suggestion = suggestion.strip()
        if not suggestion:
            return

        user = await UserService.get_user_by_id(session=session, user_id=user_id)

        user.persona.suggestions.append(suggestion)
        await UserService.update_user(
            session=session, user_id=user_id, persona=user.persona
        )
