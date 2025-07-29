from uuid import UUID

from src.exceptions.base import AppException


class HistoryMetaNotFoundError(AppException):
    def __init__(self, history_id: UUID):
        super().__init__(f"History meta with history_id={history_id} not found")
