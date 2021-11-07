from typing import Callable
from fastapi import FastAPI
from app.logic.connection_manager import ConnectionManager
from app.logic.text_generator import TextGenerator

def on_startup(app: FastAPI):
    async def _create_generator() -> Callable:
        config = app.state.config
        app.state.text_generator = TextGenerator(config=config)
        await app.state.text_generator.initialize()

    return _create_generator


def on_shutdown(app: FastAPI):
    async def _destroy_generator() -> Callable:
        if app.state.text_generator.initialized:
            await app.state.text_generator.shutdown()

    return _destroy_generator
