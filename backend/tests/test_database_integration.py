"""
Covers the process-global SQLAlchemy engine and Alembic applying the schema.

HTTP tests override ``get_db``; this file keeps the lazy engine path and migration
CLI integration honest.
"""

from __future__ import annotations

from pathlib import Path

from alembic import command
from alembic.config import Config
from sqlalchemy import text

from app.core.config import get_settings
from app.db.database import dispose_engine, get_engine

BACKEND_ROOT = Path(__file__).resolve().parents[1]


def _alembic_config() -> Config:
    cfg = Config(str(BACKEND_ROOT / "alembic.ini"))
    return cfg


def test_lazy_engine_singleton_after_alembic_upgrade(tmp_path, monkeypatch) -> None:
    db_file = tmp_path / "global_migrated.db"
    monkeypatch.setenv("DATABASE_URL", f"sqlite:///{db_file.as_posix()}")
    monkeypatch.setenv("APP_ENV", "development")
    get_settings.cache_clear()
    dispose_engine()

    command.upgrade(_alembic_config(), "head")

    first = get_engine()
    second = get_engine()
    assert first is second

    with first.connect() as conn:
        count = conn.execute(text("SELECT COUNT(*) FROM customers")).scalar_one()
        assert count == 0
        # SQLite PRAGMA shape: seq, name, unique, origin, partial
        indexes = conn.execute(text("PRAGMA index_list('customers')")).fetchall()
        index_names = {row[1] for row in indexes}
        assert "ix_customers_email" in index_names
        assert "ix_customers_created_at_id" in index_names

    dispose_engine()
    get_settings.cache_clear()
