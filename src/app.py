from __future__ import annotations

import streamlit as st

from web_gui import constants, controller
from web_gui.ui import classification as classification_ui
from web_gui.ui import page as page_ui
from web_gui.ui import sidebar as sidebar_ui
from web_gui.ui import tag_management as tag_management_ui


def main() -> None:
    st.set_page_config(page_title="Revisionator GUI", layout="wide")
    st.title("Literature Review Assistant")

    constants.RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    controller.init_state()
    controller.show_queued_toast()

    with st.sidebar:
        sidebar_ui.render_sidebar()

    if st.session_state.works_df is None:
        st.info("Upload an Excel file from the sidebar to start reviewing.")
        return

    page_ui.render_navigation()

    col_left, col_right = st.columns([2, 1], gap="medium")
    with col_left:
        page_ui.render_current_work()
    with col_right:
        classification_ui.render_classification()

    tag_management_ui.apply_pending_tag_management_clears()
    tag_management_ui.render_tag_management()


if __name__ == "__main__":
    main()
