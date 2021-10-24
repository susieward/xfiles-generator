from typing import Callable
from fastapi import FastAPI
from app.logic.text_generator import TextGenerator


def startup_generator(app: FastAPI) -> Callable:
    async def _startup() -> None:
        text_generator = TextGenerator()
        if not text_generator.initialized:
            await text_generator.initialize()
        app.state.generator = text_generator

    return _start


def shutdown_generator(app: FastAPI) -> Callable:
    async def _shutdown() -> None:
        await app.state.generator.cleanup()

    return _shutdown
