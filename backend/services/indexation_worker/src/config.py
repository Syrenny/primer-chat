from typing import Literal

import yaml  # type: ignore
from pydantic import BaseModel
from shared_config import secrets


class SegmentationPromptConfig(BaseModel):
    min_lines_per_chunk: int
    min_chars_per_chunk: int
    target_chars_per_chunk: int
    max_chars_per_chunk: int
    max_title_words: int
    max_keyphrases: int
    max_summary_sentences: int
    max_title_chars: int


class Config(BaseModel):
    max_concurrent_segments: int
    pages_batch_size: int
    embeddings_batch_size: int

    max_concurrent_summaries: int

    # RAPTOR-параметры
    window_pages: int
    overlap_pages: int

    section_summary_max_tokens: int
    document_summary_max_tokens: int

    section_source_max_chars: int
    document_source_max_chars: int

    embed_mode: Literal["content", "summary", "hybrid"]
    embed_hybrid_prefix_chars: int
    embeddings_max_char: int

    segmentation_prompt_config: SegmentationPromptConfig


def load_config(env: str) -> Config:
    with open(f"./config.{env}.yaml") as f:
        raw = yaml.safe_load(f)

    return Config(**raw)


config = load_config(secrets.app_env)
