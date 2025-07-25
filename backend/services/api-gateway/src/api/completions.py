from collections.abc import AsyncGenerator
from contextlib import aclosing

from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from loguru import logger
from src.models.completions import APICompletionsChunkResponse, APICompletionsRequest

router = APIRouter()

chat = ...


@router.post("/completions", tags=["Completions"])
async def create_completions(request: APICompletionsRequest) -> StreamingResponse:
    async def streaming_wrapper() -> AsyncGenerator[APICompletionsChunkResponse, None]:
        try:
            generator = chat.stream(request.query)
            async with aclosing(generator) as _generator:
                async for chunk in _generator:
                    yield (
                        APICompletionsChunkResponse(text=chunk).model_dump_json()
                        + "\n\n"
                    )
        except Exception as err:
            logger.exception(err)
            yield (
                APICompletionsChunkResponse(
                    type="error", text="Internal server error"
                ).model_dump_json()
                + "\n\n"
            )

    return StreamingResponse(
        content=streaming_wrapper(),
        media_type="application/json",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )
