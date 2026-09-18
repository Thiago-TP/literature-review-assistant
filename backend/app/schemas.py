"""Pydantic request/response DTOs for the API."""

from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field

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


class LastViewedUpdate(BaseModel):
    paper_id: int


# ---- Tag fields / options ------------------------------------------------


class TagOptionRead(BaseModel):
    id: int
    value: str
    position: int
    weight: float
    children: list[TagOptionRead] = []


TagOptionRead.model_rebuild()


class TagFieldRead(BaseModel):
    id: int
    name: str
    is_protected: bool
    position: int
    options: list[TagOptionRead]


class TagFieldCreate(BaseModel):
    name: str


class TagFieldUpdate(BaseModel):
    name: str


class TagOptionCreate(BaseModel):
    value: str
    parent_option_id: int | None = None
    weight: float = Field(default=0, ge=0, le=5, multiple_of=0.5)


class TagOptionUpdate(BaseModel):
    value: str | None = None
    weight: float | None = Field(default=None, ge=0, le=5, multiple_of=0.5)


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


class PaperUpdate(BaseModel):
    notes: str | None = None
    tags: dict[int, list[int]] | None = None


class RatingUpdate(BaseModel):
    rating: float = Field(ge=0.5, le=5, multiple_of=0.5)


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
    tag_distribution: list[TagDistributionEntry]
    top_papers: list[PaperListItem]
