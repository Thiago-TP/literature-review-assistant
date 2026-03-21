from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd
import streamlit as st
import tomllib

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

import app  # noqa: E402
from web_gui import constants  # noqa: E402
from web_gui.ui import classification, tag_management  # noqa: E402


class _DummyContext:
    def __enter__(self) -> _DummyContext:
        return self

    def __exit__(self, exc_type, exc, tb) -> bool:
        return False


def _prepare_state(value: str) -> None:
    st.session_state.clear()
    st.session_state.current_index = 0
    st.session_state.labels = {column: []
                               for column in constants.LABEL_COLUMNS}
    st.session_state.assignments_df = pd.DataFrame(
        {
            constants.SCOPE_COLUMN: [constants.PENDING_DIAGNOSTIC],
            constants.METHODOLOGY_COLUMN: [constants.PENDING_DIAGNOSTIC],
            constants.CONTRIBUTION_COLUMN: [value],
            constants.DIAGNOSTIC_COLUMN: [constants.PENDING_DIAGNOSTIC],
        }
    )


def test_classification_uses_fixed_contribution_and_diagnostic_options(
    monkeypatch,
) -> None:
    _prepare_state(constants.PENDING_DIAGNOSTIC)

    captured: list[tuple[str, str, int, list[str] | None]] = []

    def fake_render_dynamic_field(label_col: str,
                                  title: str,
                                  idx: int,
                                  options: list[str] | None = None) -> None:
        captured.append((label_col, title, idx, options))

    monkeypatch.setattr(classification, "render_dynamic_field",
                        fake_render_dynamic_field)
    monkeypatch.setattr(classification.st, "subheader",
                        lambda *args, **kwargs: None)
    monkeypatch.setattr(
        classification.st,
        "columns",
        lambda *args, **kwargs: [_DummyContext(), _DummyContext()],
    )
    monkeypatch.setattr(classification.st, "progress",
                        lambda *args, **kwargs: None)

    classification.render_classification()

    contribution_call = next(
        call for call in captured if call[0] == constants.CONTRIBUTION_COLUMN
    )
    assert contribution_call[1] == "Contribution Type"
    assert contribution_call[3] == constants.CONTRIBUTION_OPTIONS

    diagnostic_call = next(
        call for call in captured if call[0] == constants.DIAGNOSTIC_COLUMN
    )
    assert diagnostic_call[1] == "Adherence"
    assert diagnostic_call[3] == constants.DIAGNOSTIC_OPTIONS


def test_dynamic_field_falls_back_to_pending_for_invalid_value(
    monkeypatch,
) -> None:
    _prepare_state("Legacy value")

    radio_calls: list[dict[str, object]] = []
    update_calls: list[tuple[str, str]] = []

    def fake_radio(label: str, *, options: list[str], index: int, **kwargs):
        radio_calls.append(
            {"label": label, "options": options, "index": index})
        return options[index]

    def fake_update_assignment(label_col: str, selected_tag: str) -> None:
        update_calls.append((label_col, selected_tag))

    monkeypatch.setattr(classification.st, "markdown",
                        lambda *args, **kwargs: None)
    monkeypatch.setattr(classification.st, "radio", fake_radio)
    monkeypatch.setattr(classification.controller, "update_assignment",
                        fake_update_assignment)

    classification.render_dynamic_field(
        constants.CONTRIBUTION_COLUMN,
        "Contribution Type",
        0,
        options=constants.CONTRIBUTION_OPTIONS,
    )

    assert radio_calls == [
        {
            "label": "Contribution Type",
            "options": constants.CONTRIBUTION_OPTIONS,
            "index": 0,
        }
    ]
    assert update_calls == [(constants.CONTRIBUTION_COLUMN,
                             constants.PENDING_DIAGNOSTIC)]


