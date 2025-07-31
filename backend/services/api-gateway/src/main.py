from contextlib import asynccontextmanager
from typing import Any

import uvicorn
from anyio import to_thread
from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from loguru import logger
from shared_kafka.base import BaseKafkaConsumer
from src.api import (
    completions_router,
    files_router,
    history_meta_router,
    messages_router,
)
from src.api.middleware import SessionMiddleware
from src.config import config
from src.consumers.generation.response import GenerationResultConsumer
from src.consumers.indexation.response import IndexationResultConsumer
from src.db.session import session_manager
from src.exceptions.base import AppException
from src.kafka_init import init_kafka


@asynccontextmanager
async def lifespan(app: FastAPI) -> Any:
    await to_thread.run_sync(init_kafka)
    await session_manager.init_db(run_migrations=True)

    consumers: list[BaseKafkaConsumer] = [
        IndexationResultConsumer(),
        GenerationResultConsumer(),
    ]

    for consumer in consumers:
        await consumer.start()

    yield

    for consumer in consumers:
        await consumer.stop()


app = FastAPI(lifespan=lifespan)


@app.exception_handler(RequestValidationError)
async def app_exception_handler(request: Request, exc: AppException) -> JSONResponse:
    logger.warning(f"App error: {exc}")
    return JSONResponse(
        status_code=400,
        content={"error": exc.message},
    )


app.add_middleware(SessionMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=config.cors_allow_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=[""],
)


prefix = "/api"
app.include_router(completions_router, prefix=prefix)
app.include_router(files_router, prefix=prefix)
app.include_router(history_meta_router, prefix=prefix)
app.include_router(messages_router, prefix=prefix)


if __name__ == "__main__":
    uvicorn.run(
        app="src.main:app",
        host=config.uvicorn.host,
        port=config.uvicorn.port,
        workers=config.uvicorn.workers,
        reload=config.uvicorn.reload,
    )
