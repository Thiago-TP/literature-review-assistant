"""Pydantic request/response DTOs for the API."""

from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field

from app.constants import MAX_RATING
from app.models import PaperSource

# ---- Projects ----------------------------------------------------------


class ProjectCreate(BaseModel):
    name: str


class ProjectUpdate(BaseModel):
    name: str | None = None


class ProjectRead(BaseModel):
    id: int
    name: str
    created_at: datetime
    updated_at: datetime
    last_viewed_paper_id: int | None
    paper_count: int
    # How much of the review plan is written, so the project list can badge an
    # unfinished one without a second request per review.
    plan_filled: int
    plan_total: int


class LastViewedUpdate(BaseModel):
    paper_id: int


# ---- Tag fields / options ------------------------------------------------


class TagOptionRead(BaseModel):
    id: int
    value: str
    position: int
    weight: float
    description: str | None = None
    children: list[TagOptionRead] = []


TagOptionRead.model_rebuild()


class TagFieldRead(BaseModel):
    id: int
    name: str
    is_protected: bool
    position: int
    description: str | None = None
    options: list[TagOptionRead]


class TagFieldCreate(BaseModel):
    name: str


class TagFieldUpdate(BaseModel):
    """`name` is optional because a protected field can be described even
    though it cannot be renamed, so a description-only PATCH has to be a
    legal request."""

    name: str | None = None
    description: str | None = None


class TagOptionCreate(BaseModel):
    value: str
    parent_option_id: int | None = None
    weight: float = Field(default=0, ge=0, le=5, multiple_of=0.5)


class TagOptionUpdate(BaseModel):
    value: str | None = None
    weight: float | None = Field(default=None, ge=0, le=5, multiple_of=0.5)
    description: str | None = None


# ---- Review plan ---------------------------------------------------------


class ReviewPlanUpdate(BaseModel):
    """Every section optional: the page saves one box at a time, as it loses
    focus, and must not blank the others on the way through."""

    purpose: str | None = None
    scope: str | None = None
    search: str | None = None
    weights: str | None = None
    other: str | None = None


class ReviewPlanRead(BaseModel):
    project_id: int
    project_name: str
    purpose: str | None
    scope: str | None
    search: str | None
    weights: str | None
    other: str | None
    # The review's live fields and tags, carrying their descriptions, so the
    # plan page renders its generated sections from this one response.
    fields: list[TagFieldRead]
    filled: int
    total: int


# ---- Papers --------------------------------------------------------------


class PaperListItem(BaseModel):
    id: int
    title: str
    doi: str | None
    authors: str | None
    year: int | None
    order_index: int
    filled_field_count: int
    total_field_count: int
    notes: str
    rating: float | None
    score: float


class HighlightRead(BaseModel):
    id: str
    field: Literal["title", "abstract"]
    start: int
    end: int


class HighlightCreate(BaseModel):
    field: Literal["title", "abstract"]
    start: int = Field(ge=0)
    end: int = Field(ge=1)


class PaperDetail(BaseModel):
    id: int
    project_id: int
    title: str
    abstract: str | None
    doi: str | None
    authors: str | None
    year: int | None
    source_title: str | None
    notes: str
    source: PaperSource
    order_index: int
    tags: dict[int, list[int]]
    rating: float | None
    score: float
    highlights: list[HighlightRead]


class PaperUpdate(BaseModel):
    notes: str | None = None
    tags: dict[int, list[int]] | None = None


class RatingUpdate(BaseModel):
    rating: float = Field(ge=0.5, le=MAX_RATING, multiple_of=0.5)


class PaperCreate(BaseModel):
    title: str
    abstract: str | None = None
    doi: str | None = None
    authors: str | None = None
    year: int | None = None
    source_title: str | None = None
    source: PaperSource = PaperSource.MANUAL
    raw_metadata: dict | None = None
    force: bool = False


class DuplicateInfo(BaseModel):
    is_duplicate: bool
    reason: Literal["doi", "title"] | None = None
    matched_paper_id: int | None = None
    matched_title: str | None = None


class PaperCreateResult(BaseModel):
    paper: PaperDetail | None = None
    duplicate: DuplicateInfo | None = None


# ---- Bulk xlsx import -----------------------------------------------------


class ImportPreviewRow(BaseModel):
    row_index: int
    title: str
    abstract: str | None
    doi: str | None
    authors: str | None
    year: int | None
    source_title: str | None
    raw_metadata: dict
    is_duplicate: bool
    duplicate_reason: Literal["doi", "title"] | None
    matched_paper_id: int | None
    matched_title: str | None
    default_action: Literal["add", "skip"]


class ImportPreviewResponse(BaseModel):
    rows: list[ImportPreviewRow]
    new_count: int
    duplicate_count: int


class ImportCommitRequest(BaseModel):
    rows: list[ImportPreviewRow]
    actions: dict[int, Literal["add", "skip"]]  # row_index -> action


class ImportCommitResponse(BaseModel):
    added_count: int
    skipped_count: int
    paper_ids: list[int]


# ---- CrossRef lookup -------------------------------------------------------


class LookupDoiRequest(BaseModel):
    doi: str


class LookupTitleRequest(BaseModel):
    title: str


class LookupCandidate(BaseModel):
    title: str
    doi: str | None
    abstract: str | None
    abstract_available: bool
    authors: str | None
    year: int | None
    source_title: str | None
    score: float | None
    raw_metadata: dict
    duplicate: DuplicateInfo


class LookupDoiResponse(BaseModel):
    candidate: LookupCandidate


class LookupTitleResponse(BaseModel):
    candidates: list[LookupCandidate]


# ---- Dashboard -------------------------------------------------------------


class TagDistributionEntry(BaseModel):
    field_id: int
    field_name: str
    option_id: int
    option_path: str
    weight: float
    count: int


class DashboardStats(BaseModel):
    total_papers: int
    fully_tagged_count: int
    rated_count: int
    with_notes_count: int
    average_rating: float | None
    average_score: float
    # The scale each average is read against. Rating has a fixed ceiling;
    # score does not -- it is the sum of a paper's tag weights plus its
    # rating -- so the best score in the project stands in for one.
    max_rating: float
    max_score: float
    tag_distribution: list[TagDistributionEntry]
    top_papers: list[PaperListItem]
