import aiohttp
from loguru import logger


async def get_pdf_bytes(s3_link: str) -> bytes:
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(s3_link) as response:
                if response.status != 200:
                    raise ValueError(f"Ошибка при скачивании PDF: {response.status}")
                return await response.read()
    except Exception:
        logger.exception(f"Не удалось получить PDF по ссылке: {s3_link}")
        raise
