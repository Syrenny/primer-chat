from collections import Counter
from pathlib import Path

import fitz  # PyMuPDF


# Ключ, по которому будем группировать стили
def style_key(span: dict) -> tuple:
    font = span["font"]
    size = round(span["size"], 2)  # округляем для устойчивости
    flags = span.get("flags", 0)  # жирность, наклон и т.п.
    return (font, size, flags)


def extract_unique_styles(pdf_path: str) -> Counter:
    doc = fitz.open(pdf_path)
    styles = Counter()

    for page_num, page in enumerate(doc):
        text = page.get_text("dict")
        for block in text.get("blocks", []):
            if block.get("type") != 0:
                continue  # пропускаем изображения и прочее

            for line in block.get("lines", []):
                for span in line.get("spans", []):
                    key = style_key(span)
                    styles[key] += 1

    return styles


def pretty_print(styles: Counter):
    print(f"Найдено {len(styles)} уникальных стилей:\n")
    for (font, size, flags), count in styles.most_common():
        print(f"{font:30s} | size: {size:>5} | flags: {flags} | count: {count}")


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage: python extract_styles.py <your_file.pdf>")
        sys.exit(1)

    pdf_file = sys.argv[1]
    if not Path(pdf_file).exists():
        print("Файл не найден:", pdf_file)
        sys.exit(1)

    styles = extract_unique_styles(pdf_file)
    pretty_print(styles)
