from collections.abc import AsyncGenerator
from contextlib import aclosing
from uuid import UUID

from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from loguru import logger
from src.context.session import SessionContext
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
                async for chunk in _generator:
                    yield chunk.model_dump_json() + "\n\n"
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