def test_clear_tag_management_fields_only_clears_related_inputs() -> None:
    st.session_state.clear()
    st.session_state["new_tag_Application Scope"] = "new scope"
    st.session_state["rename_old_Application Scope"] = "old scope"
    st.session_state["rename_new_Application Scope"] = "new name"
    st.session_state["remove_tag_select_Application Scope"] = "remove me"
    st.session_state.unrelated_control = "keep"

    tag_management.clear_tag_management_fields(constants.SCOPE_COLUMN, "add")
    assert st.session_state["new_tag_Application Scope"] == ""
    assert st.session_state["rename_old_Application Scope"] == "old scope"
    assert st.session_state["rename_new_Application Scope"] == "new name"
    assert st.session_state[
        "remove_tag_select_Application Scope"
    ] == "remove me"
    assert st.session_state.unrelated_control == "keep"

    tag_management.clear_tag_management_fields(
        constants.SCOPE_COLUMN, "rename")
    assert st.session_state["rename_old_Application Scope"] == ""
    assert st.session_state["rename_new_Application Scope"] == ""

    tag_management.clear_tag_management_fields(
        constants.SCOPE_COLUMN, "remove")
    assert st.session_state["remove_tag_select_Application Scope"] == ""


def test_main_orchestrates_ui_modules(monkeypatch) -> None:
    st.session_state.clear()
    st.session_state.works_df = pd.DataFrame(
        {
            "title": ["Paper"],
            "abstract": ["Abstract"],
            "authors": ["A"],
            "journal": ["J"],
            "date": ["2026"],
        }
    )
    st.session_state.assignments_df = pd.DataFrame(
        {
            constants.SCOPE_COLUMN: [constants.PENDING_DIAGNOSTIC],
            constants.METHODOLOGY_COLUMN: [constants.PENDING_DIAGNOSTIC],
            constants.CONTRIBUTION_COLUMN: [constants.PENDING_DIAGNOSTIC],
            constants.DIAGNOSTIC_COLUMN: [constants.PENDING_DIAGNOSTIC],
        }
    )
    st.session_state.current_index = 0
    st.session_state.labels = {column: []
                               for column in constants.LABEL_COLUMNS}
    st.session_state.last_saved_path = ""
    st.session_state.last_exported_path = ""
    st.session_state.loaded_file_token = ""
    st.session_state.dataset_key = ""
    st.session_state.input_columns = []

    calls: list[str] = []

    class _SidebarContext:
        def __enter__(self) -> _SidebarContext:
            return self

        def __exit__(self, exc_type, exc, tb) -> bool:
            return False

    monkeypatch.setattr(app.st, "set_page_config",
                        lambda *args, **kwargs: None)
    monkeypatch.setattr(app.st, "title", lambda *args, **kwargs: None)
    monkeypatch.setattr(app.st, "sidebar", _SidebarContext())
    monkeypatch.setattr(app.st, "columns", lambda *args, **
                        kwargs: [_DummyContext(), _DummyContext()])
    monkeypatch.setattr(app.controller, "init_state", lambda: None)
    monkeypatch.setattr(app.controller, "show_queued_toast", lambda: None)
    monkeypatch.setattr(app.sidebar_ui, "render_sidebar",
                        lambda: calls.append("sidebar"))
    monkeypatch.setattr(app.page_ui, "render_navigation",
                        lambda: calls.append("navigation"))
    monkeypatch.setattr(app.page_ui, "render_current_work",
                        lambda: calls.append("current_work"))
    monkeypatch.setattr(app.classification_ui, "render_classification",
                        lambda: calls.append("classification"))
    monkeypatch.setattr(app.tag_management_ui, "apply_pending_tag_management_clears",
                        lambda: calls.append("apply_clears"))
    monkeypatch.setattr(app.tag_management_ui, "render_tag_management",
                        lambda: calls.append("tag_management"))
    monkeypatch.setattr(app.st, "info", lambda *args, **kwargs: None)

    app.main()

    assert calls == [
        "sidebar",
        "navigation",
        "current_work",
        "classification",
        "apply_clears",
        "tag_management",
    ]


def test_streamlit_theme_config_defines_light_and_dark_palettes() -> None:
    config_path = ROOT / ".streamlit" / "config.toml"
    data = tomllib.loads(config_path.read_text(encoding="utf-8"))

    theme = data["theme"]
    assert theme["light"]["backgroundColor"] == "#f6f1e8"
    assert theme["dark"]["backgroundColor"] == "#0f172a"
