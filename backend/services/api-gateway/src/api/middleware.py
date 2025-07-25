from loguru import logger
from pydantic import ValidationError
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response

from src.config import config
from src.context.session import SessionContext
from src.models.session import CookieData, UserContext


class SessionMiddleware(BaseHTTPMiddleware):
    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        if request.url.path == "/api/health":
            return await call_next(request)

        raw_cookie = request.cookies.get(config.cookie_name)

        if raw_cookie:
            try:
                cookie = CookieData.model_validate_json(raw_cookie)
            except ValidationError as e:
                logger.exception(e)
                cookie = CookieData()
        else:
            cookie = CookieData()

        logger.info(f"User with cookie: {cookie}")

        SessionContext.set_user_context(UserContext(user_id=cookie.user_id))
        response: Response = await call_next(request)

        if not raw_cookie:
            response.set_cookie(
                key=config.cookie_name,
                value=cookie.model_dump_json(),
                max_age=config.cookie_max_age,
                httponly=True,
                samesite="lax",
                path="/",
            )

        return response
