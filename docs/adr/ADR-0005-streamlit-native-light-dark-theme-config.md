# ADR 0005: Use Native Streamlit Light and Dark Theme Config

## Status
Accepted

## Context
The app originally applied theme styling through Python-injected CSS. That made the visual layer harder to maintain and disconnected from Streamlit's built-in theme system. The current requirement is to keep a lean light theme and a lean dark theme, both controlled by Streamlit configuration rather than custom runtime CSS.

Streamlit supports theme configuration in `.streamlit/config.toml`, including separate light and dark theme sections. It does not support TOML include syntax inside `config.toml`, so the runtime theme must live in a single config file.

## Decision
Use Streamlit's native theme configuration as the source of truth:

- Keep a single `.streamlit/config.toml` file in the repository.
- Define the active theme mode with `theme.base = "auto"` so Streamlit follows the user's light/dark preference.
- Define lean palette values under `[theme.light]` and `[theme.dark]`.
- Remove runtime CSS theme injection from the app startup path.
- Treat theming as configuration, not Python code.

## Consequences
- Positive:
  - Theme behavior is native to Streamlit and easier to reason about.
  - Light and dark styles stay simple and centralized.
  - The app startup path is smaller because it no longer injects custom theme CSS.
  - The theme can be validated with a straightforward config test.
- Negative:
  - Styling is limited to the options Streamlit exposes natively.
  - The theme cannot be split across multiple TOML files through native include syntax.
  - Fine-grained custom visual effects from the old CSS theme are no longer part of the design.

## Alternatives Considered
- Continue using Python-injected CSS for theming.
- Split light and dark palettes into separate TOML files and generate the runtime config at launch.
- Keep a custom manual theme toggle inside the app instead of using Streamlit's built-in theme behavior.

## Related
- Implementation: [.streamlit/config.toml](../../.streamlit/config.toml)
- Implementation: [src/app.py](../../src/app.py)
- Regression test: [tests/test_review_web_gui_app.py](../../tests/test_review_web_gui_app.py)
- Related ADR: [ADR 0004: Render Contribution Type From a Fixed Option Set](ADR-0004-contribution-type-fixed-enum.md)