"""
Cleanest most stable version of the app I could make.
First all widgets are created, then all callbacks are defined, then the main logic is executed.
"""

from __future__ import annotations

from io import BytesIO

import pandas as pd
import streamlit as st

from constants import (
    ABSTRACT_COLUMN,
    DOI_COLUMN,
    NOTE_COLUMN,
    REQUIRED_FIELDS,
    TITLE_COLUMN,
)

# Useful variables to introduce in session state:
# - current_work_index: int, index of the work currently being displayed
# - works_df: pd.DataFrame, dataframe containing the works and their details
# - tags: dict, mapping from field names to lists of tags options of that field
if "current_work_index" not in st.session_state:
    st.session_state.current_work_index = 0

if "works_df" not in st.session_state:
    st.session_state.works_df = None

if "tags" not in st.session_state:
    st.session_state.tags = REQUIRED_FIELDS.copy()


def main() -> None:
    """Main function with logic for the app."""

    # debug
    if st.session_state.works_df is not None:
        st.dataframe(st.session_state.works_df[list(REQUIRED_FIELDS.keys())])

    _display_app()


def _display_app() -> None:
    """Displays the app's main content based on the uploaded file."""

    _header_and_sidebar()

    if st.session_state.get("file_uploader") is None:
        st.info("Please upload an Excel file to get started.")
        return

    _display_progress_overview()

    work_col, tags_col = st.columns([3, 1], gap="medium")

    with work_col:
        _display_work_title_and_abstract()

    with tags_col:
        _display_tag_fields()

    _display_work_note()


def _header_and_sidebar() -> None:
    """Header and page configuration"""
    st.set_page_config(
        page_title="Literature Review Assistant",
        layout="wide",
        initial_sidebar_state="expanded",
    )
    st.title("Literature Review Assistant")

    with st.sidebar:
        st.header("Upload Your Data")
        st.file_uploader(
            "Upload an Excel file containing your works.",
            key="file_uploader",
            type=["xlsx"],
            accept_multiple_files=False,
            on_change=_file_uploader_callback,
        )


def _file_uploader_callback() -> None:
    """
    Callback function for the file uploader widget.
    Resets session state and loads the uploaded Excel file
    into a DataFrame when a new file is uploaded.
    """
    _reset_session_state()
    if st.session_state.file_uploader is not None:
        _load_excel_file_into_dataframe()


def _reset_session_state() -> None:
    """Reset session state variables."""
    st.session_state.current_work_index = 0
    st.session_state.works_df = None
    st.session_state.tags = REQUIRED_FIELDS.copy()


def _load_excel_file_into_dataframe() -> None:
    """
    Loads the uploaded Excel file into a pandas DataFrame and stores it in the session state.
    Add tag fields to the dataframe if they don't exist, initialized with empty lists.
    Also adds note field to the dataframe if it doesn't exist, initialized with empty strings.
    """
    st.session_state.works_df = pd.read_excel(st.session_state.file_uploader)
    for field_name in st.session_state.tags.keys():
        if field_name not in st.session_state.works_df.columns:
            st.session_state.works_df[field_name] = [
                [] for _ in range(st.session_state.works_df.shape[0])
            ]
        else:
            # If field already exists, it came from a previous session.
            # There, pill selections were saved as lists,
            # but when loading from Excel they are read as strings.
            # The snippet below converts them to lists.
            st.session_state.works_df[field_name] = st.session_state.works_df[
                field_name
            ].apply(_sanitize_assignments)
    if NOTE_COLUMN not in st.session_state.works_df.columns:
        st.session_state.works_df[NOTE_COLUMN] = [
            "" for _ in range(st.session_state.works_df.shape[0])
        ]


def _sanitize_assignments(tag: str) -> list[str]:
    # "['some/text', 'valid text']" ->
    # "'some/text', 'valid text'" ->
    # ["'some/text'", "'valid text'"] ->
    # ["some/text", "valid text"]
    entries = tag.strip("[]").split(", ")
    return [entry.strip("'").strip() for entry in entries]


