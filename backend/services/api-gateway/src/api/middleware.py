from loguru import logger
from pydantic import ValidationError
from src.config import config as local_config
from src.context.user_context import SessionContext
from src.db.dao import DaoCookie, DaoUser
from src.db.session import session_manager
from src.models.session import CookieData, UserContext
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response


def validate_cookie(raw_cookie: str) -> CookieData | None:
    cookie = None
    try:
        cookie = CookieData.model_validate_json(raw_cookie)
    except ValidationError as err:
        logger.error(f"Invalid cookie: {err}")
    return cookie


class SessionMiddleware(BaseHTTPMiddleware):
    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        if request.url.path == "/api/health":
            return await call_next(request)

        raw_cookie = request.cookies.get(local_config.cookie_name)

        cookie = validate_cookie(raw_cookie)

        _new_cookie: bool = False

        async with session_manager.session() as session:
            # Проверка, есть ли такая куки в БД
            if cookie:
                db_cookie = await DaoCookie.get_cookie(
                    session=session, cookie_id=cookie.cookie_id
                )
                # Есть -> берем данные из БД
                # Нет -> значит надо создать
                if db_cookie:
                    cookie = CookieData(
                        cookie_id=db_cookie.id, user_id=db_cookie.user_id
                    )
                else:
                    cookie = None

            # Создание новой куки и пользователя
            if not cookie:
                new_user = await DaoUser.create_user(session=session)
                db_cookie = await DaoCookie.create_cookie(
                    session=session, user_id=new_user.id
                )
                cookie = CookieData(cookie_id=db_cookie.id, user_id=db_cookie.user_id)
                _new_cookie = True

        SessionContext.set_user_context(UserContext(user_id=cookie.user_id))

        response: Response = await call_next(request)

        logger.debug(f"User cookie: {cookie}")

        if _new_cookie:
            response.set_cookie(
                key=local_config.cookie_name,
                value=cookie.model_dump_json(),
                max_age=local_config.cookie_max_age,
                httponly=True,
                samesite="lax",
                path="/",
            )

        return response
