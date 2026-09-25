import io

import pandas as pd
import pytest

from app.services.spreadsheet_import import SpreadsheetImportError, parse_spreadsheet
from tests.conftest import SAMPLE_CSV_PATH, SAMPLE_XLSX_PATH


def test_parse_sample_export():
    rows = parse_spreadsheet(SAMPLE_XLSX_PATH.read_bytes())
    assert len(rows) == 5
    first = rows[0]
    assert first.title
    assert first.abstract
    assert first.doi
    assert first.authors
    assert first.year == 2023
    assert "Author Keywords" in first.raw_metadata


def test_parse_rejects_missing_required_columns():
    buffer = io.BytesIO()
    pd.DataFrame({"Foo": ["bar"]}).to_excel(buffer, index=False)
    buffer.seek(0)

    with pytest.raises(SpreadsheetImportError) as excinfo:
        parse_spreadsheet(buffer.getvalue())
    assert "Title" in str(excinfo.value)


def test_csv_export_parses_the_same_as_the_xlsx():
    # The two fixtures hold the same rows, so which format a database was
    # exported in must make no difference to what gets imported.
    assert parse_spreadsheet(SAMPLE_CSV_PATH.read_bytes()) == parse_spreadsheet(
        SAMPLE_XLSX_PATH.read_bytes()
    )


def test_csv_with_semicolons_in_windows_1252():
    # What Excel produces from "Save as CSV" in a locale whose decimal
    # separator is a comma, on Windows: semicolon-delimited and not UTF-8.
    # Excel quotes only the cells that hold the delimiter, like Authors here.
    text = (
        "Title;Abstract;Authors;Year\n"
        'Análise de revisões;Um resumo, com vírgulas;"João S.; Maria C.";2021\n'
    )

    [row] = parse_spreadsheet(text.encode("cp1252"))

    assert row.title == "Análise de revisões"
    assert row.abstract == "Um resumo, com vírgulas"
    assert row.authors == "João S.; Maria C."
    assert row.year == 2021


def test_csv_values_are_kept_as_text():
    # Left to guess, pandas turns "NA" into a missing value and "2021.10" into
    # a float; neither is acceptable for a title or a DOI.
    text = "Title,Abstract,DOI,Year\nNA,,2021.10,not a year\n"

    [row] = parse_spreadsheet(text.encode())

    assert row.title == "NA"
    assert row.abstract is None
    assert row.doi == "2021.10"
    assert row.year is None


def test_csv_missing_required_columns():
    with pytest.raises(SpreadsheetImportError) as excinfo:
        parse_spreadsheet(b"Title,DOI\nA paper,10.0000/x\n")
    assert "Abstract" in str(excinfo.value)


def test_rejects_legacy_xls():
    with pytest.raises(SpreadsheetImportError) as excinfo:
        parse_spreadsheet(b"\xd0\xcf\x11\xe0\xa1\xb1\x1a\xe1" + b"\x00" * 64)
    assert ".xls" in str(excinfo.value)


def test_rejects_other_binary_files():
    with pytest.raises(SpreadsheetImportError) as excinfo:
        parse_spreadsheet(b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR")
    assert "neither" in str(excinfo.value)
