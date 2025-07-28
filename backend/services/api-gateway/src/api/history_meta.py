from uuid import UUID

from fastapi import APIRouter, Depends, Path, status
from src.context.user_context import SessionContext
from src.db.dao import DaoFileMeta
from src.db.dao.history_meta import DaoHistoryMeta
from src.db.session import AsyncSession, get_db
from src.models.history import (
    CreateHistoryMetaRequest,
    HistoryMeta,
    UpdateHistoryMetaRequest,
)

router = APIRouter()


@router.post(
    "/history_meta",
    tags=["History context"],
    summary="Create a new history context",
    status_code=status.HTTP_201_CREATED,
)
async def create_history_meta(
    request: CreateHistoryMetaRequest,
    session: AsyncSession = Depends(get_db),
    user_id: UUID = Depends(SessionContext.get_user_id),
) -> HistoryMeta:
    db_files = []
    if request.file_ids:
        for file_id in request.file_ids:
            db_file_meta = await DaoFileMeta.get_file_meta(
                session=session, user_id=user_id, file_id=file_id
            )
            db_files.append(db_file_meta)

    db_history_meta = await DaoHistoryMeta.add_history_meta(
        session=session, user_id=user_id, summary=request.summary, summary_index=0
    )

    return HistoryMeta.from_db([db_history_meta])[0]


@router.get(
    "/history_meta",
    tags=["History context"],
    summary="Lists all history contexts per user",
)
async def list_history_meta(
    session: AsyncSession = Depends(get_db),
    user_id: UUID = Depends(SessionContext.get_user_id),
) -> list[HistoryMeta]:
    result = await DaoHistoryMeta.list_history_meta(session=session, user_id=user_id)

    return HistoryMeta.from_db(result)


@router.get(
    "/history_meta/{history_id}",
    tags=["History context"],
    summary="Get history context",
)
async def get_history_meta(
    session: AsyncSession = Depends(get_db),
    user_id: UUID = Depends(SessionContext.get_user_id),
    history_id: UUID = Path(..., description="UUID of the history to delete"),
) -> HistoryMeta | None:
    result = await DaoHistoryMeta.get_history_meta(
        session=session, user_id=user_id, history_id=history_id
    )

    return HistoryMeta.from_db(result)


@router.delete(
    "/history_meta/{history_id}",
    tags=["History context"],
    summary="Delete a history context",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_history_meta(
    history_id: UUID = Path(..., description="UUID of the history to delete"),
    session: AsyncSession = Depends(get_db),
    user_id: UUID = Depends(SessionContext.get_user_id),
) -> None:
    await DaoHistoryMeta.delete_history_meta(
        session=session, user_id=user_id, history_id=history_id
    )


@router.patch(
    "/history_meta/{history_id}",
    tags=["History context"],
    summary="Update history context",
)
async def update_history_meta(
    request: UpdateHistoryMetaRequest,
    history_id: UUID = Path(..., description="UUID of the history to delete"),
    session: AsyncSession = Depends(get_db),
    user_id: UUID = Depends(SessionContext.get_user_id),
) -> HistoryMeta:
    db_files = []
    if request.file_ids:
        for file_id in request.file_ids:
            db_file_meta = await DaoFileMeta.get_file_meta(
                session=session, user_id=user_id, file_id=file_id
            )
            db_files.append(db_file_meta)

    result = await DaoHistoryMeta.update_history_meta(
        session=session,
        user_id=user_id,
        history_id=history_id,
        summary=request.summary,
        files=db_files,
    )

    return HistoryMeta.from_db([result])[0]
