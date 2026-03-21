# T1-T2 Instructions Report

## Summary
- Merged the approved instruction specification and instructions report into this single markdown artifact.
- Standardized cycle artifact naming across instructions, implementation, QA, and ADR deliverables.
- Removed YAML report/spec artifacts to keep external reporting assets markdown-only.

## Files Changed
- [.github/instructions/T1-T2-instructions.md](.github/instructions/T1-T2-instructions.md)
- [docs/QA/T1-T2-implementation.md](docs/QA/T1-T2-implementation.md)
- [docs/QA/T1-T2-qa.md](docs/QA/T1-T2-qa.md)

## Instruction Delta
- Replaced:
  - Split instruction artifacts (`T1-T2.yaml` + duplicate instruction report) with a single merged markdown file.
- Added:
  - A naming convention section for current and future cycle artifacts.
  - Embedded approved instruction specification in markdown format.
- Updated:
  - References so implementation and QA traceability target markdown files only.

## Output Contract
- Format: Markdown
- Required sections:
  - Summary
  - Files Changed
  - Instruction Delta
  - Naming Convention
  - Approved Instruction Specification
  - Output Contract
  - Rationale
  - Validation
  - Follow-up
- Storage location:
  - .github/instructions/T1-T2-instructions.md
  - docs/QA/T1-T2-implementation.md
  - docs/QA/T1-T2-qa.md

## Naming Convention
- Instructions report/spec: `.github/instructions/TX-TY-instructions.md`
- Implementation report: `docs/QA/TX-TY-implementation.md`
- QA report: `docs/QA/TX-TY-qa.md`
- ADR files: `docs/adr/ADR-####-kebab-case-title.md`

## Approved Instruction Specification

### Feature
Lean Streamlit app modularization and diagnostic fixed enum wiring

### Context
- Goal: Keep app entrypoint lean while preserving behavior and enforce fixed diagnostic options in UI.
- Constraints:
  - Preserve Streamlit session_state semantics and controller contracts.
  - Do not alter persistence/output compatibility contract.
  - Keep contribution and diagnostic columns as fixed-enum classification fields.

### Tasks
1. T1: Modularize Streamlit presentation layer into focused UI modules.
   - Inputs:
     - Current monolithic app composition and callbacks.
     - Existing controller/domain interfaces.
   - Outputs:
     - Lean app orchestration in app.py.
     - Extracted UI modules for sidebar/page/classification/tag management.
   - Acceptance criteria:
     - App main delegates section rendering to UI modules.
     - Navigation, classification, and tag management behavior remain unchanged.
2. T2: Wire fixed diagnostic options in classification renderer.
   - Inputs:
     - DIAGNOSTIC_OPTIONS constant.
     - Classification field rendering flow.
   - Outputs:
     - Explicit options for DIAGNOSTIC_COLUMN using DIAGNOSTIC_OPTIONS.
     - Tests asserting both fixed columns use fixed options.
   - Acceptance criteria:
     - Diagnostic radio options are never sourced from dynamic labels fallback.
     - Invalid fixed-enum value falls back to pending behavior.

### Design
- Modules:
  - src/app.py: Entrypoint orchestration only.
  - src/web_gui/ui/page.py: Navigation and current-work layout rendering.
  - src/web_gui/ui/sidebar.py: Dataset upload/load/reset section rendering.
  - src/web_gui/ui/classification.py: Classification fields rendering with fixed and dynamic option sources.
  - src/web_gui/ui/tag_management.py: Tag CRUD and pending widget-clear handling.
- Data structures:
  - labels (`dict[str, list[str]]`): Per-column dynamic labels for non-fixed columns.
  - assignments_df (`pandas.DataFrame`): Per-work classification assignments.
- APIs:
  - main: `def main() -> None`.
  - render_classification: `def render_classification() -> None`.

### Risks
- Refactor can break tests that patch old app-level functions.
- Import path divergence between legacy review_web_gui and current web_gui.

### ADR Candidates
1. Streamlit presentation modularization.
   - Decision: Extract UI concerns into dedicated modules.
2. Diagnostic as fixed enum in UI.
   - Decision: Pass DIAGNOSTIC_OPTIONS explicitly in classification rendering.

## Rationale
- A single markdown instruction artifact removes ambiguity and avoids split-source drift.
- Naming consistency improves traceability and simplifies automation.

## Validation
- Verification method:
  - Confirmed merged content includes both prior instruction report and approved spec.
  - Confirmed report/spec artifacts for instructions, implementation, QA, and ADR are markdown files.
- Evidence:
  - [.github/instructions/T1-T2-instructions.md](.github/instructions/T1-T2-instructions.md)
  - [docs/QA/T1-T2-implementation.md](docs/QA/T1-T2-implementation.md)
  - [docs/QA/T1-T2-qa.md](docs/QA/T1-T2-qa.md)
- Status:
  - pass

## Follow-up
- Remaining items:
  - Streamlit-specific test refactor remains deferred by user direction.
- Next review trigger:
  - Start of the next ADR-approved cycle touching Streamlit UI test strategy.