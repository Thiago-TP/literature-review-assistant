# Literature Review Assistant

A local-first tool for systematic literature reviews: import papers, tag and take notes on them one at a time, and track progress — all saved automatically to a local database, with a FastAPI backend and a React frontend.

## Overview

This app helps you evaluate and categorize academic papers without juggling spreadsheets and JSON exports by hand. It supports:

- **Multiple review projects** — keep several literature reviews going at once, each with its own papers, tags, and progress.
- **Bulk import** from an Excel export (Scopus, Web of Science, or any sheet with `Title`/`Abstract`/`DOI` columns), with automatic duplicate detection when combining more than one source.
- **Add a single paper by DOI or title** — metadata (title, abstract, authors, year) is fetched automatically from [CrossRef](https://www.crossref.org/), no manual typing required.
- **Real persistence** — everything is saved to a local SQLite database as you work. Close the app, come back later, and you're exactly where you left off. No re-uploading files, no manual export/import to avoid losing progress.
- **Customizable tagging** — two built-in fields (`Adherence`, `Contribution Type`) plus any custom fields/tags you define.
- **Progress overview** — an at-a-glance grid of every paper's review status, click to jump to any paper.

## Architecture

```
literature_review_assistant/
├── backend/            # FastAPI + SQLModel + SQLite
│   ├── app/
│   │   ├── main.py         # FastAPI app entrypoint
│   │   ├── models.py       # DB schema
│   │   ├── routers/        # API endpoints (projects, papers, fields, import, export)
│   │   └── services/       # dedup logic, CrossRef client, xlsx parsing
│   ├── alembic/             # DB migrations
│   ├── scripts/migrate_legacy.py  # one-off importer for the old Streamlit app's exports
│   ├── tests/               # pytest suite
│   └── data/app.db          # local SQLite database (gitignored)
├── frontend/           # React + TypeScript + Vite + Tailwind CSS
│   └── src/
│       ├── pages/           # ProjectListPage, ReviewWorkspacePage
│       ├── components/      # Progress overview, tag panel, import/add-paper modals, etc.
│       ├── hooks/           # React Query hooks wrapping the API
│       └── api/             # Typed API client
├── examples/           # Example .xlsx imports + a description of the format
├── run.py              # Cross-platform launcher (backend + frontend together)
└── run.sh, run.cmd     # Thin wrappers around run.py
```

## Requirements

- Python 3.13+
- [uv](https://docs.astral.sh/uv/getting-started/installation/) (manages the backend's Python environment and dependencies)
- Node.js 20+

## Setup (first time)

```bash
# Backend
cd backend
uv sync                        # creates backend/.venv from uv.lock
uv run alembic upgrade head    # creates backend/data/app.db

# Frontend
cd ../frontend
npm install
```

## Running

```bash
python run.py
```

Or use the wrapper for your platform: `./run.sh` on macOS/Linux, `run.cmd` on Windows.

This starts the backend at `http://localhost:8000` (API docs at `/docs`) and the frontend at `http://localhost:5173`. Open the frontend URL in your browser. Press Ctrl+C to stop both.

Or run them separately in two terminals:

```bash
cd backend && uv run uvicorn app.main:app --reload --port 8000
cd frontend && npm run dev
```

## Workflow

1. Create a review project (or open an existing one — they're listed on the home page and persist across restarts).
2. Add papers:
   - **Import a spreadsheet**: click "Import spreadsheet", choose an `.xlsx` file with `Title`/`Abstract` columns (see [`examples/`](examples/) for sample files and the full column list) (`DOI`, `Authors`, `Year`, `Source title` are picked up automatically when present, as in a Scopus export). You'll see a preview flagging likely duplicates (by DOI or title) before anything is saved — uncheck any you don't want to add.
   - **Add one paper**: click "Add paper" and search by DOI or title (metadata comes from CrossRef automatically) or enter details manually.
3. Review papers one at a time: read the abstract, assign tags, write notes. Everything saves automatically.
4. Use the progress overview grid to jump to any paper and see what's left.
5. Manage tag fields/tags in the "Manage fields and tags" panel. The two built-in fields (`Adherence`, `Contribution Type`) can't be renamed or deleted; custom fields can be freely added, renamed, or removed.

Your data lives in `backend/data/app.db`. Back it up like any file if you want an extra copy; the app itself never requires you to export/import it manually.

## Migrating data from the old Streamlit version

If you have an `.xlsx` + session-JSON pair exported from the previous version of this app:

```bash
cd backend
uv run scripts/migrate_legacy.py \
  --xlsx "/path/to/export.xlsx" \
  --json "/path/to/export_session-*.json" \
  --project-name "My Migrated Review"
```

This creates a new project pre-populated with those papers, tags, and notes. It requires the two files to have the same number of rows/entries (they're paired positionally, as the old export format did) — it will refuse to run otherwise rather than silently mis-attach tags.

## Testing

```bash
cd backend
uv run pytest
```

Covers duplicate-detection logic, xlsx parsing (against a synthetic fixture in `backend/tests/fixtures/`), the CrossRef client (mocked HTTP), and the full API (project/paper/field CRUD, protected-field rules, cascade deletes).

## License

See [LICENSE](LICENSE) file for details.
