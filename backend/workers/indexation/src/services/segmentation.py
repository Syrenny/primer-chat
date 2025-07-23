import json
import re
from typing import List, get_args

import fitz
from src.adapters.openai import FullCompletions
from src.exceptions import ResponseParsingError
from src.models.openai import ChatMessage, Usage
from src.models.segmentation import (
    HTMLTag,
    LineSignature,
    ResultChunk,
    SegmentationResult,
    StyleKey,
)
from src.prompts.render import render_prompt


class SegmentationService:
    def __init__(self):
        self.completions = FullCompletions()

    def style_key(self, span: dict) -> StyleKey:
        return StyleKey(
            font=span["font"],
            size=round(span["size"], 2),
            flags=span.get("flags", 0),
        )

    def _extract_lines(self, pages: List[fitz.Page]) -> List[LineSignature]:
        result = []
        line_index = 0

        for page in pages:
            text = page.get_text("dict")
            for block in text.get("blocks", []):
                if block.get("type") != 0:
                    continue

                for line in block.get("lines", []):
                    line_content = " ".join(
                        span["text"]
                        for span in line.get("spans", [])
                        if span.get("text")
                    )
                    if not line_content.strip():
                        continue

                    main_span = line["spans"][0]
                    result.append(
                        LineSignature(
                            index=line_index,
                            content=line_content,
                            style=self.style_key(main_span),
                        )
                    )
                    line_index += 1

        return result

    def _build_system_prompt(self, lines: List[LineSignature]) -> ChatMessage:
        tags = get_args(HTMLTag)
        content = render_prompt(
            "segmentation_system.j2",
            {"pdf_lines": [line.model_dump() for line in lines], "tags": tags},
        )
        return ChatMessage(role="system", content=content)

    def parse_from_response(self, response: str) -> list[dict]:
        match = re.search(r"\[\s*{.*?}\s*]", response, re.DOTALL)
        if not match:
            raise ResponseParsingError(
                "Не удалось найти JSON в ответе модели", raw_response=response
            )
        return json.loads(match.group(0))

    async def segment(self, pages: List[fitz.Page]) -> tuple[SegmentationResult, Usage]:
        lines = self._extract_lines(pages)
        system_prompt = self._build_system_prompt(lines)

        params = {
            "system_prompt": system_prompt,
        }

        response = await self.completions.create(**params)

        parsed = self.parse_from_response(response.choices[0].message.content)
        chunks = [ResultChunk.model_validate(chunk) for chunk in parsed]

        return SegmentationResult.model_validate({"chunks": chunks}), response.usage
