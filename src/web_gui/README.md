# web_gui Module

Core application logic and data handling for the Revisionator literature review system.

## Overview

The `web_gui` module encapsulates all business logic, data models, and application workflow for the Revisionator application. It provides a clean separation between the Streamlit presentation layer and the core functionality.

## Module Structure

### `constants.py`
Configuration and constants used throughout the application:
- **Field Definitions**: Canonical field names and their aliases for Excel column mapping
  - `title`, `authors`, `journal`, `date`, `abstract`
- **Label Columns**: Fields that users can edit during review
  - `Application Scope`: Paper's alignment with research scope
  - `Methodology`: Methodology classification
  - `Contribution Type`: How the paper contributes (enum: "New Method", "Improvement", "Review")
  - `Adherence`: Overall adherence classification (enum: "Insufficient", "Partial", "Sufficient")
- **File Paths**: Project directories for input and result files
- **Diagnostic Options**: Valid values for contribution and adherence fields

### `domain.py`
Business logic and data transformation utilities:
- **Text Normalization**: `normalize()` - standardizes strings for comparison
- **Data Safety**: `safe_str()` - safely converts values to strings, handling null values
- **Column Matching**: `find_matching_column()` - intelligently matches Excel columns to canonical field names
- **File Processing**: `dataset_key_from_upload()` - generates unique keys for datasets
- **Excel Import**: `read_uploaded_excel()` - parses uploaded Excel files and maps columns to canonical fields

### `models.py`
Data models and type definitions for the application. Contains Pydantic models or dataclasses representing:
- Paper metadata
- Review assignments
- Label configurations

### `controller.py`
Application workflow orchestration:
- **Navigation**: Navigate between papers in the review queue
- **Labeling**: Record and update paper labels
- **Progress Tracking**: Calculate review statistics
- **Export**: Generate output files in various formats (JSON, Excel, etc.)
- **Session Management**: Manage review state and persistence

### `persistence.py`
Data storage and file I/O operations:
- **Excel Operations**: Read/write Excel files for import and export
- **JSON Storage**: Serialize and deserialize review labels
- **Temporary Files**: Manage in-progress work files
- **Path Management**: Handle file paths relative to project structure

## Key Concepts

### Field Mapping
When users upload Excel files, the module automatically maps columns to canonical field names using fuzzy matching. This allows flexibility in input file structure while maintaining consistent internal representation.

**Example**: A column named "Author Names" will be matched to the canonical `authors` field.

### Contribution Types (Enum)
Papers are classified by their contribution:
- **New Method**: Introduces novel methodology or approach
- **Improvement**: Enhances or modifies existing methods
- **Review**: Surveys or synthesizes existing literature
- **PENDING**: Not yet classified

### Adherence Classification
Papers are evaluated on adherence to defined criteria:
- **Sufficient**: Paper fully aligns with scope and methodology
- **Partial**: Paper partially aligns with criteria
- **Insufficient**: Paper does not align with criteria
- **PENDING**: Not yet evaluated

## Data Flow

```
1. User uploads Excel file
          ↓
2. Excel imported and columns mapped to canonical fields
          ↓
3. Paper data stored in session state (dataframe)
          ↓
4. User navigates and labels papers
          ↓
5. Labels stored in memory and persistent files
          ↓
6. Results exported as JSON or Excel
```

## Usage in the Streamlit App

The Streamlit application (`src/app.py`) uses this module like this:

```python
from web_gui import constants, controller, domain

# Import and process a file
df, original_cols = domain.read_uploaded_excel(uploaded_file)

# Get review statistics
reviewed = controller.reviewed_count(assignments_df)

# Export results
export_path = controller.export_final()
```

## Testing

Unit tests for this module are located in `tests/`:
- `test_review_web_gui_domain.py` - Domain logic tests
- `test_review_web_gui_controller.py` - Controller workflow tests
- `test_review_web_gui_models.py` - Data model tests
- `test_review_web_gui_persistence.py` - Persistence layer tests

Run tests with:
```bash
python -m pytest tests/
```

## Extension Points

This module is designed for extension:

- **Add new label types**: Update `constants.LABEL_COLUMNS` and `CONTRIBUTION_OPTIONS`/`DIAGNOSTIC_OPTIONS`
- **Add new fields**: Extend `constants.CANONICAL_FIELDS` with additional column aliases
- **Custom export formats**: Add new export methods to `controller.py`
- **Alternate storage**: Extend or replace `persistence.py` with alternative storage backends

## Dependencies

- `pandas`: Data manipulation and Excel I/O
- `openpyxl`: Excel file handling
- `PyYAML`: Configuration parsing (if used)

Consult `src/requirements.txt` for the complete dependency list and versions.
