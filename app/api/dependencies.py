from fastapi import Depends, WebSocket
from app.logic.text_generator import TextGenerator


def text_generator_dependency(request: WebSocket) -> TextGenerator:
    return request.app.state.text_generator
