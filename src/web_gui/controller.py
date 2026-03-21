from __future__ import annotations

from typing import Any

import pandas as pd
import streamlit as st

from . import constants, domain, persistence
from .models import UploadIdentity


def init_state() -> None:
    state = st.session_state
    state.setdefault("dataset_key", "")
    state.setdefault("loaded_file_token", "")
    state.setdefault("works_df", None)
    state.setdefault("assignments_df", None)
    state.setdefault("input_columns", [])
    state.setdefault("labels", {col: [] for col in constants.LABEL_COLUMNS})
    state.setdefault("current_index", 0)
    state.setdefault("last_exported_name", "")
    state.setdefault("last_exported_bytes", b"")
    state.setdefault("pending_download_action", "")
    state.setdefault("queued_toasts", [])


def reset_dataset_state() -> None:
    st.session_state.works_df = None
    st.session_state.assignments_df = None
    st.session_state.input_columns = []
    st.session_state.dataset_key = ""
    st.session_state.loaded_file_token = ""


def load_dataset_from_upload(uploaded_file: Any) -> None:
    identity = UploadIdentity.from_uploaded_file(uploaded_file)
    dataset_key = domain.dataset_key_from_upload(identity.name, identity.size)

    # Read the raw Excel to check for label columns
    raw_df = pd.read_excel(uploaded_file)

    works_df, input_columns = domain.read_uploaded_excel(uploaded_file)
    labels = persistence.load_labels(dataset_key)

    # Check if input file has label columns and extract them
    input_assignments = domain.extract_assignments_from_input(raw_df, works_df)
    input_tags = domain.extract_tags_from_input(raw_df)

    # Merge input tags with existing labels
    if input_tags:
        for col in constants.LABEL_COLUMNS:
            input_col_tags = input_tags.get(col, [])
            if input_col_tags:
                existing = set(labels.get(col, []))
                existing.update(input_col_tags)
                labels[col] = sorted(list(existing))

    # Use input assignments if available, otherwise use empty + temp merge
    if input_assignments is not None:
        assignments = input_assignments
    else:
        assignments = domain.empty_assignments_frame(works_df)
        assignments = domain.merge_existing_assignments(
            assignments,
            persistence.temp_results_path(dataset_key),
        )

    assignments = domain.clean_deleted_tags(assignments, labels)

    st.session_state.dataset_key = dataset_key
    st.session_state.works_df = works_df
    st.session_state.labels = labels
    st.session_state.assignments_df = assignments
    st.session_state.input_columns = input_columns
    st.session_state.current_index = 0

    persistence.save_labels(dataset_key, labels)


def update_assignment(label_col: str, selected_tag: str) -> None:
    idx = st.session_state.current_index
    next_value = domain.safe_str(selected_tag).strip()
    current_value = domain.safe_str(
        st.session_state.assignments_df.at[idx, label_col]
    ).strip()
    if next_value == current_value:
        return
    st.session_state.assignments_df.at[idx, label_col] = next_value


def export_final() -> str:
    payload = persistence.build_output_excel_bytes(
        st.session_state.works_df,
        st.session_state.assignments_df,
        st.session_state.input_columns,
    )
    filename = persistence.final_results_filename(st.session_state.dataset_key)
    st.session_state.last_exported_name = filename
    st.session_state.last_exported_bytes = payload
    return filename


def get_export_file_data() -> bytes:
    return st.session_state.last_exported_bytes


def add_tag(label_col: str, new_tag: str) -> bool:
    value = domain.safe_str(new_tag).strip()
    if not value:
        return False

    labels = st.session_state.labels.copy()
    tags = set(labels.get(label_col, []))
    before = set(tags)
    tags.add(value)
    if tags == before:
        return False
    labels[label_col] = sorted(tags)
    st.session_state.labels = labels

    persistence.save_labels(st.session_state.dataset_key, labels)
    return True


def remove_tag(label_col: str, tag_to_remove: str) -> bool:
    value = domain.safe_str(tag_to_remove).strip()
    if not value:
        return False

    labels = st.session_state.labels.copy()
    tags = labels.get(label_col, [])
    if value not in tags:
        return False

    labels[label_col] = [tag for tag in tags if tag != value]
    st.session_state.labels = labels

    assignments = domain.clean_deleted_tags(
        st.session_state.assignments_df, labels)
    st.session_state.assignments_df = assignments

    persistence.save_labels(st.session_state.dataset_key, labels)
    return True


def rename_tag(label_col: str, old_tag: str, new_tag: str) -> bool:
    changed, next_labels, next_assignments = domain.rename_tag_in_state(
        st.session_state.labels,
        st.session_state.assignments_df,
        label_col,
        old_tag,
        new_tag,
    )
    if not changed:
        return False

    st.session_state.labels = next_labels
    st.session_state.assignments_df = next_assignments
    persistence.save_labels(st.session_state.dataset_key, next_labels)
    return True


def save_and_quit_feedback() -> str:
    return export_final()


def queue_toast(message: str, icon: str = ":material/check_circle:") -> None:
    queued = list(st.session_state.get("queued_toasts", []))
    queued.append({"message": message, "icon": icon})
    st.session_state["queued_toasts"] = queued


def queue_download_toasts(action: str) -> None:
    if action == "save_and_quit":
        queue_toast("You may close this tab now")
    st.session_state.pending_download_action = ""


def show_queued_toast() -> None:
    queued = list(st.session_state.get("queued_toasts", []))
    for payload in queued:
        st.toast(
            payload.get("message", ""),
            icon=payload.get("icon", ":material/check_circle:"),
        )
    st.session_state["queued_toasts"] = []


def reviewed_count(assignments_df: pd.DataFrame) -> int:
    return domain.reviewed_count(assignments_df)


def current_work_assigned_count(assignments_df: pd.DataFrame, idx: int) -> int:
    return domain.current_work_assigned_count(assignments_df, idx)
