"""
Configuration constants for the Literature Review Assistant.

This module defines all static configuration values for tag options, column names,
UI parameters, and visualization settings used throughout the application.
"""

# ============================================================================
# Tag Options - Classification Categories for Papers
# ============================================================================

# Adherence levels for classification - how well a paper aligns with review scope
ADHERENCE_OPTIONS = ["Insufficient", "Partial", "Sufficient"]

# Contribution types - categorizes the nature of the paper's contribution
CONTRIBUTION_OPTIONS = ["Improvement", "New Method", "Review", "Other"]

# Required fields that cannot be removed from the tagging interface
REQUIRED_FIELDS = {
    "Adherence": ADHERENCE_OPTIONS,
    "Contribution Type": CONTRIBUTION_OPTIONS,
}

# ============================================================================
# Excel Column Names - Expected columns in input files
# ============================================================================

# Column containing paper abstract text
ABSTRACT_COLUMN = "Abstract"

# Column containing paper title
TITLE_COLUMN = "Title"

# Column containing Digital Object Identifier (DOI) - links to paper
DOI_COLUMN = "DOI"

# Column for user notes and comments on papers
NOTE_COLUMN = "Notes"

# ============================================================================
# UI Configuration Parameters
# ============================================================================

# Maximum number of columns to display in progress overview matrix
# Higher values create wider matrices; controls responsive layout behavior
MAX_COLS_IN_OVERVIEW = 30

# Matplotlib colormap for progress visualization (RdYlGn = Red-Yellow-Green)
# Used in progress overview to show completion status across papers
COLORMAP = "RdYlGn"
