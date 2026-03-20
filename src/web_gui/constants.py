from __future__ import annotations

from pathlib import Path

CANONICAL_FIELDS = {
    "title": ["Title"],
    "authors": ["Authors"],
    "journal": ["Source title"],
    "date": ["Year"],
    "abstract": ["Abstract"],
}

SCOPE_COLUMN = "Application Scope"
METHODOLOGY_COLUMN = "Methodology"
CONTRIBUTION_COLUMN = "Contribution Type"
DIAGNOSTIC_COLUMN = "Adherence"

LABEL_COLUMNS = [
    SCOPE_COLUMN,
    METHODOLOGY_COLUMN,
    CONTRIBUTION_COLUMN,
    DIAGNOSTIC_COLUMN,
]

PENDING_DIAGNOSTIC = "PENDING"
CONTRIBUTION_OPTIONS = [
    PENDING_DIAGNOSTIC,
    "New Method",
    "Improvement",
    "Review",
]
DIAGNOSTIC_OPTIONS = [
    PENDING_DIAGNOSTIC,
    "Insufficient",
    "Partial",
    "Sufficient",
]

LABELS_FILE_SUFFIX = "_labels.json"
TEMP_RESULTS_SUFFIX = "_tmp_review.xlsx"
FINAL_RESULTS_SUFFIX = "_review_final"

PROJECT_ROOT = Path(__file__).resolve().parents[2]
RESULTS_DIR = PROJECT_ROOT / "results"
