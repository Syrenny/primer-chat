from uuid import UUID

from fastapi import APIRouter, Depends, Path
from src.context.user_context import SessionContext
from src.db.dao.history_meta import DaoHistoryMeta
from src.db.session import AsyncSession, get_db
from src.models.history import HistoryMeta

router = APIRouter()


@router.get(
    "/history_meta/{history_id}",
    tags=["History context"],
    summary="Get history context",
)
async def get_history_messages(
    session: AsyncSession = Depends(get_db),
    user_id: UUID = Depends(SessionContext.get_user_id),
    history_id: UUID = Path(..., description="UUID of the history to delete"),
) -> HistoryMeta | None:
    result = await DaoHistoryMeta.get_history_meta(
        session=session, user_id=user_id, history_id=history_id
    )

    return HistoryMeta.from_db(result)
