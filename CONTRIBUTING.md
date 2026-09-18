# Contributing

Thanks for looking at this. It's a small, local-first tool — a FastAPI backend
over SQLite and a React frontend — so contributing is mostly a matter of getting
both halves running and keeping the checks green.

## Getting set up

You need **Python 3.13+**, **[uv](https://docs.astral.sh/uv/getting-started/installation/)**
and **Node.js 20+**.

```bash
# Backend
cd backend
uv sync                        # creates backend/.venv from uv.lock
uv run alembic upgrade head    # creates backend/data/app.db

# Frontend
cd ../frontend
npm install
```

Then, from the repository root:

```bash
python run.py     # or ./run.sh on macOS/Linux, run.cmd on Windows
```

That starts the API on `http://localhost:8000` (interactive docs at `/docs`) and
the app on `http://localhost:5173`. Vite proxies `/api` through to the backend,
so the frontend talks to a same-origin URL and there is no CORS setup to think
about in development.

To work on one half at a time, run them separately:

```bash
cd backend && uv run uvicorn app.main:app --reload --port 8000
cd frontend && npm run dev
```

`examples/` has two sample `.xlsx` files if you need papers to work with.

## Before you open a pull request

```bash
cd backend
uv run ruff check .
uv run pytest

cd ../frontend
npm run lint     # oxlint
npm run build    # tsc --build, then the production bundle
```

`ruff check` and `pytest` also run in CI on every push and pull request; see
[`.github/workflows/`](.github/workflows/). `ruff format` is configured in
[`backend/ruff.toml`](backend/ruff.toml) but is deliberately **not** a gate,
because running it today would rewrite most of the tree — please don't reformat
files you aren't otherwise changing.

## Where things live

```
backend/app/
  routers/    one module per resource; all routes are under /api
  services/   logic with no FastAPI in it (dedup, CrossRef, xlsx, scoring)
  models.py   SQLModel tables — the source of truth for the schema
  schemas.py  request/response shapes
frontend/src/
  pages/      one component per route
  components/ presentational pieces
  hooks/      React Query wrappers around the API
  api/        typed fetch client
```

The split that matters on the backend is **routers vs services**: anything that
can be decided from plain data — is this a duplicate, what does this paper
score, what does this spreadsheet row mean — belongs in `services/` and gets a
unit test, so it can be exercised without spinning up the app. The bulk import
and the single-paper add deliberately share `services/dedup.py` rather than
each implementing their own check.

## Changing the database schema

Edit `backend/app/models.py`, then generate and apply a migration:

```bash
cd backend
uv run alembic revision --autogenerate -m "short description"
uv run alembic upgrade head
```

Read the generated file before committing it — autogenerate is good at columns
and tables, and unreliable about renames, constraints and data migrations. The
database is a file people keep their real work in, so a migration that drops and
recreates a table instead of altering it is a data-loss bug.

Every project is created with two protected tag fields (`Adherence`,
`Contribution Type`, in `backend/app/constants.py`). They can't be renamed or
deleted through the API; tests in `tests/test_fields_api.py` hold that line.

## Adding to the frontend

Server state goes through React Query — add a hook in `hooks/` wrapping a
function in `api/`, rather than calling `fetch` from a component. Mutations
invalidate the keys they affect.

Two things to watch:

- **Invalidate precisely.** Query keys are nested (`['projects', id, 'papers',
  paperId]`), so invalidating `['projects', id]` without `exact: true` throws
  away every paper and dashboard entry for that project as well.
- **Colour comes from tokens.** The palette, including the progress ramp, is
  defined as CSS custom properties in `src/index.css` and redeclared for dark
  mode. Reading the theme from JavaScript leaves components stale after a
  toggle.

UI strings are English.

## Commits and pull requests

Commit subjects follow [Conventional Commits](https://www.conventionalcommits.org/):
`feat:`, `fix:`, `docs:`, `style:`, `refactor:`, `test:`, `ci:`, `chore:`, with
an optional scope (`fix(frontend): ...`). Keep the subject in the imperative and
under ~72 characters.

Prefer one self-contained change per commit, and use the body to say *why* —
what was wrong, what you considered, what you deliberately left out. Reviewers
can read the diff; they can't read the reasoning.

For anything that changes what the app looks like, a before/after screenshot in
the pull request saves a round trip. If a change touches behaviour, say how you
verified it.

## Reporting a bug

Please include what you did, what happened, what you expected, and whether it
was the backend or the frontend (the browser console and the uvicorn log usually
make that obvious). If it involves an import, the shape of the spreadsheet —
which columns it had — is usually the key detail.
