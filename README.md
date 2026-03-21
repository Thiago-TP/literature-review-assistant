# Revisionator

A interactive web application for systematic literature review and academic paper assessment built with Streamlit.

## Overview

Revisionator helps researchers and reviewers systematically evaluate and label academic papers. The application guides users through importing paper metadata, reviewing each work, and assigning contribution types and adherence classifications for classification and tracking.

### Key Features

- **Interactive Paper Review**: Navigate through imported papers with an intuitive interface
- **Structured Labeling**: Assign papers to categories like "New Method", "Improvement", "Review", etc.
- **Adherence Assessment**: Rate how well papers align with defined scope and methodology criteria
- **Progress Tracking**: Monitor review progress with real-time statistics
- **Data Export**: Export review results in multiple formats for downstream analysis
- **Session Management**: Save work progress and resume reviews at any time

## Requirements

- Python 3.x
- Dependencies listed in [src/requirements.txt](src/requirements.txt)

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/revisionator.git
cd revisionator
```

2. Create a virtual environment:
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r src/requirements.txt
```

## Usage

Launch the application:
```bash
streamlit run src/app.py
```

The application will open in your default web browser at `http://localhost:8501`.

### Workflow

1. **Upload Dataset**: Import an Excel file containing paper metadata (typically from Scopus export)
   - **Expected Format**: Scopus CSV/Excel export format
   - **Required Fields**: At minimum, the file must contain an `Abstract` column
   - **Supported Fields**: The app automatically maps common column names (Title, Authors, Source title, Year, Abstract, etc.)
2. **Review Papers**: Navigate through each paper using "Previous" and "Next" buttons
3. **Label Contributions**: Assign each paper a contribution type
4. **Assess Adherence**: Rate the paper's adherence to your research scope and methodology
5. **Export Results**: Save your labeled dataset for analysis

## Project Structure

```
revisionator/
├── src/
│   ├── app.py                 # Streamlit application entry point
│   ├── requirements.txt        # Python package dependencies
│   └── web_gui/               # Core application module
│       ├── README.md           # Module documentation
│       ├── constants.py        # Configuration and constants
│       ├── domain.py           # Business logic and data utilities
│       ├── controller.py       # Application logic and workflow
│       ├── models.py           # Data models
│       └── persistence.py      # Data storage and file operations
├── tests/                      # Unit tests
├── docs/
│   └── adr/                   # Architecture Decision Records
├── input_examples/            # Sample input files
├── results/                   # Review output files
└── README.md                  # This file
```

See [src/web_gui/README.md](src/web_gui/README.md) for details on the core application module.

## Architecture

Revisionator follows a **layered architecture** with clear separation of concerns:

- **UI Layer** (`app.py`): Streamlit-based presentation and user interaction
- **Controller Layer** (`web_gui/controller.py`): Application workflow and orchestration
- **Domain Layer** (`web_gui/domain.py`): Business logic and domain entities
- **Persistence Layer** (`web_gui/persistence.py`): Data storage and file I/O

For detailed architecture decisions, see the [ADRs](docs/adr/).

## Development

### Running Tests

Execute the test suite:
```bash
python -m pytest tests/
```

### Project Configuration

- **Theme Configuration**: Streamlit theme settings are in `.streamlit/config.toml`
- **Label Definitions**: Paper classification options are defined in `web_gui/constants.py`
- **Field Mapping**: Excel column mapping logic is in `web_gui/domain.py`

## Key Design Decisions

This project uses Streamlit as the UI framework for its simplicity, existing feature set, and rapid development capability. See [Architecture Decision Records](docs/adr/) for details on:

- Framework selection (ADR-0001)
- Layered architecture (ADR-0002)
- Output compatibility contract (ADR-0003)
- Contribution type enumeration (ADR-0004)
- Theme configuration (ADR-0005)
- Streamlit presentation modularization (ADR-0006)
- Adherence fixed-enum rendering (ADR-0007)

## Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/your-feature`)
3. Commit your changes (`git commit -am 'Add some feature'`)
4. Push to the branch (`git push origin feature/your-feature`)
5. Open a Pull Request

## License

[Add your license information here]

## Contact

[Add contact information or maintainer details]
