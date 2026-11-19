"""Synchronous SQLAlchemy engine and request-scoped sessions."""

from collections.abc import Generator
from functools import lru_cache

from sqlalchemy import Engine, create_engine, text
from sqlalchemy.orm import Session, sessionmaker

from app.config import get_settings


@lru_cache
def get_engine() -> Engine:
    """Create the process-wide PostgreSQL engine on first use."""
    return create_engine(get_settings().database_url, pool_pre_ping=True)


@lru_cache
def get_session_factory() -> sessionmaker[Session]:
    """Return the configured session factory."""
    return sessionmaker(bind=get_engine(), autoflush=False, expire_on_commit=False)


def get_session() -> Generator[Session, None, None]:
    """Yield one request-scoped session; transaction owners decide when to commit."""
    session = get_session_factory()()
    try:
        yield session
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def check_database_connection() -> None:
    """Raise the driver's connection error if PostgreSQL is unavailable."""
    with get_engine().connect() as connection:
        connection.execute(text("SELECT 1"))
