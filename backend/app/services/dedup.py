"""Pure, unit-testable normalization and duplicate-classification logic.

Used identically by bulk spreadsheet import and single-paper add (by DOI/title), so a
paper can never be added twice regardless of which path it came in through.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from enum import Enum

_DOI_PREFIXES = (
    "https://doi.org/",
    "http://doi.org/",
    "https://dx.doi.org/",
    "http://dx.doi.org/",
    "doi:",
)

_PUNCTUATION_RE = re.compile(r"[^\w\s]", re.UNICODE)
_WHITESPACE_RE = re.compile(r"\s+")


def normalize_doi(doi: str | None) -> str | None:
    if not doi:
        return None
    value = doi.strip().lower()
    for prefix in _DOI_PREFIXES:
        if value.startswith(prefix):
            value = value[len(prefix) :]
            break
    value = value.strip().rstrip("/")
    return value or None


def normalize_title(title: str | None) -> str:
    if not title:
        return ""
    value = title.strip().lower()
    value = _PUNCTUATION_RE.sub("", value)
    value = _WHITESPACE_RE.sub(" ", value)
    return value.strip()


class DuplicateReason(str, Enum):
    DOI = "doi"
    TITLE = "title"


@dataclass
class ExistingPaperKey:
    """Minimal identity of an already-known paper, used for duplicate lookups."""

    paper_id: int
    title: str
    doi_normalized: str | None
    title_normalized: str


@dataclass
class Classification:
    is_duplicate: bool
    reason: DuplicateReason | None = None
    matched_paper_id: int | None = None
    matched_title: str | None = None
    default_action: str = "add"  # "add" | "skip"


@dataclass
class Candidate:
    """A row/paper being classified, plus the classification result."""

    title: str
    doi: str | None
    doi_normalized: str | None
    title_normalized: str
    classification: Classification = field(
        default_factory=lambda: Classification(is_duplicate=False)
    )


def classify(
    title: str,
    doi: str | None,
    existing: list[ExistingPaperKey],
) -> Classification:
    """Classify a candidate paper against a list of already-known papers.

    DOI match takes priority (near-zero false-positive rate) over title match
    (rare but real false positives, e.g. preprint vs. journal version with an
    identical title). Both default to "skip" but the caller/UI can override.
    """
    doi_norm = normalize_doi(doi)
    title_norm = normalize_title(title)

    if doi_norm:
        for existing_paper in existing:
            if existing_paper.doi_normalized == doi_norm:
                return Classification(
                    is_duplicate=True,
                    reason=DuplicateReason.DOI,
                    matched_paper_id=existing_paper.paper_id,
                    matched_title=existing_paper.title,
                    default_action="skip",
                )

    if title_norm:
        for existing_paper in existing:
            if existing_paper.title_normalized == title_norm:
                return Classification(
                    is_duplicate=True,
                    reason=DuplicateReason.TITLE,
                    matched_paper_id=existing_paper.paper_id,
                    matched_title=existing_paper.title,
                    default_action="skip",
                )

    return Classification(is_duplicate=False, default_action="add")


def classify_batch(
    rows: list[tuple[str, str | None]],
    existing: list[ExistingPaperKey],
) -> list[Classification]:
    """Classify a batch of (title, doi) rows, catching duplicates against both
    already-persisted papers AND earlier rows within the same batch."""
    results: list[Classification] = []
    running_existing = list(existing)
    for title, doi in rows:
        classification = classify(title, doi, running_existing)
        results.append(classification)
        running_existing.append(
            ExistingPaperKey(
                paper_id=-1,
                title=title,
                doi_normalized=normalize_doi(doi),
                title_normalized=normalize_title(title),
            )
        )
    return results
