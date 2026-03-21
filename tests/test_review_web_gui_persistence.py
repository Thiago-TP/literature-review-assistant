from __future__ import annotations

import re
import sys
from io import BytesIO
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from web_gui import constants, persistence  # noqa: E402


def test_save_then_load_labels_normalizes_and_sorts(tmp_path: Path) -> None:
    labels = {
        constants.SCOPE_COLUMN: ["  Industry", "industry", "Healthcare"],
        constants.METHODOLOGY_COLUMN: ["ML", "", "ML"],
        constants.CONTRIBUTION_COLUMN: [],
        constants.DIAGNOSTIC_COLUMN: [],
    }

    persistence.save_labels("dataset_1", labels, tmp_path)
    loaded = persistence.load_labels("dataset_1", tmp_path)

    assert loaded[constants.SCOPE_COLUMN] == [
        "Healthcare", "Industry", "industry"]
    assert loaded[constants.METHODOLOGY_COLUMN] == ["ML"]


def test_temp_and_final_paths_follow_contract(tmp_path: Path) -> None:
    temp = persistence.temp_results_path("base_key", tmp_path)
    final = persistence.final_results_path("base_key", tmp_path)

    assert temp.name == "base_key_tmp_review.xlsx"
    assert re.match(r"^base_key_review_final_\d{8}_\d{6}\.xlsx$", final.name)


def test_build_output_excel_bytes_keeps_input_columns_plus_classification(
) -> None:
    works = pd.DataFrame(
        {
            "Title": ["Paper 1", "Paper 2"],
            "Abstract": ["A", "B"],
            "work_id": ["w1", "w2"],
        }
    )
    assignments = pd.DataFrame(
        {
            "work_id": ["w1", "w2"],
            constants.SCOPE_COLUMN: ["Scope A", "Scope B"],
            constants.METHODOLOGY_COLUMN: ["Method A", "Method B"],
            constants.CONTRIBUTION_COLUMN: ["Review", "Improvement"],
            constants.DIAGNOSTIC_COLUMN: ["Partial", "Sufficient"],
        }
    )

    payload = persistence.build_output_excel_bytes(
        works_df=works,
        assignments_df=assignments,
        input_columns=["Title", "Abstract"],
    )

    saved = pd.read_excel(BytesIO(payload))

    assert list(saved.columns) == [
        "Title",
        "Abstract",
        constants.SCOPE_COLUMN,
        constants.METHODOLOGY_COLUMN,
        constants.CONTRIBUTION_COLUMN,
        constants.DIAGNOSTIC_COLUMN,
    ]
    assert saved.loc[1, constants.DIAGNOSTIC_COLUMN] == "Sufficient"


def test_load_labels_returns_default_when_file_absent(tmp_path: Path) -> None:
    loaded = persistence.load_labels("missing", tmp_path)

    assert loaded == {column: [] for column in constants.LABEL_COLUMNS}
