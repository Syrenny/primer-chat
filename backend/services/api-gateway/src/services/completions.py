from collections.abc import AsyncGenerator
from contextlib import aclosing
from typing import Callable
from uuid import UUID

from fastapi import WebSocket
from loguru import logger
from pydantic import ValidationError
from shared_adapters.redis import RedisGenerationBuffer
from sqlalchemy.ext.asyncio import AsyncSession
from src.models.dto.completions import (
    BufferResponse,
    ChunkResponse,
    CompletionsEvent,
    CompletionsRequestEvent,
    ErrorResponse,
    ResumeRequestEvent,
)
from src.services.generation import GenerationService
from src.services.messages import MessageService


class WsUtils:
    @classmethod
    async def send_error(cls, ws: WebSocket, text: str) -> None:
        logger.warning(text)
        response = ErrorResponse(type="error", text=text)
        await ws.send_text(response.model_dump_json())

    @classmethod
    async def send_buffer(cls, ws: WebSocket, text: str) -> None:
        logger.warning(text)
        response = BufferResponse(type="buffer", text=text)
        await ws.send_text(response.model_dump_json())

    @classmethod
    async def send_chunk(cls, ws: WebSocket, text: str) -> None:
        logger.warning(text)
        response = ChunkResponse(type="chunk", text=text)
        await ws.send_text(response.model_dump_json())


class CompletionsEventHandler:
    @staticmethod
    async def get_stream_generator(
        request_id: UUID, user_id: UUID, history_id: UUID
    ) -> Callable:
        async def _stream() -> AsyncGenerator[str, None]:
            generator = GenerationService.listen(
                user_id=user_id,
                history_id=history_id,
                request_id=request_id,
            )
            async with aclosing(generator) as _generator:
                async for chunk in _generator:
                    yield chunk

        return _stream

    @classmethod
    async def on_request(
        cls,
        ws: WebSocket,
        event: CompletionsRequestEvent,
        user_id: UUID,
        session: AsyncSession,
    ) -> None:
        if await RedisGenerationBuffer.exists(user_id=user_id):
            text = "⛔ Generation already in progress"
            await WsUtils.send_error(ws=ws, text=text)
            return

        request_id = await GenerationService.publish(
            user_id=user_id,
            session=session,
            history_id=event.history_id,
            query=event.query,
        )

        stream = await cls.get_stream_generator(
            user_id=user_id, history_id=event.history_id, request_id=request_id
        )
        async for chunk in stream():
            await WsUtils.send_chunk(ws=ws, text=chunk)

    @classmethod
    async def on_resume(
        cls,
        ws: WebSocket,
        event: ResumeRequestEvent,
        user_id: UUID,
    ) -> None:
        if not await RedisGenerationBuffer.exists(user_id=user_id):
            text = "⛔ No active generation"
            await WsUtils.send_error(ws=ws, text=text)
            return

        request_id = await RedisGenerationBuffer.get_request_id(user_id=user_id)
        if not request_id:
            text = "⛔ request_id not found"
            await WsUtils.send_error(ws=ws, text=text)
            return

        buffer = await MessageService.get_buffer(user_id=user_id)

        await WsUtils.send_buffer(ws=ws, text=buffer)

        stream = await cls.get_stream_generator(
            user_id=user_id,
            history_id=event.history_id,
            request_id=request_id,
        )
        async for chunk in stream():
            await WsUtils.send_chunk(ws=ws, text=chunk)


class CompletionsDispatcher:
    @classmethod
    async def handle_event(
        cls, ws: WebSocket, raw: str, user_id: UUID, session: AsyncSession
    ) -> None:
        try:
            event = CompletionsEvent.model_validate_json(raw)
        except ValidationError as err:
            logger.debug(f"Ошибка разбора события {str(err)}")
            await WsUtils.send_error(ws, "Ошибка разбора события")
        match event:
            case CompletionsRequestEvent():
                await CompletionsEventHandler.on_request(
                    ws=ws, event=event, user_id=user_id, session=session
                )
            case ResumeRequestEvent():
                await CompletionsEventHandler.on_resume(
                    ws=ws, event=event, user_id=user_id
                )
            case _:
                text = f"Неизвестный тип события: {event.type}"
                await WsUtils.send_error(ws=ws, text=text)
