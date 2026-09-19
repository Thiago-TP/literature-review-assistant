from __future__ import annotations

from datetime import UTC, datetime

from fastapi import APIRouter, HTTPException
from sqlmodel import select

from app.constants import REQUIRED_FIELDS
from app.deps import SessionDep, get_project_or_404
from app.models import Paper, Project, TagField, TagOption
from app.schemas import (
    LastViewedUpdate,
    ProjectCreate,
    ProjectRead,
    ProjectUpdate,
    ReviewPlanRead,
    ReviewPlanUpdate,
)
from app.services import review_plan, tag_repo

router = APIRouter(prefix="/api/projects", tags=["projects"])


def _plan_sections(project: Project) -> list[str | None]:
    """The plan's prose sections in display order, read off the `plan_*`
    columns by the names the service holds."""
    return [getattr(project, f"plan_{section}") for section in review_plan.PLAN_SECTIONS]


def _project_fields(session: SessionDep, project_id: int) -> list[TagField]:
    return list(
        session.exec(
            select(TagField).where(TagField.project_id == project_id).order_by(TagField.position)
        ).all()
    )


def _plan_progress(session: SessionDep, project: Project) -> review_plan.PlanProgress:
    fields = _project_fields(session, project.id)
    adherence = [f for f in fields if f.name == review_plan.ADHERENCE_FIELD_NAME]
    return review_plan.plan_progress(
        _plan_sections(project),
        [f.description for f in fields],
        [option.description for f in adherence for option in f.options],
    )


def _to_read(session: SessionDep, project: Project) -> ProjectRead:
    paper_count = len(session.exec(select(Paper.id).where(Paper.project_id == project.id)).all())
    progress = _plan_progress(session, project)
    return ProjectRead(
        id=project.id,
        name=project.name,
        created_at=project.created_at,
        updated_at=project.updated_at,
        last_viewed_paper_id=project.last_viewed_paper_id,
        paper_count=paper_count,
        plan_filled=progress.filled,
        plan_total=progress.total,
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
        field = TagField(
            project_id=project.id, name=field_name, is_protected=True, position=position
        )
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
    project.updated_at = datetime.now(UTC)
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
        raise HTTPException(
            status_code=404, detail=f"Paper {payload.paper_id} not found in project"
        )
    project.last_viewed_paper_id = payload.paper_id
    session.add(project)
    session.commit()
    session.refresh(project)
    return _to_read(session, project)


def _to_plan_read(session: SessionDep, project: Project) -> ReviewPlanRead:
    progress = _plan_progress(session, project)
    return ReviewPlanRead(
        project_id=project.id,
        project_name=project.name,
        purpose=project.plan_purpose,
        scope=project.plan_scope,
        search=project.plan_search,
        weights=project.plan_weights,
        other=project.plan_other,
        fields=[tag_repo.field_to_read(f) for f in _project_fields(session, project.id)],
        filled=progress.filled,
        total=progress.total,
    )


@router.get("/{project_id}/plan", response_model=ReviewPlanRead)
def get_review_plan(project_id: int, session: SessionDep) -> ReviewPlanRead:
    """The whole plan page in one request: the prose sections plus the live
    fields and tags, whose descriptions are the rest of the form."""
    project = get_project_or_404(project_id, session)
    return _to_plan_read(session, project)


@router.patch("/{project_id}/plan", response_model=ReviewPlanRead)
def update_review_plan(
    project_id: int, payload: ReviewPlanUpdate, session: SessionDep
) -> ReviewPlanRead:
    """Update the sections that were sent and leave the rest alone: the page
    saves one box at a time as it loses focus."""
    project = get_project_or_404(project_id, session)

    for section in review_plan.PLAN_SECTIONS:
        value = getattr(payload, section)
        if value is not None:
            # Empty means "not written", the same as never having been
            # touched, so the progress count needs only one rule.
            setattr(project, f"plan_{section}", value.strip() or None)

    # Writing the plan is work on the review, and the project list is ordered
    # by `updated_at`.
    project.updated_at = datetime.now(UTC)
    session.add(project)
    session.commit()
    session.refresh(project)
    return _to_plan_read(session, project)
