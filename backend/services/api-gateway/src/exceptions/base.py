class AppException(Exception):
    """Base class for all application exceptions."""

    def __init__(self, message: str = "Unexpected application error"):
        self.message = message
        super().__init__(message)
