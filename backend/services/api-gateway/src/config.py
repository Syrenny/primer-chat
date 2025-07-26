import yaml  # type: ignore
from pydantic import BaseModel
from shared_config import secrets


class UvicornConfig(BaseModel):
    host: str
    port: int
    workers: int
    reload: bool


class GenerationConfig(BaseModel):
    wait_for_stream_timeout: int

    max_len_history: int


class Config(BaseModel):
    cookie_name: str
    cookie_max_age: int

    max_files_per_user: int

    cors_allow_origins: list[str]

    uvicorn: UvicornConfig

    generation: GenerationConfig


def load_config(env: str) -> Config:
    with open(f"./config.{env}.yaml") as f:
        raw = yaml.safe_load(f)

    return Config(**raw)


config = load_config(secrets.app_env)
