"""`scripts/migrate_legacy.py` still runs, end to end.

It is run by hand, rarely, so nothing else exercises it: a rename in the code
it imports from would otherwise surface only when someone finally tries to
migrate a legacy review. Ruff cannot catch that, since it does not resolve
imports.

Run as a subprocess because the script binds its database when it is
imported, from LRA_DB_PATH, so it needs a process whose environment points
that at a throwaway file.
"""

from __future__ import annotations

import contextlib
import json
import os
import sqlite3
import subprocess
import sys
from pathlib import Path

from tests.conftest import SAMPLE_XLSX_PATH

BACKEND_DIR = Path(__file__).resolve().parent.parent
SCRIPT = BACKEND_DIR / "scripts" / "migrate_legacy.py"


def test_migrates_an_xlsx_and_session_json_pair(tmp_path):
    # One legacy progress entry per row of the sample export, paired by
    # position; "Domain" is a field the old app had that the new one creates.
    progress = [
        {"Adherence": ["Sufficient"], "Domain": ["Widgets"], "Notes": "First paper."},
        {"Adherence": ["Partial"], "Notes": ""},
        {},
        {"Contribution Type": ["Review"]},
        {"Domain": ["Gadgets", "Widgets"]},
    ]
    json_path = tmp_path / "session.json"
    json_path.write_text(json.dumps(progress))
    db_path = tmp_path / "migrated.db"
    command = [sys.executable, str(SCRIPT), "--xlsx", str(SAMPLE_XLSX_PATH)]
    command += ["--json", str(json_path), "--project-name", "Legacy"]

    result = subprocess.run(
        command,
        cwd=BACKEND_DIR,
        env={**os.environ, "LRA_DB_PATH": str(db_path)},
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, result.stderr
    assert "Migrated 5 papers" in result.stdout

    # closing(): a sqlite3 connection's own `with` ends a transaction but
    # leaves the connection open.
    with contextlib.closing(sqlite3.connect(db_path)) as db:
        [(paper_count,)] = db.execute("SELECT COUNT(*) FROM paper")
        [(notes,)] = db.execute("SELECT notes FROM paper ORDER BY order_index LIMIT 1")
        fields = {name for (name,) in db.execute("SELECT name FROM tagfield")}
        [(assignment_count,)] = db.execute("SELECT COUNT(*) FROM tagassignment")

    assert paper_count == 5
    assert notes == "First paper."
    assert fields == {"Adherence", "Contribution Type", "Domain"}
    assert assignment_count == 6
