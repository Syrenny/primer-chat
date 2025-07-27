from typing import AsyncIterator, Sequence
from uuid import UUID, uuid4

from fastapi import UploadFile
from loguru import logger
from shared_adapters.s3 import S3Storage
from shared_models.indexation.interface import IndexationWorkerRequest
from shared_models.worker.context import WorkerRequestContext
from sqlalchemy.ext.asyncio import AsyncSession
from src.config import config
from src.consumers.indexation.request import IndexationProducer
from src.db.dao import DaoFileMeta
from src.db.models import DBFileMeta
from src.exceptions.files import (
    FilesInvalidPdfError,
    FilesInvalidTypeError,
    FilesValidationError,
)
from src.models.files import FileMeta


class UploadFileReader:
    allowed_mime_types = {"application/pdf"}

    @staticmethod
    async def _parse_pdf(file: UploadFile) -> bytes:
        content = await file.read()
        if not content:
            raise FilesInvalidPdfError(file.filename)
        return content

    parsers = {
        "application/pdf": _parse_pdf,
    }

    @classmethod
    def _validate(cls, file: UploadFile) -> None:
        if file.content_type not in cls.allowed_mime_types:
            raise FilesInvalidTypeError(file.filename)

    @classmethod
    async def _read_iter(cls, files: Sequence[UploadFile]) -> AsyncIterator[bytes]:
        for file in files:
            cls._validate(file)

            parser = cls.parsers.get(file.content_type)
            if not parser:
                raise FilesInvalidPdfError(file.filename)

            content = await parser(file)
            yield content

    @classmethod
    async def read_all(cls, files: Sequence[UploadFile]) -> list[bytes]:
        return [content async for content in cls._read_iter(files)]


class FileProcessor:
    @classmethod
    async def process(
        cls, upload_file: UploadFile, session: AsyncSession, user_id: UUID
    ) -> FileMeta:
        await cls._validate_limits(session, user_id)

        content = await cls._read_file(upload_file)

        file_id = uuid4()

        try:
            s3_link = await cls._upload_to_storage(user_id, file_id, content)

            db_meta = await cls._store_metadata(
                session=session,
                user_id=user_id,
                filename=upload_file.filename,
                file_id=file_id,
            )
        except Exception as err:
            await FileProcessor.delete(
                file_id=file_id, session=session, user_id=user_id
            )
            logger.exception(str(err))
            raise err

        try:
            await cls._enqueue_indexation(
                s3_link, user_id=user_id, file_id=db_meta.file_id
            )
        except Exception as err:
            await FileProcessor.delete(
                file_id=file_id, session=session, user_id=user_id
            )
            raise err

        return FileMeta(
            file_id=db_meta.file_id,
            filename=db_meta.filename,
            is_indexed=False,
        )

    @staticmethod
    async def _validate_limits(session: AsyncSession, user_id: UUID) -> None:
        files = await DaoFileMeta.list_file_meta(session=session, user_id=user_id)
        if len(files) + 1 > config.max_files_per_user:
            raise FilesValidationError(config.max_files_per_user)

    @staticmethod
    async def _read_file(upload_file: UploadFile) -> bytes:
        [content] = await UploadFileReader.read_all([upload_file])
        return content

    @staticmethod
    async def _store_metadata(
        session: AsyncSession, user_id: UUID, file_id: UUID, filename: str
    ) -> DBFileMeta:
        return await DaoFileMeta.add_file_meta(
            session=session, user_id=user_id, filename=filename, file_id=file_id
        )

    @staticmethod
    async def _upload_to_storage(user_id: UUID, file_id: UUID, content: bytes) -> str:
        return await S3Storage.upload_pdf(
            user_id=user_id, file_id=file_id, content=content
        )

    @staticmethod
    async def _enqueue_indexation(s3_link: str, user_id: UUID, file_id: UUID) -> None:
        request_id = uuid4()
        context = WorkerRequestContext(
            request_id=request_id, user_id=user_id, file_id=file_id
        )
        request = IndexationWorkerRequest(s3_link=s3_link, context=context)

        async with IndexationProducer() as producer:
            await producer.send(request)

    @classmethod
    async def delete(cls, file_id: UUID, session: AsyncSession, user_id: UUID) -> None:
        await DaoFileMeta.delete_file_meta(
            session=session, user_id=user_id, file_id=file_id
        )
        await S3Storage.delete_pdf(user_id=user_id, file_id=file_id)


class FileService:
    @classmethod
    async def add_file(
        cls, upload_file: UploadFile, session: AsyncSession, user_id: UUID
    ) -> FileMeta:
        return await FileProcessor.process(
            upload_file=upload_file, session=session, user_id=user_id
        )

    @classmethod
    async def delete_file(
        cls, file_id: UUID, session: AsyncSession, user_id: UUID
    ) -> None:
        await FileProcessor.delete(file_id=file_id, session=session, user_id=user_id)

    @classmethod
    async def set_is_indexed(
        cls, file_id: UUID, session: AsyncSession, user_id: UUID, value: bool
    ) -> None:
        await DaoFileMeta.set_is_indexed(
            session=session, user_id=user_id, file_id=file_id, value=value
        )
