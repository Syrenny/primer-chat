from uuid import UUID

from fastapi import APIRouter, Depends, Path
from src.models.dto.requests import GenerationRequest
from src.services.request import RequestService

from ._context import RequestContext

router = APIRouter()


@router.get(
    "/history_messages/{history_id}",
    tags=["History messages"],
    summary="Get history messages",
)
async def get_history_messages(
    ctx: RequestContext = Depends(),
    history_id: UUID = Path(..., description="UUID of the history"),
) -> list[GenerationRequest]:
    requests = await RequestService.list_requests(
        user_id=ctx.user_id, history_id=history_id, session=ctx.session
    )

    return requests