def _display_progress_overview() -> None:
    """
    Expander widget with an overview of the user's tagging progress.
    Progress "bar" is a matrix of color-coded squares representing the user's tagging progress for each work.
    Color ranges according to the amount of tags fields completed:
    gray if 0 fields completed,
    then linearly from red to green from 1 to all fields completed.
    Hovering over a square shows the title of the corresponding work and its tagging status.
    Clicking on a square takes the user to that work in the main view.
    """
    pass


def _display_work_title_and_abstract() -> None:
    """
    Displays details of the work being read - title and abstract -
    as well as navigation buttons.
    """
    title = st.session_state.works_df.loc[
        st.session_state.current_work_index, TITLE_COLUMN
    ]
    abstract = st.session_state.works_df.loc[
        st.session_state.current_work_index, ABSTRACT_COLUMN
    ]

    st.subheader(title)
    _display_navigation_widgets()
    st.write(abstract)


def _display_navigation_widgets() -> None:
    """
    Displays navigation widgets (e.g., next/previous buttons) for navigating through works.
    """
    # Under the work's title, user has 5 options:
    # checking the work's DOI, if available
    # going to the previous work (wraps around to end if at first work)
    # going to the next work (wraps around to beginning if at last work)
    # going to a specific work by entering its index in the dataframe
    # downloading the current work's details as an Excel file

    doi_col, goto_col, download_col = st.columns(
        [2, 2, 1], gap="small", vertical_alignment="bottom"
    )

    _display_doi_button(doi_col)
    _display_goto_widget(goto_col)
    _display_download_button(download_col)


def _display_doi_button(container) -> None:
    """Displays a button that links to the work's DOI if available, or a disabled button if not."""
    label = (
        f"**Work {st.session_state.current_work_index + 1} "
        f"of {st.session_state.works_df.shape[0]}**"
    )
    _type = "primary"
    current_work = st.session_state.works_df.loc[st.session_state.current_work_index]
    doi = current_work.get(DOI_COLUMN)
    if doi is None:
        container.button(
            label=label,
            type=_type,
            icon=":material/bookmark:",
            width="stretch",
        )
    else:
        url = f"https://doi.org/{doi}"
        container.link_button(
            label=label,
            type=_type,
            icon=":material/arrow_outward:",
            icon_position="right",
            url=url,
            help=url,
            width="stretch",
        )


def _display_goto_widget(container) -> None:
    """
    Displays a widget for going to a specific work
    by entering its number (index + 1).
    """
    container.number_input(
        "Go to",
        min_value=1,
        max_value=st.session_state.works_df.shape[0],
        value=st.session_state.current_work_index + 1,
        step=1,
        on_change=_goto_work_by_index,
        key="goto_work_input",
        width="stretch",
    )


def _goto_work_by_index() -> None:
    """Go to a specific work by its index in the dataframe."""
    # Using the widget's key in its callback is kinda weird, but it gets the job done
    if st.session_state.goto_work_input is not None:
        st.session_state.current_work_index = (
            st.session_state.goto_work_input - 1
        ) % st.session_state.works_df.shape[0]


def _display_download_button(container) -> None:
    """Displays a button for downloading the current work's details as an Excel file."""
    output = BytesIO()
    st.session_state.works_df.to_excel(output, engine="openpyxl")
    container.download_button(
        ":material/download:",
        data=output.getvalue(),
        file_name="LRA_download.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        type="primary",
        help="Download the current review's progress as an Excel file.",
        width="stretch",
    )


def _display_work_note() -> None:
    """
    Displays a text area for the user to write a note about the current work.
    Notes are saved in the session state and associated with the work's index in the dataframe.
    """
    st.subheader("**Your Notes**")
    st.text_area(
        "Write your notes about this work here.",
        # key="work_note",
        height=200,
    )


def _display_tag_fields() -> None:
    """
    Displays the tags assigned to the current work, and allows the user to edit them.
    Tags are separated by fields.
    User may create and delete fields, and assign and unassign tags to each field.
    Each field has its own "Edit" button that opens a modal for editing the tags in that field.
    Required fields have a "lock" symbol and cannot be deleted or renamed.
    Their tags also cannot be deleted or renamed.
    """
    st.subheader("**Assign Tags**")
    for field_name, tag_options in st.session_state.tags.items():
        _display_assigned_tags_and_edit_modal(field_name, tag_options)

    _display_field_adding_widgets()


