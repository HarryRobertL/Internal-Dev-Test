# Build plan — Customer Information API (technical test)

**Purpose:** Audit the current repository and define an implementation order optimised for a **mid-level** submission: **backend first**, **modular architecture**, alignment with **FastAPI**, **SQLAlchemy**, **PostgreSQL-ready** design, **validation**, **pagination**, and **testing**. **UI is deferred** until the API and tests are credible.

**References:** [MRD.md](./MRD.md), [prd.md](./prd.md), [technical-architecture-note.md](./technical-architecture-note.md)

---

## 1. Current repository assessment

| Aspect | Status | Notes |
|--------|--------|--------|
| **Application code** | **Absent** | No `backend/`, `frontend/`, or monorepo root yet — only specification and architecture markdown. |
| **Product intent** | **Strong** | MRD/PRD define users, endpoints, fields, non-goals, and acceptance checklist. |
| **Technical direction** | **Strong** | Architecture note locks stack, three-tier model, and target folder shape. |
| **CI / tooling** | **None** | No `requirements.txt`, `package.json`, linters, or GitHub Actions — acceptable until scaffold exists. |
| **Doc link consistency** | **Resolved** | Docs now link to `MRD.md` consistently. |
| **Git** | **Unknown / not assumed** | Workspace was not a git repo in earlier context; version control is recommended before heavy implementation. |

**Verdict:** The repo is a **planning-only** baseline. Risk is low: no legacy code to unwind. The main job is **disciplined execution** against PRD + architecture note without scope creep.

---

## 2. Proposed folder structure

Use a **single monorepo root** (name: `customer-info-app` per architecture note, or keep the current folder as root and place `backend/` + `frontend/` inside it — either is fine if README states the convention).

```
customer-info-app/                 # or repo root
  README.md
  .gitignore                       # Python, Node, .env, SQLite files, etc.

  backend/
    app/
      __init__.py
      main.py                      # FastAPI app factory, lifespan, router include
      api/
        __init__.py
        routes.py                  # customer routes only (thin); or routes/customers.py if you split later
      core/
        config.py                  # Pydantic Settings: DATABASE_URL, CORS, etc.
      db/
        database.py                # engine, session factory, get_db dependency
      models/
        customer.py                # SQLAlchemy model: UUID PK, timestamps, columns per PRD
      schemas/
        customer.py                # Pydantic: create, read, list envelope, pagination meta
      services/
        customer_service.py        # create, get_by_id, list_paginated
      utils/
        errors.py                  # HTTPException helpers or error response builders
    alembic/
      versions/                    # migration scripts
    tests/
      conftest.py                  # app + client + db fixtures (in-memory SQLite or test DB)
      test_customers_api.py
      test_customer_service.py
    alembic.ini
    requirements.txt
    pyproject.toml                 # optional but nice: tool config, pytest paths
    .env.example

  frontend/
    src/
      api/
        customers.ts               # fetch wrappers + React Query keys
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
        utils.ts                   # cn(), formatters if needed
      App.tsx
      main.tsx
    public/
    index.html
    package.json
    vite.config.ts
    tsconfig.json
    tailwind.config.js             # or .ts / postcss as per Vite template
    .env.example
```

**Modularity rules (for reviewers):**

- **Routers** depend on **services** and **schemas**, not on raw SQL in handlers.
- **Services** depend on **models** + **db session**, not on FastAPI `Request` objects.
- **Schemas** are the contract for JSON in/out; **models** are the persistence shape.

---

## 3. Implementation phases (order)

Phases are **sequential**; do not start frontend until **Phase B** endpoints are stable and **Phase C** tests pass locally.

### Phase A — Backend skeleton and configuration

1. Python project layout under `backend/`, virtualenv, `requirements.txt` / optional `pyproject.toml`.
2. `core/config.py` — load `DATABASE_URL` and CORS origins from environment; `.env.example` with placeholders.
3. `db/database.py` — SQLAlchemy 2.x style engine + `SessionLocal` + `get_db` dependency.
4. `main.py` — FastAPI app, CORS middleware, health route (optional), include customer router stub.

**Exit criteria:** `uvicorn app.main:app` starts; OpenAPI UI loads; no DB required yet or connect with empty DB.

