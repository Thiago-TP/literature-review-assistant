# Backend

FastAPI + SQLModel over a local SQLite file. It owns everything the app
persists: projects, papers, tag fields and their nested options, ratings, notes,
and the derived numbers the dashboard shows.

It is a plain HTTP API with no authentication — it is meant to be reached from
`localhost` by the one person using the app, and CORS is limited to the Vite dev
server by default.

## Running it

```bash
uv sync                        # creates .venv from uv.lock
uv run alembic upgrade head    # creates data/app.db
uv run uvicorn app.main:app --reload --port 8000
```

Interactive docs are at `http://localhost:8000/docs`, generated from the route
signatures, and are the most reliable reference for request and response shapes.

To start the backend together with the frontend, use `python run.py` from the
repository root instead.

## Layout

```
app/
  main.py          app construction, CORS, router registration
  config.py        settings, all overridable by environment variable
  db.py            engine, session dependency, foreign-key pragma
  deps.py          shared FastAPI dependencies (session, 404 helpers)
  models.py        SQLModel tables — the source of truth for the schema
  schemas.py       request/response models
  constants.py     the tag fields every new project starts with
  routers/         one module per resource, all mounted under /api
  services/        logic with no FastAPI in it
alembic/           migrations
scripts/           one-off tools (legacy Streamlit import)
tests/             pytest suite
data/app.db        your database (gitignored)
```

The line that matters is **routers vs services**. Anything decidable from plain
data lives in `services/` and is unit-tested directly:

| Module | Responsibility |
| --- | --- |
| `services/dedup.py` | DOI/title normalisation and duplicate classification |
| `services/xlsx_import.py` | Parsing an uploaded `.xlsx` into plain rows |
| `services/crossref.py` | CrossRef lookups by DOI and by title |
| `services/paper_repo.py` | Building papers, scoring, ORM → response shapes |
| `services/dashboard.py` | Aggregate statistics for one project |

Bulk import and single-paper add both go through `services/dedup.py`, so a paper
cannot be added twice regardless of which path it came in through.

## Configuration

Every setting is an environment variable with a local-first default
(`app/config.py`):

| Variable | Default | Purpose |
| --- | --- | --- |
| `LRA_DB_PATH` | `data/app.db` | SQLite file location |
| `LRA_CORS_ORIGINS` | the Vite dev server origins | Comma-separated allowed origins |
| `CROSSREF_BASE_URL` | `https://api.crossref.org` | Override to point at a mock |
| `CROSSREF_MAILTO` | maintainer address | Sent to CrossRef for polite-pool access |
| `CROSSREF_TIMEOUT_SECONDS` | `10` | Lookup timeout |
| `LRA_SESSION_WATCH` | unset | `1` makes the server stop when the app's browser window closes |
| `LRA_SESSION_GRACE` | `90` | Seconds without a heartbeat before stopping |
| `LRA_SESSION_CLOSE_GRACE` | `5` | Seconds after an unload beacon before stopping |

Pointing `LRA_DB_PATH` at a scratch file is the easy way to demo or experiment
without touching your real review data.

## Data model

```
Project ──< Paper ──< TagAssignment >── TagOption
   └─────< TagField ──< TagOption (self-referential: parent_id)
```

Assignments reference tag options **by id**, so renaming a field or a tag never
orphans existing work — the flaw in the old Streamlit version, which keyed
progress by field name.

A few properties worth knowing before changing things:

- `TagOption.parent_id` nests tags to arbitrary depth, but `field_id` is set on
  every node regardless of depth, so "which fields does this paper have tags in"
  is one query rather than a tree walk.
- `doi_normalized` and `title_normalized` are stored alongside the originals and
  indexed; a partial unique index makes a duplicate DOI within a project
  impossible at the database level, not just in application code.
- Deletes cascade (project → papers → assignments; field → options →
  assignments), and `Project.last_viewed_paper_id` is `SET NULL` so deleting the
  paper you were last on doesn't wedge the project.
- A paper's **score** is the sum of the weights of its assigned tags plus its
  star rating, computed on read rather than stored, so changing a tag's weight
  reprices every paper immediately.

## API

Everything is under `/api`, and everything except `/api/health` is scoped to a
project.

| | |
| --- | --- |
| Projects | `GET|POST /projects`, `GET|PATCH|DELETE /projects/{id}`, `PATCH /projects/{id}/last-viewed` |
| Papers | `GET|POST /projects/{id}/papers`, `GET|PATCH|DELETE /projects/{id}/papers/{paper_id}` |
| Rating | `PUT|DELETE /projects/{id}/papers/{paper_id}/rating` |
| Tagging | `POST|DELETE /projects/{id}/papers/{paper_id}/tags/{option_id}` |
| Fields | `GET|POST /projects/{id}/fields`, `PATCH|DELETE /projects/{id}/fields/{field_id}` |
| Tags | `POST /projects/{id}/fields/{field_id}/options`, `PATCH|DELETE .../options/{option_id}` |
| Lookup | `POST /projects/{id}/papers/lookup/doi`, `.../lookup/title` |
| Import | `POST /projects/{id}/import/xlsx/preview`, `.../commit` |
| Export | `GET /projects/{id}/export.json`, `.../export.xlsx` |
| Dashboard | `GET /projects/{id}/dashboard` |
| Session | `GET /session/status`, `POST /session/heartbeat`, `POST /session/closed` |

Two shapes are worth calling out:

**Tagging is per-option, not per-list.** Assigning is `POST .../tags/{option_id}`
and unassigning is `DELETE`, rather than sending the full set of tags. Each
request only asserts one option's state, so clicking a topic and a subtopic in
quick succession cannot have one request clobber the other's result.

**The session endpoints only matter under the launcher.** `run.py` sets
`LRA_SESSION_WATCH=1` so that closing the app's window stops the servers; the
page heartbeats while it is open and beacons `/session/closed` as it unloads.
`app/session_watch.py` has the reasoning for the two signals. Without that
variable — a hand-started uvicorn, or anything else pointed at the API —
`/session/status` reports `watching: false`, the client stays quiet, and
nothing ever shuts itself down.

**Import is preview-then-commit.** `preview` parses the upload and classifies
every row against what the project already holds, writing nothing. The client
sends the rows back to `commit` with a per-row add/skip decision. Duplicates are
flagged and defaulted to skip, never dropped silently, and the reviewer can
override any of them.

## Migrations

```bash
uv run alembic revision --autogenerate -m "short description"
uv run alembic upgrade head
```

Read the generated file before committing it. Autogenerate handles added columns
and tables well and is unreliable about renames, constraints and data
migrations — and this database holds work people cannot regenerate.

## Tests

```bash
uv run pytest
uv run ruff check .
uv run ruff format --check .
```

Each test builds its own in-memory SQLite database and overrides the session
dependency, so the suite never touches `data/app.db` and needs no migration step
or fixture database. Coverage spans the pure services (dedup, xlsx parsing,
CrossRef against mocked HTTP) and the full API surface, including the
protected-field rules and cascade deletes.

## Migrating from the old Streamlit app

`scripts/migrate_legacy.py` imports an `.xlsx` + session-JSON pair from the
previous version. The old format paired the two positionally, so the script
refuses to run unless they have matching lengths rather than risk attaching
tags to the wrong papers. See the root README for the invocation.
