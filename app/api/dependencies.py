from fastapi import Depends, WebSocket
from app.logic.text_generator import TextGenerator


def get_generator(request: WebSocket) -> TextGenerator:
    return request.app.state.generator
