"""Pure, unit-testable handling of highlighted spans over a paper's text.

A highlight is a half-open character range ``[start, end)`` into the plain
text of one field, carrying an id so a client can remove exactly the one it
clicked. Offsets are into the stored string, which is what the client renders,
so the two agree as long as neither re-wraps the text.

Overlapping or touching spans in the same field are merged, because two passes
of a highlighter over adjoining text is one mark, not two — and without
merging, removing "the highlight you clicked" would be ambiguous.
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass

HIGHLIGHTABLE_FIELDS = ("title", "abstract")


class HighlightError(ValueError):
    pass


@dataclass(frozen=True)
class Highlight:
    id: str
    field: str
    start: int
    end: int

    def as_dict(self) -> dict:
        return {"id": self.id, "field": self.field, "start": self.start, "end": self.end}


def from_stored(raw: list | None) -> list[Highlight]:
    """Read back what was stored, skipping anything malformed.

    The column is JSON, so a row could in principle hold anything; a bad entry
    should cost one highlight, not the whole paper.
    """
    highlights: list[Highlight] = []
    for entry in raw or []:
        if not isinstance(entry, dict):
            continue
        try:
            highlight = Highlight(
                id=str(entry["id"]),
                field=str(entry["field"]),
                start=int(entry["start"]),
                end=int(entry["end"]),
            )
        except (KeyError, TypeError, ValueError):
            continue
        if highlight.field in HIGHLIGHTABLE_FIELDS and highlight.start < highlight.end:
            highlights.append(highlight)
    return highlights


def to_stored(highlights: list[Highlight]) -> list[dict]:
    return [h.as_dict() for h in highlights]


def _sorted(highlights: list[Highlight]) -> list[Highlight]:
    return sorted(highlights, key=lambda h: (h.field, h.start, h.end))


def add(
    existing: list[Highlight],
    field: str,
    start: int,
    end: int,
    text_length: int,
) -> list[Highlight]:
    """Add a span, merging it with any it overlaps or touches in that field.

    `text_length` is the length of the field's current text; the span is
    clamped to it so a stale client offset cannot store a range that points
    past the end.
    """
    if field not in HIGHLIGHTABLE_FIELDS:
        raise HighlightError(f"Cannot highlight '{field}'; expected one of {HIGHLIGHTABLE_FIELDS}")
    if text_length <= 0:
        raise HighlightError(f"This paper has no {field} to highlight")

    start = max(0, min(int(start), text_length))
    end = max(0, min(int(end), text_length))
    if start >= end:
        raise HighlightError("A highlight must cover at least one character")

    merged_start, merged_end = start, end
    kept: list[Highlight] = []
    for highlight in existing:
        if highlight.field != field:
            kept.append(highlight)
            continue
        # Touching counts as overlapping: [0,5) and [5,9) are one mark.
        if highlight.start <= merged_end and merged_start <= highlight.end:
            merged_start = min(merged_start, highlight.start)
            merged_end = max(merged_end, highlight.end)
        else:
            kept.append(highlight)

    kept.append(Highlight(id=uuid.uuid4().hex, field=field, start=merged_start, end=merged_end))
    return _sorted(kept)


def remove(existing: list[Highlight], highlight_id: str) -> list[Highlight]:
    remaining = [h for h in existing if h.id != highlight_id]
    if len(remaining) == len(existing):
        raise HighlightError(f"No highlight {highlight_id} on this paper")
    return remaining


def clamp_to_text(existing: list[Highlight], lengths: dict[str, int]) -> list[Highlight]:
    """Drop or shorten spans that no longer fit their field's text.

    Editing a paper's abstract can leave older highlights pointing past its
    end; this keeps what is stored consistent with what can be rendered.
    """
    kept: list[Highlight] = []
    for highlight in existing:
        limit = lengths.get(highlight.field, 0)
        start = min(highlight.start, limit)
        end = min(highlight.end, limit)
        if start < end:
            kept.append(Highlight(id=highlight.id, field=highlight.field, start=start, end=end))
    return _sorted(kept)