### Phase B — Domain model, migrations, service layer, routes

1. **`models/customer.py`** — UUID primary key, `created_at` (UTC), columns: `name`, `email`, `phone`, `request_details`. Use types that work on **PostgreSQL** and **SQLite** (e.g. `UUID` / string UUID strategy documented in architecture — pick one and apply in Alembic).
2. **`schemas/customer.py`** — Pydantic v2 models: create body, public read model, **pagination** response wrapper (e.g. `items`, `total`, `page`, `page_size`).
3. **`services/customer_service.py`** — `create_customer`, `get_customer`, `list_customers(page, page_size)` with total count query or equivalent for UI paging.
4. **`api/routes.py`** — `POST /api/customers`, `GET /api/customers/{id}`, `GET /api/customers` with query params; delegate to service; map domain errors to HTTP status.
5. **`utils/errors.py`** — Consistent error JSON for 422 vs 404 vs 500 (PRD “consistent responses”).
6. **Alembic** — **Done:** baseline revision `67c84f970ba5` (`alembic/versions/`); app does not use `create_all` at startup; see **`backend/README.md`** for `upgrade head`, autogenerate workflow, and empty-revision / `stamp head` notes.

**Exit criteria:** Manual testing via OpenAPI or curl succeeds against SQLite or Postgres; validation rejects bad email and missing fields.

### Phase C — Backend testing hardening

1. **`tests/conftest.py`** — Test database (SQLite file or `:memory:` with StaticPool if needed), session override for FastAPI `dependency_overrides`.
2. **`test_customers_api.py`** — Happy paths + 404 + validation errors + pagination boundaries (empty list, second page).
3. **`test_customer_service.py`** — Pagination math, optional business rules, isolation from HTTP.

**Exit criteria:** `pytest` green locally; README documents one command to run tests.

### Phase D — README and developer experience (backend-complete)

1. Root **README**: prerequisites, clone, backend venv, `cp .env.example`, migrate, run API, run tests, how to use Postgres vs SQLite.
2. **`.gitignore`**: `.env`, `*.db`, `__pycache__`, `node_modules`, etc.

**Exit criteria:** A reviewer can go from zero to passing tests in **minutes** on a typical machine (PRD quality bar).

### Phase E — Frontend scaffold (after API is stable)

1. Vite + React + TypeScript + Tailwind; `VITE_API_URL` in `.env.example`.
2. **`types/customer.ts`** and **`api/customers.ts`** aligned with backend JSON (including error shape).
3. **TanStack Query** — queries for list + mutation for create; keys and invalidation after successful POST.

**Exit criteria:** App loads; can create and see list against running backend.

### Phase F — UI features and UX states

1. **CustomerForm** — fields per PRD; client-side validation mirroring server rules.
2. **CustomerTable** + pagination controls bound to API metadata.
3. **StatusBanner** / inline messages — loading, success, failure, **empty list** state.
4. **PageShell** — internal-tool layout (spacing, table readability).

**Exit criteria:** PRD frontend checklist satisfied without over-engineering.

### Phase G — Frontend tests (time-boxed)

1. Vitest + RTL: form validation, maybe one happy-path component test with mocked API.
2. Do **not** block shipping on 100% FE coverage; backend tests carry more weight for this test.

### Phase H — Final pass

1. Cross-check PRD acceptance checklist.
2. Verify docs and setup instructions are consistent and up to date.
3. Optional: `docker-compose.yml` for Postgres only — nice-to-have, not required by MRD non-goals.

---

## 4. Major technical decisions (and why)

