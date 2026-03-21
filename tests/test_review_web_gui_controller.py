from __future__ import annotations

import sys
from io import BytesIO
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from web_gui import constants, controller  # noqa: E402


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


def test_init_state_sets_pending_action_and_toast_queue_defaults() -> None:
    controller.st.session_state.clear()

    controller.init_state()

    assert controller.st.session_state.pending_download_action == ""
    assert controller.st.session_state.queued_toasts == []


def _build_excel_bytes(df: pd.DataFrame) -> bytes:
    buffer = BytesIO()
    df.to_excel(buffer, index=False)
    return buffer.getvalue()


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

    assert controller.remove_tag(constants.SCOPE_COLUMN, "Healthcare") is True
    assert controller.st.session_state.labels[constants.SCOPE_COLUMN] == []
    assert controller.st.session_state.assignments_df.loc[
        0,
        constants.SCOPE_COLUMN,
    ] == constants.PENDING_DIAGNOSTIC
    assert controller.remove_tag(constants.SCOPE_COLUMN, "Healthcare") is False
    assert controller.remove_tag(constants.SCOPE_COLUMN, "") is False


def test_export_final_generates_in_memory_download(monkeypatch) -> None:
    _prepare_state()
    controller.st.session_state.input_columns = ["Title"]
    controller.st.session_state.works_df = pd.DataFrame({
        "work_id": ["w1"],
        "Title": ["Paper A"],
    })

    monkeypatch.setattr(
        controller.persistence,
        "build_output_excel_bytes",
        lambda *args, **kwargs: _build_excel_bytes(
            pd.DataFrame({"Title": ["Paper A"]})),
    )

    filename = controller.export_final()

    assert filename.startswith("dataset_1_review_final_")
    assert filename.endswith(".xlsx")
    assert controller.st.session_state.last_exported_name == filename
    assert controller.st.session_state.last_exported_bytes


def test_save_and_quit_feedback_generates_in_memory_download(
    monkeypatch,
) -> None:
    _prepare_state()
    controller.st.session_state.input_columns = ["Title"]
    controller.st.session_state.works_df = pd.DataFrame({
        "work_id": ["w1"],
        "Title": ["Paper A"],
    })

    monkeypatch.setattr(
        controller.persistence,
        "build_output_excel_bytes",
        lambda *args, **kwargs: _build_excel_bytes(
            pd.DataFrame({"Title": ["Paper A"]})),
    )

    filename = controller.save_and_quit_feedback()

    assert filename.startswith("dataset_1_review_final_")
    assert filename.endswith(".xlsx")
    assert controller.st.session_state.last_exported_name == filename
    assert controller.st.session_state.last_exported_bytes


def test_show_queued_toast_flushes_all_toasts_in_order(monkeypatch) -> None:
    _prepare_state()
    controller.st.session_state.queued_toasts = [
        {"message": "first", "icon": ":material/check_circle:"},
        {"message": "second", "icon": ":material/info:"},
    ]
    calls: list[tuple[str, str]] = []

    monkeypatch.setattr(
        controller.st,
        "toast",
        lambda message, icon=None: calls.append((message, icon)),
    )

    controller.show_queued_toast()

    assert calls == [
        ("first", ":material/check_circle:"),
        ("second", ":material/info:"),
    ]
    assert controller.st.session_state.queued_toasts == []
