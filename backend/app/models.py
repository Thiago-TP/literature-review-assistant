"""SQLModel ORM tables.

Replaces the old Streamlit app's `session_progress[i][field_name] = [strings]`
design with ID-based relations: renaming a field/tag no longer breaks existing
assignments, and deleting a field/option cascades cleanly.
"""

from datetime import datetime, timezone
from enum import Enum

from sqlalchemy import JSON, Column, Index, text
from sqlmodel import Field, Relationship, SQLModel


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


class PaperSource(str, Enum):
    XLSX_IMPORT = "xlsx_import"
    CROSSREF_DOI = "crossref_doi"
    CROSSREF_TITLE = "crossref_title"
    MANUAL = "manual"


class Project(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(unique=True, index=True)
    created_at: datetime = Field(default_factory=_utcnow)
    updated_at: datetime = Field(default_factory=_utcnow)
    last_viewed_paper_id: int | None = Field(
        default=None, foreign_key="paper.id", ondelete="SET NULL"
    )

    papers: list["Paper"] = Relationship(
        back_populates="project",
        sa_relationship_kwargs={
            "cascade": "all, delete-orphan",
            "foreign_keys": "Paper.project_id",
        },
    )
    fields_: list["TagField"] = Relationship(
        back_populates="project",
        sa_relationship_kwargs={"cascade": "all, delete-orphan"},
    )


class Paper(SQLModel, table=True):
    __table_args__ = (
        Index(
            "ix_paper_project_doi_normalized_unique",
            "project_id",
            "doi_normalized",
            unique=True,
            sqlite_where=text("doi_normalized IS NOT NULL"),
        ),
    )

    id: int | None = Field(default=None, primary_key=True)
    project_id: int = Field(foreign_key="project.id", ondelete="CASCADE", index=True)
    title: str
    abstract: str | None = None
    doi: str | None = None
    doi_normalized: str | None = Field(default=None, index=True)
    title_normalized: str = Field(index=True)
    authors: str | None = None
    year: int | None = None
    source_title: str | None = None
    notes: str = Field(default="")
    source: PaperSource = Field(default=PaperSource.MANUAL)
    raw_metadata: dict | list | None = Field(default=None, sa_column=Column(JSON))
    order_index: int = Field(default=0)
    created_at: datetime = Field(default_factory=_utcnow)

    project: Project = Relationship(
        back_populates="papers",
        sa_relationship_kwargs={"foreign_keys": "Paper.project_id"},
    )
    tag_assignments: list["TagAssignment"] = Relationship(
        back_populates="paper",
        sa_relationship_kwargs={"cascade": "all, delete-orphan"},
    )


class TagField(SQLModel, table=True):
    __table_args__ = (Index("ix_tagfield_project_name_unique", "project_id", "name", unique=True),)

    id: int | None = Field(default=None, primary_key=True)
    project_id: int = Field(foreign_key="project.id", ondelete="CASCADE", index=True)
    name: str
    is_protected: bool = Field(default=False)
    position: int = Field(default=0)

    project: Project = Relationship(back_populates="fields_")
    options: list["TagOption"] = Relationship(
        back_populates="field",
        sa_relationship_kwargs={"cascade": "all, delete-orphan"},
    )


class TagOption(SQLModel, table=True):
    __table_args__ = (Index("ix_tagoption_field_value_unique", "field_id", "value", unique=True),)

    id: int | None = Field(default=None, primary_key=True)
    field_id: int = Field(foreign_key="tagfield.id", ondelete="CASCADE", index=True)
    value: str
    position: int = Field(default=0)

    field: TagField = Relationship(back_populates="options")
    assignments: list["TagAssignment"] = Relationship(
        back_populates="tag_option",
        sa_relationship_kwargs={"cascade": "all, delete-orphan"},
    )


class TagAssignment(SQLModel, table=True):
    __table_args__ = (
        Index("ix_tagassignment_paper_option_unique", "paper_id", "tag_option_id", unique=True),
    )

    id: int | None = Field(default=None, primary_key=True)
    paper_id: int = Field(foreign_key="paper.id", ondelete="CASCADE", index=True)
    tag_option_id: int = Field(foreign_key="tagoption.id", ondelete="CASCADE", index=True)

    paper: Paper = Relationship(back_populates="tag_assignments")
    tag_option: TagOption = Relationship(back_populates="assignments")
