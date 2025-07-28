from pathlib import Path
from typing import Literal
from zoneinfo import ZoneInfo

import yaml  # type: ignore
from loguru import logger
from pydantic import BaseModel, PostgresDsn, SecretStr, computed_field
from pydantic_core import MultiHostUrl
from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).parent.parent.parent


class Secrets(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=BASE_DIR / ".env", env_file_encoding="utf-8"
    )

    app_env: Literal["prod", "dev"]

    openai_key: SecretStr
    embeddings_key: SecretStr

    s3_access_key: SecretStr
    s3_secret_key: SecretStr

    postgres_db: SecretStr
    postgres_user: SecretStr
    postgres_password: SecretStr

    def is_dev(self) -> bool:
        return self.app_env == "dev"

    @computed_field
    def sqlalchemy_url(self) -> PostgresDsn:
        return MultiHostUrl.build(
            scheme="postgresql+asyncpg",
            username=self.postgres_user.get_secret_value(),
            password=self.postgres_password.get_secret_value(),
            host="localhost",
            port=5432,
            path=self.postgres_db.get_secret_value(),
        )


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
    generation: KafkaConsumer


class S3Config(BaseModel):
    service_name: str
    region: str
    endpoint: str
    pdf_bucket: str
    chunks_bucket: str
    presign_expire_seconds: int


class RedisConnectionConfig(BaseModel):
    host: str
    port: int
    db: int


class RedisStreamConfig(BaseModel):
    key: str


class RedisActiveHistoryConfig(BaseModel):
    key_prefix: str
    ttl_seconds: int


class RedisConfig(BaseModel):
    connection: RedisConnectionConfig
    stream: RedisStreamConfig
    active_history: RedisActiveHistoryConfig


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

    redis: RedisConfig


def load_config(env: str) -> Config:
    with open(BASE_DIR / f"config.{env}.yaml") as f:
        raw = yaml.safe_load(f)

    return Config(**raw)


timezone = ZoneInfo("Europe/Moscow")

secrets = Secrets()
config = load_config(secrets.app_env)

logger.info(f"Application environment: {secrets.app_env}")
