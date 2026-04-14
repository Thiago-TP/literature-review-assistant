from __future__ import annotations
from datetime import datetime
from io import BytesIO

import streamlit as st
import pandas as pd
from matplotlib.colors import LinearSegmentedColormap, rgb2hex

# Global variables
completion_colormap = LinearSegmentedColormap.from_list(
    "completion_colormap",
    [
        "#BCC4DB",  # Pale Slate
        "#EF8354",  # Coral Glow
        "#F1CD18",  # Gold
        "#0F7173",  # Stormy Teal
    ],
)
legends = {
    0.0: "Not Started",
    0.25: "Initiated",
    0.5: "Halfway",
    0.75: "Almost Done",
    1.0: "Completed",
}
max_cols = 30
# Standard Scopus columns that are expected to come
# in the Excel and can be ignored when looking for user defined tags
scopus_fields = [
    "Title",
    "Authors",
    "Year",
    "Source title",
    "Volume",
    "Issue",
    "Art. No.",
    "Page start",
    "Page end",
    "Page count",
    "Cited by",
    "DOI",
    "Link",
    "Abstract",
    "Cited by",
    "Affiliations",
    "Index Keywords",
    "Author Keywords",
    "Correspondence Address",
    "Editors",
    "Publisher",
    "Language of Original Document",
    "Document Type",
    "Source",
    "Open Access",
    "PubMed ID",
    "Abbreviated Source Title",
    "Author(s) ID",
    "Author full names",
    "Authors with affiliations",
    "Publication Stage",
    "EID",
    "ISBN",
    "ISSN",
    "Unnamed: 0",
    "CODEN",
]


# Streamlit session state variables
# works_df: dataframe uploaded by user
# current_work_index: index in the dataframe of the work being displayed
# total_works: number of rows in the dataframe
if "works_df" not in st.session_state:
    st.session_state.works_df = None
if "current_work_index" not in st.session_state:
    st.session_state.current_work_index = None
if "total_works" not in st.session_state:
    st.session_state.total_works = 0
if "expander_button_list" not in st.session_state:
    st.session_state.expander_button_list = []

# State session variables for tags and options
if "tags_dict" not in st.session_state or "tags" not in st.session_state:
    st.session_state.tags = ["Adherence", "Contribution Type"]
    adherence_options = ["Insufficient", "Partial", "Sufficient"]
    contribution_options = ["Improvement", "New Method", "Review", "Other"]
    st.session_state.tags_dict = dict(
        zip(st.session_state.tags, [adherence_options, contribution_options])
    )


def clear_session_state() -> None:
    # Clear pill button selections for all tags and works
    for key in st.session_state.keys():
        for tag in st.session_state.tags:
            if f"{tag}_" in st.session_state:
                if isinstance(st.session_state[key], list):
                    st.session_state[key] = []
                else:
                    st.session_state[key] = None
    st.session_state.works_df = None
    st.session_state.current_work_index = None
    st.session_state.total_works = 0
    st.session_state.expander_button_list = []
    st.session_state.tags = ["Adherence", "Contribution Type"]
    adherence_options = ["Insufficient", "Partial", "Sufficient"]
    contribution_options = ["Improvement", "New Method", "Review", "Other"]
    st.session_state.tags_dict = dict(
        zip(st.session_state.tags, [adherence_options, contribution_options])
    )


def process_uploaded_file() -> None:

    clear_session_state()

    if st.session_state.file_uploader is None:
        return

    st.session_state.works_df = pd.read_excel(
        BytesIO(st.session_state.file_uploader.getvalue()), engine="openpyxl"
    )

    # Sanity check
    if st.session_state.works_df.empty:
        st.warning("Excel is empty!")
        st.session_state.works_df = None
        return

    st.session_state.current_work_index = 0
    st.session_state.total_works = len(st.session_state.works_df)

    # Add tag columns if they don't exist
    for tag in st.session_state.tags_dict:
        if tag not in st.session_state.works_df.columns:
            st.session_state.works_df[tag] = None

    # Add a "Tags Done" column if it doesn't exist
    if "Tags Done" not in st.session_state.works_df.columns:
        st.session_state.works_df["Tags Done"] = 0


