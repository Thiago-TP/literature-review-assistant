from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import pandas as pd


@dataclass
class DatasetContext:
    dataset_key: str
    works_df: pd.DataFrame
    assignments_df: pd.DataFrame
    input_columns: list[str]
    labels: dict[str, list[str]]


@dataclass
class UploadIdentity:
    name: str
    size: int

    @classmethod
    def from_uploaded_file(cls, uploaded_file: Any) -> "UploadIdentity":
        name = str(getattr(uploaded_file, "name", "uploaded_file.xlsx"))
        size = int(getattr(uploaded_file, "size", 0))
        return cls(name=name, size=size)
