import yaml  # type: ignore
from pydantic import BaseModel
from shared_config import secrets


class UvicornConfig(BaseModel):
    host: str
    port: int
    workers: int
    reload: bool


class GenerationConfig(BaseModel):
    listen_timeout_seconds: int
    listen_max_attempts: int

    max_len_history: int


class RetrieverConfig(BaseModel):
    max_chunks_per_file: int


class Config(BaseModel):
    cookie_name: str
    cookie_max_age: int

    max_files_per_user: int

    cors_allow_origins: list[str]

    uvicorn: UvicornConfig

    generation: GenerationConfig

    retriever: RetrieverConfig


def load_config(env: str) -> Config:
    with open(f"./config.{env}.yaml") as f:
        raw = yaml.safe_load(f)

    return Config(**raw)


config = load_config(secrets.app_env)
