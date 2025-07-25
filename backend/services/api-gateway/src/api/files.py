from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, UploadFile, status
from shared_adapters.s3 import S3Storage
from src.context.session import SessionContext
from src.db.dao import DaoFileMeta
from src.db.session import AsyncSession, get_db
from src.models.files import FileMeta

router = APIRouter()
from src.models.files import FileStatus, SignedUrl
from src.services import FileService, get_file_service


@router.post(
    "/files",
    tags=["Files"],
    summary="Upload a file",
)
async def add_file(
    file: UploadFile,
    session: AsyncSession = Depends(get_db),
    file_service: FileService = Depends(get_file_service),
    user_id: UUID = Depends(SessionContext.get_user_id),
) -> FileMeta:
    response = await file_service.add_file(
        upload_file=file, session=session, user_id=user_id
    )

    return response


@router.get("/files/{file_id}/status", tags=["Files"], response_model=FileStatus)
async def get_indexing_status(
    file_id: UUID,
    session: AsyncSession = Depends(get_db),
    user_id: UUID = Depends(SessionContext.get_user_id),
) -> FileStatus:
    status = await DaoFileMeta.is_indexed(
        session=session, user_id=user_id, file_id=file_id
    )
    return FileStatus(file_id=file_id, status=status)


@router.delete(
    "/files/{file_id}",
    tags=["Files"],
    summary="Delete a file",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_file(
    file_id: UUID,
    session: AsyncSession = Depends(get_db),
    file_service: FileService = Depends(get_file_service),
    user_id: UUID = Depends(SessionContext.get_user_id),
) -> None:
    await file_service.delete_file(file_id=file_id, session=session, user_id=user_id)


@router.get(
    "/files/{file_id}/signed-url",
    tags=["Files"],
    summary="Generate temporary link",
    response_model=SignedUrl,
)
async def get_signed_url(
    file_id: UUID,
    session: AsyncSession = Depends(get_db),
    user_id: UUID = Depends(SessionContext.get_user_id),
) -> SignedUrl:
    # Проверка, что файл существует и принадлежит пользователю
    file_meta = await DaoFileMeta.get_file_meta(
        session=session, user_id=user_id, file_id=file_id
    )
    if not file_meta:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Файл не найден"
        )

    # Генерация ссылки
    presigned_url = await S3Storage.generate_presigned_url(
        user_id=user_id,
        file_id=file_id,
    )
    return SignedUrl(url=presigned_url)


@router.get(
    "/files",
    tags=["Files"],
    summary="List all files",
)
async def list_files(
    session: AsyncSession = Depends(get_db),
    user_id: UUID = Depends(SessionContext.get_user_id),
) -> list[FileMeta]:
    result = await DaoFileMeta.list_file_meta(session=session, user_id=user_id)

    return result
