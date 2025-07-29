from uuid import UUID

from src.exceptions.base import AppException


class CookieNotFoundError(AppException):
    def __init__(self, cookie_id: UUID):
        super().__init__(f"Cookie with id={cookie_id} not found")


class UserNotFoundError(AppException):
    def __init__(self, user_id: UUID):
        super().__init__(f"User with id={user_id} not found")
