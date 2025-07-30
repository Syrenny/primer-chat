import asyncio
import json
import re
from typing import List, get_args

from shared_adapters.openai import OpenAIFullCompletions
from shared_models.indexation.segmentation import (
    HTMLTag,
    LineSignature,
    ResultChunk,
    SegmentationResult,
)
from shared_models.openai.completions import ChatMessage, Usage
from src.config import config
from src.exceptions import ResponseParsingError
from src.prompts.render import render_prompt

semaphore = asyncio.Semaphore(config.max_concurrent_segments)


class SegmentationService:
    def __init__(self) -> None:
        self.completions = OpenAIFullCompletions()

    def _build_system_prompt(self, lines: List[LineSignature]) -> ChatMessage:
        tags = get_args(HTMLTag)
        content = render_prompt(
            "segmentation_system.j2",
            {"pdf_lines": [line.model_dump() for line in lines], "tags": tags},
        )
        return ChatMessage(role="system", content=content)

    def parse_from_response(self, txt: str) -> list[dict]:
        cleaned = txt.strip("` \n")
        try:
            if cleaned.startswith("["):
                return json.loads(cleaned)
            match = re.search(r"\[\s*{.*?}\s*]", cleaned, re.S)

            if not match:
                raise ValueError
            return json.loads(match.group(0))
        except Exception:
            raise ResponseParsingError("LLM вернула не JSON", raw_response=txt)

    async def segment(
        self, lines: List[LineSignature]
    ) -> tuple[SegmentationResult, Usage]:
        system_prompt = self._build_system_prompt(lines)

        params = {"system_prompt": system_prompt, "query": None, "history": None}

        response, usage = await self.completions.create(**params)

        parsed = self.parse_from_response(response)
        chunks = [ResultChunk.model_validate(chunk) for chunk in parsed]

        return SegmentationResult.model_validate({"chunks": chunks}), usage

    async def limited_segment(
        self, lines: List[LineSignature]
    ) -> tuple[SegmentationResult, Usage]:
        async with semaphore:
            return await self.segment(lines)
