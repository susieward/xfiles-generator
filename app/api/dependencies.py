from fastapi import Request, Depends, WebSocket
from app.logic.text_generator import TextGenerator


def get_model(request: WebSocket):
    return request.app.state.model


def get_tokenizer(request: WebSocket):
    return request.app.state.tokenizer


def text_generator_dependency(
    model = Depends(get_model),
    tokenizer = Depends(get_tokenizer)
) -> TextGenerator:
    return TextGenerator(model=model, tokenizer=tokenizer)