def _display_field_adding_widgets() -> None:
    st.button(
        "Add field",
        on_click=_add_field_callback,
        width="stretch",
    )


def _add_field_callback() -> None:
    new_field_name = f"Field {len(st.session_state.tags) + 1}"
    st.session_state.tags[new_field_name] = []
    st.session_state.works_df[new_field_name] = [
        [] for _ in range(st.session_state.works_df.shape[0])
    ]


def _display_assigned_tags_and_edit_modal(
    field_name: str, tag_options: list[str]
) -> None:
    _field_col, _edit_modal_col = st.columns([1, 0.1])

    with _field_col:
        _display_tags_for_field(field_name, tag_options)

    with _edit_modal_col:
        st.button(
            ":material/edit:",
            type="tertiary",
            on_click=_display_tag_editing_modal,
            args=[field_name],
            disabled=field_name in REQUIRED_FIELDS,
            key=f"modal_{field_name}",
        )


def _display_tags_for_field(field_name: str, tag_options: list[str]) -> None:
    _label_decoration = (
        ":material/lock:" if field_name in REQUIRED_FIELDS else ":material/edit:"
    )
    _label = f"{_label_decoration} **{field_name}**"
    _current_assignment = st.session_state.works_df.loc[
        st.session_state.current_work_index, field_name
    ]
    _key = f"tags_{field_name}_work_{st.session_state.current_work_index}"
    st.pills(
        label=_label,
        options=tag_options,
        default=_current_assignment,
        selection_mode="multi",
        key=_key,
        on_change=_update_works_df_with_assigned_tags,
        args=[field_name, _key],
    )


def _update_works_df_with_assigned_tags(field_name: str, key: str) -> None:
    """
    Updates the works dataframe in the session state with the tags assigned to the current work.
    This function is called whenever the user changes the assigned tags for a field.
    """
    assigned_tags = st.session_state.get(key, [])
    st.session_state.works_df.loc[st.session_state.current_work_index, field_name] = [
        *assigned_tags  # re-casting to list avoids default python parsing
    ]


@st.dialog("Edit Field")
def _display_tag_editing_modal(field_name: str) -> None:
    """
    Displays a modal for editing the tags in a specific field,
    or the field itself.
    Allows the user to add new tags, delete existing tags, and rename tags.
    Also allows the user to rename the field or delete the field.
    Required fields cannot be renamed or deleted, and their tags cannot be renamed or deleted.
    """

    st.header(field_name)

    # TODO: review field editing widgets (adding too)
    _display_field_renaming_widgets(field_name)
    _display_field_deleting_widgets(field_name)

    # TODO: implement tag editing widgets
    # _display_tag_adding_widgets(field_name)
    # _display_tag_renaming_widgets(field_name)
    # _display_tag_deleting_widgets(field_name)


def _display_field_renaming_widgets(field_name: str) -> None:
    _key = f"rename_{field_name}_input"
    st.text_input(
        "Rename field",
        value=field_name,
        key=_key,
        on_change=_rename_field_callback,
        args=[field_name, _key],
    )


def _rename_field_callback(field_name: str, key: str) -> None:
    new_field_name = st.session_state.get(key)
    if new_field_name and new_field_name != field_name:
        _rename_field(field_name, new_field_name)


def _rename_field(old_name: str, new_name: str) -> None:
    st.session_state.tags[new_name] = st.session_state.tags.pop(old_name)
    st.session_state.works_df[new_name] = st.session_state.works_df.pop(old_name)


def _display_field_deleting_widgets(field_name: str) -> None:
    st.button(
        "Delete field",
        on_click=_delete_field_callback,
        args=[field_name],
        disabled=field_name in REQUIRED_FIELDS,
    )


def _delete_field_callback(field_name: str) -> None:
    _delete_field(field_name)


def _delete_field(field_name: str) -> None:
    st.session_state.tags.pop(field_name, None)
    st.session_state.works_df.pop(field_name, None)


if __name__ == "__main__":
    main()
