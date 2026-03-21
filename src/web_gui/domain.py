from __future__ import annotations

from pathlib import Path
from typing import Any

import pandas as pd

from . import constants


def normalize(name: str) -> str:
    return " ".join(str(name).strip().lower().replace("_", " ").split())


def safe_str(value: Any) -> str:
    if pd.isna(value):
        return ""
    return str(value)


def find_matching_column(df: pd.DataFrame,
                         candidates: list[str]) -> str | None:
    normalized_to_original = {normalize(col): col for col in df.columns}
    for candidate in candidates:
        hit = normalized_to_original.get(normalize(candidate))
        if hit is not None:
            return hit
    return None


def dataset_key_from_upload(file_name: str, file_size: int) -> str:
    stem = Path(file_name).stem
    sanitized = "".join(ch if ch.isalnum()
                        or ch in "-_" else "_" for ch in stem)
    return f"{sanitized}_{file_size}"


def read_uploaded_excel(uploaded_file: Any) -> tuple[pd.DataFrame, list[str]]:
    df = pd.read_excel(uploaded_file)
    if df.empty:
        raise ValueError("Uploaded Excel is empty.")

    input_columns = list(df.columns)
    adapted = df.copy()

    resolved = {
        key: find_matching_column(df, aliases)
        for key, aliases in constants.CANONICAL_FIELDS.items()
    }
    for canonical_name, original_col in resolved.items():
        adapted[canonical_name] = df[original_col].map(
            safe_str) if original_col else ""

    source_file = safe_str(
        getattr(uploaded_file, "name", "uploaded_file.xlsx"))
    adapted["source_file"] = source_file
    adapted["source_row"] = range(1, len(adapted) + 1)

    adapted["work_id"] = adapted.apply(
        lambda row: (
            f"{row['source_file']}::{row['source_row']}::"
            f"{normalize(row['title'])[:120]}"
        ),
        axis=1,
    )
    return adapted, input_columns


def find_input_label_columns(
    input_df: pd.DataFrame,
) -> dict[str, str | None]:
    """Check if input dataframe has label columns and return mapping."""
    result = {}
    for label_col in constants.LABEL_COLUMNS:
        result[label_col] = find_matching_column(
            input_df, [label_col]
        )
    return result


def extract_assignments_from_input(
    input_df: pd.DataFrame,
    works_df: pd.DataFrame,
) -> pd.DataFrame | None:
    """Extract label assignments from input file if columns exist."""
    input_label_cols = find_input_label_columns(input_df)

    # If no label columns found, return empty assignments
    if all(v is None for v in input_label_cols.values()):
        return None

    # Create a frame with only the label data from input
    label_data = {"work_id": works_df["work_id"].copy()}
    for label_col, input_col in input_label_cols.items():
        if input_col is not None:
            # Align input data by row index with works_df
            label_data[label_col] = (
                input_df[input_col]
                .iloc[:len(works_df)]
                .map(safe_str)
                .values
            )
        else:
            label_data[label_col] = constants.PENDING_DIAGNOSTIC

    input_assignments = pd.DataFrame(label_data)
    return input_assignments


def extract_tags_from_input(
    input_df: pd.DataFrame,
) -> dict[str, list[str]]:
    """Extract unique values from label columns to populate tags."""
    input_label_cols = find_input_label_columns(input_df)
    tags = {col: [] for col in constants.LABEL_COLUMNS}

    for label_col, input_col in input_label_cols.items():
        if input_col is not None:
            unique_vals = set(input_df[input_col].map(safe_str).unique())
            unique_vals.discard("")
            unique_vals.discard(constants.PENDING_DIAGNOSTIC)
            tags[label_col] = sorted(list(unique_vals))

    return tags


def empty_assignments_frame(works_df: pd.DataFrame) -> pd.DataFrame:
    assignments = pd.DataFrame({"work_id": works_df["work_id"]})
    for col in constants.LABEL_COLUMNS:
        assignments[col] = constants.PENDING_DIAGNOSTIC
    return assignments


