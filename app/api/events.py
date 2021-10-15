from typing import Callable
from fastapi import FastAPI
from transformers import pipeline, GPT2Tokenizer
from app.logic.custom_model import CustomModel

def init_model(app: FastAPI):
    def _init_model_and_tokenizer():
        config = app.state.config

        tokenizer = GPT2Tokenizer.from_pretrained('gpt2')
        model = CustomModel.from_pretrained(config.MODEL_PATH)

        app.state.model = model
        app.state.tokenizer = tokenizer

    return _init_model_and_tokenizer
