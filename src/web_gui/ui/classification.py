from __future__ import annotations

import streamlit as st

from web_gui import constants, controller
from web_gui.domain import safe_str


def render_dynamic_field(
    label_col: str,
    title: str,
    idx: int,
    options: list[str] | None = None,
) -> None:
    if options is None:
        tags = st.session_state.labels.get(label_col, [])
        options = [constants.PENDING_DIAGNOSTIC, *
                   [t for t in tags if t != constants.PENDING_DIAGNOSTIC]]

    current_value = safe_str(
        st.session_state.assignments_df.at[idx, label_col])
    if current_value not in options:
        current_value = constants.PENDING_DIAGNOSTIC

    st.markdown(
        f"<div class='modern-section'><strong>{title}</strong></div>",
        unsafe_allow_html=True)
    selected = st.radio(
        title,
        options=options,
        index=options.index(current_value),
        key=f"assign_{label_col}_{idx}",
        label_visibility="collapsed",
    )
    if selected != safe_str(st.session_state.assignments_df.at[idx, label_col]):  # noqa: E501
        controller.update_assignment(label_col, selected)


def render_classification() -> None:
    idx = st.session_state.current_index
    st.subheader("Classification")

    left1, right1 = st.columns(2, gap="small")
    with left1:
        render_dynamic_field(constants.SCOPE_COLUMN, "Application Scope", idx)
    with right1:
        render_dynamic_field(constants.CONTRIBUTION_COLUMN,
                             "Contribution Type",
                             idx,
                             options=constants.CONTRIBUTION_OPTIONS)

    left2, right2 = st.columns(2, gap="small")
    with left2:
        render_dynamic_field(constants.METHODOLOGY_COLUMN, "Methodology", idx)
    with right2:
        render_dynamic_field(constants.DIAGNOSTIC_COLUMN,
                             "Adherence",
                             idx,
                             options=constants.DIAGNOSTIC_OPTIONS)

    assigned = controller.current_work_assigned_count(
        st.session_state.assignments_df, idx)
    total = len(constants.LABEL_COLUMNS)
    st.progress(
        assigned / total if total else 0,
        text=f"Current work progress: {assigned}/{total} tags assigned",
    )
