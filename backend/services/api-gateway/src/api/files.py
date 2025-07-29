from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, UploadFile, status
from loguru import logger
from shared_adapters.s3 import S3Storage
from src.db.dao import DaoFileMeta
from src.models.dto.files import FileMeta, FileStatus, SignedUrl
from src.services import FileService, get_file_service

from ._context import RequestContext

router = APIRouter()


@router.post(
    "/files",
    tags=["Files"],
    summary="Upload a file",
    status_code=status.HTTP_201_CREATED,
)
async def add_file(
    file: UploadFile,
    file_service: FileService = Depends(get_file_service),
    ctx: RequestContext = Depends(),
) -> FileMeta:
    response = await file_service.add_file(
        upload_file=file, session=ctx.session, user_id=ctx.user_id
    )

    return response


@router.get("/files/{file_id}/status", tags=["Files"], response_model=FileStatus)
async def get_indexing_status(
    file_id: UUID,
    ctx: RequestContext = Depends(),
) -> FileStatus:
    status = await DaoFileMeta.get_is_indexed(
        session=ctx.session, user_id=ctx.user_id, file_id=file_id
    )
    return FileStatus(file_id=file_id, is_indexed=status)


@router.delete(
    "/files/{file_id}",
    tags=["Files"],
    summary="Delete a file",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_file(
    file_id: UUID,
    file_service: FileService = Depends(get_file_service),
    ctx: RequestContext = Depends(),
) -> None:
    await file_service.delete_file(
        file_id=file_id, session=ctx.session, user_id=ctx.user_id
    )


@router.get(
    "/files/{file_id}/signed_url",
    tags=["Files"],
    summary="Generate temporary link",
    response_model=SignedUrl,
)
async def get_signed_url(
    file_id: UUID,
    ctx: RequestContext = Depends(),
) -> SignedUrl:
    # Проверка, что файл существует и принадлежит пользователю
    file_meta = await DaoFileMeta.get_file_meta(
        session=ctx.session, user_id=ctx.user_id, file_id=file_id
    )
    if not file_meta:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Файл не найден"
        )

    # Генерация ссылки
    presigned_url = await S3Storage.generate_presigned_url(
        user_id=ctx.user_id,
        file_id=file_id,
    )
    return SignedUrl(url=presigned_url)


@router.get(
    "/files",
    tags=["Files"],
    summary="List all files",
)
async def list_files(
    ctx: RequestContext = Depends(),
) -> list[FileMeta]:
    result = await DaoFileMeta.list_file_meta(session=ctx.session, user_id=ctx.user_id)

    logger.debug(result)

    return FileMeta.from_orm_list(result)
