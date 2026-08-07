"""Pydantic request/response DTOs for the API."""

from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import BaseModel

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


class TagOptionUpdate(BaseModel):
    value: str


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


class PaperUpdate(BaseModel):
    notes: str | None = None
    tags: dict[int, list[int]] | None = None


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
