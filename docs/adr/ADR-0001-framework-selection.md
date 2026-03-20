# ADR 0001: Keep Streamlit and Refactor Architecture

## Status
Accepted

## Context
The project needs a sleeker, more modern browser GUI with leaner code while preserving existing review behavior and output compatibility. We considered whether to keep Streamlit or migrate to another Python web UI framework.

## Decision
Keep Streamlit as the UI framework and deliver modernization through a modular refactor, design token-based styling, and improved component composition.

## Consequences
- Positive:
  - Lower migration risk and faster delivery because current behavior is already implemented in Streamlit.
  - Existing run/dependency model remains simple for users.
  - Enables focused refactor on code quality and UX polish without framework churn.
- Negative:
  - Streamlit imposes styling and interaction constraints compared with lower-level frontend frameworks.
  - Some advanced UI patterns may require workarounds.

## Alternatives Considered
- Option A: Keep Streamlit and refactor to modular architecture with improved theming.
- Option B: Migrate to another Python browser UI framework (for example, NiceGUI or Dash).

## Related
- Spec: Tech Lead YAML spec approved in chat (2026-03-19)
- Supersedes: ADR-XXXX (if any)
