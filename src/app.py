"""
Cleanest most stable version of the app I could make.
First all widgets are created, then all callbacks are defined, then the main logic is executed.
"""

from __future__ import annotations

import json

import matplotlib
import pandas as pd
import streamlit as st

from constants import (
    ABSTRACT_COLUMN,
    COLORMAP,
    DOI_COLUMN,
    MAX_COLS_IN_OVERVIEW,
    NOTE_COLUMN,
    REQUIRED_FIELDS,
    TITLE_COLUMN,
)

ProgressDict = dict[str, list[str] | str]

# Useful variables to introduce in session state:
# - current_work_index: int, index of the work currently being displayed
# - works_df: pd.DataFrame, input dataframe containing the works and their details
# - tags: dict, mapping from field names to lists of tags options of that field
# - session_progress: list of dicts, each dict containing the progress for a work
# (assigned tags and notes), indexed by the work's index in the dataframe
if "current_work_index" not in st.session_state:
    st.session_state.current_work_index = 0

if "works_df" not in st.session_state:
    st.session_state.works_df = None

if "tags" not in st.session_state:
    st.session_state.tags = REQUIRED_FIELDS.copy()

if "session_progress" not in st.session_state:
    st.session_state.session_progress: list[ProgressDict] = []


def main() -> None:
    """Main function with logic for the app."""

    _display_app()


def _display_app() -> None:
    """Displays the app's main content based on the uploaded file."""

    _display_header()

    with st.sidebar:
        _display_sidebar()

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

    _display_management()


def _display_header() -> None:
    """Header and page configuration"""
    st.set_page_config(
        page_title="Literature Review Assistant",
        layout="wide",
        initial_sidebar_state="expanded",
    )
    st.title("Literature Review Assistant")