def process_tag_selections(tag, options, key):
    # If new selections are empty, we set the tag value to None
    # in the dataframe
    tag_selections = st.session_state[key]
    if tag_selections == [] or tag_selections is None:
        st.session_state.works_df.at[st.session_state.current_work_index, tag] = None
        return

    # Adherence tag returns a string instead of a list,
    # so we convert it to a list for consistency
    if tag == "Adherence":
        tag_selections = [tag_selections]
    ordered_selections = sorted(tag_selections, key=lambda x: options.index(x))
    st.session_state.works_df.at[st.session_state.current_work_index, tag] = ", ".join(
        ordered_selections
    )


def main() -> None:
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
            on_change=process_uploaded_file,
        )

    if st.session_state.works_df is None:
        st.info("Upload an Excel file from the sidebar to start reviewing.")
        return

    # Setup expander at the top of the page
    progress_expander = st.expander("Progress Overview")

    # Second expander for loading tagging if uploaded excel
    # is a work in progress from a previous session
    with st.sidebar:
        wip_expander = st.expander("Work in Progress from another session?")
        with wip_expander:
            st.info(
                "If you uploaded an Excel file that has tags from "
                "a previous session, you can pick up where you left off "
                "by indicating them here."
            )
            possible_tags = st.session_state.works_df.columns.tolist()
            # Remove default tags from the options, since they are already assigned
            for default_tag in [
                "Adherence",
                "Contribution Type",
                "Tags Done",
            ] + scopus_fields:
                if default_tag in possible_tags:
                    possible_tags.remove(default_tag)
            wip_tags = st.pills(
                "These tags may have been created in a previous session",
                possible_tags,
                selection_mode="multi",
            )
            if wip_tags:
                for tag in wip_tags:
                    if tag in st.session_state.works_df.columns:
                        st.session_state.tags.append(tag)
                        st.session_state.tags_dict[tag] = []
                        # Extract unique values from the column to use as options
                        unique_values = (
                            st.session_state.works_df[tag].dropna().unique().tolist()
                        )
                        st.session_state.tags_dict[tag] = unique_values

    # Display the details of the currently selected work in the left column,
    # and user defined tagging in the right column
    work_col, tags_col = st.columns([3, 1], gap="medium")
    if st.session_state.current_work_index is not None:
        with work_col:
            current_work = st.session_state.works_df.iloc[
                st.session_state.current_work_index
            ]
            st.subheader(current_work.get("Title", "Untitled Work"))
            # Under the work's title, user has 5 options:
            # checking the work's DOI, if available
            # going to the previous work (wraps around to end if at first work)
            # going to the next work (wraps around to beginning if at last work)
            # going to a specific work by entering its index in the dataframe
            # downloading the current work's details as an Excel file
            doi_col, prev_col, next_col, goto_col, download_col = st.columns(
                [2, 0.5, 0.5, 2, 0.5], gap="small", vertical_alignment="bottom"
            )
            with doi_col:
                label = (
                    f"**Work {st.session_state.current_work_index + 1} "
                    f"of {st.session_state.total_works}**"
                )
                _type = "primary"
                doi = current_work.get("DOI", None)
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
            with prev_col:
                if st.button(
                    ":material/arrow_back:",
                    key="prev_button",
                    width="stretch",
                ):
                    st.session_state.current_work_index = (
                        st.session_state.current_work_index - 1
                    ) % st.session_state.total_works
                    st.rerun()
            with next_col:
                if st.button(
                    ":material/arrow_forward:",
                    key="next_button",
                    width="stretch",
                ):
                    st.session_state.current_work_index = (
                        st.session_state.current_work_index + 1
                    ) % st.session_state.total_works
                    st.rerun()
            with goto_col:
                goto_input_col, goto_button_col = st.columns(
                    [2, 1], gap="small", vertical_alignment="bottom"
                )
                with goto_input_col:
                    goto_index = st.number_input(
                        "Go to",
                        min_value=1,
                        max_value=st.session_state.total_works,
                        value=st.session_state.current_work_index + 1,
                        step=1,
                        key="goto_input",
                        width="stretch",
                    )
                with goto_button_col:
                    if st.button(
                        ":material/search:",
                        key="goto_button",
                        width="stretch",
                    ):
                        st.session_state.current_work_index = goto_index - 1
                        st.rerun()
            with download_col:
                output = BytesIO()
                st.session_state.works_df.to_excel(output, engine="openpyxl")
                date = datetime.now().strftime("%Y-%m-%d")
                st.download_button(
                    ":material/download:",
                    data=output.getvalue(),
                    file_name=f"LRA_downloads_{date}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    type="primary",
                    help="Download the review done so far as an excel",
                    width="stretch",
                )

            # Under navigation options,
            # we display the abstract of the work, if available
            st.write(
                current_work["Abstract"]
                if "Abstract" in current_work
                else "No abstract available."
            )
    with tags_col:
        st.subheader("**Assign Tags**")
        for tag, options in st.session_state.tags_dict.items():
            # If the tag is already filled for the current work,
            # we set it as the default selection
            assignment = st.session_state.works_df.at[
                st.session_state.current_work_index, tag
            ]
            if pd.notnull(assignment):
                current_values = [v.strip() for v in assignment.split(",")]
            else:
                current_values = None
            key = f"{tag}_{st.session_state.current_work_index}"
            label = f"**{tag}**"
            if tag in ["Adherence", "Contribution Type"]:
                label = ":material/lock: " + label
            st.pills(
                label,
                options,
                key=key,
                selection_mode="single" if tag == "Adherence" else "multi",
                default=current_values,
                on_change=process_tag_selections,
                args=(tag, options, key),
            )

    # Update Status column based on the number of
    # "None" values left in the tag columns
    for i in st.session_state.works_df.index:
        row = st.session_state.works_df.loc[i]
        tag_values = row[st.session_state.tags]
        none_count = tag_values.isnull().sum()
        n_tags = len(st.session_state.tags_dict)
        completion_status = n_tags - none_count
        st.session_state.works_df.loc[i, "Tags Done"] = completion_status

    # Update the progress overview expander
    # Makes a tile color coding each work according to its review status
    with progress_expander:
        # Pill buttons for filtering works by completion status
        selections = st.pills("Filter by", legends.values(), selection_mode="multi")

        # Message on the amount of works selected
        selection_results = st.container()

        # Slider control for adjusting the number of columns in the grid
        num_columns = st.slider(
            "Number of columns",
            min_value=1,
            max_value=min(max_cols, len(st.session_state.works_df)),
            value=min(max_cols, len(st.session_state.works_df)),
            step=1,
        )
        columns = st.columns(num_columns, gap="small")

        n_selected = 0
        for i, (_, row) in enumerate(st.session_state.works_df.iterrows()):
            # Convert the number of tags done to a percentage
            # for filtering and coloring
            status = row["Tags Done"] / len(st.session_state.tags_dict)

            # Legends are defined for discrete values,
            # so we round the status to the nearest defined legend value
            rounded_status = min(legends.keys(), key=lambda x: abs(x - status))
            if selections and legends.get(rounded_status) not in selections:
                continue

            n_selected += 1
            key = f"work_{i}"
            st.session_state.expander_button_list.append((key, i))
            color = rgb2hex(completion_colormap(status))
            title = row.get("Title", f"Work {i}")

            with columns[i % len(columns)]:
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
                    "",
                    key=key,
                    help=title,
                    width="stretch",
                )

        # Update the selection results message
        with selection_results:
            if st.session_state.total_works == 0:
                percentage = 0
            else:
                percentage = 100 * (n_selected / st.session_state.total_works)

            if n_selected == 1:
                preffix = "Viewing 1 work"
            else:
                preffix = f"Viewing {n_selected} works"

            suffix = f"of {st.session_state.total_works} ({percentage:.2f}%)"
            st.info(f"{preffix} {suffix}")

    # Check if expander button was clicked
    # and update the current work index accordingly
    for key, i in st.session_state.expander_button_list:
        if key in st.session_state and st.session_state[key]:
            st.session_state.current_work_index = i
            st.rerun()

    # Tag management
    # User can introduce or remove a tag field (except for Adherence, Contribution Type)
    # and may add, remove or rename entries in any tag field
    with work_col:
        st.divider()
        st.subheader("**Manage Tags**")
        tag_fields_col, tag_entries_col = st.columns([1, 1], gap="small")
        with tag_fields_col:
            st.subheader("Tag Fields")
            # Add functionality
            add_field_col, add_field_button_col = st.columns(
                [4, 1], gap="small", vertical_alignment="bottom"
            )
            with add_field_col:
                new_field = st.text_input(
                    "Add a new tag field",
                    placeholder="Enter new tag field name",
                    key="new_field_input",
                )
            with add_field_button_col:
                add_field_button = st.button(
                    ":material/add:",
                    key="add_field_button",
                    help="Add a new empty tag field for analysis",
                    width="stretch",
                )
                if add_field_button:
                    new_field = new_field.strip()
                    if new_field and new_field not in st.session_state.tags_dict:
                        st.session_state.tags_dict[new_field] = []
                        st.session_state.works_df[new_field] = None
                        st.session_state.tags.append(new_field)
                        st.rerun()

            # Remove functionality
            delete_field_col, delete_field_button_col = st.columns(
                [4, 1], gap="small", vertical_alignment="bottom"
            )
            with delete_field_col:
                field_to_delete = st.selectbox(
                    "Remove a tag field",
                    options=[
                        tag
                        for tag in st.session_state.tags
                        if tag not in ["Adherence", "Contribution Type"]
                    ],
                    key="delete_field_select",
                    index=None,
                )
            with delete_field_button_col:
                delete_field_button = st.button(
                    ":material/delete:",
                    key="delete_field_button",
                    help="Delete a tag field and all its values",
                    width="stretch",
                )
                if delete_field_button:
                    if field_to_delete in st.session_state.tags_dict:
                        del st.session_state.tags_dict[field_to_delete]
                        st.session_state.works_df.drop(
                            columns=[field_to_delete], inplace=True
                        )
                        st.session_state.tags.remove(field_to_delete)
                        st.rerun()

            # Rename functionality
            rename_field_select_col, rename_field_input_col, rename_field_button_col = (
                st.columns([2, 2, 1], gap="small", vertical_alignment="bottom")
            )
            with rename_field_select_col:
                field_to_rename = st.selectbox(
                    "Rename a tag field",
                    options=[
                        tag
                        for tag in st.session_state.tags
                        if tag not in ["Adherence", "Contribution Type"]
                    ],
                    key="rename_field_select",
                    index=None,
                )
            with rename_field_input_col:
                new_field_name = st.text_input(
                    "New name",
                    placeholder="Enter new name",
                    key="rename_field_input",
                )
            with rename_field_button_col:
                rename_field_button = st.button(
                    ":material/edit:",
                    key="rename_field_button",
                    help="Rename a tag field",
                    width="stretch",
                )
                if rename_field_button:
                    new_field_name = new_field_name.strip()
                    if (
                        field_to_rename in st.session_state.tags_dict
                        and new_field_name
                        and new_field_name not in st.session_state.tags_dict
                    ):
                        # Rename the column in the dataframe
                        st.session_state.works_df.rename(
                            columns={field_to_rename: new_field_name}, inplace=True
                        )
                        # Update the tags list and dict
                        st.session_state.tags.remove(field_to_rename)
                        st.session_state.tags.append(new_field_name)
                        st.session_state.tags_dict[new_field_name] = (
                            st.session_state.tags_dict.pop(field_to_rename)
                        )
                        st.rerun()

        # Each tag field has an expander where
        # user can manage its entries (add, remove, rename)
        with tag_entries_col:
            st.subheader("Tag Entries")
            if st.session_state.tags == ["Adherence", "Contribution Type"]:
                st.info("New tag fields will appear here.")
                return

            tags_not_default = [
                tag
                for tag in st.session_state.tags
                if tag not in ["Adherence", "Contribution Type"]
            ]

            for tag in tags_not_default:
                tag_expander = st.expander(
                    f"Manage entries for '{tag}'", expanded=False
                )
                # An expander is similar to the tag field management section,
                # but for entries instead of fields
                with tag_expander:
                    entries = st.session_state.tags_dict.get(tag, [])
                    if entries is None:
                        entries = []
                    # Add functionality
                    add_entry_input_col, add_entry_button_col = st.columns(
                        [4, 1], gap="small", vertical_alignment="bottom"
                    )
                    with add_entry_input_col:
                        new_entry = st.text_input(
                            "Add a new entry",
                            placeholder="Enter new entry",
                            key=f"new_entry_input_{tag}",
                        )
                    with add_entry_button_col:
                        add_entry_button = st.button(
                            ":material/add:",
                            key=f"add_entry_button_{tag}",
                            help=f"Add a new entry to the '{tag}' field",
                            width="stretch",
                        )
                    if add_entry_button:
                        new_entry = new_entry.strip()
                        if (
                            new_entry
                            and new_entry not in st.session_state.tags_dict[tag]
                        ):
                            st.session_state.tags_dict[tag].append(new_entry)
                            st.rerun()

                    # Remove fuctionality
                    delete_entry_select_col, delete_entry_button_col = st.columns(
                        [4, 1], gap="small", vertical_alignment="bottom"
                    )
                    with delete_entry_select_col:
                        entry_to_delete = st.selectbox(
                            "Remove an entry",
                            options=st.session_state.tags_dict.get(tag, []),
                            key=f"delete_entry_select_{tag}",
                            index=None,
                        )
                    with delete_entry_button_col:
                        delete_entry_button = st.button(
                            ":material/delete:",
                            key=f"delete_entry_button_{tag}",
                            help=f"Delete an entry from the '{tag}' field",
                            width="stretch",
                        )
                    if delete_entry_button:
                        if (
                            entry_to_delete
                            and entry_to_delete in st.session_state.tags_dict[tag]
                        ):
                            st.session_state.tags_dict[tag].remove(entry_to_delete)
                            # Also remove the entry from any works that have it assigned
                            for i in st.session_state.works_df.index:
                                current_value = st.session_state.works_df.at[i, tag]
                                if pd.notnull(current_value):
                                    current_values = [
                                        v.strip() for v in current_value.split(",")
                                    ]
                                    if entry_to_delete in current_values:
                                        current_values.remove(entry_to_delete)
                                        if current_values:
                                            st.session_state.works_df.at[i, tag] = (
                                                ", ".join(current_values)
                                            )
                                        else:
                                            st.session_state.works_df.at[i, tag] = None
                            st.rerun()

                    # Rename functionality
                    (
                        rename_entry_select_col,
                        rename_entry_input_col,
                        rename_entry_button_col,
                    ) = st.columns([2, 2, 1], gap="small", vertical_alignment="bottom")
                    with rename_entry_select_col:
                        entry_to_rename = st.selectbox(
                            "Rename an entry",
                            options=st.session_state.tags_dict.get(tag, []),
                            key=f"rename_entry_select_{tag}",
                            index=None,
                        )
                    with rename_entry_input_col:
                        new_entry_name = st.text_input(
                            "",
                            placeholder="Enter new name",
                            key=f"rename_entry_input_{tag}",
                        )
                    with rename_entry_button_col:
                        rename_entry_button = st.button(
                            ":material/edit:",
                            key=f"rename_entry_button_{tag}",
                            help=f"Rename an entry from the '{tag}' field",
                            width="stretch",
                        )
                    if rename_entry_button:
                        new_entry_name = new_entry_name.strip()
                        if (
                            entry_to_rename
                            and new_entry_name
                            and new_entry_name not in st.session_state.tags_dict[tag]
                        ):
                            # Update the entry in the tags dict
                            entries = st.session_state.tags_dict.get(tag, [])
                            if entries is not None:
                                index = entries.index(entry_to_rename)
                                st.session_state.tags_dict[tag][index] = new_entry_name
                                # Also update the entry in any works that have it assigned
                                for i in st.session_state.works_df.index:
                                    current_value = st.session_state.works_df.at[i, tag]
                                    if pd.notnull(current_value):
                                        current_values = [
                                            v.strip() for v in current_value.split(",")
                                        ]
                                        if entry_to_rename in current_values:
                                            current_values = [
                                                new_entry_name
                                                if v.strip() == entry_to_rename
                                                else v.strip()
                                                for v in current_values
                                            ]
                                            st.session_state.works_df.at[i, tag] = (
                                                ", ".join(current_values)
                                            )
                                st.rerun()

    # Dataframe display for debugging purposes
    with st.expander("Dataframe Debug View", expanded=True):
        st.dataframe(
            st.session_state.works_df[st.session_state.tags + ["Tags Done"]],
            width="stretch",
        )


if __name__ == "__main__":
    main()
