"""FastAPI application entry point."""

import logging
from contextlib import asynccontextmanager
from typing import AsyncIterator

from fastapi import FastAPI

from app.config import get_settings


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    """Validate settings and initialize process logging at startup."""
    settings = get_settings()
    logging.basicConfig(
        level=settings.log_level,
        format="%(asctime)s %(levelname)s %(name)s %(message)s",
    )
    yield


def create_app() -> FastAPI:
    """Build the application without opening database connections at import time."""
    application = FastAPI(
        title="Purely Sports API",
        version="0.1.0",
        lifespan=lifespan,
    )

    @application.get("/health", tags=["health"])
    def health() -> dict[str, str]:
        """Report that the HTTP process is running."""
        return {"status": "ok"}

    return application


app = create_app()
