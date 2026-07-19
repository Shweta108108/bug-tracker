# IssueHub

A lightweight bug tracker: create projects, file issues, comment on them, and
track status. Backend is Python/FastAPI, database is PostgreSQL, frontend is
a React (Vite) single-page app.

**Status: work in progress.** This README is updated as features land; see
the checklist below for what's done.

## Tech stack & key decisions

- **Backend**: FastAPI, SQLAlchemy 2.x, Alembic migrations, PostgreSQL.
- **Auth**: JWT (HS256) sent as a `Bearer` token in the `Authorization`
  header, stored client-side (not an httpOnly cookie).
- **Frontend**: React + TypeScript via Vite (SPA, not Next.js), Tailwind CSS
  v4, `react-router-dom`.
- **Membership invites**: adding a project member by email requires that
  email to already have an account (no pending-invite state — returns a 404
  if the email isn't registered).

## Repo layout

```
backend/   FastAPI app, Alembic migrations, pytest tests
frontend/  Vite + React + TypeScript SPA
```

## Setup

### Prerequisites

- Python 3.12+
- Node.js 20+
- PostgreSQL running locally (this project assumes a local install, not Docker)

### Backend

```bash
cd backend
python -m venv .venv
.venv/Scripts/activate        # Windows; use `source .venv/bin/activate` on macOS/Linux
pip install -r requirements.txt
cp .env.example .env          # then fill in real values
```

Create the databases (adjust user/host as needed for your local Postgres):

```bash
createdb issuehub
createdb issuehub_test
```

Apply migrations:

```bash
alembic upgrade head
```

Run the API:

```bash
uvicorn app.main:app --reload --port 8000
```

Health check: `GET http://localhost:8000/health` → `{"status": "ok"}`

### Frontend

```bash
cd frontend
npm install
cp .env.example .env           # then fill in real values
npm run dev
```

Runs at `http://localhost:5173` by default.

## Running tests

Backend tests run against the real `issuehub_test` Postgres database (not
SQLite), so create it first (see Setup above) — the test suite applies
migrations to it automatically on each run.

```bash
cd backend
pytest                                    # run all tests
pytest tests/test_auth.py -v              # run one file
pytest tests/test_auth.py::test_login_success_returns_usable_token  # run a single test
```

## Progress checklist

- [x] Repo scaffold: backend `/health` endpoint, frontend Tailwind-styled placeholder page
- [x] Database schema + migrations
- [x] Auth endpoints (signup/login/me)
- [ ] Projects + membership endpoints
- [ ] Issue CRUD + filter/search/sort
- [ ] Comments
- [ ] Frontend auth pages
- [ ] Frontend projects/issues/issue-detail pages
- [ ] Seed script + demo credentials
- [ ] Final docs polish (architecture notes, trade-offs, known limitations)

## Deviations from the example API contract

Documented here as they're introduced; see `CLAUDE.md` for the full running list.
