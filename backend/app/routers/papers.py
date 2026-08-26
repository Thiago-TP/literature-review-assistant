from __future__ import annotations

from fastapi import APIRouter, HTTPException
from sqlalchemy.exc import IntegrityError
from sqlmodel import select

from app.deps import SessionDep, get_paper_or_404, get_project_or_404
from app.models import TagAssignment, TagField
from app.schemas import (
    DuplicateInfo,
    PaperCreate,
    PaperCreateResult,
    PaperDetail,
    PaperListItem,
    PaperUpdate,
    RatingUpdate,
)
from app.services import dedup
from app.services.paper_repo import (
    apply_tag_updates,
    build_paper,
    existing_paper_keys,
    next_order_index,
    option_id_to_field_id,
    paper_to_detail,
    paper_to_list_item,
)

router = APIRouter(prefix="/api/projects/{project_id}/papers", tags=["papers"])


@router.get("", response_model=list[PaperListItem])
def list_papers(project_id: int, session: SessionDep) -> list[PaperListItem]:
    project = get_project_or_404(project_id, session)
    total_field_count = len(
        session.exec(select(TagField.id).where(TagField.project_id == project_id)).all()
    )
    option_to_field = option_id_to_field_id(session, project_id)
    papers = sorted(project.papers, key=lambda p: p.order_index)
    return [paper_to_list_item(p, option_to_field, total_field_count) for p in papers]


@router.get("/{paper_id}", response_model=PaperDetail)
def get_paper(project_id: int, paper_id: int, session: SessionDep) -> PaperDetail:
    paper = get_paper_or_404(project_id, paper_id, session)
    return paper_to_detail(paper)


@router.patch("/{paper_id}", response_model=PaperDetail)
def update_paper(project_id: int, paper_id: int, payload: PaperUpdate, session: SessionDep) -> PaperDetail:
    paper = get_paper_or_404(project_id, paper_id, session)
    if payload.notes is not None:
        paper.notes = payload.notes
        session.add(paper)
    if payload.tags is not None:
        apply_tag_updates(session, paper, payload.tags)
    session.commit()
    session.refresh(paper)
    return paper_to_detail(paper)


@router.post("/{paper_id}/tags/{option_id}", response_model=PaperDetail)
def assign_tag(project_id: int, paper_id: int, option_id: int, session: SessionDep) -> PaperDetail:
    """Assign a single tag, idempotently. Used by the UI instead of the
    replace-the-whole-field PATCH above so that clicking a topic and then a
    subtopic in quick succession can't race: each click only ever asserts
    "this one option is assigned", never a client-computed full list that a
    slightly-stale response could clobber."""
    paper = get_paper_or_404(project_id, paper_id, session)
    already_assigned = session.exec(
        select(TagAssignment).where(
            TagAssignment.paper_id == paper_id, TagAssignment.tag_option_id == option_id
        )
    ).first()
    if not already_assigned:
        session.add(TagAssignment(paper_id=paper_id, tag_option_id=option_id))
        try:
            session.commit()
        except IntegrityError:
            session.rollback()  # a concurrent request already assigned it -- that's the desired end state
    session.refresh(paper)
    return paper_to_detail(paper)


@router.delete("/{paper_id}/tags/{option_id}", response_model=PaperDetail)
def unassign_tag(project_id: int, paper_id: int, option_id: int, session: SessionDep) -> PaperDetail:
    paper = get_paper_or_404(project_id, paper_id, session)
    assignment = session.exec(
        select(TagAssignment).where(
            TagAssignment.paper_id == paper_id, TagAssignment.tag_option_id == option_id
        )
    ).first()
    if assignment:
        session.delete(assignment)
        session.commit()
    session.refresh(paper)
    return paper_to_detail(paper)


@router.put("/{paper_id}/rating", response_model=PaperDetail)
def set_rating(project_id: int, paper_id: int, payload: RatingUpdate, session: SessionDep) -> PaperDetail:
    paper = get_paper_or_404(project_id, paper_id, session)
    paper.rating = payload.rating
    session.add(paper)
    session.commit()
    session.refresh(paper)
    return paper_to_detail(paper)


@router.delete("/{paper_id}/rating", response_model=PaperDetail)
def clear_rating(project_id: int, paper_id: int, session: SessionDep) -> PaperDetail:
    paper = get_paper_or_404(project_id, paper_id, session)
    paper.rating = None
    session.add(paper)
    session.commit()
    session.refresh(paper)
    return paper_to_detail(paper)


@router.delete("/{paper_id}", status_code=204)
def delete_paper(project_id: int, paper_id: int, session: SessionDep) -> None:
    paper = get_paper_or_404(project_id, paper_id, session)
    session.delete(paper)
    session.commit()


@router.post("", response_model=PaperCreateResult, status_code=201)
def create_paper(project_id: int, payload: PaperCreate, session: SessionDep) -> PaperCreateResult:
    get_project_or_404(project_id, session)
    title = payload.title.strip()
    if not title:
        raise HTTPException(status_code=400, detail="Title cannot be empty")

    if not payload.force:
        classification = dedup.classify(title, payload.doi, existing_paper_keys(session, project_id))
        if classification.is_duplicate:
            return PaperCreateResult(
                duplicate=DuplicateInfo(
                    is_duplicate=True,
                    reason=classification.reason,
                    matched_paper_id=classification.matched_paper_id,
                    matched_title=classification.matched_title,
                )
            )

    paper = build_paper(
        project_id=project_id,
        title=title,
        abstract=payload.abstract,
        doi=payload.doi,
        authors=payload.authors,
        year=payload.year,
        source_title=payload.source_title,
        source=payload.source,
        raw_metadata=payload.raw_metadata,
        order_index=next_order_index(session, project_id),
    )
    session.add(paper)
    try:
        session.commit()
    except IntegrityError as exc:
        session.rollback()
        raise HTTPException(
            status_code=409,
            detail="This DOI is already used by another paper in the project; a DOI match cannot be forced.",
        ) from exc
    session.refresh(paper)
    return PaperCreateResult(paper=paper_to_detail(paper))
