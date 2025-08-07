from fastapi import APIRouter, Depends
from src.models.dto.retriever import ApiRetrieverRequest, ApiRetrieverResponse
from src.services.retriever import RetrieveService

from ._context import RequestContext

router = APIRouter()


@router.post("/retrieve", tags=["Retriever"])
async def retrieve(
    request: ApiRetrieverRequest, ctx: RequestContext = Depends()
) -> ApiRetrieverResponse:
    chunks = await RetrieveService.retrieve(
        session=ctx.session,
        user_id=ctx.user_id,
        history_id=request.history_id,
        query=request.query,
    )

    return ApiRetrieverResponse(chunks=chunks)
