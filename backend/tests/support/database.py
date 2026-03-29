"""Isolated in-memory SQLite engines for tests (no shared state with dev DB files)."""

from __future__ import annotations

from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.db.base import Base

# StaticPool: TestClient runs sync views on a threadpool; default SQLite pooling would open
# a new :memory: database per connection (no shared schema).
SQLITE_MEMORY_URL = "sqlite://"


def create_memory_engine() -> Engine:
    return create_engine(
        SQLITE_MEMORY_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
        pool_pre_ping=False,
    )


def create_tables(engine: Engine) -> None:
    from app.models import customer as _customer  # noqa: F401 — register ORM mappers

    Base.metadata.create_all(bind=engine)


def session_factory(engine: Engine) -> sessionmaker[Session]:
    return sessionmaker(autocommit=False, autoflush=False, bind=engine)
