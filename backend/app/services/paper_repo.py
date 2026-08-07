"""Shared read/write helpers for Paper rows, used by the papers, import, and
lookup routers so dedup + serialization logic lives in exactly one place."""

from __future__ import annotations

from sqlmodel import Session, select

from app.models import Paper, TagAssignment, TagField, TagOption
from app.schemas import PaperDetail, PaperListItem
from app.services.dedup import ExistingPaperKey, normalize_doi, normalize_title


def existing_paper_keys(session: Session, project_id: int) -> list[ExistingPaperKey]:
    papers = session.exec(select(Paper).where(Paper.project_id == project_id)).all()
    return [
        ExistingPaperKey(
            paper_id=paper.id,
            title=paper.title,
            doi_normalized=paper.doi_normalized,
            title_normalized=paper.title_normalized,
        )
        for paper in papers
    ]


def option_id_to_field_id(session: Session, project_id: int) -> dict[int, int]:
    rows = session.exec(
        select(TagOption.id, TagField.id)
        .join(TagField, TagOption.field_id == TagField.id)
        .where(TagField.project_id == project_id)
    ).all()
    return {option_id: field_id for option_id, field_id in rows}


def paper_to_detail(paper: Paper) -> PaperDetail:
    tags: dict[int, list[int]] = {}
    for assignment in paper.tag_assignments:
        tags.setdefault(assignment.tag_option.field_id, []).append(assignment.tag_option_id)
    return PaperDetail(
        id=paper.id,
        project_id=paper.project_id,
        title=paper.title,
        abstract=paper.abstract,
        doi=paper.doi,
        authors=paper.authors,
        year=paper.year,
        source_title=paper.source_title,
        notes=paper.notes,
        source=paper.source,
        order_index=paper.order_index,
        tags=tags,
    )


def paper_to_list_item(
    paper: Paper, option_to_field: dict[int, int], total_field_count: int
) -> PaperListItem:
    filled_fields = {
        option_to_field[a.tag_option_id]
        for a in paper.tag_assignments
        if a.tag_option_id in option_to_field
    }
    return PaperListItem(
        id=paper.id,
        title=paper.title,
        doi=paper.doi,
        authors=paper.authors,
        year=paper.year,
        order_index=paper.order_index,
        filled_field_count=len(filled_fields),
        total_field_count=total_field_count,
    )


def build_paper(
    *,
    project_id: int,
    title: str,
    abstract: str | None,
    doi: str | None,
    authors: str | None,
    year: int | None,
    source_title: str | None,
    source,
    raw_metadata: dict | None,
    order_index: int,
) -> Paper:
    return Paper(
        project_id=project_id,
        title=title,
        abstract=abstract,
        doi=doi,
        doi_normalized=normalize_doi(doi),
        title_normalized=normalize_title(title),
        authors=authors,
        year=year,
        source_title=source_title,
        source=source,
        raw_metadata=raw_metadata,
        order_index=order_index,
    )


def next_order_index(session: Session, project_id: int) -> int:
    papers = session.exec(select(Paper.order_index).where(Paper.project_id == project_id)).all()
    return (max(papers) + 1) if papers else 0


def apply_tag_updates(session: Session, paper: Paper, tags: dict[int, list[int]]) -> None:
    """Replace paper's tag assignments for the given fields with the provided option ids."""
    existing_by_field: dict[int, list[TagAssignment]] = {}
    for assignment in paper.tag_assignments:
        existing_by_field.setdefault(assignment.tag_option.field_id, []).append(assignment)

    for field_id, option_ids in tags.items():
        for assignment in existing_by_field.get(field_id, []):
            session.delete(assignment)
        for option_id in option_ids:
            session.add(TagAssignment(paper_id=paper.id, tag_option_id=option_id))
