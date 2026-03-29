# Customer Information API

Production-minded full stack technical submission with:

- **Backend:** FastAPI + SQLAlchemy + Alembic + pytest
- **Frontend:** React + TypeScript + Vite + Tailwind + Vitest/RTL
- **Database:** PostgreSQL-ready schema, SQLite local fallback

## Repository structure

- `backend/` — API, migrations, tests, env example
- `frontend/` — single-page internal dashboard, API client, tests, env example
- `MRD.md` — market requirements framing
- `prd.md` — product requirements
- `technical-architecture-note.md` — architecture and stack
- `build-plan.md` — delivery plan and risk notes

## Quick start

### 1) Backend

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # optional
alembic upgrade head
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Backend API: [http://localhost:8000/docs](http://localhost:8000/docs)

### 2) Frontend

```bash
cd frontend
npm install
cp .env.example .env   # optional
npm run dev
```

Frontend app: [http://localhost:5173](http://localhost:5173)

## Environment files

- `backend/.env.example`
  - `DATABASE_URL`
  - `CORS_ORIGINS`
  - `APP_ENV`
- `frontend/.env.example`
  - `VITE_API_URL`

## Migrations (Alembic)

Schema is managed through Alembic migrations for environment consistency and drift control.

```bash
cd backend
alembic upgrade head
```

When models change:

```bash
alembic revision --autogenerate -m "describe_your_change"
alembic upgrade head
```

If autogenerate creates an empty migration (`upgrade()` and `downgrade()` are only `pass`), remove it only if it has not been applied/committed/shared.

## PostgreSQL validation (local)

The app supports PostgreSQL through `psycopg` via:

- `DATABASE_URL=postgresql+psycopg://...`

Start PostgreSQL with Docker:

```bash
docker run --name customer-info-postgres -e POSTGRES_PASSWORD=postgres -e POSTGRES_DB=customer_info -p 5432:5432 -d postgres:16
```

Then run migration + PostgreSQL validation test:

```bash
cd backend
export TEST_DATABASE_URL="postgresql+psycopg://postgres:postgres@localhost:5432/customer_info"
bash scripts/test_postgres.sh
```

## Key Design Decisions

- **Service layer:** Business logic lives in services rather than routes to keep API handlers thin, improve testability, and make future consumers (CLI/jobs) reuse the same rules.
- **Alembic over `create_all`:** Versioned migrations provide deterministic schema evolution, rollback paths, and safer team workflows; `create_all` is convenient for local prototypes but does not manage incremental production change.
- **Consistent API envelope (`data`, `error`, `meta`):** A single response shape reduces frontend branching, makes error handling predictable, and lowers contract drift risk as endpoints grow.
- **Pagination approach:** Offset/page pagination (`page`, `limit`, `total`, `total_pages`) was chosen for clarity and easy UI implementation. Trade-off: deep pages can become less efficient than cursor-based pagination at very large scale.
- **SQLite vs PostgreSQL:** SQLite keeps local setup fast and frictionless; PostgreSQL is the target production shape for stronger concurrency and operational parity. Migrations and tests are designed to validate behavior across both.

## Verification commands (clean run)

### Backend

```bash
cd backend
.venv/bin/alembic upgrade head
.venv/bin/alembic current
.venv/bin/pytest -q
```

### Frontend

```bash
cd frontend
npm run test
npm run build
npm run lint
```

## What I would improve with more time

- Add CI pipeline (backend + frontend tests, lint, build, migration check) on PRs
- Add typed API schema sharing between backend and frontend (OpenAPI codegen or contract package)
- Add frontend integration tests with MSW for richer error/edge scenarios
- Add backend test matrix against PostgreSQL and SQLite in CI
- Add rate-limiting / request-id middleware and structured request logging
- Add Docker/devcontainer setup for 1-command onboarding

## Final submission checklist

- [x] Backend endpoints implemented (`POST /api/customers`, `GET /api/customers/{id}`, paginated `GET /api/customers`)
- [x] Validation and consistent success/error envelopes implemented
- [x] Service-layer architecture with thin routes
- [x] SQLAlchemy model and Alembic baseline migration (`67c84f970ba5`)
- [x] `create_all` not used in production app path
- [x] Backend tests pass (API + service + exception + migration/lazy-engine coverage)
- [x] Frontend single-page dashboard implemented (form + table + pagination)
- [x] Frontend UX polished for internal-tool usage
- [x] Frontend tests pass (validation, success, API error handling, empty + loading states)
- [x] Env examples present for backend and frontend
- [x] Setup, migration, and verification commands documented
- [x] Naming and docs links consistent (`MRD.md` canonical)
