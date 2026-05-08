# Literature Review Assistant

A modern, interactive web application for systematic literature reviews and academic paper assessment built with **Streamlit**. Streamline the paper review process with structured tagging, progress tracking, and session management.

## Table of Contents

- [Overview](#overview)
- [Key Features](#key-features)
- [Requirements](#requirements)
- [Installation](#installation)
- [Usage](#usage)
- [Project Structure](#project-structure)
- [Workflow](#workflow)
- [Data Format](#data-format)
- [FAQ](#faq)

## Overview

The Literature Review Assistant helps researchers and academic reviewers efficiently evaluate and categorize academic papers. Instead of managing spreadsheets and notes across multiple applications, this tool provides an integrated interface to:

- **Import** paper metadata (title, abstract, DOI) from Excel exports
- **Review** papers one at a time with full article information
- **Classify** papers using customizable tag fields and categories
- **Track** your progress with real-time visual indicators
- **Save** your work and resume at any time
- **Export** results for further analysis

The application is ideal for:
- Conducting systematic literature reviews
- Pre-screening papers for research projects
- Team-based peer review workflows
- Building research databases with structured metadata

## Key Features

### 📄 **Interactive Paper Review**
- One-paper-at-a-time interface minimizes cognitive load
- Display title, abstract, and DOI with direct links to papers
- Navigation controls to move between papers (next, previous, go-to-specific)
- Quick DOI links to access full articles

### 🏷️ **Structured Tagging System**
- **Pre-defined fields**: "Adherence" and "Contribution Type" (protected fields)
- **Custom fields**: Create unlimited custom classification fields
- **Multi-select tags**: Assign multiple tags per field per paper
- **Field management**: Add, rename, and delete custom fields (keep protected fields intact)
- **Tag management**: Add, rename, and delete tags within each field

### 📊 **Progress Tracking**
- **Visual matrix**: Color-coded grid showing review status for all papers
  - Gray: No fields completed
  - Red → Yellow → Green: Increasing completion as fields are tagged
- **Interactive shortcuts**: Click any paper in the matrix to jump to it
- **Progress persistence**: Track which papers are fully reviewed vs. partial

### 📝 **Notes & Metadata**
- Write detailed notes for each paper
- Notes are automatically saved with your session
- View previous notes while reviewing

### 💾 **Session Management**
- **Auto-save**: Progress is saved in session state
- **Export sessions**: Download review progress as JSON for sharing or backup
- **Resume sessions**: Upload previously saved JSON to continue reviewing
- **Session naming**: Exports include timestamp for easy identification

### 📥 **Data Import/Export**
- **Import**: Upload Excel files with paper metadata
- **Export**: Download review results as JSON with all tags and notes
- Compatible with Scopus, Web of Science, and custom exports

## Requirements

- **Python 3.10+**
- **Streamlit 1.55.0+**
- **Pandas 1.x+** (via openpyxl for Excel support)
- **Matplotlib 3.x+** (for progress visualization)

See [requirements.txt](src/requirements.txt) for exact versions.

## Installation

### Option 1: Quick Start (Recommended)

```bash
# Clone the repository
git clone https://github.com/yourusername/literature-review-assistant.git
cd literature-review-assistant

# Create and activate virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r src/requirements.txt

# Run the application
streamlit run src/app.py
```

The app will open automatically at `http://localhost:8501` in your default browser.

### Option 2: Docker (Optional)

```bash
docker build -t literature-review .
docker run -p 8501:8501 literature-review
```

## Usage

### Starting a Review

1. **Launch the app**: `streamlit run src/app.py`
2. **Upload Excel file**: Use the sidebar to upload your paper metadata (must contain "Title" and "Abstract" columns)
3. **Review papers**: Navigate through papers using the main interface
4. **Assign tags**: Use the tag section to classify each paper
5. **Save progress**: Click the download button to export your work as JSON
6. **Resume later**: Upload the JSON file to continue where you left off

### Excel File Format

Required columns:
- **Title**: Paper title (string)
- **Abstract**: Paper abstract (string)

Optional columns:
- **DOI**: Digital Object Identifier (string) - enables direct paper links
- **Notes**: Your preliminary notes (string)
- Any other columns are preserved but not displayed in the review interface

Example structure:
```
| Title                              | Abstract                    | DOI            |
|------------------------------------|-----------------------------|-----------------
| "Machine Learning in Healthcare"  | "This paper explores..."    | "10.1234/xyz"  |
| ...                                | ...                         | ...            |
```

### Tagging Workflow

1. **Pre-defined tags** (cannot be modified):
   - **Adherence**: Insufficient | Partial | Sufficient
   - **Contribution Type**: New Method | Improvement | Review | Other

2. **Custom tags** (editable):
   - Add new fields in the "Manage Tag Fields" section
   - Each field can have multiple tags
   - Select tags for each paper using multi-select interface
   - Delete or rename custom fields and tags anytime

3. **Saving tags**:
   - Tags are saved automatically when selected
   - Download JSON to persist your progress
   - Upload JSON to resume reviewing

### Exporting Results

Your review progress is exported as JSON with the structure:
```json
[
  {
    "Title": "Paper 1 Title",
    "Adherence": ["Sufficient"],
    "Contribution Type": ["New Method"],
    "Your Custom Field": ["custom_tag1", "custom_tag2"],
    "Notes": "Your notes about this paper..."
  },
  ...
]
```

## Project Structure

```
literature-review-assistant/
├── README.md                          # This file
├── LICENSE                            # Project license
├── requirements.txt → src/requirements.txt
├── src/
│   ├── app.py                        # Main Streamlit application
│   ├── constants.py                  # Configuration constants
│   └── requirements.txt               # Python dependencies
├── input_examples/
│   └── scopus_export_*.json          # Example input files
└── .streamlit/
    └── config.toml                   # Streamlit configuration (optional)
```

### File Descriptions

- **app.py**: Main application logic
  - Session state initialization
  - UI components and layout
  - Tag and progress management
  - File I/O operations

- **constants.py**: Configuration and constants
  - Tag definitions (adherence options, contribution types)
  - Column names for Excel data
  - UI parameters (color scheme, layout settings)

- **requirements.txt**: Python package dependencies
  - Streamlit (web framework)
  - Pandas (data handling)
  - Matplotlib (visualization)
  - openpyxl (Excel support)

## Workflow

### Typical Review Session

```
1. START
   ↓
2. Upload Excel file with papers
   ↓
3. Review Progress Overview (see color-coded matrix)
   ↓
4. For each paper:
   ├─ Read title and abstract
   ├─ Check DOI link if available
   ├─ Write notes
   ├─ Assign tags (required: Adherence, Contribution Type)
   ├─ Add custom tags as needed
   └─ Move to next paper
   ↓
5. Download session as JSON
   ↓
6. (Optional) Resume later by uploading saved JSON
   ↓
7. END
```

### Managing Custom Tags

**Add a new field:**
1. Go to "Manage Tag Fields" → "Add a new field"
2. Enter field name (e.g., "Domain", "Year Range")
3. Press Enter to create

**Add tags to a field:**
1. Go to "Manage Tag Entries" → Expand the field
2. Enter tag name (e.g., "Machine Learning", "2024")
3. Press Enter to add

**Rename or delete:**
1. Use the "Select a field/tag to rename" or "Delete" options
2. Protected fields (Adherence, Contribution Type) cannot be modified

## Data Format

### Input: Excel Format

Papers are imported from Excel files. Required structure:

| Required Column | Type   | Example                          |
|-----------------|--------|----------------------------------|
| Title           | String | "Attention is All You Need"      |
| Abstract        | String | "The dominant sequence transduction models..." |

| Optional Column | Type   | Example                    |
|-----------------|--------|----------------------------|
| DOI             | String | "10.48550/arXiv.1706.03762" |
| Notes           | String | "Foundational transformer paper" |

### Output: JSON Format

Reviews are exported as JSON arrays. Each object represents one paper:

```json
{
  "Adherence": ["Sufficient"],
  "Contribution Type": ["New Method"],
  "Your_Field_1": ["tag_a", "tag_b"],
  "Your_Field_2": [],
  "Notes": "This paper is highly relevant..."
}
```

## FAQ

**Q: Can I use this with papers from Scopus or Web of Science?**
A: Yes! Export from Scopus/WoS to Excel format (including Title, Abstract, DOI columns) and upload.

**Q: How do I backup my progress?**
A: Click the download button to save a JSON file with your entire review session. Keep this file safe.

**Q: Can multiple people review the same papers?**
A: Each person should have their own session. Export individual JSON files and compare results afterward.

**Q: What if a paper doesn't have a DOI?**
A: The DOI link won't display, but the paper can still be reviewed. This is normal for older or non-traditional publications.

**Q: Can I edit papers or add new ones mid-review?**
A: Upload a new Excel file to start a fresh review. To add papers to an existing review, combine them in Excel before uploading.

**Q: How large can my dataset be?**
A: Streamlit comfortably handles 500-1000 papers. For larger datasets (10,000+ papers), consider splitting into batches.

**Q: Can I use this offline?**
A: Yes. Install Streamlit and run locally - no internet required (except for DOI links).

## Contributing

Contributions welcome! Areas for improvement:
- Batch tagging capabilities
- Advanced filtering and search
- Export formats (CSV, PDF reports)
- Dark mode support
- Collaborative features

## License

See [LICENSE](LICENSE) file for details.

## Citation

If you use this tool in your research, please cite:

```
@software{literature_review_assistant_2024,
  title = {Literature Review Assistant},
  author = {Thiago Tomás de Paula},
  year = {2026},
  url = {https://github.com/yourusername/literature-review-assistant}
}
```

---

**Questions or issues?** Open an issue on GitHub or contact the maintainers.