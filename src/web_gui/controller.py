from __future__ import annotations

from pathlib import Path
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
    state.setdefault("last_saved_path", "")
    state.setdefault("last_exported_path", "")


def reset_dataset_state() -> None:
    st.session_state.works_df = None
    st.session_state.assignments_df = None
    st.session_state.input_columns = []
    st.session_state.dataset_key = ""
    st.session_state.loaded_file_token = ""


def build_upload_token(uploaded_file: Any) -> str:
    identity = UploadIdentity.from_uploaded_file(uploaded_file)
    return f"{identity.name}::{identity.size}"


def load_dataset_from_upload(uploaded_file: Any) -> None:
    identity = UploadIdentity.from_uploaded_file(uploaded_file)
    dataset_key = domain.dataset_key_from_upload(identity.name, identity.size)

    works_df, input_columns = domain.read_uploaded_excel(uploaded_file)
    labels = persistence.load_labels(dataset_key)

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
    path = persistence.save_temp_excel(
        dataset_key,
        works_df,
        assignments,
        input_columns,
    )
    st.session_state.last_saved_path = str(path)


def update_assignment(label_col: str, selected_tag: str) -> None:
    idx = st.session_state.current_index
    st.session_state.assignments_df.at[idx, label_col] = domain.safe_str(
        selected_tag).strip()
    persist_temp()


def persist_temp() -> Path:
    path = persistence.save_temp_excel(
        st.session_state.dataset_key,
        st.session_state.works_df,
        st.session_state.assignments_df,
        st.session_state.input_columns,
    )
    st.session_state.last_saved_path = str(path)
    return path


def export_final() -> Path:
    path = persistence.save_final_excel(
        st.session_state.dataset_key,
        st.session_state.works_df,
        st.session_state.assignments_df,
        st.session_state.input_columns,
    )
    st.session_state.last_exported_path = str(path)
    return path


def get_export_file_data() -> bytes:
    path_str = st.session_state.last_exported_path
    if not path_str:
        return b""

    path = Path(path_str)
    if not path.exists():
        return b""
    return path.read_bytes()


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
    persist_temp()
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
    persist_temp()
    return True


def save_and_quit_feedback() -> str:
    path = persist_temp()
    return str(path)


def queue_toast(message: str, icon: str = ":material/check_circle:") -> None:
    st.session_state["queued_toast"] = {"message": message, "icon": icon}


def show_queued_toast() -> None:
    payload = st.session_state.pop("queued_toast", None)
    if payload:
        st.toast(
            payload.get("message", ""),
            icon=payload.get("icon", ":material/check_circle:"),
        )


def reviewed_count(assignments_df: pd.DataFrame) -> int:
    return domain.reviewed_count(assignments_df)


def current_work_assigned_count(assignments_df: pd.DataFrame, idx: int) -> int:
    return domain.current_work_assigned_count(assignments_df, idx)
