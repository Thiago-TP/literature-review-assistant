from __future__ import annotations

from typing import Any

import streamlit as st

from web_gui import controller


def _upload_token(uploaded_file: Any) -> str:
    """Build a stable token to detect when the user selected a new file."""
    return f"{uploaded_file.name}:{uploaded_file.size}"


def render_sidebar() -> None:
    st.header("Dataset")
    uploaded_file = st.file_uploader(
        "Upload one Excel file",
        type=["xlsx", "xls"],
        accept_multiple_files=False,
    )

    if uploaded_file is not None:
        token = _upload_token(uploaded_file)
        if st.session_state.loaded_file_token != token:
            try:
                controller.load_dataset_from_upload(uploaded_file)
                st.session_state.loaded_file_token = token
                st.success("File loaded successfully.")
            except Exception as exc:  # noqa: BLE001
                st.error(f"Could not load file: {exc}")
    else:
        controller.reset_dataset_state()
