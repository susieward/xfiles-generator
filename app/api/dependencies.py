from fastapi import Depends, WebSocket
from app.logic.text_generator import TextGenerator
from transformers import GPT2Tokenizer
from app.models.transformer.custom_model import CustomModel

def get_model(request: WebSocket):
    config = request.app.state.config
    model = CustomModel.from_pretrained(config.MODEL_PATH)
    return model


def get_tokenizer(request: WebSocket):
    tokenizer = GPT2Tokenizer.from_pretrained('gpt2')
    return tokenizer


def text_generator_dependency(
    model = Depends(get_model),
    tokenizer = Depends(get_tokenizer)
) -> TextGenerator:
    return TextGenerator(model=model, tokenizer=tokenizer)
