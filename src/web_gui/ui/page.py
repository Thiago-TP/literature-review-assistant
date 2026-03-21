from __future__ import annotations

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
        if st.button("Export", use_container_width=True):
            controller.export_final()
            st.session_state.pending_download_action = "export_final"
    with col_quit:
        if st.button("Save and Quit",
                     type="primary",
                     use_container_width=True):
            controller.save_and_quit_feedback()
            st.session_state.pending_download_action = "save_and_quit"

    if (
        st.session_state.pending_download_action
        and st.session_state.last_exported_name
    ):
        payload = controller.get_export_file_data()
        if payload:
            st.markdown("Do you wish to download the generated output now?")
            col_yes, col_no = st.columns(2)
            with col_yes:
                st.download_button(
                    label="",
                    data=payload,
                    file_name=st.session_state.last_exported_name,
                    mime=(
                        "application/vnd.openxmlformats-officedocument."
                        "spreadsheetml.sheet"
                    ),
                    on_click=controller.queue_download_toasts,
                    args=(st.session_state.pending_download_action,),
                    use_container_width=True,
                    icon=":material/download:",
                )
            with col_no:
                if st.button(
                    "",
                    use_container_width=True,
                    icon=":material/close:",
                ):
                    st.session_state.pending_download_action = ""
                    st.rerun()


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
