from __future__ import annotations

from datetime import datetime
from pathlib import Path

import pandas as pd
import streamlit as st

from web_gui import constants, controller
from web_gui.domain import safe_str


def _render_navigation() -> None:
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


def _render_current_work() -> None:
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


def _render_dynamic_field(
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


def _clear_widget_value(widget_key: str) -> None:
    if widget_key in st.session_state:
        st.session_state[widget_key] = ""


def _clear_tag_management_fields(label_col: str, action: str) -> None:
    if action == "add":
        _clear_widget_value(f"new_tag_{label_col}")
    elif action == "rename":
        _clear_widget_value(f"rename_old_{label_col}")
        _clear_widget_value(f"rename_new_{label_col}")
    elif action == "remove":
        _clear_widget_value(f"remove_tag_select_{label_col}")


def _request_tag_management_clear(label_col: str, action: str) -> None:
    pending = st.session_state.setdefault("pending_tag_clears", [])
    if action == "add":
        pending.append((label_col, "add"))
    elif action == "rename":
        pending.append((label_col, "rename"))
    elif action == "remove":
        pending.append((label_col, "remove"))


def _apply_pending_tag_management_clears() -> None:
    pending = st.session_state.pop("pending_tag_clears", [])
    for label_col, action in pending:
        _clear_tag_management_fields(label_col, action)


def _handle_add_tag(label_col: str) -> None:
    new_tag = st.session_state.get(f"new_tag_{label_col}", "")
    if controller.add_tag(label_col, new_tag):
        _request_tag_management_clear(label_col, "add")
        controller.queue_toast(f"Tag added: {new_tag}")


def _handle_rename_tag(label_col: str) -> None:
    old_tag = st.session_state.get(f"rename_old_{label_col}", "")
    new_name = st.session_state.get(f"rename_new_{label_col}", "")
    if controller.rename_tag(label_col, old_tag, new_name):
        _request_tag_management_clear(label_col, "rename")
        controller.queue_toast(f"Tag renamed: {old_tag} -> {new_name}")


def _handle_remove_tag(label_col: str) -> None:
    remove_target = st.session_state.get(f"remove_tag_select_{label_col}", "")
    if controller.remove_tag(label_col, remove_target):
        _request_tag_management_clear(label_col, "remove")
        controller.queue_toast(f"Tag removed: {remove_target}")


def _render_classification() -> None:
    idx = st.session_state.current_index
    st.subheader("Classification")

    left1, right1 = st.columns(2, gap="small")
    with left1:
        _render_dynamic_field(constants.SCOPE_COLUMN, "Application Scope", idx)
    with right1:
        _render_dynamic_field(constants.CONTRIBUTION_COLUMN,
                              "Contribution Type",
                              idx,
                              options=constants.CONTRIBUTION_OPTIONS)

    left2, right2 = st.columns(2, gap="small")
    with left2:
        _render_dynamic_field(constants.METHODOLOGY_COLUMN, "Methodology", idx)
    with right2:
        _render_dynamic_field(constants.DIAGNOSTIC_COLUMN, "Adherence", idx)

    assigned = controller.current_work_assigned_count(
        st.session_state.assignments_df, idx)
    total = len(constants.LABEL_COLUMNS)
    st.progress(
        assigned / total if total else 0,
        text=f"Current work progress: {assigned}/{total} tags assigned",
    )


def _render_tag_management() -> None:
    st.subheader("Tag Management")
    editable_cols = [
        c
        for c in constants.LABEL_COLUMNS
        if c not in {constants.DIAGNOSTIC_COLUMN, constants.CONTRIBUTION_COLUMN}  # noqa: E501
    ]

    cols = st.columns(2, gap="small")
    for index, label_col in enumerate(editable_cols):
        with cols[index % 2]:
            with st.container(border=True):
                st.markdown(f"**{label_col} Tags**")
                tags = st.session_state.labels.get(label_col, [])

                add_col, add_btn_col = st.columns([3.5, 1])
                with add_col:
                    st.text_input(
                        f"Add tag for {label_col}",
                        key=f"new_tag_{label_col}",
                        label_visibility="collapsed",
                    )
                with add_btn_col:
                    st.button(
                        ":material/add:",
                        key=f"add_btn_{label_col}",
                        use_container_width=True,
                        on_click=_handle_add_tag,
                        args=(label_col,),
                    )

                rename_old_col, rename_new_col, rename_btn_col = st.columns(
                    [1.75, 1.75, 1]
                )
                with rename_old_col:
                    st.selectbox(
                        f"Tag to rename in {label_col}",
                        ["", *tags],
                        key=f"rename_old_{label_col}",
                        label_visibility="collapsed",
                    )
                with rename_new_col:
                    st.text_input(
                        f"New tag name in {label_col}",
                        key=f"rename_new_{label_col}",
                        label_visibility="collapsed",
                    )
                with rename_btn_col:
                    st.button(
                        ":material/edit:",
                        key=f"rename_btn_{label_col}",
                        use_container_width=True,
                        on_click=_handle_rename_tag,
                        args=(label_col,),
                    )

                rm_col, rm_btn_col = st.columns([3.5, 1])
                with rm_col:
                    st.selectbox(
                        f"Remove tag from {label_col}",
                        ["", *tags],
                        key=f"remove_tag_select_{label_col}",
                        label_visibility="collapsed",
                    )
                with rm_btn_col:
                    st.button(
                        ":material/delete:",
                        key=f"rm_btn_{label_col}",
                        use_container_width=True,
                        on_click=_handle_remove_tag,
                        args=(label_col,),
                    )


def main() -> None:
    st.set_page_config(page_title="Revisionator GUI", layout="wide")
    st.title("Literature Review Assistant")

    constants.RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    controller.init_state()
    controller.show_queued_toast()

    with st.sidebar:
        st.header("Dataset")
        uploaded_file = st.file_uploader(
            "Upload one Excel file",
            type=["xlsx", "xls"],
            accept_multiple_files=False,
        )

        if uploaded_file is not None:
            token = controller.build_upload_token(uploaded_file)
            if token != st.session_state.loaded_file_token:
                try:
                    controller.load_dataset_from_upload(uploaded_file)
                    st.session_state.loaded_file_token = token
                    st.success("File loaded successfully.")
                except Exception as exc:  # noqa: BLE001
                    st.error(f"Could not load file: {exc}")
        else:
            controller.reset_dataset_state()

        st.markdown("---")
        st.write(f"Temporary outputs are saved under: {constants.RESULTS_DIR}")
        if st.session_state.last_saved_path:
            stamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            st.caption(f"Autosaved at {stamp}")

    if st.session_state.works_df is None:
        st.info("Upload an Excel file from the sidebar to start reviewing.")
        return

    _render_navigation()

    col_left, col_right = st.columns([2, 1], gap="medium")
    with col_left:
        _render_current_work()
    with col_right:
        _render_classification()

    _apply_pending_tag_management_clears()
    _render_tag_management()


if __name__ == "__main__":
    main()
