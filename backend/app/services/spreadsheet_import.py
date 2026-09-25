"""Parses an uploaded export (.xlsx or .csv, from Scopus, Web of Science, or a
hand-built sheet) into plain paper rows. Only Title/Abstract are required; DOI,
Authors, Year and Source title are picked up when present but optional. Any
other columns are preserved in `raw_metadata` so nothing is silently lost."""

from __future__ import annotations

import csv
import math
from dataclasses import dataclass
from io import BytesIO, StringIO

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

# The format is read from the file's first bytes rather than its name, so a
# renamed download, or an upload whose name the browser did not send, still
# lands on the right reader. An .xlsx is a zip archive; a legacy .xls is an OLE
# compound file, which pandas could only read with a library we do not ship.
_ZIP_SIGNATURE = b"PK\x03\x04"
_OLE_SIGNATURE = b"\xd0\xcf\x11\xe0\xa1\xb1\x1a\xe1"

# UTF-8 first (utf-8-sig also strips the byte-order mark Scopus writes), then
# Windows-1252, which is what Excel on Windows still produces from a plain
# "CSV" save and which UTF-8 would reject on the first accented name.
_CSV_ENCODINGS = ("utf-8-sig", "cp1252")
# Scopus writes commas, but Excel writes semicolons in locales where the comma
# is the decimal separator, so a hand-edited export can arrive either way.
_CSV_DELIMITERS = ",;\t"


class SpreadsheetImportError(ValueError):
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


def _read_xlsx(file_bytes: bytes) -> pd.DataFrame:
    try:
        return pd.read_excel(BytesIO(file_bytes))
    except Exception as exc:  # pandas/openpyxl raise a variety of error types
        raise SpreadsheetImportError(f"Could not read the uploaded file as .xlsx: {exc}") from exc


def _decode_csv(file_bytes: bytes) -> str:
    for encoding in _CSV_ENCODINGS:
        try:
            return file_bytes.decode(encoding)
        except UnicodeDecodeError:
            continue
    raise SpreadsheetImportError(
        "Could not work out the text encoding of the uploaded .csv. "
        "Save it as 'CSV UTF-8' and try again."
    )


def _csv_delimiter(text: str) -> str:
    """The delimiter, judged from the header row alone.

    Only the header, because it is the one row with no free text in it:
    abstracts and author lists are full of commas and semicolons (Scopus
    separates authors with "; "), which would muddy a guess taken over the
    whole file. A header with a single column has nothing to judge by, and a
    single column is the same file whatever the delimiter, so comma it is.
    """
    header = text.split("\n", 1)[0]
    try:
        return csv.Sniffer().sniff(header, delimiters=_CSV_DELIMITERS).delimiter
    except csv.Error:
        return ","


def _read_csv(file_bytes: bytes) -> pd.DataFrame:
    text = _decode_csv(file_bytes)
    try:
        # Every column as text, with no NA guessing: otherwise a DOI or title
        # that happens to look like a number, or like "NA", is mangled before
        # it reaches us. Blank cells come through as "" and _clean drops them.
        return pd.read_csv(
            StringIO(text), sep=_csv_delimiter(text), dtype=str, keep_default_na=False
        )
    except Exception as exc:  # pandas raises several parser/empty-data error types
        raise SpreadsheetImportError(f"Could not read the uploaded file as .csv: {exc}") from exc


def _read_frame(file_bytes: bytes) -> pd.DataFrame:
    if file_bytes.startswith(_ZIP_SIGNATURE):
        return _read_xlsx(file_bytes)
    if file_bytes.startswith(_OLE_SIGNATURE):
        raise SpreadsheetImportError(
            "This looks like an old-style .xls file, which is not supported. "
            "Save it as .xlsx or .csv and try again."
        )
    # Text never contains a NUL byte; anything that does is some other binary
    # format, and reading it as CSV would only produce a baffling
    # missing-columns error.
    if b"\x00" in file_bytes[:4096]:
        raise SpreadsheetImportError("The uploaded file is neither an .xlsx nor a .csv file.")
    return _read_csv(file_bytes)


def parse_spreadsheet(file_bytes: bytes) -> list[ParsedRow]:
    df = _read_frame(file_bytes)

    missing = [col for col in REQUIRED_COLUMNS if col not in df.columns]
    if missing:
        raise SpreadsheetImportError(
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
