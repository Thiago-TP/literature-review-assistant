"""Secondary/optional export for backup or sharing — NOT the persistence
mechanism (that's the SQLite database, written to on every mutation)."""

from __future__ import annotations

from io import BytesIO

import pandas as pd
from fastapi import APIRouter
from fastapi.responses import JSONResponse, StreamingResponse
from sqlmodel import select

from app.deps import SessionDep, get_project_or_404
from app.models import TagField

router = APIRouter(tags=["export"])


def _rows_for_export(session: SessionDep, project_id: int) -> tuple[list[dict], list[str]]:
    project = get_project_or_404(project_id, session)
    fields = session.exec(
        select(TagField).where(TagField.project_id == project_id).order_by(TagField.position)
    ).all()
    field_names = [f.name for f in fields]

    rows = []
    for paper in sorted(project.papers, key=lambda p: p.order_index):
        tags_by_field_name: dict[str, list[str]] = {name: [] for name in field_names}
        for assignment in paper.tag_assignments:
            field = assignment.tag_option.field
            tags_by_field_name.setdefault(field.name, []).append(assignment.tag_option.value)

        rows.append(
            {
                "Title": paper.title,
                "Abstract": paper.abstract,
                "DOI": paper.doi,
                "Authors": paper.authors,
                "Year": paper.year,
                "Notes": paper.notes,
                **{name: tags for name, tags in tags_by_field_name.items()},
            }
        )
    return rows, field_names


@router.get("/api/projects/{project_id}/export.json")
def export_json(project_id: int, session: SessionDep):
    rows, _ = _rows_for_export(session, project_id)
    return JSONResponse(content=rows)


@router.get("/api/projects/{project_id}/export.xlsx")
def export_xlsx(project_id: int, session: SessionDep):
    rows, field_names = _rows_for_export(session, project_id)
    flattened = [
        {**{k: v for k, v in row.items() if k not in field_names}, **{name: ", ".join(row[name]) for name in field_names}}
        for row in rows
    ]
    df = pd.DataFrame(flattened)
    buffer = BytesIO()
    df.to_excel(buffer, index=False)
    buffer.seek(0)
    return StreamingResponse(
        buffer,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": "attachment; filename=export.xlsx"},
    )