def merge_existing_assignments(base_df: pd.DataFrame,
                               existing_path: Path) -> pd.DataFrame:
    if not existing_path.exists():
        return base_df

    loaded = pd.read_excel(existing_path)
    keep_cols = ["work_id", *constants.LABEL_COLUMNS]

    if "work_id" in loaded.columns:
        available_cols = [col for col in keep_cols if col in loaded.columns]
        loaded = loaded[available_cols].copy()

        for col in constants.LABEL_COLUMNS:
            if col not in loaded.columns:
                loaded[col] = constants.PENDING_DIAGNOSTIC

        merged = base_df.merge(
            loaded[["work_id", *constants.LABEL_COLUMNS]],
            on="work_id",
            how="left",
            suffixes=("", "_old"),
        )

        for col in constants.LABEL_COLUMNS:
            combined = merged[f"{col}_old"].fillna(merged[col]).map(safe_str)
            combined = combined.replace("", constants.PENDING_DIAGNOSTIC)
            merged.loc[:, col] = combined
            merged = merged.drop(columns=[f"{col}_old"])
        return merged

    if not set(constants.LABEL_COLUMNS).issubset(set(loaded.columns)):
        return base_df

    merged = base_df.copy()
    for col in constants.LABEL_COLUMNS:
        loaded_values = loaded[col].map(safe_str).reset_index(drop=True)
        preferred = pd.Series(loaded_values, index=merged.index)
        merged.loc[:, col] = preferred.where(
            preferred != "",
            merged[col].map(safe_str),
        )
        merged.loc[:, col] = merged[col].map(safe_str).replace(
            "", constants.PENDING_DIAGNOSTIC
        )
    return merged


def clean_deleted_tags(
    assignments_df: pd.DataFrame,
    labels: dict[str, list[str]],
) -> pd.DataFrame:
    cleaned = assignments_df.copy()
    for col in constants.LABEL_COLUMNS:
        if col in {constants.DIAGNOSTIC_COLUMN, constants.CONTRIBUTION_COLUMN}:
            cleaned.loc[:, col] = cleaned[col].replace(
                "", constants.PENDING_DIAGNOSTIC
            )
            continue

        valid = set(labels.get(col, []))
        cleaned.loc[:, col] = cleaned[col].apply(
            lambda value: (
                value
                if value in valid or value == constants.PENDING_DIAGNOSTIC
                else constants.PENDING_DIAGNOSTIC
            )
        )
    return cleaned


def reviewed_count(assignments_df: pd.DataFrame) -> int:
    diagnostic = assignments_df[constants.DIAGNOSTIC_COLUMN].map(
        lambda x: safe_str(x).strip())
    is_reviewed = diagnostic.map(
        lambda x: x not in {"", constants.PENDING_DIAGNOSTIC}
    )
    return int(is_reviewed.sum())


def current_work_assigned_count(assignments_df: pd.DataFrame, idx: int) -> int:
    row = assignments_df.iloc[idx]
    assigned = sum(
        1
        for col in constants.LABEL_COLUMNS
        if safe_str(row[col]).strip() not in {"", constants.PENDING_DIAGNOSTIC}
    )
    return int(assigned)


def rename_tag_in_state(
    labels: dict[str, list[str]],
    assignments_df: pd.DataFrame,
    label_col: str,
    old_tag: str,
    new_tag: str,
) -> tuple[bool, dict[str, list[str]], pd.DataFrame]:
    old_value = safe_str(old_tag).strip()
    new_value = safe_str(new_tag).strip()
    if not old_value or not new_value or old_value == new_value:
        return False, labels, assignments_df

    tags = labels.get(label_col, [])
    if old_value not in tags:
        return False, labels, assignments_df

    next_labels = labels.copy()
    next_labels[label_col] = sorted(
        {new_value if tag == old_value else tag for tag in tags},
        key=str.casefold,
    )

    next_assignments = assignments_df.copy()
    next_assignments.loc[:, label_col] = next_assignments[label_col].apply(
        lambda value: new_value if safe_str(
            value).strip() == old_value else value
    )

    return True, next_labels, next_assignments
