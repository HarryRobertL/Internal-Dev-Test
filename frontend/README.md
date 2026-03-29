# Frontend (React + Vite)

Single-page internal dashboard for creating and listing customer requests.

## Tech

- React + TypeScript + Vite
- Tailwind CSS
- Vitest + React Testing Library

## Setup

From this directory (`frontend/`):

```bash
npm install
cp .env.example .env   # optional
npm run dev
```

Default app URL: [http://localhost:5173](http://localhost:5173)

## Environment

- `VITE_API_URL` (default: `http://localhost:8000`)

## Scripts

```bash
npm run dev
npm run test
npm run build
npm run lint
```

## API contract used by frontend

- `POST /api/customers`
- `GET /api/customers/{id}`
- `GET /api/customers?page=1&limit=10`

Expected response envelopes:

- all responses use: `{ "data": ..., "error": ..., "meta": ... }`
- success example: `{ "data": {...}, "error": null, "meta": null }`
- list success example: `{ "data": [...], "error": null, "meta": { "pagination": {...} } }`
- error example: `{ "data": null, "error": { "code", "message", "details" }, "meta": null }`
