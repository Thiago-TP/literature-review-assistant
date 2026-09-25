# Contributing

Thanks for looking at this. 
It's a small, local-first tool that uses a FastAPI backend over SQLite and a React frontend. 
Contributing is mostly a matter of getting both halves running and keeping the checks green.

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
python main.py     # or uv run main.py or ./run.sh on macOS/Linux, run.cmd on Windows
```

That starts the API on `http://localhost:8000` and
the app on `http://localhost:5173`, and opens a browser window. Closing that
window stops both servers; `--no-browser` skips opening one and leaves them
running until Ctrl+C. Vite proxies `/api` through to the backend, so the
frontend talks to a same-origin URL and there is no CORS setup to think about
in development.

Either default port being busy is fine, the launcher falls forward to the next free one and prints what it used.

To work on one half at a time, run them separately:

```bash
cd backend && uv run uvicorn app.main:app --reload --port 8000
cd frontend && npm run dev
```

> [!TIP]
> `examples/` has two sample `.xlsx` files if you need papers to work with.

## Before you open a pull request

```bash
cd backend
uv run ruff check .
uv run ruff format .
uv run ruff check --config ruff.toml ../scripts    # the utility scripts, same rules
uv run ruff format --config ruff.toml ../scripts
uv run pytest

cd ../frontend
npm run lint     # oxlint
npm run build    # tsc --build, then the production bundle
```

All the backend commands run in CI on every push and pull request; see [`.github/workflows/`](.github/workflows/). 
Formatting is not a matter of taste here, run `ruff format` and commit what it produces. 
Its settings live in [`backend/ruff.toml`](backend/ruff.toml).

## Where things live

```
backend/app/
  routers/    one module per resource; all routes are under /api
  services/   logic with no FastAPI in it (dedup, CrossRef, xlsx, scoring)
  models.py   SQLModel tables, the source of truth for the schema
  schemas.py  request/response shapes
frontend/src/
  pages/      one component per route
  components/ presentational pieces
  hooks/      React Query wrappers around the API
  api/        typed fetch client
```

The split that matters on the backend is **routers vs services**: anything that
can be decided from plain data (duplicate checking, paper score, spreadsheet row meaning) 
belongs in `services/` and gets a unit test, so it can be exercised without spinning up the app. 
The bulk import and the single-paper add deliberately share `services/dedup.py` 
rather than each implementing their own check.

## Changing the database schema

Edit `backend/app/models.py`, then generate and apply a migration:

```bash
cd backend
uv run alembic revision --autogenerate -m "short description"
uv run alembic upgrade head
```

Read the generated file before committing it. 
Autogenerate is good at columns and tables, but unreliable about renames, constraints and data migrations. 
The database is a file people keep their real work in, so a migration that drops and recreates a table instead of altering it is a data-loss bug.

Every project is created with two protected tag fields (`Adherence`, `Contribution Type`, in `backend/app/constants.py`). 
They can't be renamed or deleted through the API; tests in `tests/test_fields_api.py` hold that line.

## Adding to the frontend

Server state goes through React Query, so add a hook in `hooks/` wrapping a
function in `api/`, rather than calling `fetch` from a component. 
Mutations invalidate the keys they affect.

Two things to watch:

- **Invalidate precisely.** Query keys are nested (`['projects', id, 'papers',
  paperId]`), so invalidating `['projects', id]` without `exact: true` throws
  away every paper and dashboard entry for that project as well.
- **Colour comes from tokens.** The palette, including the progress ramp, is
  defined as CSS custom properties in `src/index.css` and redeclared for dark mode. 
  Reading the theme from JavaScript leaves components stale after a toggle.

UI strings are English.

## Commits and pull requests

Commit subjects follow [Conventional Commits](https://www.conventionalcommits.org/):
`feat:`, `fix:`, `docs:`, `style:`, `refactor:`, `test:`, `ci:`, `chore:`, with
an optional scope (`fix(frontend): ...`). 
Keep the subject in the imperative and under ~72 characters.

Prefer one self-contained change per commit, and use the body to say *why*:
what was wrong, what you considered, what you deliberately left out. 
Reviewers can read the diff, not the reasoning.

For anything that changes what the app looks like, a before/after screenshot in the pull request saves a round trip. 
If a change touches behaviour, say how you verified it.

## Updating the documentation screenshots

The images in the root README (`docs/screenshots/`) and on the help page
(`frontend/public/help/`) are generated, not taken by hand. After a visible
change, retake them from the repository root:

```bash
uv run scripts/take_screenshots.py                    # all of them, both themes, in place
uv run scripts/take_screenshots.py --only plan        # just some: readme, workspace, overview, fields, dashboard, plan
uv run scripts/take_screenshots.py --out /tmp/shots   # write elsewhere, to compare before overwriting
```

It runs both servers against a throwaway database filled with the example
review in [`scripts/screenshot_data.py`](scripts/screenshot_data.py), then
photographs the app in a headless browser, so nothing opens on screen and your
own `app.db` is never touched. The README's picture, `workspace.png`, is the
light and dark shots joined along a slanted cut (`SLICE_TOP`/`SLICE_BOTTOM` in
the script move it). It needs the backend and frontend set up as
above, plus Google Chrome or Edge (or Playwright's Chromium:
`uv run --with playwright playwright install chromium`). To change what the
pictures show, edit the example data, not the script.

## Reporting a bug

Please include what you did, what happened, what you expected, and whether it was the backend or the frontend 
(the browser console and the uvicorn log usually make that obvious). 
If it involves an import, the shape of the spreadsheet (which columns it had) is usually the key detail.
