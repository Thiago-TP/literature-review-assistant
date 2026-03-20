from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path

import pandas as pd

from . import constants
from .domain import safe_str


def labels_file_path(dataset_key: str,
                     results_dir: Path = constants.RESULTS_DIR) -> Path:
    return results_dir / f"{dataset_key}{constants.LABELS_FILE_SUFFIX}"


def temp_results_path(dataset_key: str,
                      results_dir: Path = constants.RESULTS_DIR) -> Path:
    return results_dir / f"{dataset_key}{constants.TEMP_RESULTS_SUFFIX}"


def final_results_path(dataset_key: str,
                       results_dir: Path = constants.RESULTS_DIR) -> Path:
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return results_dir / f"{dataset_key}{constants.FINAL_RESULTS_SUFFIX}_{timestamp}.xlsx"  # noqa: E501


def load_labels(
    dataset_key: str,
    results_dir: Path = constants.RESULTS_DIR,
) -> dict[str, list[str]]:
    path = labels_file_path(dataset_key, results_dir)
    if not path.exists():
        return {column: [] for column in constants.LABEL_COLUMNS}

    data = json.loads(path.read_text(encoding="utf-8"))
    labels: dict[str, list[str]] = {}
    for column in constants.LABEL_COLUMNS:
        values = data.get(column, [])
        labels[column] = sorted(
            {safe_str(v).strip() for v in values if safe_str(v).strip()}
        )
    return labels


def save_labels(
    dataset_key: str,
    labels: dict[str, list[str]],
    results_dir: Path = constants.RESULTS_DIR,
) -> Path:
    path = labels_file_path(dataset_key, results_dir)
    path.parent.mkdir(parents=True, exist_ok=True)

    serializable = {
        col: sorted({safe_str(tag).strip()
                    for tag in tags if safe_str(tag).strip()})
        for col, tags in labels.items()
    }
    path.write_text(
        json.dumps(serializable, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    return path


def save_temp_excel(
    dataset_key: str,
    works_df: pd.DataFrame,
    assignments_df: pd.DataFrame,
    input_columns: list[str],
    results_dir: Path = constants.RESULTS_DIR,
) -> Path:
    out_path = temp_results_path(dataset_key, results_dir)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    output_df = works_df[input_columns].copy()
    for col in constants.LABEL_COLUMNS:
        output_df[col] = assignments_df[col].values
    output_df.to_excel(out_path, index=False)
    return out_path


def save_final_excel(
    dataset_key: str,
    works_df: pd.DataFrame,
    assignments_df: pd.DataFrame,
    input_columns: list[str],
    results_dir: Path = constants.RESULTS_DIR,
) -> Path:
    out_path = final_results_path(dataset_key, results_dir)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    output_df = works_df[input_columns].copy()
    for col in constants.LABEL_COLUMNS:
        output_df[col] = assignments_df[col].values
    output_df.to_excel(out_path, index=False)
    return out_path
