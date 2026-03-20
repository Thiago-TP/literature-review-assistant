# ADR 0004: Render Contribution Type From a Fixed Option Set

## Status
Accepted

## Context
The Contribution Type field already has a predefined set of values in `CONTRIBUTION_OPTIONS`, but the GUI was rendering it through the same dynamic tag path used for user-managed labels. That left the radio control nearly empty whenever the dynamic label list was blank.

## Decision
Render Contribution Type from the fixed `CONTRIBUTION_OPTIONS` list in the GUI.

- Keep Application Scope and Methodology backed by the dynamic label lists.
- Keep the existing `PENDING` fallback when the stored value is missing or invalid.
- Leave Contribution Type out of tag add, rename, and remove flows.

## Consequences
- Positive:
  - The Contribution Type radio always shows the intended choices.
  - The UI is clearer because fixed classifications are no longer mixed with editable tags.
  - A regression test can guard the fixed option set directly.
- Negative:
  - Users cannot invent arbitrary Contribution Type values through tag management.
  - The renderer now has two option sources instead of one shared path.

## Alternatives Considered
- Continue treating Contribution Type as a dynamic tag field.
- Store Contribution Type options in labels JSON and manage them like user tags.

## Related
- Implementation: [src/app.py](../../src/app.py)
- Source options: [src/review_web_gui/constants.py](../../src/review_web_gui/constants.py)
- Regression test: [tests/test_review_web_gui_app.py](../../tests/test_review_web_gui_app.py)
- Related ADR: [ADR 0005: Use Native Streamlit Light and Dark Theme Config](ADR-0005-streamlit-native-light-dark-theme-config.md)