| Decision | Choice | Why |
|----------|--------|-----|
| **API style** | REST JSON under `/api/customers` | Matches PRD and reviewer expectations; OpenAPI for free with FastAPI. |
| **ID type** | UUID string in JSON, UUID/native in DB for Postgres | PRD requires UUID; stable public identifiers; document string format in API. |
| **Pagination** | Offset/limit or page/page_size with `total` | Simple for internal tools; React table + “next page” is straightforward. Cursor-based is optional and usually unnecessary here. |
| **DB for local dev** | SQLite OK if Alembic + URL switch to Postgres is documented | PRD allows SQLite for speed; PostgreSQL-ready means no SQLite-only hacks in models without comment. |
| **Session scope** | One session per request via dependency | Standard FastAPI + SQLAlchemy pattern; easy to test with overrides. |
| **Validation split** | Pydantic on boundary; service assumes validated DTOs | Keeps routes thin; avoids duplicate validation logic scattered in handlers. |
| **422 vs custom 400** | Prefer FastAPI/Pydantic 422 for body validation; 404 for missing id | Familiar to clients; document in README if you unify error envelope. |
| **CORS** | Allow Vite dev origin via env | Required for local full-stack dev without proxy complexity. |
| **React data layer** | TanStack Query | PRD asks for loading/error/refetch; avoids useEffect spaghetti. |
| **shadcn/ui** | Default **skip** unless it saves time | Architecture note: only if it speeds you up cleanly; Tailwind alone is enough for internal UI. |

---

## 5. Dependencies list

### Backend (`requirements.txt` or `pyproject.toml` equivalents)

**Runtime (minimum credible set):**

- `fastapi`
- `uvicorn[standard]` — ASGI server for local and simple deploy
- `sqlalchemy`
- `alembic`
- `pydantic-settings` — optional but clean for `config.py`
- Driver: `psycopg[binary]` or `asyncpg` only if you go async end-to-end (sync + `psycopg` is simpler for mid-level scope)
- For SQLite: stdlib / SQLAlchemy built-in; no extra package required

**Dev / test:**

- `pytest`
- `httpx` — FastAPI `TestClient` uses it
- Optional: `pytest-cov`, `ruff` or `black` (quality signal without ceremony)

**Notes:**

- Pin major versions in submission repos to avoid surprise breakage.
- If you use `email-validator` for Pydantic `EmailStr`, add `email-validator` explicitly.

### Frontend (`package.json`)

**Runtime / build:**

- `react`, `react-dom`
- `typescript`
- `vite`
- `@vitejs/plugin-react`
- `tailwindcss`, `postcss`, `autoprefixer`
- `@tanstack/react-query`

**Dev / test:**

- `vitest`
- `@testing-library/react`, `@testing-library/jest-dom`, `@testing-library/user-event`
- `jsdom` (usually pulled by Vitest for DOM tests)

**Optional:**

- `clsx` + `tailwind-merge` (common pair for `cn()` in `lib/utils.ts`)
- shadcn/ui only if adopted — brings `class-variance-authority`, `lucide-react`, etc. (add only if you commit to that path)

---

## 6. Risks and likely failure points

| Risk | Impact | Mitigation |
|------|--------|------------|
| **UUID + SQLite + Alembic quirks** | Migrations or types differ from Postgres | Use one strategy (e.g. `String(36)` for UUID on SQLite vs native UUID on Postgres) and document it; test migration against both if time allows. |
| **Fat route handlers** | Reviewers mark down “no service layer” | Enforce rule: routes only parse, validate (implicit via Pydantic), call service, return schema. |
| **Inconsistent error JSON** | Frontend hacks; looks amateur | Define one error shape in `errors.py`; use `HTTPException(detail=...)` or exception handlers consistently. |
| **Pagination without `total`** | UI cannot build proper pager | PRD asks for metadata; include total count or explain cursor contract — offset+total is easier. |
| **CORS misconfiguration** | Frontend “mysteriously” fails | Set allowed origins from env; README calls out `VITE` port vs API port. |
| **Tests coupled to production DB** | Flaky CI / slow onboarding | Tests use isolated SQLite or disposable Postgres schema; never require manual seed data. |
| **Scope creep (auth, Docker swarm, etc.)** | Time lost; violates MRD non-goals | Treat README and backend tests as the “polish” investment, not new features. |
| **Doc consistency drift** | Confusion during review | Keep one canonical naming convention and validate links during final pass. |
| **Frontend before API freeze** | Rework when JSON changes | Strict **Phase E** gate: complete Phases A–D first. |

---

## Summary

The repository is **documentation-ready** but **implementation-empty**. Follow **Phases A→D** to deliver a **reviewer-friendly backend** (modular packages, Alembic, validation, pagination, pytest), then **E→G** for React + UX states. Align dependencies with the tables above, decide UUID/pagination/error envelope early, and treat **thin routes + tested services** as the highest-signal part of the submission.
