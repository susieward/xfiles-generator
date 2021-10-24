from typing import Callable
from fastapi import FastAPI
from app.logic.connection_manager import ConnectionManager
from app.logic.text_generator import TextGenerator


def on_startup(app: FastAPI) -> Callable:
    async def _create() -> None:
        text_generator = TextGenerator()
        manager = ConnectionManager(generator=text_generator)
        app.state.connection_manager = await manager.startup()

    return _create


def on_shutdown(app: FastAPI) -> Callable:
    async def _shutdown() -> None:
        await app.state.connection_manager.shutdown()

    return _shutdown
