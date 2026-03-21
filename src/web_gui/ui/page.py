from __future__ import annotations

from pathlib import Path

import pandas as pd
import streamlit as st

from web_gui import controller


def render_navigation() -> None:
    works_df: pd.DataFrame = st.session_state.works_df
    assignments_df: pd.DataFrame = st.session_state.assignments_df

    total = len(works_df)
    reviewed = controller.reviewed_count(assignments_df)
    ratio = reviewed / total if total else 0
    st.progress(
        ratio,
        text=f"Progress: {reviewed}/{total} works reviewed ({100 * ratio:.2f}%)",  # noqa: E501
    )

    col_prev, col_next, col_export, col_quit = st.columns(4)
    with col_prev:
        if st.button("Go to previous work", use_container_width=True):
            st.session_state.current_index = max(
                0, st.session_state.current_index - 1)
            st.rerun()
    with col_next:
        if st.button("Go to next work", use_container_width=True):
            st.session_state.current_index = min(
                total - 1, st.session_state.current_index + 1)
            st.rerun()
    with col_export:
        if st.button("Export Final", use_container_width=True):
            path = controller.export_final()
            st.success(f"Final export created: {path}")
    with col_quit:
        if st.button("Save and Quit",
                     type="primary",
                     use_container_width=True):
            path = controller.save_and_quit_feedback()
            st.success(f"Work saved to temporary file: {path}")
            st.info("You can now close this browser tab/window.")

    if st.session_state.last_exported_path:
        payload = controller.get_export_file_data()
        if payload:
            st.download_button(
                label="Download Final Export",
                data=payload,
                file_name=Path(st.session_state.last_exported_path).name,
                mime=(
                    "application/vnd.openxmlformats-officedocument."
                    "spreadsheetml.sheet"
                ),
                use_container_width=True,
            )


def render_current_work() -> None:
    works_df: pd.DataFrame = st.session_state.works_df
    idx = st.session_state.current_index
    row = works_df.iloc[idx]

    st.subheader(f"Work {idx + 1} of {len(works_df)}")
    st.markdown(f"**Title:** {row['title'] or '(missing)'}")
    st.markdown("**Abstract:**")
    st.write(row["abstract"] or "(missing)")
    st.markdown(f"**Authors:** {row['authors'] or '(missing)'}")
    st.markdown(f"**Journal:** {row['journal'] or '(missing)'}")
    st.markdown(f"**Date:** {row['date'] or '(missing)'}")
