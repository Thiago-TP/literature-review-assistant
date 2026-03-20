from __future__ import annotations

import sys
from io import BytesIO
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from review_web_gui import constants, domain  # noqa: E402


class UploadedExcel(BytesIO):
    def __init__(self, payload: bytes, name: str) -> None:
        super().__init__(payload)
        self.name = name
        self.size = len(payload)


def _build_excel_bytes(df: pd.DataFrame) -> bytes:
    buffer = BytesIO()
    df.to_excel(buffer, index=False)
    return buffer.getvalue()


def test_read_uploaded_excel_maps_canonical_fields_and_work_id() -> None:
    raw = pd.DataFrame(
        {
            "Title": ["Paper A"],
            "Authors": ["Alice, Bob"],
            "Source title": ["Sensors"],
            "Year": [2025],
            "Abstract": ["A short abstract."],
        }
    )
    uploaded = UploadedExcel(_build_excel_bytes(raw), "dataset.xlsx")

    adapted, input_cols = domain.read_uploaded_excel(uploaded)

    assert input_cols == ["Title", "Authors",
                          "Source title", "Year", "Abstract"]
    assert adapted.loc[0, "title"] == "Paper A"
    assert adapted.loc[0, "authors"] == "Alice, Bob"
    assert adapted.loc[0, "journal"] == "Sensors"
    assert adapted.loc[0, "date"] == "2025"
    assert adapted.loc[0, "abstract"] == "A short abstract."
    assert adapted.loc[0, "source_file"] == "dataset.xlsx"
    assert adapted.loc[0, "source_row"] == 1
    assert adapted.loc[0, "work_id"] == "dataset.xlsx::1::paper a"


def test_merge_existing_assignments_prefers_work_id_match(tmp_path: Path) -> None:  # noqa: E501
    base = pd.DataFrame(
        {
            "work_id": ["file::1::a", "file::2::b"],
            constants.SCOPE_COLUMN: [constants.PENDING_DIAGNOSTIC] * 2,
            constants.METHODOLOGY_COLUMN: [constants.PENDING_DIAGNOSTIC] * 2,
            constants.CONTRIBUTION_COLUMN: [constants.PENDING_DIAGNOSTIC] * 2,
            constants.DIAGNOSTIC_COLUMN: [constants.PENDING_DIAGNOSTIC] * 2,
        }
    )
    previous = pd.DataFrame(
        {
            "work_id": ["file::1::a"],
            constants.SCOPE_COLUMN: ["Industrial"],
            constants.DIAGNOSTIC_COLUMN: ["Sufficient"],
        }
    )
    old_path = tmp_path / "old.xlsx"
    previous.to_excel(old_path, index=False)

    merged = domain.merge_existing_assignments(base, old_path)

    assert merged.loc[0, constants.SCOPE_COLUMN] == "Industrial"
    assert merged.loc[0, constants.DIAGNOSTIC_COLUMN] == "Sufficient"
    assert merged.loc[1,
                      constants.SCOPE_COLUMN] == constants.PENDING_DIAGNOSTIC


def test_merge_existing_assignments_falls_back_to_row_order(tmp_path: Path) -> None:  # noqa: E501
    base = pd.DataFrame(
        {
            "work_id": ["w1", "w2"],
            constants.SCOPE_COLUMN: [constants.PENDING_DIAGNOSTIC] * 2,
            constants.METHODOLOGY_COLUMN: [constants.PENDING_DIAGNOSTIC] * 2,
            constants.CONTRIBUTION_COLUMN: [constants.PENDING_DIAGNOSTIC] * 2,
            constants.DIAGNOSTIC_COLUMN: [constants.PENDING_DIAGNOSTIC] * 2,
        }
    )
    previous = pd.DataFrame(
        {
            constants.SCOPE_COLUMN: ["Domain A", "Domain B"],
            constants.METHODOLOGY_COLUMN: ["Method A", "Method B"],
            constants.CONTRIBUTION_COLUMN: ["Improvement", "Review"],
            constants.DIAGNOSTIC_COLUMN: ["Partial", "Sufficient"],
        }
    )
    old_path = tmp_path / "legacy.xlsx"
    previous.to_excel(old_path, index=False)

    merged = domain.merge_existing_assignments(base, old_path)

    assert list(merged[constants.SCOPE_COLUMN]) == ["Domain A", "Domain B"]
    assert list(merged[constants.DIAGNOSTIC_COLUMN]) == [
        "Partial", "Sufficient"]


def test_clean_deleted_tags_resets_dynamic_labels_only() -> None:
    assignments = pd.DataFrame(
        {
            "work_id": ["w1"],
            constants.SCOPE_COLUMN: ["Removed Scope"],
            constants.METHODOLOGY_COLUMN: ["Method X"],
            constants.CONTRIBUTION_COLUMN: ["UnexpectedValue"],
            constants.DIAGNOSTIC_COLUMN: ["UnexpectedValue"],
        }
    )
    labels = {
        constants.SCOPE_COLUMN: ["In scope"],
        constants.METHODOLOGY_COLUMN: ["Method Y"],
        constants.CONTRIBUTION_COLUMN: [],
        constants.DIAGNOSTIC_COLUMN: [],
    }

    cleaned = domain.clean_deleted_tags(assignments, labels)

    assert cleaned.loc[0,
                       constants.SCOPE_COLUMN] == constants.PENDING_DIAGNOSTIC
    assert cleaned.loc[0,
                       constants.METHODOLOGY_COLUMN] == constants.PENDING_DIAGNOSTIC  # noqa: E501
    assert cleaned.loc[0, constants.CONTRIBUTION_COLUMN] == "UnexpectedValue"
    assert cleaned.loc[0, constants.DIAGNOSTIC_COLUMN] == "UnexpectedValue"


def test_rename_tag_in_state_updates_labels_and_assignments() -> None:
    labels = {
        constants.SCOPE_COLUMN: ["Healthcare", "Industry"],
        constants.METHODOLOGY_COLUMN: ["ML"],
        constants.CONTRIBUTION_COLUMN: [],
        constants.DIAGNOSTIC_COLUMN: [],
    }
    assignments = pd.DataFrame(
        {
            "work_id": ["w1", "w2"],
            constants.SCOPE_COLUMN: ["Healthcare", "Industry"],
            constants.METHODOLOGY_COLUMN: [constants.PENDING_DIAGNOSTIC] * 2,
            constants.CONTRIBUTION_COLUMN: [constants.PENDING_DIAGNOSTIC] * 2,
            constants.DIAGNOSTIC_COLUMN: [constants.PENDING_DIAGNOSTIC] * 2,
        }
    )

    changed, next_labels, next_assignments = domain.rename_tag_in_state(
        labels,
        assignments,
        constants.SCOPE_COLUMN,
        "Healthcare",
        "Health",
    )

    assert changed is True
    assert next_labels[constants.SCOPE_COLUMN] == ["Health", "Industry"]
    assert list(next_assignments[constants.SCOPE_COLUMN]) == [
        "Health", "Industry"]
