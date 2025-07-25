from typing import Literal
from zoneinfo import ZoneInfo

import yaml  # type: ignore
from loguru import logger
from pydantic import BaseModel, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Secrets(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    app_env: Literal["prod", "dev"]

    openai_key: SecretStr
    embeddings_key: SecretStr

    s3_access_key: SecretStr
    s3_secret_key: SecretStr

    def is_dev(self) -> bool:
        return self.app_env == "dev"


class KafkaDefaults(BaseModel):
    partitions: int
    replication_factor: int


class KafkaConsumer(BaseModel):
    topic: str
    group_id: str


class KafkaTopicPair(BaseModel):
    request: KafkaConsumer
    response: KafkaConsumer


class KafkaConfig(BaseModel):
    bootstrap_servers: str
    auto_offset_reset: str
    enable_auto_commit: bool
    max_poll_records: int
    session_timeout_ms: int

    defaults: KafkaDefaults

    indexation: KafkaTopicPair
    generation: KafkaTopicPair
    summarization: KafkaTopicPair


class S3Config(BaseModel):
    service_name: str
    region: str
    endpoint: str
    bucket: str
    presign_expire_seconds: int


class RedisConfig(BaseModel):
    host: str
    port: int
    db: 0
    stream_key: str


class OpenAIConfig(BaseModel):
    model: str
    base_url: str
    temperature: float
    max_tokens: int
    throttle_rate_limit: int
    throttle_period: float


class OpenAIEmbeddingsConfig(BaseModel):
    model: str
    base_url: str
    dimensions: int
    throttle_rate_limit: int
    throttle_period: float


class Config(BaseModel):
    openai: OpenAIConfig

    embeddings: OpenAIEmbeddingsConfig

    kafka: KafkaConfig

    s3: S3Config


def load_config(env: str) -> Config:
    with open(f"./config.{env}.yaml") as f:
        raw = yaml.safe_load(f)

    return Config(**raw)


timezone = ZoneInfo("Europe/Moscow")

secrets = Secrets()
config = load_config(secrets.app_env)

logger.info(f"Application environment: {secrets.app_env}")
