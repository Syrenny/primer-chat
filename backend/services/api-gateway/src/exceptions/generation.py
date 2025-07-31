from src.exceptions.base import AppException


class GenerationWorkerError(AppException):
    def __init__(self, message: str):
        super().__init__(f"Error in generation worker: {message}")


class RequestIdNotFoundError(AppException):
    def __init__(self):
        super().__init__("Request id not found")
