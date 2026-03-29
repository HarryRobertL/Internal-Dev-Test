"""
Alembic runtime — reads ``DATABASE_URL`` via ``get_settings()`` (same as the FastAPI app).

Run from the ``backend/`` directory so ``prepend_sys_path = .`` resolves the ``app`` package
and ``.env`` is discovered by Pydantic settings.
"""

from __future__ import annotations

from logging.config import fileConfig

from alembic import context
from sqlalchemy import create_engine, pool

from app.core.config import get_settings
from app.db.base import Base

# Register ORM models with Base.metadata for autogenerate
from app.models import customer as _customer  # noqa: F401

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata


def _connect_args(url: str) -> dict:
    if url.startswith("sqlite"):
        return {"check_same_thread": False}
    return {}


def run_migrations_offline() -> None:
    """Emit SQL without a live connection (CI / review). URL comes from env config."""
    url = get_settings().database_url
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
        compare_server_default=True,
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Apply migrations using a one-off engine (NullPool — migration CLI, not the app pool)."""
    settings = get_settings()
    url = settings.database_url
    connectable = create_engine(
        url,
        connect_args=_connect_args(url),
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,
            compare_server_default=True,
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
