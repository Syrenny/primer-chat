from itertools import islice
from typing import Iterable, List

import fitz
from src.config import config as local_config
from src.models.core import LineSignature, PdfLinePosition, StyleKey


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
    def _to_pdf_coords_top_left_bbox(
        cls, bbox: tuple[float, float, float, float], page: fitz.Page
    ) -> list[float]:
        # bbox из get_text("dict"): [x0, y0, x1, y1], origin top-left
        x0, y0, x1, y1 = bbox
        H = float(page.rect.height)  # высота страницы в pt
        # инвертируем y и меняем местами нижнюю/верхнюю границы
        return [x0, H - y1, x1, H - y0]

    @classmethod
    def extract_lines(cls, pages: List[fitz.Page]) -> List[LineSignature]:
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
                    ).strip()
                    if not line_content:
                        continue

                    # Лучше брать bbox всей линии, а не первого спана
                    # (меньше «съезда» по высоте и ширине)
                    line_bbox = line.get("bbox") or line["spans"][0]["bbox"]

                    pdf_bbox = cls._to_pdf_coords_top_left_bbox(line_bbox, page)

                    result.append(
                        LineSignature(
                            index=line_index,
                            content=line_content,
                            style=cls.style_key(line["spans"][0]),
                            position=PdfLinePosition(
                                page=int(page.number) + 1, xyxy=list(pdf_bbox)
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
