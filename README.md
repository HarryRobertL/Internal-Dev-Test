# Customer request system

This project demonstrates a **production-minded internal customer request system**, focusing on clean architecture, API consistency, test coverage, CI integration, and resilient frontend behaviour. It is **not** a minimal CRUD demo: it is structured as a **production-aware internal tool** with migrations, envelopes, and operational guardrails.

## Key features

- Service-layer FastAPI backend and typed React dashboard
- Alembic-managed schema (no `create_all` on the app runtime path)
- Standard `{ data, error, meta }` API contract and resilient frontend client
- CI on every push and PR: migrations, tests, lint, build
- Backend and frontend tests, plus optional PostgreSQL validation

## Architecture overview

```
Frontend (React + TypeScript)
  → API client (typed calls, timeout + bounded retries)
  → FastAPI routes (thin controllers: parse, validate, delegate)
  → Service layer (business rules, orchestration)
  → Database (SQLAlchemy ORM + Alembic migrations)
```

**Why this separation:** Routes stay easy to read and change; **business logic lives in one place** so it is **unit-testable** without HTTP. The API client isolates **network behaviour** (timeouts, retries, errors) from UI components. Together this scales to more endpoints and consumers (jobs, CLIs) without duplicating rules or tangling UI with transport details.

## Request lifecycle

When a user submits the **Submit Request** form:

1. **Frontend** validates inputs locally, then calls the API client.
2. **API client** sends `POST /api/customers` with a JSON body, **enforces a timeout**, and **retries only** on timeout or **5xx** (not on network/CORS failures, to avoid retry storms).
3. **FastAPI** applies **Pydantic validation** on the payload; invalid data returns a structured **error envelope** without hitting the DB.
4. **Service layer** applies domain rules and persists via SQLAlchemy.
5. **Database** commits the row; schema is defined by **Alembic** revisions, not ad-hoc DDL.
6. **Response** returns the same **envelope** shape: success with `data` (and optional `meta`), or failure with `error` (`code`, `message`, `details`).

The list view follows the same pattern: **GET** with pagination query params → validation → service query → envelope with `data` and `meta.pagination`.

## Continuous integration

Workflow: [`.github/workflows/ci.yml`](.github/workflows/ci.yml).

CI runs on **every push and pull request**. It **applies Alembic migrations** and runs **backend tests**, then runs **frontend lint**, **frontend tests**, and a **production build**. That **enforces migrations, tests, lint, and build** before code is merged.

**This ensures code quality and prevents regressions before changes are merged.**

## Production considerations

| Problem | Solution |
|--------|----------|
| Clients must handle success and errors consistently | **Standard envelope** `{ data, error, meta }` so the UI branches on one contract |
| Slow or flaky networks cause hung UI or noisy retries | **Timeout + bounded retries** (timeouts / 5xx only); list loads are **abort-safe** on navigation |
| Schema drift between environments | **Alembic** versions the schema; production path does not rely on `create_all` |
| Operating without visibility or liveness signal | **Request logging** (method, path, status, duration, request id) and **`/health`** including DB check |
| “Works on SQLite” is not enough for real deploys | **PostgreSQL driver and URL shape** supported; optional **validation script** against a real Postgres instance |

## Key design decisions

- **Pagination:** Offset/page (`page`, `limit`, `total`, `total_pages`) for a simple internal UI; cursor-based pagination would be the next step at very large scale.
- **SQLite vs PostgreSQL:** SQLite for fast local work; PostgreSQL as the production-shaped target, with migrations and tests designed to stay compatible.

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

---

This project is intentionally structured to reflect **real-world internal systems**, focusing on **reliability, maintainability, and predictable behaviour** rather than minimal implementation.
