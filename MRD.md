# Market Requirements Document (MRD)

## Project name

**Customer Information API** (full stack: API + operator UI)

---

## Objective

Deliver a small, **production-minded** full stack application that lets an internal user submit customer information from a React frontend, persist it through a Python backend into a **relational database**, and **retrieve** individual records plus **paginated lists**. The submission should read as intentional engineering work: strong backend structure, clear API contracts, a clean frontend, validation, automated tests, and judgment appropriate to real delivery—not a minimal toy CRUD demo.

---

## Why this matters (assessment context)

The target role is **Mid-Level Software Developer** across React, Python, AWS, APIs, scalable services, system design, maintainability, and code quality. Evaluators should see evidence of:

- Architecture and module boundaries, not a single-script backend
- API design, validation, and error handling
- Persistence via SQLAlchemy against a real relational model
- Frontend states that reflect real usage (loading, success, errors, form validation)
- Tests that exercise backend logic and HTTP behaviour
- Documentation (notably a **polished README**) that explains how to run, test, and reason about the system

The build is **not** measured by feature count alone; it is measured by how credibly it resembles a small internal product.

---

## Primary user

**Internal business user or operator** who needs to create and look up **customer request records** through a simple, dependable web UI backed by a stable API.

---

## Success criteria

The initiative is successful when all of the following are true.

### API and data

| Requirement | Description |
|-------------|-------------|
| Create | `POST /api/customers` accepts validated customer payloads and persists them |
| Read one | `GET /api/customers/{id}` returns a single customer when it exists; handles missing resources appropriately |
| Read many | `GET /api/customers` returns a **paginated** list of customers |
| Persistence | Data is stored in a **relational database** using **SQLAlchemy** |
| Validation | Request and domain validation is explicit and consistent with API responses |

### Backend engineering

- **FastAPI** backend with **modular layout** and **service-layer separation** (routes thin, business/data access organised)
- **Error handling** that is predictable for clients (clear status codes and payloads where appropriate)
- **Automated tests** covering meaningful backend logic and API behaviour (not only “smoke” checks)

### Frontend engineering

- **React** UI for submit and browse/list flows
- **Form validation** aligned with API expectations
- **UX states**: loading, success, and error handling surfaced to the user
- Execution that is **clean and maintainable**, without an over-engineered UI stack

### Delivery quality

- Repository **reads like a production-minded submission**: structure, naming, and README quality support onboarding and review
- Scope stays **focused**; no fake complexity or unnecessary large refactors for show

---

## Non-goals

| Non-goal | Rationale |
|----------|-----------|
| **Authentication / authorisation** | Out of scope; keeps focus on API design, validation, and data flow |
| **Full production deployment** | Local or developer-run environments are sufficient; no requirement for a full AWS rollout in scope |
| **Heavy UI framework or design system** | Avoid over-engineered frontend architecture; polish through clarity and states, not framework sprawl |
| **Microservices** | Single deployable backend is appropriate; no split into unnecessary services |
| **Artificial complexity** | No large, unrelated code changes or buzzword architecture solely to impress |

---

## Scope summary

- **In scope:** CRUD-shaped customer flows (create, get by id, paginated list), relational persistence, modular FastAPI + SQLAlchemy, React operator UI with validation and states, tests, strong README.
- **Explicitly out of scope:** Auth, full cloud deployment, microservices, and UI framework excess.

---

## Document control

| Field | Value |
|-------|--------|
| Document | MRD — Customer Information API |
| Purpose | Product framing and acceptance bar for the build / technical assessment |
