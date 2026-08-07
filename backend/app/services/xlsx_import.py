"""Parses an uploaded .xlsx export (Scopus, Web of Science, or a hand-built
sheet) into plain paper rows. Only Title/Abstract are required; DOI, Authors,
Year and Source title are picked up when present but optional. Any other
columns are preserved in `raw_metadata` so nothing is silently lost."""

from __future__ import annotations

import math
from dataclasses import dataclass
from io import BytesIO

import pandas as pd

REQUIRED_COLUMNS = ("Title", "Abstract")
KNOWN_COLUMNS = {
    "Title": "title",
    "Abstract": "abstract",
    "DOI": "doi",
    "Authors": "authors",
    "Year": "year",
    "Source title": "source_title",
}


class XlsxImportError(ValueError):
    pass


@dataclass
class ParsedRow:
    title: str
    abstract: str | None
    doi: str | None
    authors: str | None
    year: int | None
    source_title: str | None
    raw_metadata: dict


def _clean(value: object) -> str | None:
    if value is None:
        return None
    if isinstance(value, float) and math.isnan(value):
        return None
    text = str(value).strip()
    return text or None


def parse_xlsx(file_bytes: bytes) -> list[ParsedRow]:
    try:
        df = pd.read_excel(BytesIO(file_bytes))
    except Exception as exc:  # pandas/openpyxl raise a variety of error types
        raise XlsxImportError(f"Could not read the uploaded file as .xlsx: {exc}") from exc

    missing = [col for col in REQUIRED_COLUMNS if col not in df.columns]
    if missing:
        raise XlsxImportError(
            "Missing required column(s): " + ", ".join(missing) + ". "
            "Expected at least 'Title' and 'Abstract' columns."
        )

    rows: list[ParsedRow] = []
    for _, record in df.iterrows():
        row_dict = record.to_dict()
        title = _clean(row_dict.get("Title"))
        if not title:
            continue  # skip blank rows

        year_raw = _clean(row_dict.get("Year"))
        year = None
        if year_raw:
            try:
                year = int(float(year_raw))
            except ValueError:
                year = None

        extra_metadata = {
            key: _clean(value)
            for key, value in row_dict.items()
            if key not in KNOWN_COLUMNS and _clean(value) is not None
        }

        rows.append(
            ParsedRow(
                title=title,
                abstract=_clean(row_dict.get("Abstract")),
                doi=_clean(row_dict.get("DOI")),
                authors=_clean(row_dict.get("Authors")),
                year=year,
                source_title=_clean(row_dict.get("Source title")),
                raw_metadata=extra_metadata,
            )
        )

    return rows
