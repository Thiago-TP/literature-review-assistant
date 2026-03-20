from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from review_web_gui import constants, controller  # noqa: E402


def _prepare_state() -> None:
    controller.st.session_state.clear()
    controller.st.session_state.dataset_key = "dataset_1"
    controller.st.session_state.labels = {
        column: [] for column in constants.LABEL_COLUMNS
    }
    controller.st.session_state.works_df = pd.DataFrame({"work_id": ["w1"]})
    controller.st.session_state.assignments_df = pd.DataFrame(
        {
            "work_id": ["w1"],
            constants.SCOPE_COLUMN: [constants.PENDING_DIAGNOSTIC],
            constants.METHODOLOGY_COLUMN: [constants.PENDING_DIAGNOSTIC],
            constants.CONTRIBUTION_COLUMN: [constants.PENDING_DIAGNOSTIC],
            constants.DIAGNOSTIC_COLUMN: [constants.PENDING_DIAGNOSTIC],
        }
    )
    controller.st.session_state.input_columns = []


def test_add_tag_returns_true_only_on_real_change(monkeypatch) -> None:
    _prepare_state()

    monkeypatch.setattr(controller.persistence, "save_labels",
                        lambda *args, **kwargs: None)

    assert controller.add_tag(constants.SCOPE_COLUMN, "Healthcare") is True
    assert controller.st.session_state.labels[constants.SCOPE_COLUMN] == [
        "Healthcare"
    ]
    assert controller.add_tag(constants.SCOPE_COLUMN, "Healthcare") is False
    assert controller.add_tag(constants.SCOPE_COLUMN, "") is False


def test_remove_tag_returns_true_only_when_tag_exists(monkeypatch) -> None:
    _prepare_state()
    controller.st.session_state.labels[constants.SCOPE_COLUMN] = ["Healthcare"]
    controller.st.session_state.assignments_df.loc[
        0,
        constants.SCOPE_COLUMN,
    ] = "Healthcare"

    monkeypatch.setattr(controller.persistence, "save_labels",
                        lambda *args, **kwargs: None)
    monkeypatch.setattr(controller.persistence, "save_temp_excel",
                        lambda *args, **kwargs: Path("/tmp/temp.xlsx"))

    assert controller.remove_tag(constants.SCOPE_COLUMN, "Healthcare") is True
    assert controller.st.session_state.labels[constants.SCOPE_COLUMN] == []
    assert controller.st.session_state.assignments_df.loc[
        0,
        constants.SCOPE_COLUMN,
    ] == constants.PENDING_DIAGNOSTIC
    assert controller.remove_tag(constants.SCOPE_COLUMN, "Healthcare") is False
    assert controller.remove_tag(constants.SCOPE_COLUMN, "") is False
