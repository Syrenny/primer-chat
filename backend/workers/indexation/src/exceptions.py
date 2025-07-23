class ResponseParsingError(Exception):
    """Ошибка при парсинге ответа от LLM"""

    def __init__(self, message: str, raw_response: str | None = None):
        self.message = message
        self.raw_response = raw_response
        super().__init__(message)

    def __str__(self):
        return f"ResponseParsingError: {self.message}" + (
            f"\nRaw response:\n{self.raw_response}" if self.raw_response else ""
        )
