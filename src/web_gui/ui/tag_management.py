from __future__ import annotations

import streamlit as st

from web_gui import constants, controller


def clear_widget_value(widget_key: str) -> None:
    if widget_key in st.session_state:
        st.session_state[widget_key] = ""


def clear_tag_management_fields(label_col: str, action: str) -> None:
    if action == "add":
        clear_widget_value(f"new_tag_{label_col}")
    elif action == "rename":
        clear_widget_value(f"rename_old_{label_col}")
        clear_widget_value(f"rename_new_{label_col}")
    elif action == "remove":
        clear_widget_value(f"remove_tag_select_{label_col}")


def request_tag_management_clear(label_col: str, action: str) -> None:
    pending = st.session_state.setdefault("pending_tag_clears", [])
    if action == "add":
        pending.append((label_col, "add"))
    elif action == "rename":
        pending.append((label_col, "rename"))
    elif action == "remove":
        pending.append((label_col, "remove"))


def apply_pending_tag_management_clears() -> None:
    pending = st.session_state.pop("pending_tag_clears", [])
    for label_col, action in pending:
        clear_tag_management_fields(label_col, action)


def handle_add_tag(label_col: str) -> None:
    new_tag = st.session_state.get(f"new_tag_{label_col}", "")
    if controller.add_tag(label_col, new_tag):
        request_tag_management_clear(label_col, "add")
        controller.queue_toast(f"Tag added: {new_tag}")


def handle_rename_tag(label_col: str) -> None:
    old_tag = st.session_state.get(f"rename_old_{label_col}", "")
    new_name = st.session_state.get(f"rename_new_{label_col}", "")
    if controller.rename_tag(label_col, old_tag, new_name):
        request_tag_management_clear(label_col, "rename")
        controller.queue_toast(f"Tag renamed: {old_tag} -> {new_name}")


def handle_remove_tag(label_col: str) -> None:
    remove_target = st.session_state.get(f"remove_tag_select_{label_col}", "")
    if controller.remove_tag(label_col, remove_target):
        request_tag_management_clear(label_col, "remove")
        controller.queue_toast(f"Tag removed: {remove_target}")


def render_tag_management() -> None:
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
                        on_click=handle_add_tag,
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
                        on_click=handle_rename_tag,
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
                        on_click=handle_remove_tag,
                        args=(label_col,),
                    )
