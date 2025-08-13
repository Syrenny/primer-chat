import asyncio
import json
import re
from typing import List

from loguru import logger
from shared_adapters.openai import OpenAIFullCompletions
from shared_models.openai.completions import ChatMessage, Usage
from src.config import config
from src.exceptions import ResponseParsingError
from src.models.core import LineSignature, ResultChunk, SegmentationResult
from src.prompts.render import render_prompt

semaphore = asyncio.Semaphore(config.max_concurrent_segments)


class SegmentationService:
    def __init__(self) -> None:
        self.completions = OpenAIFullCompletions()

    def _build_system_prompt(self, lines: List[LineSignature]) -> ChatMessage:
        content = render_prompt(
            "segmentation_system.j2",
            {
                "pdf_lines": [line.model_dump() for line in lines],
                "params": config.segmentation_prompt_config.model_dump(),
            },
        )
        return ChatMessage(role="system", content=content)

    def parse_from_response(self, txt: str) -> list[dict]:
        cleaned = txt.strip("` \n")
        try:
            # 1) JSON из ответа
            if cleaned.startswith("["):
                raw = json.loads(cleaned)
            else:
                match = re.search(r"\[\s*{.*?}\s*]", cleaned, re.S)
                if not match:
                    raise ValueError
                raw = json.loads(match.group(0))

            if not isinstance(raw, list):
                raise ValueError("root must be list")

            # 2) дефолты КО ВСЕМ веткам
            items: list[dict] = []
            for it in raw:
                if not isinstance(it, dict):
                    continue
                it.setdefault("title", "")
                it.setdefault("keyphrases", [])
                it.setdefault("local_summary", "")
                # Совместимость: если модель вдруг пришлёт html_tag — окей, просто не используем дальше
                items.append(it)

            # 3) sanity-check
            for it in items:
                if int(it["start_line"]) > int(it["end_line"]):
                    raise ResponseParsingError(
                        "start_line > end_line", raw_response=txt
                    )

            for it in items:
                # жёсткие клипы
                it["title"] = (it.get("title") or "")[
                    : config.segmentation_prompt_config.max_title_chars
                ]
                if isinstance(it.get("keyphrases"), list):
                    max_k = config.segmentation_prompt_config.max_keyphrases

                    it["keyphrases"] = [str(x)[:64] for x in it["keyphrases"][:max_k]]
                it["local_summary"] = (it.get("local_summary") or "")[:1000]

            return items
        except Exception as err:
            logger.exception(err)
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
