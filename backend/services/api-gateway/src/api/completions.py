import asyncio
from collections.abc import AsyncGenerator
from contextlib import aclosing
from uuid import UUID

from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse, StreamingResponse
from loguru import logger
from shared_adapters.redis import RedisActiveHistory
from src.context.user_context import SessionContext
from src.db.session import AsyncSession, get_db
from src.models.completions import APICompletionsChunkResponse, APICompletionsRequest
from src.services.generation import GenerationService

router = APIRouter()


@router.post("/completions", tags=["Completions"])
async def create_completions(
    request: APICompletionsRequest,
    session: AsyncSession = Depends(get_db),
    user_id: UUID = Depends(SessionContext.get_user_id),
) -> StreamingResponse:
    if not await RedisActiveHistory.acquire(
        user_id=user_id, history_id=request.history_id
    ):
        logger.warning(
            f"⛔ Generation already in progress for history_id={request.history_id}, user_id={user_id}"
        )

        return JSONResponse(
            status_code=409,
            content={
                "detail": f"Generation already in progress for history_id={request.history_id}"
            },
        )

    await GenerationService.publish(
        user_id=user_id,
        session=session,
        history_id=request.history_id,
        query=request.query,
    )

    async def streaming_wrapper() -> AsyncGenerator[str, None]:
        try:
            generator = GenerationService.listen(
                user_id=user_id, history_id=request.history_id
            )
            async with aclosing(generator) as _generator:
                async for worker_response in _generator:
                    api_response = APICompletionsChunkResponse.from_worker_response(
                        worker_response
                    )
                    yield api_response.model_dump_json() + "\n\n"
        except asyncio.CancelledError:
            logger.info("🚫 Client disconnected during stream")
            raise
        except Exception as err:
            logger.exception(err)
            yield (
                APICompletionsChunkResponse(
                    type="error", text="Internal server error"
                ).model_dump_json()
                + "\n\n"
            )
        finally:
            await RedisActiveHistory.release(user_id=user_id)

    return StreamingResponse(
        content=streaming_wrapper(),
        media_type="text/plain",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )
