from loguru import logger
from src.config import config as local_config
from src.context.user_context import SessionContext
from src.db.dao import DaoCookie, DaoUser
from src.db.session import session_manager
from src.models.session import CookieData, UserContext
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response


class SessionMiddleware(BaseHTTPMiddleware):
    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        if request.url.path == "/api/health":
            return await call_next(request)

        raw_cookie = request.cookies.get(local_config.cookie_name)

        async with session_manager.session() as session:
            user_id = None

            if raw_cookie:
                try:
                    cookie = CookieData.model_validate_json(raw_cookie)
                    db_cookie = await DaoCookie.get_cookie(
                        session=session, cookie_id=cookie.id
                    )
                    if db_cookie:
                        user_id = db_cookie.user_id
                except Exception as e:
                    logger.exception(f"Invalid cookie: {e}")

            if user_id is None:
                # Новый пользователь и кука
                new_user = await DaoUser.create_user(session=session)
                db_cookie = await DaoCookie.create_cookie(
                    session=session, user_id=new_user.id
                )
                await session.commit()
                user_id = new_user.id
                raw_cookie = CookieData(
                    id=db_cookie.id, user_id=db_cookie.user_id
                ).model_dump_json()

            SessionContext.set_user_context(UserContext(user_id=user_id))

        response: Response = await call_next(request)

        if not request.cookies.get(local_config.cookie_name):
            response.set_cookie(
                key=local_config.cookie_name,
                value=raw_cookie,
                max_age=local_config.cookie_max_age,
                httponly=True,
                samesite="lax",
                path="/",
            )

        return response
