from ..celery_app import celery_app
from services.indexation import IndexationService


@celery_app.task(name="index_pdf", bind=True)
def index_pdf(self, pdf_bytes: bytes):
    try:
        indexer = IndexationService()
        indexer.run(pdf_bytes)
    except Exception as e:
        # можно сделать логгирование или retry
        raise self.retry(exc=e, countdown=10, max_retries=3)
