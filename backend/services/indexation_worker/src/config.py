import yaml  # type: ignore
from pydantic import BaseModel
from shared_config import secrets


class Config(BaseModel):
    max_concurrent_segments: int
    pages_batch_size: int
    embeddings_batch_size: int


def load_config(env: str) -> Config:
    with open(f"./config.{env}.yaml") as f:
        raw = yaml.safe_load(f)

    return Config(**raw)


config = load_config(secrets.app_env)
