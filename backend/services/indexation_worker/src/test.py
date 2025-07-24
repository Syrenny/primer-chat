import asyncio
import json
import sys
from pathlib import Path

from loguru import logger
from shared_models.indexation.response import (
    IndexationWorkerResponse,
    IndexationWorkerResponseDefault,
    IndexationWorkerResponseError,
)
from src.services.indexation import IndexationService


async def run_indexation(pdf_bytes: bytes) -> IndexationWorkerResponse:
    try:
        service = IndexationService()
        result = await service.run(pdf_bytes)
        return IndexationWorkerResponseDefault(type="default", result=result)
    except Exception as err:
        logger.exception("Ошибка во время индексации")
        return IndexationWorkerResponseError(type="error", message=str(err))


def main():
    if len(sys.argv) != 2:
        print("Usage: python test_indexation.py <path_to_pdf>")
        sys.exit(1)

    pdf_path = Path(sys.argv[1])
    if not pdf_path.exists():
        print(f"Файл не найден: {pdf_path}")
        sys.exit(1)

    pdf_bytes = pdf_path.read_bytes()
    response = asyncio.run(run_indexation(pdf_bytes))

    output_path = Path("output.json")
    output_path.write_text(
        json.dumps(response.model_dump(mode="json"), indent=2, ensure_ascii=False)
    )
    print(f"Индексация завершена. Результат сохранён в {output_path.absolute()}")


if __name__ == "__main__":
    main()
