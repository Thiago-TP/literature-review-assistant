from __future__ import annotations

from datetime import datetime, timezone

from fastapi import APIRouter, HTTPException
from sqlmodel import select

from app.constants import REQUIRED_FIELDS
from app.deps import SessionDep, get_project_or_404
from app.models import Paper, Project, TagField, TagOption
from app.schemas import LastViewedUpdate, ProjectCreate, ProjectRead, ProjectUpdate

router = APIRouter(prefix="/api/projects", tags=["projects"])


def _to_read(session: SessionDep, project: Project) -> ProjectRead:
    paper_count = len(
        session.exec(select(Paper.id).where(Paper.project_id == project.id)).all()
    )
    return ProjectRead(
        id=project.id,
        name=project.name,
        created_at=project.created_at,
        updated_at=project.updated_at,
        last_viewed_paper_id=project.last_viewed_paper_id,
        paper_count=paper_count,
    )


@router.post("", response_model=ProjectRead, status_code=201)
def create_project(payload: ProjectCreate, session: SessionDep) -> ProjectRead:
    name = payload.name.strip()
    if not name:
        raise HTTPException(status_code=400, detail="Project name cannot be empty")
    if session.exec(select(Project).where(Project.name == name)).first():
        raise HTTPException(status_code=400, detail=f"Project '{name}' already exists")

    project = Project(name=name)
    session.add(project)
    session.flush()

    for position, (field_name, options) in enumerate(REQUIRED_FIELDS.items()):
        field = TagField(project_id=project.id, name=field_name, is_protected=True, position=position)
        session.add(field)
        session.flush()
        for option_position, value in enumerate(options):
            session.add(TagOption(field_id=field.id, value=value, position=option_position))

    session.commit()
    session.refresh(project)
    return _to_read(session, project)


@router.get("", response_model=list[ProjectRead])
def list_projects(session: SessionDep) -> list[ProjectRead]:
    projects = session.exec(select(Project).order_by(Project.updated_at.desc())).all()
    return [_to_read(session, project) for project in projects]


@router.get("/{project_id}", response_model=ProjectRead)
def get_project(project_id: int, session: SessionDep) -> ProjectRead:
    project = get_project_or_404(project_id, session)
    return _to_read(session, project)


@router.patch("/{project_id}", response_model=ProjectRead)
def update_project(project_id: int, payload: ProjectUpdate, session: SessionDep) -> ProjectRead:
    project = get_project_or_404(project_id, session)
    if payload.name is not None:
        name = payload.name.strip()
        if not name:
            raise HTTPException(status_code=400, detail="Project name cannot be empty")
        project.name = name
    project.updated_at = datetime.now(timezone.utc)
    session.add(project)
    session.commit()
    session.refresh(project)
    return _to_read(session, project)


@router.delete("/{project_id}", status_code=204)
def delete_project(project_id: int, session: SessionDep) -> None:
    project = get_project_or_404(project_id, session)
    session.delete(project)
    session.commit()


@router.patch("/{project_id}/last-viewed", response_model=ProjectRead)
def set_last_viewed(project_id: int, payload: LastViewedUpdate, session: SessionDep) -> ProjectRead:
    project = get_project_or_404(project_id, session)
    paper = session.get(Paper, payload.paper_id)
    if paper is None or paper.project_id != project_id:
        raise HTTPException(status_code=404, detail=f"Paper {payload.paper_id} not found in project")
    project.last_viewed_paper_id = payload.paper_id
    session.add(project)
    session.commit()
    session.refresh(project)
    return _to_read(session, project)
