from __future__ import annotations

from fastapi import APIRouter, HTTPException
from sqlmodel import select

from app.deps import SessionDep, get_field_or_404, get_option_or_404, get_project_or_404
from app.models import TagAssignment, TagField, TagOption
from app.schemas import (
    TagFieldCreate,
    TagFieldRead,
    TagFieldUpdate,
    TagOptionCreate,
    TagOptionRead,
    TagOptionUpdate,
)

router = APIRouter(prefix="/api/projects/{project_id}/fields", tags=["fields"])


def _field_to_read(field: TagField) -> TagFieldRead:
    options = sorted(field.options, key=lambda option: option.position)
    return TagFieldRead(
        id=field.id,
        name=field.name,
        is_protected=field.is_protected,
        position=field.position,
        options=[TagOptionRead(id=o.id, value=o.value, position=o.position) for o in options],
    )


@router.get("", response_model=list[TagFieldRead])
def list_fields(project_id: int, session: SessionDep) -> list[TagFieldRead]:
    get_project_or_404(project_id, session)
    fields = session.exec(
        select(TagField).where(TagField.project_id == project_id).order_by(TagField.position)
    ).all()
    return [_field_to_read(f) for f in fields]


@router.post("", response_model=TagFieldRead, status_code=201)
def create_field(project_id: int, payload: TagFieldCreate, session: SessionDep) -> TagFieldRead:
    get_project_or_404(project_id, session)
    name = payload.name.strip()
    if not name:
        raise HTTPException(status_code=400, detail="Field name cannot be empty")
    if session.exec(
        select(TagField).where(TagField.project_id == project_id, TagField.name == name)
    ).first():
        raise HTTPException(status_code=400, detail=f"Field '{name}' already exists")

    existing_positions = session.exec(
        select(TagField.position).where(TagField.project_id == project_id)
    ).all()
    next_position = (max(existing_positions) + 1) if existing_positions else 0

    field = TagField(project_id=project_id, name=name, is_protected=False, position=next_position)
    session.add(field)
    session.commit()
    session.refresh(field)
    return _field_to_read(field)


@router.patch("/{field_id}", response_model=TagFieldRead)
def rename_field(
    project_id: int, field_id: int, payload: TagFieldUpdate, session: SessionDep
) -> TagFieldRead:
    field = get_field_or_404(project_id, field_id, session)
    if field.is_protected:
        raise HTTPException(status_code=400, detail="Protected fields cannot be renamed")
    new_name = payload.name.strip()
    if not new_name:
        raise HTTPException(status_code=400, detail="Field name cannot be empty")
    if session.exec(
        select(TagField).where(TagField.project_id == project_id, TagField.name == new_name)
    ).first():
        raise HTTPException(status_code=400, detail=f"Field '{new_name}' already exists")
    field.name = new_name
    session.add(field)
    session.commit()
    session.refresh(field)
    return _field_to_read(field)


@router.delete("/{field_id}", status_code=204)
def delete_field(project_id: int, field_id: int, session: SessionDep) -> None:
    field = get_field_or_404(project_id, field_id, session)
    if field.is_protected:
        raise HTTPException(status_code=400, detail="Protected fields cannot be deleted")
    session.delete(field)
    session.commit()


@router.post("/{field_id}/options", response_model=TagOptionRead, status_code=201)
def create_option(
    project_id: int, field_id: int, payload: TagOptionCreate, session: SessionDep
) -> TagOptionRead:
    field = get_field_or_404(project_id, field_id, session)
    value = payload.value.strip()
    if not value:
        raise HTTPException(status_code=400, detail="Tag value cannot be empty")
    if session.exec(
        select(TagOption).where(TagOption.field_id == field_id, TagOption.value == value)
    ).first():
        raise HTTPException(status_code=400, detail=f"Tag '{value}' already exists in this field")

    existing_positions = session.exec(
        select(TagOption.position).where(TagOption.field_id == field_id)
    ).all()
    next_position = (max(existing_positions) + 1) if existing_positions else 0

    option = TagOption(field_id=field.id, value=value, position=next_position)
    session.add(option)
    session.commit()
    session.refresh(option)
    return TagOptionRead(id=option.id, value=option.value, position=option.position)


@router.patch("/{field_id}/options/{option_id}", response_model=TagOptionRead)
def rename_option(
    project_id: int,
    field_id: int,
    option_id: int,
    payload: TagOptionUpdate,
    session: SessionDep,
) -> TagOptionRead:
    field = get_field_or_404(project_id, field_id, session)
    option = get_option_or_404(field_id, option_id, session)
    if field.is_protected:
        raise HTTPException(status_code=400, detail="Tags in protected fields cannot be renamed")
    new_value = payload.value.strip()
    if not new_value:
        raise HTTPException(status_code=400, detail="Tag value cannot be empty")
    if session.exec(
        select(TagOption).where(TagOption.field_id == field_id, TagOption.value == new_value)
    ).first():
        raise HTTPException(status_code=400, detail=f"Tag '{new_value}' already exists in this field")
    option.value = new_value
    session.add(option)
    session.commit()
    session.refresh(option)
    return TagOptionRead(id=option.id, value=option.value, position=option.position)


@router.delete("/{field_id}/options/{option_id}", status_code=204)
def delete_option(project_id: int, field_id: int, option_id: int, session: SessionDep) -> None:
    field = get_field_or_404(project_id, field_id, session)
    option = get_option_or_404(field_id, option_id, session)
    if field.is_protected:
        raise HTTPException(status_code=400, detail="Tags in protected fields cannot be deleted")

    assigned_papers = session.exec(
        select(TagAssignment.paper_id).where(TagAssignment.tag_option_id == option_id)
    ).all()
    if assigned_papers:
        raise HTTPException(
            status_code=400,
            detail={
                "message": "Cannot delete a tag that is currently assigned to papers",
                "affected_paper_ids": assigned_papers,
            },
        )
    session.delete(option)
    session.commit()
