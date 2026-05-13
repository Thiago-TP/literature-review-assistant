"""
Literature Review Assistant - Interactive Streamlit Application.

A Streamlit-based tool for systematic literature reviews enabling researchers to:
- Import academic paper metadata from Excel files
- Review papers interactively with title, abstract, and DOI information
- Assign customizable tags across multiple classification fields
- Track review progress with visual progress indicators
- Save and resume review sessions using JSON export/import
- Manage custom tag fields and options dynamically

Architecture:
    This module follows a clean separation of concerns pattern:
    1. Session state initialization (module-level)
    2. Main entry point and display orchestration (main(), _display_app())
    3. Component display functions (_display_*)
    4. Callback functions for state management
    5. Helper/utility functions

Session State Management:
    The application maintains the following session state variables:
    - current_work_index: int - Index of the work currently displayed
    - works_df: pd.DataFrame - Imported paper metadata with columns: Title, Abstract, DOI, etc.
    - tags: dict[str, list[str]] - Maps field names to available tag options
    - session_progress: list[ProgressDict] - Review progress for each paper (tags assigned, notes)
    - file_uploader: UploadedFile - Currently loaded Excel file
    - previous_progress_uploader: UploadedFile - Loaded JSON progress file

UI Layout:
    - Header: Page title and configuration
    - Sidebar: File upload controls (Excel and JSON files)
    - Main Area: Paper review interface with:
        * Progress overview (color-coded status matrix)
        * Paper details (title, abstract, DOI, navigation)
        * Tag assignment controls
        * Notes section
        * Tag management controls
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
    disabled = st.session_state.get("file_uploader") is not None
    export_file = st.file_uploader(
        "Upload an Excel file containing your works.",
        key="file_uploader",
        type=["xlsx"],
        accept_multiple_files=False,
        disabled=disabled,
    )

    if export_file is not None:
        _load_excel_file_into_dataframe()

    st.divider()
    if st.session_state.get("file_uploader") is not None:
        st.header("Work in progress?")
        previous_progress_file = st.file_uploader(
            "Upload a JSON file from a previous session.",
            type=["json"],
            accept_multiple_files=False,
        )
        if previous_progress_file is not None:
            st.session_state.session_progress = json.load(previous_progress_file)
            st.success("Previous progress loaded successfully!")


def _load_excel_file_into_dataframe() -> None:
    """
    Load and initialize session state from an uploaded Excel file.

    Performs the following initialization steps:
    1. Reads the Excel file into a pandas DataFrame
    2. Validates required columns are present (Title, Abstract)
    3. Initializes session_progress tracking structure:
       - Creates a progress entry for each paper
       - Pre-populates Notes field and tag fields with empty values
    4. Sets current_work_index to 0 (first paper)

    The loaded DataFrame is stored in session state for display and reference.
    Progress tracking is initialized with empty dictionaries for each paper,
    ready to be populated as the user assigns tags during review.

    Raises:
        KeyError: If required columns (Title, Abstract) are missing
        pd.errors.ParserError: If file is not a valid Excel format
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
    Display an interactive progress overview matrix showing review status for all papers.

    Creates a grid of colored squares where each column represents a paper and the color
    indicates the completion status based on how many tag fields have been filled:
    - Gray (color_code[0]): No fields completed
    - Red to Yellow to Green: Progressive completion from 1 field to all fields

    Each square is an interactive button that:
    - Shows the paper title as a tooltip on hover
    - Jumps to that paper when clicked
    - Updates color dynamically as tags are assigned

    The grid is wrapped in an expander widget for compact UI and displayed in a
    responsive layout that respects MAX_COLS_IN_OVERVIEW for mobile compatibility.
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
    Render the main paper content display with navigation controls.

    Displays:
    1. Paper title (as a subheader)
    2. Navigation bar with:
       - DOI link button (if DOI available, else disabled)
       - Work counter (e.g., "Work 5 of 127")
       - Go-to-specific-work input field and search button
       - Download session progress as JSON button
    3. Full abstract text

    The layout is responsive with the navigation bar beneath the title
    and the abstract displayed below for easy reading.
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
    Render paper navigation controls in a responsive row layout.

    Displays three main navigation components:
    1. **DOI Button** - Links to paper on doi.org (if available) or shows disabled button
    2. **Go-To Controls** - Allows jumping to a specific paper by entering its number
    3. **Download Button** - Exports current session progress as JSON

    Layout:
    - Left (2 cols): DOI button showing work counter (e.g., "Work 5 of 127")
    - Center (2 cols): Go-to input and search button
    - Right (1 col): Download button

    All controls are vertically centered and use primary styling for consistency.
    """

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
    if doi is None or pd.isna(doi) or doi.strip() == "":
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
    st.subheader("**Your Notes**")
    new_note = st.text_area(
        "Write your notes about this work here.",
        value=_current_note,
        height=150,
    )
    st.session_state.session_progress[st.session_state.current_work_index][
        NOTE_COLUMN
    ] = new_note


def _display_tag_fields() -> None:
    """
    Render the tag assignment interface for the current paper.

    Displays all available tag fields (both required and custom) with multi-select pills.
    For each field:
    - Shows a lock icon (🔒) for protected required fields (Adherence, Contribution Type)
    - Shows an edit icon (✏️) for custom user-created fields
    - Displays available tag options as interactive pills
    - Pre-selects tags already assigned to the current paper

    Required fields cannot be deleted but their content is always visible.
    Custom fields can be managed in the "Manage Tag Fields" and "Manage Tag Entries" sections.

    When a tag is selected/deselected, _update_progress_with_assigned_tags is called
    to automatically save the selection to session state.
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
    assigned_tags = st.pills(
        label=_label,
        options=tag_options,
        default=_current_assignment,
        selection_mode="multi",
    )

    st.session_state.session_progress[st.session_state.current_work_index][
        field_name
    ] = assigned_tags


def _display_management() -> None:
    """
    Render the tag and field management control panel.

    Split into two columns:

    **Left column - Field Management:**
    - Add new custom tag fields
    - Rename existing custom fields (protected fields excluded)
    - Delete custom fields (protected fields cannot be deleted)

    **Right column - Tag Management:**
    - For each custom field, manage the available tags:
      * Add new tags to a field
      * Rename existing tags (except assigned ones in protected fields)
      * Delete unassigned tags from a field

    Protected fields (Adherence, Contribution Type) are read-only and their tags
    are predefined and immutable.

    This section is typically collapsed by default to minimize UI clutter while
    reviewing papers. Users expand it when they need to customize their tagging structure.
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
    """
    Create a new custom tag field in the tagging system.

    Processes the user's input from the "Add a new field" text input:
    1. Retrieves the field name from session state
    2. Strips whitespace and validates non-empty
    3. Checks field doesn't already exist
    4. Adds field to tags dictionary with empty tag list
    5. Initializes empty tag list for each paper in session_progress
    6. Clears the input field for next entry

    New fields are not required (unlike Adherence, Contribution Type).
    Users can modify and delete them anytime.
    """
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
    """
    Add a new tag option to an existing custom field.

    Processes user input from the "Add a new tag" text input:
    1. Retrieves tag name from the field-specific session state key
    2. Strips whitespace and validates non-empty
    3. Checks tag doesn't already exist in this field
    4. Appends new tag to the field's tag options list
    5. Clears the input field for next entry

    Args:
        field_name: Name of the field to add the tag to

    Note:
        Tags in protected fields (Adherence, Contribution Type) are predefined
        and cannot be modified through this function.
    """
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


if __name__ == "__main__":
    main()
