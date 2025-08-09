from uuid import UUID

from fastapi import APIRouter, Depends
from shared_models.indexation.core import ExtendedIndexedChunk
from src.config import config as local_config
from src.models.dto.retriever import ApiRetrieverRequest, ApiRetrieverResponse
from src.services.chunks import ChunkService
from src.services.retriever import RetrieveService

from ._context import RequestContext

router = APIRouter()


@router.post("/chunks", tags=["Dev"])
async def retrieve(
    request: ApiRetrieverRequest, ctx: RequestContext = Depends()
) -> ApiRetrieverResponse:
    db_chunks = await RetrieveService.find_chunks(
        session=ctx.session,
        user_id=ctx.user_id,
        history_id=request.history_id,
        query=request.query,
        limit=local_config.retriever.max_chunks_per_file,
    )

    chunks = ChunkService.from_db_chunks(db_chunks)

    return ApiRetrieverResponse(chunks=chunks)


@router.get(
    "/chunks/{file_id}",
    tags=["Dev"],
    summary="List all file chunks",
)
async def list_file_chunks(
    file_id: UUID,
    ctx: RequestContext = Depends(),
) -> list[ExtendedIndexedChunk]:
    return await ChunkService.list_chunks(
        user_id=ctx.user_id, file_id=file_id, session=ctx.session
    )
