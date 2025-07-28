import gzip
import json
from uuid import UUID

import aioboto3
import aiohttp
from loguru import logger
from shared_config import config, secrets
from shared_models.indexation.core import IndexationResult


class S3Storage:
    @staticmethod
    def _build_pdf_key(user_id: UUID, file_id: UUID) -> str:
        return f"{user_id}/{file_id}.pdf"

    @staticmethod
    def _create_session():
        return aioboto3.Session().client(
            service_name=config.s3.service_name,
            region_name=config.s3.region,
            aws_access_key_id=secrets.s3_access_key.get_secret_value(),
            aws_secret_access_key=secrets.s3_secret_key.get_secret_value(),
            endpoint_url=config.s3.endpoint,
        )

    @classmethod
    async def upload_pdf(cls, user_id: UUID, file_id: UUID, content: bytes) -> str:
        key = cls._build_pdf_key(user_id, file_id)

        async with cls._create_session() as client:
            await client.put_object(
                Bucket=config.s3.pdf_bucket,
                Key=key,
                Body=content,
                ContentType="application/pdf",
            )

            logger.debug(f"✅ Uploaded file to S3: {key}")

            url = await client.generate_presigned_url(
                ClientMethod="get_object",
                Params={"Bucket": config.s3.pdf_bucket, "Key": key},
                ExpiresIn=config.s3.presign_expire_seconds,
            )

        return url

    @classmethod
    async def delete_pdf(cls, user_id: UUID, file_id: UUID) -> None:
        key = cls._build_pdf_key(user_id, file_id)

        try:
            async with cls._create_session() as client:
                await client.delete_object(Bucket=config.s3.pdf_bucket, Key=key)
                logger.debug(f"🗑️ Deleted file from S3: {key}")
        except Exception:
            logger.exception(f"❌ Failed to delete file from S3: {key}")
            raise

    @classmethod
    async def generate_presigned_url(cls, user_id: UUID, file_id: UUID) -> str:
        key = cls._build_pdf_key(user_id, file_id)

        async with cls._create_session() as client:
            return await client.generate_presigned_url(
                ClientMethod="get_object",
                Params={"Bucket": config.s3.pdf_bucket, "Key": key},
                ExpiresIn=config.s3.presign_expire_seconds,
            )

    @classmethod
    async def get_pdf_bytes_from_url(cls, s3_link: str) -> bytes:
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(s3_link) as response:
                    if response.status != 200:
                        raise ValueError(
                            f"Ошибка при скачивании PDF: {response.status}"
                        )
                    return await response.read()
        except Exception:
            logger.exception(f"Не удалось получить PDF по ссылке: {s3_link}")
            raise

    @staticmethod
    def _build_chunks_key(user_id: UUID, file_id: UUID) -> str:
        return f"{user_id}/{file_id}.chunks.json.gz"

    @classmethod
    async def upload_chunks(
        cls, user_id: UUID, file_id: UUID, result: IndexationResult
    ) -> None:
        key = cls._build_chunks_key(user_id, file_id)

        serialized = result.model_dump_json()
        compressed = gzip.compress(serialized.encode("utf-8"))

        async with cls._create_session() as client:
            await client.put_object(
                Bucket=config.s3.chunks_bucket,
                Key=key,
                Body=compressed,
                ContentType="application/json",
                ContentEncoding="gzip",
            )
            logger.debug(f"✅ Uploaded chunks to S3: {key}")

    @classmethod
    async def download_chunks(cls, user_id: UUID, file_id: UUID) -> IndexationResult:
        key = cls._build_chunks_key(user_id, file_id)

        async with cls._create_session() as client:
            response = await client.get_object(Bucket=config.s3.chunks_bucket, Key=key)
            raw = await response["Body"].read()
            decompressed = gzip.decompress(raw).decode("utf-8")
            data = json.loads(decompressed)

            return IndexationResult.model_validate(data)

    @classmethod
    async def delete_chunks(cls, user_id: UUID, file_id: UUID) -> None:
        key = cls._build_chunks_key(user_id, file_id)

        try:
            async with cls._create_session() as client:
                await client.delete_object(Bucket=config.s3.chunks_bucket, Key=key)
                logger.debug(f"🗑️ Deleted chunks from S3: {key}")
        except Exception:
            logger.exception(f"❌ Failed to delete chunks from S3: {key}")
            raise
