from __future__ import annotations

import streamlit as st

from web_gui import controller


def render_sidebar() -> None:
    st.header("Dataset")
    uploaded_file = st.file_uploader(
        "Upload one Excel file",
        type=["xlsx", "xls"],
        accept_multiple_files=False,
    )

    if uploaded_file is not None:
        try:
            controller.load_dataset_from_upload(uploaded_file)
            st.success("File loaded successfully.")
        except Exception as exc:  # noqa: BLE001
            st.error(f"Could not load file: {exc}")
    else:
        controller.reset_dataset_state()
