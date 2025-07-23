import asyncio

from celery_app import celery_app
from loguru import logger
from src.models.worker_response import WorkerResponse
from src.services.indexation import IndexationService


@celery_app.task(name="run_indexation")
def run_indexation_task(pdf_bytes: bytes) -> dict:
    """Синхронная оболочка для async run()"""

    async def _run() -> WorkerResponse:
        try:
            service = IndexationService()
            result = await service.run(pdf_bytes)

            return WorkerResponse(type="default", result=result)
        except Exception as err:
            logger.exception(f"Ошибка во время индексации: {str(err)}")
            return WorkerResponse(type="error", message=str(err))

    response = asyncio.run(_run())
    return response.model_dump(mode="json")
