"""Application settings, sourced from environment variables with sane local-first defaults."""

from __future__ import annotations

import os
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BACKEND_DIR / "data"
DATA_DIR.mkdir(exist_ok=True)

DATABASE_PATH = Path(os.environ.get("LRA_DB_PATH", DATA_DIR / "app.db"))
DATABASE_URL = f"sqlite:///{DATABASE_PATH}"

CROSSREF_BASE_URL = os.environ.get("CROSSREF_BASE_URL", "https://api.crossref.org")
CROSSREF_MAILTO = os.environ.get("CROSSREF_MAILTO", "pedrofernandes.olv@gmail.com")
CROSSREF_TIMEOUT_SECONDS = float(os.environ.get("CROSSREF_TIMEOUT_SECONDS", "10"))

CORS_ORIGINS = os.environ.get(
    "LRA_CORS_ORIGINS", "http://localhost:5173,http://127.0.0.1:5173"
).split(",")
