"""Readiness endpoint behavior tests."""

from fastapi.testclient import TestClient
from sqlalchemy.exc import OperationalError

import app.main as main_module
from app.main import app


def test_readiness_succeeds_when_database_is_available(monkeypatch):
    monkeypatch.setenv(
        "DATABASE_URL",
        "postgresql+psycopg://user:pass@localhost:5432/purely_sports",
    )
    monkeypatch.setattr(main_module, "check_database_connection", lambda: None)
    with TestClient(app) as client:
        response = client.get("/ready")
    assert response.status_code == 200
    assert response.json() == {"status": "ready"}


def test_readiness_returns_service_unavailable_when_database_fails(monkeypatch):
    monkeypatch.setenv(
        "DATABASE_URL",
        "postgresql+psycopg://user:pass@localhost:5432/purely_sports",
    )

    def fail_connection() -> None:
        raise OperationalError("SELECT 1", {}, RuntimeError("database unavailable"))

    monkeypatch.setattr(main_module, "check_database_connection", fail_connection)
    with TestClient(app) as client:
        response = client.get("/ready")
    assert response.status_code == 503
    assert response.json() == {"detail": "Database unavailable"}
