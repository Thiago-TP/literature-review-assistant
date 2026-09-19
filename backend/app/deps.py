from __future__ import annotations

from typing import Annotated

from fastapi import Depends, HTTPException
from sqlmodel import Session

from app.db import get_session
from app.models import Paper, Project, TagField, TagOption

SessionDep = Annotated[Session, Depends(get_session)]


def get_project_or_404(project_id: int, session: SessionDep) -> Project:
    project = session.get(Project, project_id)
    if project is None:
        raise HTTPException(status_code=404, detail=f"Project {project_id} not found")
    return project


def get_paper_or_404(project_id: int, paper_id: int, session: SessionDep) -> Paper:
    paper = session.get(Paper, paper_id)
    if paper is None or paper.project_id != project_id:
        raise HTTPException(
            status_code=404, detail=f"Paper {paper_id} not found in project {project_id}"
        )
    return paper


def get_field_or_404(project_id: int, field_id: int, session: SessionDep) -> TagField:
    field = session.get(TagField, field_id)
    if field is None or field.project_id != project_id:
        raise HTTPException(
            status_code=404, detail=f"Field {field_id} not found in project {project_id}"
        )
    return field


def get_option_or_404(field_id: int, option_id: int, session: SessionDep) -> TagOption:
    option = session.get(TagOption, option_id)
    if option is None or option.field_id != field_id:
        raise HTTPException(
            status_code=404, detail=f"Option {option_id} not found in field {field_id}"
        )
    return option
