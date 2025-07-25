from functools import lru_cache

from .files import FileService
from .generation import GenerationService


@lru_cache
def get_file_service() -> FileService:
    return FileService()


@lru_cache
def get_generation_service() -> GenerationService:
    return GenerationService()