def _display_sidebar() -> None:
    """
    Displays sidebar with file uploaders for the Excel file and previous progress JSON file.
    """
    st.header("Upload Your Export")
    st.file_uploader(
        "Upload an Excel file containing your works.",
        key="file_uploader",
        type=["xlsx"],
        accept_multiple_files=False,
        on_change=_file_uploader_callback,
    )

    st.divider()
    if st.session_state.get("file_uploader") is not None:
        st.header("Work in progress?")
        st.file_uploader(
            "Upload a JSON file from a previous session.",
            key="previous_progress_uploader",
            type=["json"],
            accept_multiple_files=False,
            on_change=_previous_progress_uploader_callback,
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


def _previous_progress_uploader_callback() -> None:
    """
    Callback function for the previous progress file uploader widget.
    Loads the uploaded JSON file containing previous progress and updates the session state accordingly.
    """
    if st.session_state.previous_progress_uploader is not None:
        st.session_state.session_progress = json.load(
            st.session_state.previous_progress_uploader
        )
        st.info("Previous progress loaded successfully!")


def _reset_session_state() -> None:
    """Reset session state variables."""
    st.session_state.current_work_index = 0
    st.session_state.works_df = None
    st.session_state.tags = REQUIRED_FIELDS.copy()
    st.session_state.session_progress = []


def _load_excel_file_into_dataframe() -> None:
    """
    Loads the uploaded Excel file into a pandas DataFrame and stores it in the session state
    for later referencing (title, abstract, doi, etc.).
    Also initializes the progress tracking variable in session state.
    """
    st.session_state.works_df = pd.read_excel(st.session_state.file_uploader)
    st.session_state.session_progress = [
        {} for _ in range(len(st.session_state.works_df))
    ]

    for i in st.session_state.works_df.index:
        _work_title = st.session_state.works_df.loc[i, TITLE_COLUMN]
        st.session_state.session_progress[i][NOTE_COLUMN] = ""
        for field in st.session_state.tags.keys():
            st.session_state.session_progress[i][field] = []


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
    _n_fields = len(st.session_state.tags)
    _n_works = len(st.session_state.session_progress)

    color_code = matplotlib.colormaps[COLORMAP](
        [i / _n_fields for i in range(_n_fields + 1)]
    )
    color_code = [matplotlib.colors.rgb2hex(c) for c in color_code]

    works_colors = [color_code[0]] * _n_works

    for i, work_progress in enumerate(st.session_state.session_progress):
        n_completed_fields = sum(
            1 if work_progress[field] else 0 for field in st.session_state.tags.keys()
        )
        works_colors[i] = color_code[n_completed_fields]

    # Display the progress overview in an expander
    _n_cols = min(MAX_COLS_IN_OVERVIEW, _n_works)
    with st.expander("Progress Overview", expanded=True):
        # Make a button for each work with the corresponding color, and a tooltip showing the title
        shortcut_button_cols = st.columns(_n_cols, gap="small")
        for index, color in enumerate(works_colors):
            title = st.session_state.works_df.loc[index, TITLE_COLUMN]
            tooltip = f"{title}\n"
            key = f"progress_overview_work_{index}"
            col = shortcut_button_cols[index % MAX_COLS_IN_OVERVIEW]
            with col:
                _display_colored_shortcut_button(index, color, tooltip, key)


def _display_colored_shortcut_button(
    index: int, color: str, tooltip: str, key: str
) -> None:
    # Markdown hack for coloring the button based on the status
    # https://discuss.streamlit.io/t/button-css-for-streamlit/45888/9
    st.markdown(
        """
        <style>
        .element-container:has(#"""
        + key
        + """) + div button {
            background-color: """
        + color
        + """;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )
    st.markdown(f'<span id="{key}"></span>', unsafe_allow_html=True)
    st.button(
        label="",
        key=key,
        help=tooltip,
        on_click=_goto_work_by_index,
        args=[index],
        width="stretch",
    )


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
    _display_navigation()
    st.write(abstract)


def _display_navigation() -> None:
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

    with doi_col:
        _display_doi_button()

    with goto_col:
        _display_goto_widget()

    with download_col:
        _display_download_button()


def _display_doi_button() -> None:
    """Displays a button that links to the work's DOI if available, or a disabled button if not."""
    label = (
        f"**Work {st.session_state.current_work_index + 1} "
        f"of {len(st.session_state.session_progress)}**"
    )
    _type = "primary"
    current_work = st.session_state.works_df.loc[st.session_state.current_work_index]
    doi = current_work.get(DOI_COLUMN)
    if doi is None:
        st.button(
            label=label,
            type=_type,
            icon=":material/bookmark:",
            width="stretch",
        )
    else:
        url = f"https://doi.org/{doi}"
        st.link_button(
            label=label,
            type=_type,
            icon=":material/arrow_outward:",
            icon_position="right",
            url=url,
            help=url,
            width="stretch",
        )


def _display_goto_widget() -> None:
    """
    Displays a widget for going to a specific work
    by entering its number (index + 1).
    """
    work_number_input_col, goto_button_col = st.columns(
        [2, 1], gap="small", vertical_alignment="bottom"
    )
    with work_number_input_col:
        st.number_input(
            "Go to",
            min_value=1,
            max_value=len(st.session_state.session_progress),
            value=st.session_state.current_work_index + 1,
            step=1,
            key="goto_work_input",
            width="stretch",
        )
    with goto_button_col:
        st.button(
            ":material/search:",
            on_click=_goto_work_by_index,
            args=[st.session_state.goto_work_input - 1],
            width="stretch",
            type="primary",
        )


def _goto_work_by_index(goto_index: int) -> None:
    """Go to a specific work by its index in the dataframe."""
    if goto_index is not None:
        st.session_state.current_work_index = (goto_index) % len(
            st.session_state.session_progress
        )


def _display_download_button() -> None:
    """Displays a button for downloading the current work's details (tagging) as JSON file."""

    input_file_name = st.session_state.file_uploader.name
    date = pd.Timestamp.now().strftime("%Y-%m-%d")
    download_name = input_file_name.replace(".xlsx", f"_session-{date}.json")
    output_data = json.dumps(st.session_state.session_progress, indent=4)

    st.download_button(
        ":material/download:",
        data=output_data,
        file_name=download_name,
        mime="application/json",
        type="primary",
        help="Download the current review's progress as JSON file.",
        width="stretch",
    )


def _display_work_note() -> None:
    """
    Displays a text area for the user to write a note about the current work.
    Notes are saved in the session state and associated with the work's index in the dataframe.
    """
    _current_note = st.session_state.session_progress[
        st.session_state.current_work_index
    ][NOTE_COLUMN]
    st.info(f"Note: {_current_note}")
    st.subheader("**Your Notes**")
    st.text_area(
        "Write your notes about this work here.",
        key=f"work_{st.session_state.current_work_index}_note_input",
        value=_current_note,
        height=150,
        on_change=_save_note_for_current_work,
    )


def _save_note_for_current_work() -> None:
    """Saves the user's note for the current work in the session state."""
    st.session_state.session_progress[st.session_state.current_work_index][
        NOTE_COLUMN
    ] = st.session_state[f"work_{st.session_state.current_work_index}_note_input"]


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
        _display_tags_for_field(field_name, tag_options)


def _display_tags_for_field(field_name: str, tag_options: list[str]) -> None:
    _label_decoration = (
        ":material/lock:" if field_name in REQUIRED_FIELDS else ":material/edit:"
    )
    _label = f"{_label_decoration} **{field_name}**"
    _current_assignment = st.session_state.session_progress[
        st.session_state.current_work_index
    ][field_name]
    _key = f"tags_{field_name}_work_{st.session_state.current_work_index}"
    st.pills(
        label=_label,
        options=tag_options,
        default=_current_assignment,
        selection_mode="multi",
        key=_key,
        on_change=_update_progress_with_assigned_tags,
        args=[field_name, _key],
    )


def _display_management() -> None:
    """
    Displays widgets for managing tag fields and options.
    User can add new fields, delete existing fields (except required ones), and edit the tags in each field.
    """
    # Left column: field management (add, delete, rename fields)
    # Right column: tag management (add, delete, rename tags in each field)
    field_mgmt_col, tag_mgmt_col = st.columns(2, gap="medium")

    with field_mgmt_col:
        st.subheader("**Manage Tag Fields**")
        _display_field_management()

    with tag_mgmt_col:
        st.subheader("**Manage Tag Entries**")
        _display_tag_management_for_fields()


def _display_field_management() -> None:
    """
    Displays widgets for managing tag fields.
    User can add new fields, delete existing fields (except required ones), and rename fields.
    """
    _display_add_field()
    _display_rename_field()
    _display_delete_field()


def _display_add_field() -> None:
    """
    Displays widgets for adding a new tag field.
    User can enter the name of the new field and click "Add Field" to create it.
    """
    st.text_input(
        "Add a new field",
        placeholder="Enter new field name and press Enter",
        key="new_field_input",
        on_change=_add_new_field,
    )


def _add_new_field() -> None:
    """Adds a new tag field to the session state and updates the dataframe."""
    new_field_name = st.session_state.new_field_input.strip()
    if new_field_name and new_field_name not in st.session_state.tags:
        st.session_state.tags[new_field_name] = []
        for work_progress in st.session_state.session_progress:
            work_progress[new_field_name] = []

    # Clear input after adding
    st.session_state.new_field_input = ""


def _display_rename_field() -> None:
    """
    Displays widgets for renaming existing tag fields.
    User picks a field from a dropdown and enters a new name to rename it.
    Required fields cannot be renamed.
    """
    _valid_fields = [
        field for field in st.session_state.tags.keys() if field not in REQUIRED_FIELDS
    ]
    if not _valid_fields:
        st.info("Renameable fields will appear here.")
        return

    _box_col, _input_col = st.columns([1, 1], gap="medium", vertical_alignment="bottom")

    with _box_col:
        st.selectbox(
            "Select a field to rename",
            options=_valid_fields,
            key="rename_field_select",
            width="stretch",
        )

    with _input_col:
        st.text_input(
            "Enter new name for the selected field",
            placeholder="Enter new field name and press Enter",
            key="rename_field_input",
            on_change=_rename_field,
            width="stretch",
        )


def _rename_field() -> None:
    """Renames a tag field in the session state and updates progress."""
    selected_field = st.session_state.rename_field_select
    new_field_name = st.session_state.rename_field_input.strip()
    if (
        selected_field
        and new_field_name
        and new_field_name not in st.session_state.tags
        and selected_field not in REQUIRED_FIELDS
    ):
        # Rename field in tags dict
        st.session_state.tags[new_field_name] = st.session_state.tags.pop(
            selected_field
        )
        # Rename column in session progress
        for work_progress in st.session_state.session_progress:
            work_progress[new_field_name] = work_progress.pop(selected_field)

    # Clear input after renaming
    st.session_state.rename_field_input = ""


def _display_delete_field() -> None:
    """
    Displays widgets for deleting existing tag fields.
    User picks a field from a dropdown and clicks "Delete Field" to delete it.
    Required fields cannot be deleted.
    """
    _valid_fields = [
        field for field in st.session_state.tags.keys() if field not in REQUIRED_FIELDS
    ]
    if not _valid_fields:
        st.info("Deleteable fields will appear here.")
        return

    _select_col, _button_col = st.columns(
        [1, 1], gap="medium", vertical_alignment="bottom"
    )

    with _select_col:
        st.selectbox(
            "Select a field to delete",
            options=_valid_fields,
            key="delete_field_select",
            width="stretch",
        )

    with _button_col:
        st.button(
            "Delete Field",
            on_click=_delete_field,
            args=[st.session_state.delete_field_select],
            width="stretch",
        )


def _delete_field(field_name: str) -> None:
    """Deletes a tag field from the session state and updates progress."""
    st.session_state.tags.pop(field_name)
    for work_progress in st.session_state.session_progress:
        work_progress.pop(field_name, None)

    # Clear selection after deleting
    st.session_state.delete_field_select = ""


def _display_tag_management_for_fields() -> None:
    """
    Displays widgets for managing tags in each field.
    For each field, user can add new tags, delete existing tags (except those assigned to works), and rename tags.
    Tag editing widgets are displayed in an expander for each field to keep the UI organized.
    """
    _valid_fields = [
        field for field in st.session_state.tags.keys() if field not in REQUIRED_FIELDS
    ]

    if not _valid_fields:
        st.info("Editable tags will appear here for each field.")
        return

    for field_name in _valid_fields:
        tag_options = st.session_state.tags.get(field_name, [])
        with st.expander(f"Manage tags for **{field_name}**", expanded=False):
            _display_tag_management_for_field(field_name, tag_options)


def _display_tag_management_for_field(field_name: str, tag_options: list[str]) -> None:
    """
    Displays widgets for managing tags in a specific field.
    User can add new tags, delete existing tags (except those assigned to works), and rename tags.
    """
    _display_add_tag_for_field(field_name)
    _display_rename_tag_for_field(field_name, tag_options)
    _display_delete_tag_for_field(field_name, tag_options)


def _display_add_tag_for_field(field_name: str) -> None:
    """
    Displays widgets for adding a new tag to a specific field.
    User can enter the name of the new tag and click "Add Tag" to create it.
    """
    st.text_input(
        f"Add a new tag to **{field_name}**",
        placeholder="Enter new tag name and press Enter",
        key=f"new_tag_input_{field_name}",
        on_change=_add_new_tag_for_field,
        args=[field_name],
    )


def _add_new_tag_for_field(field_name: str) -> None:
    """Adds a new tag to a specific field in the session state."""
    new_tag_name = st.session_state[f"new_tag_input_{field_name}"].strip()
    if new_tag_name and new_tag_name not in st.session_state.tags[field_name]:
        st.session_state.tags[field_name].append(new_tag_name)

    # Clear input after adding
    st.session_state[f"new_tag_input_{field_name}"] = ""


def _display_rename_tag_for_field(field_name: str, tag_options: list[str]) -> None:
    """
    Displays widgets for renaming existing tags in a specific field.
    User picks a tag from a dropdown and enters a new name to rename it.
    """

    if not tag_options:
        st.info("Renameable tags will appear here.")
        return

    _box_col, _input_col = st.columns([1, 1], gap="medium", vertical_alignment="bottom")

    with _box_col:
        st.selectbox(
            f"Select a tag to rename in **{field_name}**",
            options=tag_options,
            key=f"rename_tag_select_{field_name}",
            width="stretch",
        )

    with _input_col:
        st.text_input(
            f"Enter new name for the selected tag in **{field_name}**",
            placeholder="Enter new tag name and press Enter",
            key=f"rename_tag_input_{field_name}",
            on_change=_rename_tag_for_field,
            args=[field_name],
            width="stretch",
        )


def _rename_tag_for_field(field_name: str) -> None:
    """Renames a tag in a specific field in the session state."""
    selected_tag = st.session_state[f"rename_tag_select_{field_name}"]
    new_tag_name = st.session_state[f"rename_tag_input_{field_name}"].strip()

    if (
        selected_tag
        and new_tag_name
        and new_tag_name not in st.session_state.tags[field_name]
    ):
        # Rename tag in tags list
        tag_index = st.session_state.tags[field_name].index(selected_tag)
        st.session_state.tags[field_name][tag_index] = new_tag_name

    # Clear input after renaming
    st.session_state[f"rename_tag_input_{field_name}"] = ""


def _display_delete_tag_for_field(field_name: str, tag_options: list[str]) -> None:
    """
    Displays widgets for deleting existing tags in a specific field.
    User picks a tag from a dropdown and clicks "Delete Tag" to delete it.
    Tags that are assigned to works cannot be deleted.
    """

    if not tag_options:
        st.info("Deleteable tags will appear here.")
        return

    _select_col, _button_col = st.columns(
        [1, 1], gap="medium", vertical_alignment="bottom"
    )

    with _select_col:
        st.selectbox(
            f"Select a tag to delete in **{field_name}**",
            options=tag_options,
            key=f"delete_tag_select_{field_name}",
            width="stretch",
        )

    with _button_col:
        st.button(
            "Delete Tag",
            on_click=_delete_tag_for_field,
            args=[field_name, st.session_state[f"delete_tag_select_{field_name}"]],
            width="stretch",
        )


def _delete_tag_for_field(field_name: str, tag_name: str) -> None:
    """Deletes a tag from a specific field in the session state."""
    if tag_name and tag_name in st.session_state.tags[field_name]:
        # Remove tag from tags list
        st.session_state.tags[field_name].remove(tag_name)

    # Clear selection after deleting
    st.session_state[f"delete_tag_select_{field_name}"] = ""


def _update_progress_with_assigned_tags(field_name: str, key: str) -> None:
    """
    Updates the session progress in the session state with the tags assigned to the current work.
    This function is called whenever the user changes the assigned tags for a field.
    """
    assigned_tags = st.session_state.get(key, [])
    st.session_state.session_progress[st.session_state.current_work_index][
        field_name
    ] = assigned_tags


if __name__ == "__main__":
    main()
