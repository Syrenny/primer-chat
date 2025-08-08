from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from loguru import logger
from shared_adapters.redis import RedisGenerationBuffer
from src.models.dto.completions import ApiBufferResponse, CompletionsRequest
from src.services.generation import GenerationService
from src.services.messages import GenerationBufferService

from ._context import RequestContext

router = APIRouter()


@router.post("/completions", tags=["Completions"])
async def create_completions(
    request: CompletionsRequest, ctx: RequestContext = Depends()
) -> StreamingResponse:
    if await RedisGenerationBuffer.exists(user_id=ctx.user_id):
        detail = f"⛔ Generation already in progress for history_id={request.history_id}, user_id={ctx.user_id}"
        logger.warning(detail)

        raise HTTPException(status_code=409, detail=detail)

    request_id = await GenerationService.publish(
        user_id=ctx.user_id,
        session=ctx.session,
        history_id=request.history_id,
        query=request.query,
    )

    stream = GenerationService.stream_api_chunks(
        user_id=ctx.user_id, history_id=request.history_id, request_id=request_id
    )

    return StreamingResponse(
        content=stream,
        media_type="text/plain",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


@router.get("/completions/buffer", tags=["Completions"])
async def completions_buffer(ctx: RequestContext = Depends()) -> ApiBufferResponse:
    if not await RedisGenerationBuffer.exists(user_id=ctx.user_id):
        detail = "⛔ No active generation"
        logger.warning(detail)

        raise HTTPException(status_code=409, detail=detail)

    request_id = await RedisGenerationBuffer.get_request_id(user_id=ctx.user_id)
    if not request_id:
        detail = "⛔ request_id not found"
        logger.warning(detail)

        raise HTTPException(status_code=409, detail=detail)

    buffer = await GenerationBufferService.get_buffer(user_id=ctx.user_id)

    return ApiBufferResponse(buffer=buffer)


@router.get("/completions/stream", tags=["Completions"])
async def listen_completions(ctx: RequestContext = Depends()) -> StreamingResponse:
    if not await RedisGenerationBuffer.exists(user_id=ctx.user_id):
        detail = "⛔ No active generation"
        logger.warning(detail)

        raise HTTPException(status_code=409, detail=detail)

    history_id = await RedisGenerationBuffer.get_history_id(user_id=ctx.user_id)
    request_id = await RedisGenerationBuffer.get_request_id(user_id=ctx.user_id)

    stream = GenerationService.stream_api_chunks(
        user_id=ctx.user_id, history_id=history_id, request_id=request_id
    )

    return StreamingResponse(
        content=stream,
        media_type="text/plain",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )
