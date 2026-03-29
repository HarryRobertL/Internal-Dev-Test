"""
Pytest wiring: each test gets an isolated SQLite :memory: schema.

``APP_ENV=test`` is set before ``app.main`` is imported. Schema is not created at
app startup; use ``alembic upgrade head`` for the real DB (tests use overrides + ``create_all`` in-memory).
"""

from __future__ import annotations

import os

os.environ["APP_ENV"] = "test"

from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker

from app.core.config import get_settings
from app.db.database import dispose_engine, get_db
from app.main import app
from tests.support.database import create_memory_engine, create_tables, session_factory


@pytest.fixture(scope="session")
def fastapi_app():
    """Shared FastAPI application instance."""
    return app


@pytest.fixture(autouse=True)
def _reset_global_db_runtime() -> Generator[None, None, None]:
    """Reset global engine cache between tests (safety if code hits ``get_engine()``)."""
    dispose_engine()
    get_settings.cache_clear()
    # Re-apply test env after cache clear so Settings() reloads with APP_ENV=test
    os.environ["APP_ENV"] = "test"
    yield
    app.dependency_overrides.clear()
    dispose_engine()
    get_settings.cache_clear()
    os.environ["APP_ENV"] = "test"


@pytest.fixture
def memory_engine_session() -> Generator[tuple[Engine, sessionmaker[Session]], None, None]:
    engine = create_memory_engine()
    create_tables(engine)
    factory = session_factory(engine)
    try:
        yield engine, factory
    finally:
        engine.dispose()


@pytest.fixture
def db_session(
    memory_engine_session: tuple[Engine, sessionmaker[Session]],
) -> Generator[Session, None, None]:
    _engine, factory = memory_engine_session
    session = factory()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture
def client(
    fastapi_app,
    memory_engine_session: tuple[Engine, sessionmaker[Session]],
) -> Generator[TestClient, None, None]:
    _engine, factory = memory_engine_session

    def override_get_db() -> Generator[Session, None, None]:
        db = factory()
        try:
            yield db
        finally:
            db.close()

    fastapi_app.dependency_overrides[get_db] = override_get_db
    # Surface 5xx as responses so contract tests can assert JSON error bodies (PRD: no raw traces in API).
    with TestClient(fastapi_app, raise_server_exceptions=False) as test_client:
        yield test_client
