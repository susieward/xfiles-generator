from fastapi import Depends, WebSocket
from app.logic.text_generator import TextGenerator
from app.logic.connection_manager import ConnectionManager


async def get_manager(request: WebSocket) -> ConnectionManager:
    return request.app.state.connection_manager
