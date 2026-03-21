# ADR 0007: Render Adherence From a Fixed Option Set

## Status
Accepted

## Context
The Adherence field already had a fixed definition in DIAGNOSTIC_OPTIONS, but the UI rendered it through the dynamic tag path. When dynamic labels were empty, the radio options became sparse and inconsistent with the intended diagnostic contract.

## Decision
Render Adherence using constants.DIAGNOSTIC_OPTIONS in the classification panel, symmetric to Contribution Type.

- Keep Contribution Type and Adherence as fixed-enum fields.
- Keep Application Scope and Methodology as user-managed dynamic labels.
- Preserve fallback to PENDING when stored values are invalid.
- Keep Adherence and Contribution Type excluded from tag add/rename/remove flows.

## Consequences
- Positive:
  - Adherence radio options are always complete and deterministic.
  - Fixed-enum semantics are explicit in UI rendering code.
  - Tests can assert option wiring directly, reducing regression risk.
- Negative:
  - Adherence values cannot be extended through tag management.
  - Renderer now intentionally supports both dynamic and fixed option sources.

## Alternatives Considered
- Continue deriving Adherence options from dynamic labels.
- Persist fixed diagnostic options in labels JSON and treat them as editable tags.
- Infer Adherence options from historical assignment values.

## Related
- Implementation: [src/web_gui/constants.py](../../src/web_gui/constants.py)
- Implementation: [src/web_gui/ui/classification.py](../../src/web_gui/ui/classification.py)
- Regression test: [tests/test_review_web_gui_app.py](../../tests/test_review_web_gui_app.py)
- Related ADR: [ADR 0004: Render Contribution Type From a Fixed Option Set](ADR-0004-contribution-type-fixed-enum.md)
- Related ADR: [ADR 0006: Modularize Streamlit Presentation Layer](ADR-0006-streamlit-presentation-modularization.md)
