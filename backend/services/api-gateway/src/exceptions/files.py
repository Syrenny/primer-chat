from uuid import UUID

from src.exceptions.base import AppException


class FilesValidationError(AppException):
    def __init__(self, max_files: int):
        super().__init__(f"File limit exceeded: max {max_files} files allowed")


class FilesInvalidTypeError(AppException):
    def __init__(self, filename: str):
        super().__init__(f"Invalid file type for: {filename}")


class FilesEncryptedError(AppException):
    def __init__(self, filename: str):
        super().__init__(f"PDF is encrypted: {filename}")


class FilesInvalidPdfError(AppException):
    def __init__(self, filename: str):
        super().__init__(f"Failed to parse PDF: {filename}")


class MissingFileIdsError(AppException):
    def __init__(self, ids: set[UUID]):
        super().__init__(f"Missing file_ids: {ids}")
