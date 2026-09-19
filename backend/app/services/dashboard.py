"""Aggregates papers/tags/notes into summary stats for the dashboard page."""

from __future__ import annotations

from sqlmodel import Session, select

from app.models import Project, TagField, TagOption
from app.schemas import DashboardStats, TagDistributionEntry
from app.services.paper_repo import option_id_to_field_id, paper_score, paper_to_list_item


def _option_path(option: TagOption) -> str:
    parts = [option.value]
    node = option.parent
    while node is not None:
        parts.append(node.value)
        node = node.parent
    return " > ".join(reversed(parts))


def compute_dashboard_stats(session: Session, project_id: int) -> DashboardStats:
    project = session.get(Project, project_id)
    papers = project.papers

    total_field_count = len(
        session.exec(select(TagField.id).where(TagField.project_id == project_id)).all()
    )
    option_to_field = option_id_to_field_id(session, project_id)

    scores = [paper_score(p) for p in papers]
    ratings = [p.rating for p in papers if p.rating is not None]
    with_notes_count = sum(1 for p in papers if p.notes and p.notes.strip())
    fully_tagged_count = sum(
        1
        for p in papers
        if total_field_count > 0
        and len(
            {
                option_to_field[a.tag_option_id]
                for a in p.tag_assignments
                if a.tag_option_id in option_to_field
            }
        )
        == total_field_count
    )

    counts: dict[int, int] = {}
    for paper in papers:
        for assignment in paper.tag_assignments:
            counts[assignment.tag_option_id] = counts.get(assignment.tag_option_id, 0) + 1

    options = session.exec(
        select(TagOption)
        .join(TagField, TagOption.field_id == TagField.id)
        .where(TagField.project_id == project_id)
    ).all()
    field_names = {
        f.id: f.name
        for f in session.exec(select(TagField).where(TagField.project_id == project_id)).all()
    }

    tag_distribution = sorted(
        (
            TagDistributionEntry(
                field_id=option.field_id,
                field_name=field_names.get(option.field_id, ""),
                option_id=option.id,
                option_path=_option_path(option),
                weight=option.weight,
                count=counts[option.id],
            )
            for option in options
            if option.id in counts
        ),
        key=lambda entry: entry.count,
        reverse=True,
    )

    ranked_papers = sorted(papers, key=paper_score, reverse=True)[:10]
    top_papers = [paper_to_list_item(p, option_to_field, total_field_count) for p in ranked_papers]

    return DashboardStats(
        total_papers=len(papers),
        fully_tagged_count=fully_tagged_count,
        rated_count=len(ratings),
        with_notes_count=with_notes_count,
        average_rating=(sum(ratings) / len(ratings)) if ratings else None,
        average_score=(sum(scores) / len(scores)) if scores else 0.0,
        tag_distribution=tag_distribution,
        top_papers=top_papers,
    )
