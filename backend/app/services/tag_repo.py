"""Fields and tags: ORM -> response shapes.

Split out of the fields router so the review plan can render the same field
and tag tree without one router importing another. The sibling of
`paper_repo.py`, and like it, free of FastAPI.
"""

from __future__ import annotations

from app.models import TagField, TagOption
from app.schemas import TagFieldRead, TagOptionRead


def build_option_tree(
    options: list[TagOption], parent_id: int | None = None
) -> list[TagOptionRead]:
    """Turn the flat list of a field's options (all depths) into a nested tree."""
    children = sorted((o for o in options if o.parent_id == parent_id), key=lambda o: o.position)
    return [
        TagOptionRead(
            id=o.id,
            value=o.value,
            position=o.position,
            weight=o.weight,
            description=o.description,
            children=build_option_tree(options, o.id),
        )
        for o in children
    ]


def field_to_read(field: TagField) -> TagFieldRead:
    return TagFieldRead(
        id=field.id,
        name=field.name,
        is_protected=field.is_protected,
        position=field.position,
        description=field.description,
        options=build_option_tree(field.options),
    )
