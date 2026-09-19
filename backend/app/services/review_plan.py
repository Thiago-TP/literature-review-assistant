"""The review plan: which sections exist, and when one counts as written.

No FastAPI and no ORM in here, so the completeness rule -- the thing the whole
"your plan is incomplete" badge hangs on -- can be exercised directly.
"""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass

# The prose sections of a review plan, in the order the page shows them. The
# names match the `plan_*` columns on Project; keep the two in step.
PLAN_SECTIONS: tuple[str, ...] = (
    "purpose",
    "scope",
    "search",
    "weights",
    "other",
)

# The field whose tags are the in-or-out judgement of a review. Its three tags
# are the only individual tags that count towards completeness, because the
# reader is asked, by name, to say what each level means.
ADHERENCE_FIELD_NAME = "Adherence"


@dataclass(frozen=True)
class PlanProgress:
    """How much of a plan has been written, as a count of countable items."""

    filled: int
    total: int

    @property
    def is_complete(self) -> bool:
        return self.filled >= self.total


def is_written(text: str | None) -> bool:
    """Whether a box counts as filled in. Whitespace is not an answer, so a
    space bar cannot be used to clear the badge."""
    return bool(text and text.strip())


def count_written(values: Iterable[str | None]) -> int:
    return sum(1 for value in values if is_written(value))


def plan_progress(
    section_texts: Iterable[str | None],
    field_descriptions: Iterable[str | None],
    adherence_tag_descriptions: Iterable[str | None],
) -> PlanProgress:
    """Count the plan's items: the five prose sections, a description for each
    of the review's fields, and what each level of Adherence means.

    Descriptions of individual non-Adherence tags are deliberately left out.
    They are encouraged, and shown beside the tag while reviewing, but a review
    with sixty tags would never reach "complete" if each one counted, and a
    target nobody reaches is not encouragement.
    """
    sections = list(section_texts)
    fields = list(field_descriptions)
    adherence = list(adherence_tag_descriptions)

    filled = count_written(sections) + count_written(fields) + count_written(adherence)
    total = len(sections) + len(fields) + len(adherence)
    return PlanProgress(filled=filled, total=total)
