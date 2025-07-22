from collections import Counter
from typing import get_args

import fitz
from src.adapters.openai import FullCompletions
from src.models.classifier import ClassifierResponse, StyleKey, TagType
from src.models.openai import ChatMessage
from src.prompts.render import render_prompt

_examples: list[ChatMessage] = [
    ChatMessage(role="user", content="font: LinLibertineT, size: 8.97, flags: 4"),
    ChatMessage(role="assistant", content="<p>"),
    ChatMessage(role="user", content="font: LinLibertineTB, size: 10.91, flags: 20"),
    ChatMessage(role="assistant", content="<h2>"),
]


class LayoutClassifier:
    def __init__(self):
        self.completions = FullCompletions()

    # Ключ, по которому будем группировать стили
    def style_key(self, span: dict) -> StyleKey:
        font = span["font"]
        size = round(span["size"], 2)  # округляем для устойчивости
        flags = span.get("flags", 0)  # жирность, наклон и т.п.
        return StyleKey(font=font, size=size, flags=flags)

    def _extract_unique_styles(self, doc: fitz.Document):
        styles = Counter()

        for _, page in enumerate(doc):
            text = page.get_text("dict")
            for block in text.get("blocks", []):
                if block.get("type") != 0:
                    continue  # пропускаем изображения и прочее

                for line in block.get("lines", []):
                    for span in line.get("spans", []):
                        key = self.style_key(span)
                        styles[key] += 1

        return styles

    def _build_system_prompt(self, styles: list[StyleKey, int]) -> str:
        tags = get_args(TagType)
        return render_prompt(
            "layout_classification.j2",
            {"styles": [s.model_dump() for s in styles], "tags": tags},
        )

    async def classify(self, doc: fitz.Document) -> ClassifierResponse:
        unique = self._extract_unique_styles(doc)
        unique_top_n = unique.most_common(10)

        params = {
            "history": _examples,
            "system_prompt": self._build_system_prompt(unique_top_n),
        }

        response = self.completions.create(**params)

        return ClassifierResponse(mapping=response)
