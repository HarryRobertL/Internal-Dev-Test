"""Optional PostgreSQL validation for migration + runtime type behaviour."""

from __future__ import annotations

import os
import uuid
from pathlib import Path

import pytest
from alembic import command
from alembic.config import Config
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.db.database import dispose_engine, get_engine
from app.schemas.customer import CustomerCreate
from app.services.customer_service import create_customer

BACKEND_ROOT = Path(__file__).resolve().parents[1]
ALEMBIC_HEAD = "8f3c2db4c3a1"


def _postgres_test_url() -> str | None:
    url = os.getenv("TEST_DATABASE_URL")
    if not url:
        return None
    if not url.startswith("postgresql+psycopg://"):
        return None
    return url


pytestmark = pytest.mark.skipif(
    _postgres_test_url() is None,
    reason="Set TEST_DATABASE_URL=postgresql+psycopg://... to run PostgreSQL validation.",
)


def _alembic_config() -> Config:
    return Config(str(BACKEND_ROOT / "alembic.ini"))


def test_postgres_migrations_and_runtime_behaviour(monkeypatch) -> None:
    postgres_url = _postgres_test_url()
    assert postgres_url is not None

    monkeypatch.setenv("DATABASE_URL", postgres_url)
    monkeypatch.setenv("APP_ENV", "test")
    get_settings.cache_clear()
    dispose_engine()

    command.upgrade(_alembic_config(), "head")
    command.downgrade(_alembic_config(), "base")
    command.upgrade(_alembic_config(), "head")

    engine = get_engine()
    with Session(engine) as session:
        row = create_customer(
            session,
            CustomerCreate.model_validate(
                {
                    "name": "Postgres Tester",
                    "email": "postgres.tester@example.com",
                    "phone": "+1 555 0102",
                    "request_details": "Validate UUID and timezone-aware timestamp.",
                }
            ),
        )
        session.refresh(row)
        assert isinstance(row.id, uuid.UUID)
        assert row.created_at.tzinfo is not None
        assert row.created_at.utcoffset() is not None

    with engine.connect() as conn:
        version = conn.execute(text("SELECT version_num FROM alembic_version")).scalar_one()
        assert version == ALEMBIC_HEAD

        rows = conn.execute(
            text(
                """
                SELECT indexname
                FROM pg_indexes
                WHERE schemaname = 'public' AND tablename = 'customers'
                """
            )
        ).fetchall()
        index_names = {row[0] for row in rows}
        assert "ix_customers_email" in index_names
        assert "ix_customers_created_at_id" in index_names

    dispose_engine()
    get_settings.cache_clear()
