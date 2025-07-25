import yaml  # type: ignore
from pydantic import BaseModel
from shared_config import secrets


class UvicornConfig(BaseModel):
    host: str
    port: int
    workers: int
    reload: bool


class Config(BaseModel):
    max_files_per_user: int

    cors_allow_origins: list[str]

    uvicorn: UvicornConfig


def load_config(env: str) -> Config:
    with open(f"./config.{env}.yaml") as f:
        raw = yaml.safe_load(f)

    return Config(**raw)


config = load_config(secrets.app_env)
