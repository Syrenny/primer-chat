from typing import Literal
from zoneinfo import ZoneInfo

import yaml  # type: ignore
from loguru import logger
from pydantic import BaseModel, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Secrets(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    summarization_env: Literal["prod", "dev"]

    openai_key: SecretStr

    def is_dev(self) -> bool:
        return self.summarization_env == "dev"


class Config(BaseModel):
    openai_model: str
    openai_base_url: str
    openai_temperature: float
    openai_max_tokens: int
    openai_throttle_rate_limit: int
    openai_throttle_period: float

    kafka_bootstrap_servers: str
    kafka_request_topic: str
    kafka_response_topic: str
    kafka_group_id: str


def load_config(env: str) -> Config:
    with open(f"./config.{env}.yaml") as f:
        raw = yaml.safe_load(f)

    return Config(**raw)


timezone = ZoneInfo("Europe/Moscow")

secrets = Secrets()
config = load_config(secrets.summarization_env)

logger.info(f"Application environment: {secrets.summarization_env}")
