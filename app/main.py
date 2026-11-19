"""FastAPI application entry point."""

import logging
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from sqlalchemy.exc import SQLAlchemyError

from app.config import get_settings
from app.db.session import check_database_connection
from app.logging_config import configure_logging


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    """Validate settings and initialize process logging at startup."""
    settings = get_settings()
    configure_logging(settings.log_level)
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

    @application.get("/ready", tags=["health"])
    def ready() -> dict[str, str]:
        """Report database readiness, returning 503 when PostgreSQL is unavailable."""
        try:
            check_database_connection()
        except SQLAlchemyError as exc:
            logging.getLogger(__name__).exception("Database readiness check failed")
            raise HTTPException(status_code=503, detail="Database unavailable") from exc
        return {"status": "ready"}

    return application


app = create_app()
