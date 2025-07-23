from typing import Literal
from zoneinfo import ZoneInfo

import yaml  # type: ignore
from loguru import logger
from pydantic import BaseModel, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Secrets(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    indexation_env: Literal["prod", "dev"]

    openai_key: SecretStr
    embeddings_key: SecretStr

    def is_dev(self) -> bool:
        return self.teplitsa_env == "dev"


class Config(BaseModel):
    openai_model: str
    openai_base_url: str
    openai_temperature: float
    openai_max_tokens: int
    openai_throttle_rate_limit: int
    openai_throttle_period: float

    embeddings_model: str
    embeddings_base_url: str
    embeddings_dimensions: int
    embeddings_throttle_rate_limit: int
    embeddings_throttle_period: float

    max_concurrent_segments: int
    pages_batch_size: int
    embeddings_batch_size: int


def load_config(env: str) -> Config:
    with open(f"./config.{env}.yaml") as f:
        raw = yaml.safe_load(f)

    return Config(**raw)


timezone = ZoneInfo("Europe/Moscow")

secrets = Secrets()
config = load_config(secrets.indexation_env)

logger.info(f"Application environment: {secrets.indexation_env}")
