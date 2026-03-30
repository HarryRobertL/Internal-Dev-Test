# Customer request system

This project demonstrates a **production-minded internal customer request system**, focusing on clean architecture, API consistency, test coverage, CI integration, and resilient frontend behaviour. It is **not** a minimal CRUD demo: it is structured as a **production-aware internal tool** with migrations, envelopes, and operational guardrails.

This project is structured to reflect **real-world internal tools** rather than a simplified tutorial implementation.

## Key features

- **FastAPI backend** with a **service-layer** architecture (thin routes, testable domain logic)
- **Alembic migrations** — versioned schema; **`create_all` is not used** on the production app path
- **PostgreSQL compatibility** with local SQLite for fast dev; optional **PostgreSQL validation** script
- **Standardised API envelope** — `{ data, error, meta }` for predictable clients and error handling
- **React + TypeScript** internal dashboard (form, table, pagination) with a **clean internal-tool UX**
- **Resilient API client** — timeouts, bounded retries (timeouts / 5xx; no network-error retry storms), abort-safe list loading
- **CI pipeline** — backend migrations + pytest; frontend lint, tests, and build (see `.github/workflows/ci.yml`)
- **Backend and frontend test coverage** — API, services, migrations/engine paths, and UI states

> **GitHub repository description** (paste into repo **Settings → General → Description**):  
> Production-minded full-stack customer request system built with FastAPI and React, featuring CI, PostgreSQL validation, structured API contracts, and resilient frontend data handling.

## Repository structure

- `backend/` — API, migrations, tests, env example
- `frontend/` — single-page internal dashboard, API client, tests, env example
- `MRD.md` — market requirements framing
- `prd.md` — product requirements
- `technical-architecture-note.md` — architecture and stack
- `build-plan.md` — delivery plan and risk notes
- `.github/workflows/ci.yml` — continuous integration

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
cp .env.example .env   # set VITE_API_URL=http://localhost:8000
npm run dev -- --host 0.0.0.0 --port 6001 --strictPort
```

Frontend app: [http://localhost:6001](http://localhost:6001)

## Environment files

- `backend/.env.example` — `DATABASE_URL`, `CORS_ORIGINS`, `APP_ENV`
- `frontend/.env.example` — `VITE_API_URL` (required at build/runtime; no silent default in the client)

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

If autogenerate creates an empty migration (`upgrade()` and `downgrade()` are only `pass`), remove it only if it has not been applied, committed, or shared.

## PostgreSQL validation (local)

The app supports PostgreSQL through `psycopg` via `DATABASE_URL=postgresql+psycopg://...`.

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

## Key design decisions

- **Service layer:** Business logic lives in services rather than routes to keep API handlers thin, improve testability, and allow future consumers (CLI/jobs) to reuse the same rules.
- **Alembic over `create_all`:** Versioned migrations provide deterministic schema evolution, rollback paths, and safer team workflows; `create_all` is convenient for local prototypes but does not manage incremental production change.
- **Consistent API envelope (`data`, `error`, `meta`):** A single response shape reduces frontend branching, makes error handling predictable, and lowers contract drift risk as endpoints grow.
- **Pagination:** Offset/page pagination (`page`, `limit`, `total`, `total_pages`) for clarity and straightforward UI wiring. Trade-off: deep pages can be less efficient than cursor-based pagination at very large scale.
- **SQLite vs PostgreSQL:** SQLite keeps local setup fast; PostgreSQL is the production-shaped target. Migrations and tests are designed to validate behaviour across both.

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

- **Typed contract sharing** between backend and frontend (OpenAPI codegen or a small shared package)
- **Frontend integration tests** with MSW for richer error and edge-case coverage
- **CI matrix** running backend tests against both SQLite (default) and PostgreSQL on PRs
- **API rate limiting** for public or multi-tenant exposure
- **Docker Compose / devcontainer** for one-command onboarding

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
- [x] CI workflow for backend migrations/tests and frontend lint/test/build
- [x] Naming and docs links consistent (`MRD.md` canonical)
