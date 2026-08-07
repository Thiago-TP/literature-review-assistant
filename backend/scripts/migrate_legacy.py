#!/usr/bin/env python3
"""One-off bridge from the old Streamlit app's (xlsx, exported-JSON) pair into
the new database.

The old export format paired the JSON progress list with the xlsx rows
*positionally* (JSON entry i belongs to xlsx row i) -- exactly the fragility
this rewrite fixes going forward. This script performs that one fragile
pairing exactly once, so a review already done in the old app isn't lost.

Usage:
    python scripts/migrate_legacy.py \\
        --xlsx "/path/to/old_export.xlsx" \\
        --json "/path/to/old_export_session-YYYY-MM-DD.json" \\
        --project-name "My Migrated Review"
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from sqlmodel import Session, select  # noqa: E402

from app.constants import REQUIRED_FIELDS  # noqa: E402
from app.db import engine, init_db  # noqa: E402
from app.models import Project, TagAssignment, TagField, TagOption  # noqa: E402
from app.services.paper_repo import build_paper  # noqa: E402
from app.services.xlsx_import import parse_xlsx  # noqa: E402


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--xlsx", required=True, type=Path, help="Path to the legacy .xlsx export")
    parser.add_argument("--json", required=True, type=Path, help="Path to the legacy session JSON export")
    parser.add_argument("--project-name", required=True, help="Name for the new project to create")
    args = parser.parse_args()

    rows = parse_xlsx(args.xlsx.read_bytes())
    progress: list[dict] = json.loads(args.json.read_text())

    if len(rows) != len(progress):
        sys.exit(
            f"Row count mismatch: xlsx has {len(rows)} papers but JSON has {len(progress)} entries. "
            "The two files are paired positionally and can't be safely merged if they've "
            "diverged (e.g. the xlsx was re-exported/reordered after the JSON was saved). Aborting."
        )

    field_names_in_json = {
        key for entry in progress for key in entry.keys() if key != "Notes"
    }
    extra_field_names = field_names_in_json - set(REQUIRED_FIELDS.keys())

    init_db()
    with Session(engine) as session:
        if session.exec(select(Project).where(Project.name == args.project_name)).first():
            sys.exit(f"Project '{args.project_name}' already exists. Choose a different --project-name.")

        project = Project(name=args.project_name)
        session.add(project)
        session.flush()

        option_lookup: dict[tuple[str, str], TagOption] = {}
        all_field_definitions = dict(REQUIRED_FIELDS)
        for extra_name in extra_field_names:
            values_seen = sorted({v for entry in progress for v in entry.get(extra_name, [])})
            all_field_definitions[extra_name] = values_seen

        for position, (field_name, options) in enumerate(all_field_definitions.items()):
            field = TagField(
                project_id=project.id,
                name=field_name,
                is_protected=field_name in REQUIRED_FIELDS,
                position=position,
            )
            session.add(field)
            session.flush()
            for option_position, value in enumerate(options):
                option = TagOption(field_id=field.id, value=value, position=option_position)
                session.add(option)
                session.flush()
                option_lookup[(field_name, value)] = option

        for index, (row, entry) in enumerate(zip(rows, progress)):
            paper = build_paper(
                project_id=project.id,
                title=row.title,
                abstract=row.abstract,
                doi=row.doi,
                authors=row.authors,
                year=row.year,
                source_title=row.source_title,
                source="xlsx_import",
                raw_metadata=row.raw_metadata,
                order_index=index,
            )
            paper.notes = entry.get("Notes", "")
            session.add(paper)
            session.flush()

            for field_name, values in entry.items():
                if field_name == "Notes":
                    continue
                for value in values:
                    option = option_lookup.get((field_name, value))
                    if option is None:
                        continue
                    session.add(TagAssignment(paper_id=paper.id, tag_option_id=option.id))

        session.commit()
        project_id = project.id

    print(f"Migrated {len(rows)} papers into project '{args.project_name}' (id={project_id}).")
    print("Spot-check a few entries against the legacy JSON before relying on this data.")


if __name__ == "__main__":
    main()
