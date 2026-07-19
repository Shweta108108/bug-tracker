# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project

IssueHub — a lightweight bug tracker (projects, issues, comments, roles).
Full requirements are in `assignment.txt`. Monorepo: `backend/` (FastAPI +
PostgreSQL + Alembic) and `frontend/` (Vite + React + TypeScript + Tailwind
v4). Implementation plan and milestone order originally tracked at
`C:\Users\User\.claude\plans\read-the-assignment-in-valiant-toucan.md`.

## Commands

### Backend (run from `backend/`)

```bash
python -m venv .venv && .venv/Scripts/activate   # Windows
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000        # run dev server
pytest                                            # run all tests
pytest tests/test_issues.py::test_name -v         # run a single test
alembic upgrade head                              # apply migrations
alembic downgrade base                            # roll back all migrations
alembic revision --autogenerate -m "message"       # new migration (review output — see Schema notes below)
```

PostgreSQL is a local install (Postgres 17, service `postgresql-x64-17`), not
Docker. `psql` isn't on PATH by default — use
`"/c/Program Files/PostgreSQL/17/bin/psql.exe"` or add it to PATH.
Databases `issuehub` and `issuehub_test` must be created manually
(`createdb issuehub`, `createdb issuehub_test`) before running migrations/tests.

### Frontend (run from `frontend/`)

```bash
npm install
npm run dev        # dev server, http://localhost:5173
npm run build       # tsc -b && vite build
npm run lint         # eslint
```

## Architecture

### Backend module boundaries (`backend/app/`)

Strict layering to keep permission logic from being duplicated per route:

- `routers/` — thin HTTP adapters only (parse request, call a service, return response). No business logic or DB queries here.
- `services/` — business logic and authorization decisions live here (e.g. `issue_service.update_issue` decides field-level permission based on reporter vs maintainer).
- `dao/` — SQLAlchemy query builders (e.g. `issue_dao` builds the combined filter/search/sort/pagination query for issue listing).
- `core/deps.py` — shared FastAPI dependencies: `get_current_user` (JWT decode), `get_current_project_membership` and `get_issue_membership` (both call the same `services/authz.get_membership_or_403` helper — one place that enforces "is this user a member of this project").
- `core/security.py` — password hashing (passlib/bcrypt) and JWT create/decode (python-jose, HS256).
- `core/exceptions.py` — `AppError` + subclasses, mapped to the structured `{"error": {"code", "message", "details"}}` response shape via exception handlers registered in `main.py`.

Role/ownership rule of thumb: maintainers can act on any issue/membership in
their project; regular members can only edit `title`/`description` on issues
they reported, and cannot change `status`/`assignee_id` or delete issues.

### Database schema

Single Alembic migration `0001_initial_schema` defines all 5 tables. Notable
choices (see README's deviations list for the "why"):

- `status`/`priority`/`role` are text columns + `CHECK` constraints, not native Postgres enums.
- `project_members` has **no surrogate id** — composite primary key `(project_id, user_id)` is what enforces one-role-per-user-per-project.
- `users.email` has a functional unique index on `lower(email)` for case-insensitive lookup.
- `issues.title` has a `pg_trgm` GIN index to accelerate `ILIKE` search (requires `CREATE EXTENSION pg_trgm`, done in the migration).

### Frontend structure (`frontend/src/`)

- `api/client.ts` — the only place that attaches the `Authorization: Bearer <token>` header and parses the backend's structured error envelope; other `api/*.ts` files call it.
- `api/authToken.ts` — plain (non-React) localStorage wrapper, so `client.ts` can read the token outside the React tree.
- `auth/AuthContext.tsx` — mirrors token state into React, rehydrates via `GET /api/me` on load, listens for a custom `"issuehub:unauthorized"` event (dispatched by `client.ts` on a 401) to redirect to `/login`.
- Filter/search/sort/pagination state for issue lists is kept in the URL (`useSearchParams`), not component state, so it's bookmarkable and survives refresh.
- No axios, no react-query/SWR, no UI kit — hand-written fetch wrapper and a small custom `ToastProvider`. This is intentional (documented in README as a "would add with more time" trade-off), not an oversight.

## Key decisions (won't need re-litigating)

1. Monorepo, not two repos.
2. Vite React SPA, not Next.js.
3. JWT Bearer token stored client-side, not httpOnly cookie.
4. Invite-by-email requires an existing account (404 otherwise) — no pending-invite schema.
5. Local PostgreSQL install, not Docker Compose.
6. Tailwind CSS v4 (via `@tailwindcss/vite` plugin, not the PostCSS/config-file setup — v4 changed this).
7. `DELETE /api/issues/{id}` is maintainer-only (spec doesn't specify; chosen to avoid accidental data loss).
8. Two endpoints added beyond the example API contract: `GET /api/projects/{id}` and `GET /api/projects/{id}/members` (needed by the frontend for role display and assignee/member UI).

## Workflow conventions for this repo

- Commit and push after each meaningful milestone (a working feature/endpoint/component), not every small edit — this project pushes progress continuously to `git@github.com:Shweta108108/bug-tracker.git`.
- Update this file and `README.md` incrementally as milestones land (e.g. add env vars when they're introduced, update the progress checklist), not only in one final pass.
- Git identity for this repo is configured globally as `Shwet108108 <shwetaspatil1777@gmail.com>`.
