from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect
from src.services.completions import CompletionsDispatcher

from ._context import RequestContext

router = APIRouter()


@router.websocket("/ws/completions")
async def websocket_completions(
    websocket: WebSocket, ctx: RequestContext = Depends()
) -> None:
    await websocket.accept()
    try:
        while True:
            raw = await websocket.receive_text()
            await CompletionsDispatcher.handle_event(
                ws=websocket, raw=raw, user_id=ctx.user_id, session=ctx.session
            )
    except WebSocketDisconnect:
        print("🔌 Client disconnected")
    except Exception as e:
        await websocket.send_text(f"❗ Internal error: {e}")
