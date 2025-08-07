from itertools import islice
from typing import Iterable, List

import fitz
from shared_models.indexation.core import LineSignature, PdfLinePosition, StyleKey
from src.config import config as local_config


class FitzService:
    @classmethod
    def get_content(cls, lines: List[LineSignature]) -> str:
        text = " ".join([line.content for line in lines])
        return text.strip()

    @classmethod
    def style_key(cls, span: dict) -> StyleKey:
        return StyleKey(
            font=span["font"],
            size=round(span["size"], 2),
            flags=span.get("flags", 0),
        )

    @classmethod
    def extract_lines(cls, pages: List[fitz.Page]) -> List[LineSignature]:
        result = []
        line_index = 0

        for i, page in enumerate(pages):
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
                            style=cls.style_key(main_span),
                            position=PdfLinePosition(
                                page=i + 1, xyxy=list(main_span.get("bbox"))
                            ),
                        )
                    )
                    line_index += 1

        return result

    @classmethod
    def batch_lines(cls, pdf_bytes: bytes) -> Iterable[list[LineSignature]]:
        with fitz.open(stream=pdf_bytes, filetype="pdf") as doc:
            it = iter(doc.pages())
            while True:
                batch = list(islice(it, local_config.pages_batch_size))
                if not batch:
                    break
                yield FitzService.extract_lines(batch)
