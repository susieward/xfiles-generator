from fastapi import Depends, WebSocket
from app.logic.connection_manager import ConnectionManager

def connection_manager_dependency(request: WebSocket) -> ConnectionManager:
    return request.app.state.connection_manager
