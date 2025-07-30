from uuid import UUID

from fastapi import APIRouter, Depends, Path, status
from src.db.dao.history_meta import DaoHistoryMeta
from src.models.dto.history import (
    CreateHistoryMetaRequest,
    HistoryMeta,
    HistoryMetaSummary,
    UpdateHistoryMetaRequest,
)
from src.services.files import FileService
from src.services.history import HistoryMetaService

from ._context import RequestContext

router = APIRouter()


@router.post(
    "/history_meta",
    tags=["History context"],
    summary="Create a new history context",
    status_code=status.HTTP_201_CREATED,
)
async def create_history_meta(
    body: CreateHistoryMetaRequest, ctx: RequestContext = Depends()
) -> HistoryMeta:
    db_files = await FileService.get_files_by_ids(
        user_id=ctx.user_id, session=ctx.session, file_ids=body.file_ids
    )

    history_meta = await HistoryMetaService.create_history_meta(
        session=ctx.session,
        user_id=ctx.user_id,
        db_files=db_files,
    )

    return history_meta


@router.get(
    "/history_meta",
    tags=["History context"],
    summary="Lists all history contexts per user",
)
async def list_history_meta(ctx: RequestContext = Depends()) -> list[HistoryMeta]:
    result = await DaoHistoryMeta.list_history_meta(
        session=ctx.session, user_id=ctx.user_id
    )

    return HistoryMeta.from_orm_list(result)


@router.get(
    "/history_meta/{history_id}",
    tags=["History context"],
    summary="Get history context",
)
async def get_history_meta(
    ctx: RequestContext = Depends(),
    history_id: UUID = Path(..., description="UUID of the history"),
) -> HistoryMeta | None:
    result = await HistoryMetaService.get_history_meta(
        user_id=ctx.user_id, session=ctx.session, history_id=history_id
    )
    return result


@router.delete(
    "/history_meta/{history_id}",
    tags=["History context"],
    summary="Delete a history context",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_history_meta(
    ctx: RequestContext = Depends(),
    history_id: UUID = Path(..., description="UUID of the history"),
) -> None:
    await DaoHistoryMeta.delete_history_meta(
        session=ctx.session, user_id=ctx.user_id, history_id=history_id
    )


@router.patch(
    "/history_meta/{history_id}",
    tags=["History context"],
    summary="Update history context",
)
async def update_history_meta(
    body: UpdateHistoryMetaRequest,
    ctx: RequestContext = Depends(),
    history_id: UUID = Path(..., description="UUID of the history"),
) -> HistoryMeta:
    db_files = await FileService.get_files_by_ids(
        user_id=ctx.user_id, session=ctx.session, file_ids=body.file_ids
    )

    result = await DaoHistoryMeta.update_history_meta(
        session=ctx.session,
        user_id=ctx.user_id,
        history_id=history_id,
        summary=HistoryMetaSummary(),
        files=db_files,
    )

    return HistoryMeta.from_orm(result)
