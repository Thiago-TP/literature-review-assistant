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
from app.services import tag_repo

router = APIRouter(prefix="/api/projects/{project_id}/fields", tags=["fields"])

# Shared with the review plan, which renders the same tree (services/tag_repo.py).
_build_option_tree = tag_repo.build_option_tree
_field_to_read = tag_repo.field_to_read


def _collect_with_descendants(option: TagOption) -> list[int]:
    """This option's id plus every descendant's id, recursively."""
    ids = [option.id]
    for child in option.children:
        ids.extend(_collect_with_descendants(child))
    return ids


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
def update_field(
    project_id: int, field_id: int, payload: TagFieldUpdate, session: SessionDep
) -> TagFieldRead:
    """Rename and/or describe a field. Renaming is blocked for protected
    fields (Adherence, Contribution Type), but describing them is not --
    saying what Adherence asks of a paper is the whole point of the review
    plan, and it is the built-in fields that most need saying."""
    field = get_field_or_404(project_id, field_id, session)

    if payload.name is not None:
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

    if payload.description is not None:
        # Empty means "not written" everywhere else, so store it as such
        # rather than as a blank string the progress count would have to
        # special-case.
        field.description = payload.description.strip() or None

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
    get_field_or_404(project_id, field_id, session)
    value = payload.value.strip()
    if not value:
        raise HTTPException(status_code=400, detail="Tag value cannot be empty")

    parent_id = payload.parent_option_id
    if parent_id is not None:
        get_option_or_404(field_id, parent_id, session)  # 404s if missing or in a different field

    if session.exec(
        select(TagOption).where(
            TagOption.field_id == field_id,
            TagOption.parent_id == parent_id,
            TagOption.value == value,
        )
    ).first():
        raise HTTPException(status_code=400, detail=f"Tag '{value}' already exists at this level")

    sibling_positions = session.exec(
        select(TagOption.position).where(
            TagOption.field_id == field_id, TagOption.parent_id == parent_id
        )
    ).all()
    next_position = (max(sibling_positions) + 1) if sibling_positions else 0

    option = TagOption(
        field_id=field_id,
        parent_id=parent_id,
        value=value,
        position=next_position,
        weight=payload.weight,
    )
    session.add(option)
    session.commit()
    session.refresh(option)
    return TagOptionRead(
        id=option.id,
        value=option.value,
        position=option.position,
        weight=option.weight,
        children=[],
    )


@router.patch("/{field_id}/options/{option_id}", response_model=TagOptionRead)
def update_option(
    project_id: int,
    field_id: int,
    option_id: int,
    payload: TagOptionUpdate,
    session: SessionDep,
) -> TagOptionRead:
    """Rename, reweight and/or describe a tag. Renaming is blocked for
    protected fields (Adherence, Contribution Type) same as before, but
    reweighting and describing aren't -- assigning point values and meanings
    to the built-in options is expected, just not renaming/deleting them."""
    field = get_field_or_404(project_id, field_id, session)
    option = get_option_or_404(field_id, option_id, session)

    if payload.value is not None:
        if field.is_protected:
            raise HTTPException(
                status_code=400, detail="Tags in protected fields cannot be renamed"
            )
        new_value = payload.value.strip()
        if not new_value:
            raise HTTPException(status_code=400, detail="Tag value cannot be empty")
        if session.exec(
            select(TagOption).where(
                TagOption.field_id == field_id,
                TagOption.parent_id == option.parent_id,
                TagOption.value == new_value,
                TagOption.id != option_id,
            )
        ).first():
            raise HTTPException(
                status_code=400, detail=f"Tag '{new_value}' already exists at this level"
            )
        option.value = new_value

    if payload.weight is not None:
        option.weight = payload.weight

    if payload.description is not None:
        option.description = payload.description.strip() or None

    session.add(option)
    session.commit()
    session.refresh(option)
    return TagOptionRead(
        id=option.id,
        value=option.value,
        position=option.position,
        weight=option.weight,
        description=option.description,
        children=_build_option_tree(option.field.options, option.id),
    )


@router.delete("/{field_id}/options/{option_id}", status_code=204)
def delete_option(project_id: int, field_id: int, option_id: int, session: SessionDep) -> None:
    field = get_field_or_404(project_id, field_id, session)
    option = get_option_or_404(field_id, option_id, session)
    if field.is_protected:
        raise HTTPException(status_code=400, detail="Tags in protected fields cannot be deleted")

    subtree_ids = _collect_with_descendants(option)
    assigned_papers = session.exec(
        select(TagAssignment.paper_id).where(TagAssignment.tag_option_id.in_(subtree_ids))
    ).all()
    if assigned_papers:
        raise HTTPException(
            status_code=400,
            detail={
                "message": (
                    "Cannot delete a tag that is currently assigned to papers "
                    "(directly or via a subtopic)"
                ),
                "affected_paper_ids": sorted(set(assigned_papers)),
            },
        )
    session.delete(option)
    session.commit()
