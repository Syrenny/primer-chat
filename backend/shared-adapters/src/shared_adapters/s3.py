from uuid import UUID
from typing import Any
import aioboto3
import aiohttp
from loguru import logger
from shared_config import config, secrets


class S3Storage:
    _client = None

    @classmethod
    async def _get_client(cls) -> Any:
        if cls._client is None:
            session = aioboto3.Session()
            cls._client = await session.client(
                service_name=config.s3.service_name,
                region_name=config.s3.region,
                aws_access_key_id=secrets.s3_access_key.get_secret_value(),
                aws_secret_access_key=secrets.s3_secret_key.get_secret_value(),
                endpoint_url=config.s3.endpoint,
            ).__aenter__()  # запускаем как async context один раз
        return cls._client

    @classmethod
    async def upload_pdf(cls, user_id: UUID, file_id: UUID, content: bytes) -> str:
        key = f"{user_id}/{file_id}.pdf"
        client = await cls._get_client()

        await client.put_object(
            Bucket=config.s3.bucket,
            Key=key,
            Body=content,
            ContentType="application/pdf",
        )

        logger.debug(f"Uploaded file to S3: {key}")

        # Генерируем временную ссылку (presigned)
        url = await client.generate_presigned_url(
            ClientMethod="get_object",
            Params={"Bucket": config.s3.bucket, "Key": key},
            ExpiresIn=config.s3.presign_expire_seconds,
        )

        return url

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

    @classmethod
    async def delete_pdf(cls, user_id: UUID, file_id: UUID) -> None:
        key = f"{user_id}/{file_id}.pdf"
        client = await cls._get_client()

        try:
            await client.delete_object(Bucket=config.s3.bucket, Key=key)
            logger.debug(f"Deleted file from S3: {key}")
        except Exception:
            logger.exception(f"Не удалось удалить файл из S3: {key}")
            raise

    @classmethod
    async def generate_presigned_url(cls, user_id: UUID, file_id: UUID) -> str:
        key = f"{user_id}/{file_id}.pdf"
        client = await cls._get_client()

        return await client.generate_presigned_url(
            ClientMethod="get_object",
            Params={"Bucket": config.s3.bucket, "Key": key},
            ExpiresIn=config.s3.presign_expire_seconds,
        )
