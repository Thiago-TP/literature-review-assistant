from __future__ import annotations

import os
import tempfile
from pathlib import Path

os.environ.setdefault("LRA_DB_PATH", os.path.join(tempfile.gettempdir(), "lra_test_unused.db"))

import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine
from sqlmodel.pool import StaticPool

from app.db import get_session
from app.main import app

TESTS_DIR = Path(__file__).resolve().parent
SAMPLE_XLSX_PATH = TESTS_DIR / "fixtures" / "sample_export.xlsx"
# The same five rows as a Scopus CSV download: byte-order mark, every field quoted.
SAMPLE_CSV_PATH = TESTS_DIR / "fixtures" / "sample_export.csv"


@pytest.fixture(name="session")
def session_fixture():
    engine = create_engine(
        "sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool
    )
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session


@pytest.fixture(name="client")
def client_fixture(session: Session):
    def get_session_override():
        return session

    app.dependency_overrides[get_session] = get_session_override
    with TestClient(app) as client:
        yield client
    app.dependency_overrides.clear()


@pytest.fixture
def project(client: TestClient) -> dict:
    response = client.post("/api/projects", json={"name": "Test Project"})
    assert response.status_code == 201
    return response.json()
