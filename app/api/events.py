from typing import Callable
from fastapi import FastAPI
from app.logic.connection_manager import ConnectionManager
from app.logic.text_generator import TextGenerator

async def on_startup():
    async def _create() -> None:
        manager = ConnectionManager()
        app.state.connection_manager = manager

    return _create
