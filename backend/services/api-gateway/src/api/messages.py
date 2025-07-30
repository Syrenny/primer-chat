from uuid import UUID

from fastapi import APIRouter, Depends, Path
from src.db.dao import DaoMessages
from src.models.dto.messages import ChatHistoryMessage

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
) -> list[ChatHistoryMessage]:
    db_messages = await DaoMessages.list_messages(
        session=ctx.session, user_id=ctx.user_id, history_id=history_id
    )

    return ChatHistoryMessage.from_orm_list(db_messages)
