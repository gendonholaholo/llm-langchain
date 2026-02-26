"""FastAPI application factory with lifespan."""

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.router import api_router
from app.core.database import engine
from app.core.logging import setup_logging


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None]:
    setup_logging()
    yield
    await engine.dispose()


def create_app() -> FastAPI:
    app = FastAPI(
        title="WhatsApp AI Chatbot",
        version="0.1.0",
        lifespan=lifespan,
    )
    app.include_router(api_router)
    return app


app = create_app()
