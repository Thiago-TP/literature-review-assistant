from __future__ import annotations

from datetime import datetime

import streamlit as st

from web_gui import constants, controller


def render_sidebar() -> None:
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
