# Customer Information API (backend)

## Database migrations (Alembic)

**Schema policy:** The database schema is managed **exclusively through Alembic migrations** so every environment (local SQLite, PostgreSQL, shared dev/stage/prod) applies the same versioned DDL and **model definitions cannot silently drift** from what is deployed. The application never calls `Base.metadata.create_all()` at startup.

**Test-only exception:** Isolated pytest databases use `create_all` in `tests/support/` to spin up in-memory SQLite without touching your real `DATABASE_URL` — that path is **not** used for runtime or production-shaped databases.

Reviewer checklist (`env.py` wiring, baseline migration): see **`alembic/README`**.

**Baseline revision:** `67c84f970ba5` (`alembic/versions/67c84f970ba5_init.py`) creates `customers` and the email index. New clones / empty databases only need **`alembic upgrade head`** — you do **not** need to run `revision --autogenerate` again for that schema.

From this directory (`backend/`):

```bash
# Apply all pending migrations (SQLite or PostgreSQL)
alembic upgrade head
```

**When you change SQLAlchemy models** (`app/models/`), generate a new revision, review the diff, then upgrade:

```bash
alembic revision --autogenerate -m "describe_your_change"
alembic upgrade head
```

If autogenerate produces a file whose `upgrade()` (and `downgrade()`) are **only** `pass`, the database already matches the models — there is nothing to migrate. **Remove that new file** only if you have **not** yet run `alembic upgrade` against it and **not** committed or shared it. If it was already applied anywhere, **keep** the revision in the repo so `alembic_version` stays consistent (an empty migration is harmless).

`alembic/env.py` reads **`DATABASE_URL`** via `get_settings()` (same as the FastAPI app). Run Alembic from **`backend/`** so `prepend_sys_path = .` resolves the `app` package.

### “Table already exists”

If `alembic upgrade head` fails because tables already exist (e.g. an older dev DB was created with `create_all`) but the live schema matches the latest migration, stamp without re-running DDL:

```bash
alembic stamp head
```

Then `alembic current` should show `(head)`.

## Run the API

From this directory (`backend/`):

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # optional
alembic upgrade head
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## Tests

Install dev dependencies (included in `requirements.txt`):

```bash
pip install -r requirements.txt
```

Run the suite (must be run from `backend/` so `app` resolves):

```bash
pytest
```

Verbose output:

```bash
pytest -v
```

Coverage report (terminal + HTML):

```bash
pytest --cov=app --cov-report=term-missing --cov-report=html
open htmlcov/index.html   # macOS
```

### Test database strategy

- Each test gets a **fresh SQLite in-memory database** using **`StaticPool`**, so the schema is shared across connections (required because `TestClient` executes the app on a worker thread).
- FastAPI’s `get_db` is **overridden** to use that engine so HTTP tests never read or write a developer’s on-disk `customer_info.db`.
- `APP_ENV=test` is set before importing `app.main`.
- Service tests use the same in-memory fixture without going through HTTP.
- `tests/test_database_integration.py` runs **`alembic upgrade head`** against a temporary file DB, then asserts **`get_engine()`** can query `customers` (covers the global engine path + migrations).

### Shell note (`APP_ENV`)

`tests/conftest.py` forces `APP_ENV=test` for pytest. That only affects the current process. If you ever run **`pytest` and then `uvicorn` in the same shell**, ensure the server sees the right mode, for example:

```bash
unset APP_ENV
# or
export APP_ENV=development
uvicorn app.main:app --reload
```

Using a **new terminal tab** after tests avoids stale env vars entirely.

### Imports (`get_engine` / `get_session_factory`)

Use `from app.db.database import get_engine, get_session_factory, dispose_engine` — the old module-level `engine` / `SessionLocal` exports were removed in favour of lazy initialisation.
