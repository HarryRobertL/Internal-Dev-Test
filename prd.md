# Product Requirements Document (PRD)

## Product

**Customer Information API** — internal operator tool: React frontend + Python API + relational persistence for customer request records.

**Companion doc:** [MRD.md](./MRD.md) (market framing and assessment intent).

---

## Goals

1. Let operators submit and browse customer requests reliably.
2. Enforce validation and consistent API responses end to end.
3. Ship code that is structured, tested, and easy to run locally in minutes.

---

## Core features

| ID | Feature | Detail |
|----|---------|--------|
| F1 | Submit customer request | User submits from a **React** form; payload is sent to the backend create endpoint. |
| F2 | Dual validation | **Client-side** validation for immediate feedback; **server-side** validation as source of truth. |
| F3 | Persist with identity and time | Each stored request has a **UUID** primary key and **timestamp(s)** (e.g. created_at; updated_at optional if justified). |
| F4 | Retrieve one | Fetch a single customer/request by **ID** via API; UI or API consumer can display or use the record. |
| F5 | List with pagination | List endpoint supports **pagination** (e.g. page/limit or cursor — choose one pattern and document it). |
| F6 | Consistent responses | **Success** and **error** payloads follow a predictable shape (status codes + structured body where applicable). |
| F7 | Internal-tool UI | Records are shown in the UI in a **clean, internal-tool** style: readable tables/cards, clear hierarchy, no marketing chrome. |

---

## API surface (normative)

Endpoints must exist and behave as follows (paths may use a shared prefix such as `/api`).

| Method | Path | Behaviour |
|--------|------|-----------|
| `POST` | `/api/customers` | Create customer request; validate body; return created resource with UUID and timestamps on success. |
| `GET` | `/api/customers/{id}` | Return one record by ID; **404** (or equivalent) when missing. |
| `GET` | `/api/customers` | Return **paginated** list; include enough metadata for the client to page (e.g. total count and/or next page indicator). |

**Payload fields (create / display):**

- `name` — required  
- `email` — required, **valid email format**  
- `phone` — required (format rules as documented, consistent client + server)  
- `request_details` — required  

Additional read-only fields: at minimum **id** (UUID), **created_at** (and any other agreed timestamps).

---

## Backend requirements

### Stack and style

- **Python** backend, **FastAPI** preferred (per spec).
- **RESTful** resource design around `customers` (nouns, appropriate verbs/HTTP methods).
- **SQLAlchemy** ORM for persistence.
- **PostgreSQL-ready** schema and configuration; **SQLite** acceptable for **local** development if the codebase clearly supports switching to PostgreSQL (connection URL, dialect-appropriate types where needed, migrations or documented schema approach).

### Validation and handling

- Validate **required fields** and **email format** on the server (Pydantic or equivalent aligned with FastAPI).
- **Sanitised, structured** request handling: parse JSON once, validate, then delegate; avoid ad hoc dict plumbing in routes.
- Errors map to **clear HTTP status codes** and **consistent** error bodies (e.g. validation vs not found vs server error).

### Architecture

- **Service layer** (or equivalent modules) owns business rules and persistence orchestration; **route handlers stay thin** (bind HTTP ↔ service, no fat logic in routers).

### Testing

- **Tests for HTTP endpoints** (integration or API tests against the app).
- **Tests for service-layer logic** where behaviour is non-trivial (validation edge cases, pagination rules, etc.).
- **Unit tests** as appropriate; suite runnable locally without manual steps beyond documented env setup.

---

## Frontend requirements

### Stack

- **React** UI (matches role requirement).

### Screens / flows

1. **Submit form** — fields: **name**, **email**, **phone**, **request_details**.  
2. **Customer list** — shows records from the paginated API with **pagination controls** wired to the backend.  
3. **Detail or inline display** — as needed to satisfy “retrieve one”; at minimum the API must support GET by id (UI may link from list to detail or show id after create).

### UX requirements

| State | Requirement |
|-------|-------------|
| Loading | Visible during fetches and submission. |
| Empty | Clear **empty state** when no customers exist. |
| Validation | Inline or summary validation before submit; align messages with server rules where possible. |
| Submission feedback | Distinct **success** and **failure** feedback after create. |
| Errors | Network/server errors communicated clearly without raw stack traces. |

### Visual

- **Polished internal-tool feel**: sensible spacing, typography, tables or lists that scan well; functional, not decorative.

---

## Quality and repository requirements

| Area | Requirement |
|------|-------------|
| Structure | **Clean** package/layout for backend and frontend; boundaries easy to navigate. |
| Code | **Readable**; **consistent naming** across layers. |
| README | **Clear**: what it does, prerequisites, how to run API + UI, how to run tests, how to point at DB. |
| Configuration | **Example env files** (e.g. `.env.example`) documenting variables; **no secrets** committed. |
| Startup | **Deterministic** steps (documented commands); a new developer can run locally **in minutes**. |
| Testing | Backend **unit / API** tests executable locally; frontend testing optional unless spec extended—backend test bar is explicit above. |

---

## Out of scope (inherits MRD)

- Authentication / authorisation  
- Full production deployment  
- Microservices  
- Heavy proprietary UI frameworks beyond what React needs  

---

## Acceptance checklist

- [ ] `POST /api/customers` creates records with UUID + timestamps; validates required fields and email.  
- [ ] `GET /api/customers/{id}` returns one record or appropriate not-found response.  
- [ ] `GET /api/customers` returns paginated data with documented query parameters.  
- [ ] Success and error response shapes are documented and used consistently.  
- [ ] SQLAlchemy + DB design is PostgreSQL-ready; local SQLite OK if switch is documented.  
- [ ] Service layer present; routers thin.  
- [ ] Tests cover endpoints, meaningful service logic, and public error JSON (validation, not-found, and unhandled 500 envelope).  
- [ ] React: form, list + pagination, loading / empty / validation / success / error states.  
- [ ] README + `.env.example` (or equivalent); no secrets in repo.  

---

## Document control

| Field | Value |
|-------|--------|
| Document | PRD — Customer Information API |
| Purpose | Detailed product and engineering requirements for implementation |
