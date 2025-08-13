import asyncio
from collections import defaultdict
from typing import List, Tuple

from shared_adapters.openai import OpenAIFullCompletions
from shared_models.openai.completions import ChatMessage, Usage
from src.config import config
from src.models.core import LineSignature
from src.prompts.render import render_prompt

_summary_semaphore = asyncio.Semaphore(config.max_concurrent_summaries)


class WindowSpec(Tuple[int, int]):  # (start_page, end_page) включительно
    pass


class SummarizationService:
    def __init__(self) -> None:
        self.completions = OpenAIFullCompletions()

    @staticmethod
    def _group_lines_by_page(
        lines: List[LineSignature],
    ) -> dict[int, List[LineSignature]]:
        by_page: dict[int, List[LineSignature]] = defaultdict(list)
        for ln in lines:
            by_page[ln.position.page].append(ln)
        return dict(sorted(by_page.items(), key=lambda kv: kv[0]))

    @staticmethod
    def build_windows(pages: List[int]) -> List[WindowSpec]:
        w, o = config.window_pages, config.overlap_pages
        if w <= 0:  # защита
            return []
        windows: List[WindowSpec] = []
        i = 0
        while i < len(pages):
            start_page = pages[i]
            end_idx = min(i + w - 1, len(pages) - 1)
            end_page = pages[end_idx]
            windows.append((start_page, end_page))
            if end_idx == len(pages) - 1:
                break
            i = i + (w - o if w > o else 1)
        return windows

    def _system_prompt_section(self, window_lines: List[LineSignature]) -> ChatMessage:
        # Предклип текста окна (символьный суррогат, ~ пропорция токенам)
        raw = " ".join(l.content for l in window_lines)
        max_chars = config.section_source_max_chars
        if len(raw) > max_chars:
            raw = raw[:max_chars]
        content = render_prompt(
            "section_summary_system.j2",
            {
                "text": raw,
                "max_tokens": config.section_summary_max_tokens,
            },
        )
        return ChatMessage(role="system", content=content)

    def _system_prompt_document(self, section_summaries: List[str]) -> ChatMessage:
        # Предклип текста окна (символьный суррогат, ~ пропорция токенам)
        raw = " ".join(section_summaries)
        max_chars = config.document_source_max_chars
        if len(raw) > max_chars:
            raw = raw[:max_chars]
        content = render_prompt(
            "document_summary_system.j2",
            {
                "sections": section_summaries,
                "max_tokens": config.document_summary_max_tokens,
            },
        )
        return ChatMessage(role="system", content=content)

    async def summarize_section(
        self, window_lines: List[LineSignature]
    ) -> tuple[str, Usage]:
        system_prompt = self._system_prompt_section(window_lines)
        params = {"system_prompt": system_prompt, "query": None, "history": None}
        response, usage = await self.completions.create(**params)
        summary = (response or "").strip()
        if not summary:
            summary = "No content"
        return summary, usage

    async def limited_summarize_section(
        self, window_lines: List[LineSignature]
    ) -> tuple[str, Usage]:
        async with _summary_semaphore:
            return await self.summarize_section(window_lines)

    async def summarize_document(
        self, section_summaries: List[str]
    ) -> tuple[str, Usage]:
        system_prompt = self._system_prompt_document(section_summaries)
        params = {"system_prompt": system_prompt, "query": None, "history": None}
        response, usage = await self.completions.create(**params)
        summary = (response or "").strip()
        if not summary:
            summary = "No content"
        return summary, usage

    def materialize_windows(
        self, lines: List[LineSignature]
    ) -> list[tuple[WindowSpec, list[LineSignature]]]:
        by_page = self._group_lines_by_page(lines)
        pages = list(by_page.keys())
        windows = self.build_windows(pages)
        result = []
        for start_page, end_page in windows:
            window_lines: list[LineSignature] = []
            for p in range(start_page, end_page + 1):
                window_lines.extend(by_page.get(p, []))
            result.append(((start_page, end_page), window_lines))
        return result
