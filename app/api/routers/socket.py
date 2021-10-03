from fastapi import APIRouter, WebSocket, Depends

from app.api.dependencies import text_generator_dependency
from app.logic.connection_manager import ConnectionManager
from app.logic.text_generator import TextGenerator

router = APIRouter()

@router.websocket("/ws/{client_id}")
async def socket(
    websocket: WebSocket,
    client_id: str,
    text_generator: TextGenerator = Depends(text_generator_dependency)
):
    on_receive = text_generator.generate

    async with ConnectionManager(websocket, on_receive, client_id) as conn:
        await conn.receive_json()
