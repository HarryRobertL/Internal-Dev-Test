"""Health endpoint contract tests."""

from __future__ import annotations

import app.api.health as health_api

def test_health_uses_standard_envelope(client) -> None:
    response = client.get("/health")
    assert response.status_code == 200
    body = response.json()
    assert body == {
        "data": {"status": "ok", "database": {"status": "ok"}},
        "error": None,
        "meta": None,
    }


def test_health_returns_503_when_db_is_unreachable(client, monkeypatch) -> None:
    class _BrokenConnection:
        def __enter__(self):
            raise RuntimeError("db unavailable")

        def __exit__(self, exc_type, exc, tb):
            return False

    class _BrokenEngine:
        def connect(self):
            return _BrokenConnection()

    monkeypatch.setattr(health_api, "get_engine", lambda: _BrokenEngine())

    response = client.get("/health")
    assert response.status_code == 503
    assert response.json() == {
        "data": None,
        "error": {
            "code": "service_unavailable",
            "message": "Database connectivity check failed",
            "details": None,
        },
        "meta": None,
    }
