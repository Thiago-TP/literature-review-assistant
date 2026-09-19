import pytest

from app.services.xlsx_import import XlsxImportError, parse_xlsx
from tests.conftest import SAMPLE_XLSX_PATH


def test_parse_sample_export():
    rows = parse_xlsx(SAMPLE_XLSX_PATH.read_bytes())
    assert len(rows) == 5
    first = rows[0]
    assert first.title
    assert first.abstract
    assert first.doi
    assert first.authors
    assert first.year == 2023
    assert "Author Keywords" in first.raw_metadata


def test_parse_rejects_missing_required_columns():
    import io

    import pandas as pd

    buffer = io.BytesIO()
    pd.DataFrame({"Foo": ["bar"]}).to_excel(buffer, index=False)
    buffer.seek(0)

    with pytest.raises(XlsxImportError) as excinfo:
        parse_xlsx(buffer.getvalue())
    assert "Title" in str(excinfo.value)
