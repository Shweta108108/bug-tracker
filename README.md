# IssueHub

A lightweight bug tracker: create projects, file issues, comment on them, and
track status, with role-based permissions (member vs. maintainer). Backend is
Python/FastAPI + PostgreSQL, frontend is a React (Vite) single-page app.

## Tech choices & trade-offs

| Choice | Why |
|---|---|
| **FastAPI** over Flask/Django | Native Pydantic validation, async-ready, and OpenAPI docs for free — matched the spec's "FastAPI preferred". |
| **SQLAlchemy 2.x + Alembic** | Explicit schema control via hand-written migrations (see below) rather than framework-managed migrations. |
| **Vite + React SPA**, not Next.js | The API is already a separate REST/JSON backend; SSR/file-routing would add complexity with no real benefit here. Trade-off: no SSR, so first paint waits on JS — fine for an internal tool. |
| **JWT Bearer token in `localStorage`**, not an httpOnly cookie | Simpler CORS (no credentialed requests), no CSRF concerns. Trade-off: more exposed to XSS than an httpOnly cookie if the app ever renders unsanitized user HTML (it doesn't — React escapes by default). |
| **`bcrypt` (pinned to `4.0.1`) for password hashing** | Spec suggested bcrypt/argon2; bcrypt has simpler cross-platform installs. Newer `bcrypt` (4.1+) breaks `passlib`'s internal self-test, so the version is pinned deliberately — see `CLAUDE.md`. |
| **PostgreSQL installed locally**, not Docker Compose | Simpler for this environment; trade-off is setup isn't fully one-command reproducible — see Setup below. |
| **Tailwind CSS v4** | Fast to build a clean, responsive UI without a component library; v4 uses the `@tailwindcss/vite` plugin (no `tailwind.config.js`/PostCSS setup — that changed from v3). |
| **No axios / react-query / UI kit** | Hand-written `fetch` wrapper and a small custom `ToastProvider` instead. Kept dependencies minimal for a project this size — see "What I'd do with more time" for where a real app would want these. |
| **Text columns + `CHECK` constraints** for `status`/`priority`/`role`, not native Postgres enums | Simpler to extend later (`ALTER TYPE ... ADD VALUE` has transactional restrictions that Alembic autogenerate handles poorly). |
| **`ILIKE` + `pg_trgm` GIN index** for title search, not full-text (`tsvector`) | Simple substring search is what the spec asks for ("text search in title"); full-text search would be over-engineering here. |

## Architecture

**Backend** (`backend/app/`) is layered to keep authorization logic from being
duplicated per route:

- `routers/` — thin HTTP adapters: parse the request, call a service, shape the response. No business logic.
- `services/` — business logic and permission decisions (e.g. `issue_service.update_issue` decides what a reporter vs. a maintainer may change).
- `dao/` — SQLAlchemy query building (e.g. `issue_dao` builds the combined filter/search/sort/pagination query in one place).
- `core/` — cross-cutting concerns: JWT + password hashing (`security.py`), the `get_current_user` dependency (`deps.py`), and structured error handling (`exceptions.py`).
- `services/authz.py` is the single source of truth for "is this user a member of this project" and "is this user a maintainer" — both project-scoped and issue-scoped routes call the same helper rather than re-implementing the check.

**Frontend** (`frontend/src/`) mirrors this separation:

- `api/` — one `client.ts` fetch wrapper handles the auth header and structured-error parsing for every request; resource-specific files (`auth.ts`, `projects.ts`, `issues.ts`, `comments.ts`) are thin typed wrappers around it.
- `auth/AuthContext.tsx` — the only place session state lives; rehydrates via `GET /api/me` on load so a page refresh doesn't lose the session.
- `components/` — grouped by domain (`issues/`, `projects/`, `comments/`) plus a small `ui/` primitive kit (`Button`, `Input`, `Select`, `Modal`, `ToastProvider`).
- Filter/search/sort/pagination state for issue lists lives in the URL (`useSearchParams`), so it's bookmarkable and survives a refresh.
- Maintainer-only UI (status/assignee controls, member management) is gated off the caller's `role`, returned alongside project data — not a separate permissions call.

See `CLAUDE.md` for more implementation-level detail (exact module responsibilities, schema notes, testing infrastructure).

## Setup

### Prerequisites

- Python 3.12+
- Node.js 20+
- PostgreSQL running locally (this project assumes a local install, not Docker — see trade-offs above)

### Backend

```bash
cd backend
python -m venv .venv
.venv/Scripts/activate        # Windows; use `source .venv/bin/activate` on macOS/Linux
pip install -r requirements.txt
cp .env.example .env          # then fill in real values (DB credentials, JWT secret)
```

Create the databases (adjust user/host as needed for your local Postgres):

```bash
createdb issuehub
createdb issuehub_test
```

Apply migrations, then run the API:

```bash
alembic upgrade head
uvicorn app.main:app --reload --port 8000
```

Health check: `GET http://localhost:8000/health` → `{"status": "ok"}`

Environment variables (`backend/.env`, see `.env.example`): `DATABASE_URL`,
`TEST_DATABASE_URL`, `JWT_SECRET_KEY`, `JWT_ALGORITHM`, `JWT_EXPIRE_MINUTES`,
`CORS_ALLOWED_ORIGINS`, `ENV`.

### Seed data (optional)

Populates 2 demo projects, 4 users, ~16 issues with varied status/priority/
assignee, and a few comments. Safe to re-run — skips if already seeded.

```bash
python -m app.scripts.seed
```

Demo accounts (all use password `password123`):

| Email | Role |
|---|---|
| alice@example.com | Maintainer of both "Website Revamp" (WEB) and "Mobile App" (MOB) |
| bob@example.com | Member of WEB |
| carol@example.com | Member of WEB, maintainer of MOB |
| dave@example.com | Member of MOB |

### Frontend

```bash
cd frontend
npm install
cp .env.example .env           # then fill in real values (VITE_API_BASE_URL)
npm run dev
```

Runs at `http://localhost:5173` by default.

## Running tests

Backend tests run against a real `issuehub_test` Postgres database (not
SQLite/mocks), so create it first (see Setup above) — the test suite applies
migrations to it automatically on each run.

```bash
cd backend
pytest                                    # run all tests
pytest tests/test_auth.py -v              # run one file
pytest tests/test_auth.py::test_login_success_returns_usable_token  # run a single test
```

46 backend tests cover auth, project/membership permission boundaries, the
full issue reporter-vs-maintainer permission matrix, filter/search/sort/
pagination correctness, and comment access scoping.

The frontend has no automated test suite (see Known limitations); it was
verified manually via a Playwright-driven headless-browser flow covering the
full multi-role journey — signup, project creation, member invite, issue
creation/filter/search/sort, maintainer status/assignee changes, and comments
from both a maintainer and a regular member — checking for console errors
and failed network requests at each step.

## Deviations from the example API contract

- **`GET /api/projects/{id}`** and **`GET /api/projects/{id}/members`** added — not in the original contract, but needed by the frontend to show the caller's role in a project and to populate assignee/member-management UI.
- **Structured error codes are specific**, not just the generic `NOT_FOUND`/`CONFLICT`: adding a member with an unregistered email returns `USER_NOT_FOUND` (404), adding an existing member returns `ALREADY_MEMBER` (409), assigning an issue to a non-member returns `ASSIGNEE_NOT_MEMBER` (400).
- **Invite-by-email requires an existing account** — returns `USER_NOT_FOUND` rather than creating a pending invite.
- **Pagination added** to `GET /api/projects/{id}/issues` (`page`/`page_size` query params, response wrapped as `{items, total, page, page_size}`) — the example contract didn't show these params, but the frontend spec explicitly requires pagination.
- **`DELETE /api/issues/{id}` is maintainer-only.** The spec doesn't say whether reporters can delete their own issues; maintainer-only was chosen to avoid accidental data loss.
- **Priority sort uses an explicit severity ranking** (`critical > high > medium > low`), not alphabetical string order.
- **Title search is `ILIKE`-based** (substring, case-insensitive), accelerated by a `pg_trgm` GIN index — not full-text (`tsvector`) search.

## Known limitations

- No pending-invite flow — adding a member requires them to already have an account.
- No refresh tokens; the JWT access token has a fixed expiry and there's no server-side logout/invalidation (logout is a client-side token discard).
- Frontend has no automated test suite (backend does — 46 tests); frontend correctness was verified manually (see "Running tests" above), not via CI-runnable checks.
- Toasts cap at 3 visible at once; several rapid actions in a row can still visually overlap page controls briefly before auto-dismissing (4s).
- No CI pipeline configured — tests and linting are run locally.

## What I'd do with more time

- Add a frontend test suite (Vitest + React Testing Library for components, Playwright for E2E) and wire up CI to run both backend and frontend tests on push.
- Pending-invite flow: let a maintainer invite an email that doesn't have an account yet, auto-attaching them to the project on signup.
- Refresh tokens + server-side session invalidation, so logout actually revokes access instead of waiting out the token expiry.
- Swap the hand-rolled `fetch` wrapper + local component state for `react-query`/SWR once the app has more than a couple of data-dependent pages, to get caching and request de-duplication for free.
- Full-text search (`tsvector`) across title *and* description if search needs to scale beyond simple substring matching.
- A GitHub Actions workflow: spin up Postgres as a service container, run backend tests + frontend build/lint on every push.
