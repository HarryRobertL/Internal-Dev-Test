# Technical architecture note

**Product:** Customer Information API (full stack)  
**Related:** [MRD.md](./MRD.md), [prd.md](./prd.md)

---

## Architectural model

Use a **simple three-tier architecture** because that is what the brief describes:

1. **Presentation** — React SPA talking to the API over HTTP  
2. **Application** — Python API (FastAPI) exposing REST endpoints, validation, and orchestration  
3. **Data** — Relational database accessed through SQLAlchemy  

**Schema governance:** The database schema is **managed exclusively through Alembic migrations** (versioned DDL applied via `alembic upgrade head`) so environments stay consistent and model definitions do not drift from the live database. The runtime app does not use `create_all` at startup; tests may use `create_all` only for isolated in-memory SQLite (see `backend/README.md`).

No microservices, no extra tiers unless a future PRD explicitly adds them.

---

## Recommended stack

### Backend

| Layer | Choice | Role |
|-------|--------|------|
| Framework | **FastAPI** | HTTP API, OpenAPI, async-capable ASGI app |
| Persistence | **SQLAlchemy** | ORM, PostgreSQL-ready models and sessions |
| Validation / IO | **Pydantic** | Request/response schemas aligned with FastAPI |
| Migrations | **Alembic** | Versioned schema; supports PostgreSQL and SQLite |
| Database | **PostgreSQL** (default) | Production-shaped local and deployed target |
| Local convenience | **SQLite** | Optional fallback for fast local demo if configuration clearly switches via env |
| Tests | **pytest** | Unit and API tests |

### Frontend

| Layer | Choice | Role |
|-------|--------|------|
| UI library | **React** | Matches role requirement |
| Language | **TypeScript** | Safer contracts with API types |
| Tooling | **Vite** | Dev server and build |
| Styling | **Tailwind CSS** | Utility-first layout and internal-tool polish |
| Components | **shadcn/ui** | Optional — use **only** if it speeds delivery without clutter |
| Server state | **TanStack Query (React Query)** | API calls, caching, loading/error states, refetch |
| Tests | **Vitest** + **React Testing Library** | Component and integration-style frontend tests |

---

## Repository layout

Root monorepo folder: **`customer-info-app`** (or equivalent single root containing both apps).

```
customer-info-app/
  backend/
    app/
      api/
        routes.py
      core/
        config.py
      db/
        database.py
      models/
        customer.py
      schemas/
        customer.py
      services/
        customer_service.py
      utils/
        errors.py
      main.py
    tests/
      test_customers_api.py
      test_customer_service.py
    alembic.ini
    requirements.txt
    .env.example

  frontend/
    src/
      api/
        customers.ts
      components/
        CustomerForm.tsx
        CustomerTable.tsx
        StatusBanner.tsx
        PageShell.tsx
      pages/
        CustomersPage.tsx
      types/
        customer.ts
      lib/
        utils.ts
      App.tsx
      main.tsx
    package.json
    .env.example

  README.md
```

### Rationale

- **`app/api`** — HTTP surface only; thin handlers that call services.  
- **`app/models`** — SQLAlchemy entities (UUID, timestamps, columns per PRD).  
- **`app/schemas`** — Pydantic models for request/response and validation boundaries.  
- **`app/services`** — Business rules and orchestration (create, get by id, list with pagination).  
- **`app/db`** — Session/engine wiring and dependency injection hooks.  
- **`app/core`** — Settings and environment (e.g. database URL, CORS).  
- **`app/utils`** — Shared error types / helpers for consistent API errors.  
- **`tests/`** — Split **API** tests (`test_customers_api.py`) and **service** tests (`test_customer_service.py`) to match the PRD bar.  
- **Frontend `src/api`** — Centralised fetch/query functions consumed by React Query.  
- **Components + pages** — Form, table, status/empty/error UI, single shell for internal-tool layout.

This shape matches the ideal build emphasis: **backend-first**, clear **separation of routes, models, schemas, services, and database**, with a **structured frontend** that mirrors API boundaries.

---

## Cross-cutting decisions

| Topic | Guidance |
|-------|----------|
| Schema / Alembic | Baseline revision `67c84f970ba5`; `DATABASE_URL` from env; `alembic upgrade head` before running the API. See **`backend/README.md`** (migrations + empty-autogenerate caveat). |
| API base URL | Configure via `frontend/.env.example` (e.g. `VITE_API_URL`); document in README. |
| CORS | Backend allows frontend origin in dev; document production expectations without full deploy scope. |
| Pagination | One consistent pattern (e.g. `page` + `page_size` or `limit` + `offset`); document in README and OpenAPI. |
| Errors | Map domain/not-found/validation to stable JSON shape from `app/utils/errors.py` (or equivalent). |
| Secrets | Never commit; only `.env.example` with placeholder keys. |

---

## Document control

| Field | Value |
|-------|--------|
| Document | Technical architecture note — Customer Information API |
| Purpose | Stack and folder conventions for implementation |
