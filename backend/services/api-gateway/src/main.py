import uvicorn
from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from loguru import logger
from src.api import (
    completions_router,
    health_router,
    history_router,
    menu_router,
    notes_router,
)
from src.api.middleware import SessionMiddleware
from src.config import config
from src.exceptions.base import AppException

app = FastAPI()


@app.exception_handler(RequestValidationError)
async def app_exception_handler(request: Request, exc: AppException):
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
app.include_router(history_router, prefix=prefix)
app.include_router(completions_router, prefix=prefix)
app.include_router(menu_router, prefix=prefix)
app.include_router(health_router, prefix=prefix)
app.include_router(notes_router, prefix=prefix)


if __name__ == "__main__":
    uvicorn.run(
        app="src.main:app",
        host=config.uvicorn_host,
        port=config.uvicorn_port,
        workers=config.uvicorn_workers,
        reload=config.uvicorn_reload,
    )
