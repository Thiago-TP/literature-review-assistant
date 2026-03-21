# ADR 0006: Modularize Streamlit Presentation Layer

## Status
Accepted

## Context
The UI orchestration in app.py had accumulated navigation, sidebar upload handling, classification rendering, and tag-management callbacks in one file. This made testing and incremental changes harder because UI behavior was tightly coupled to entrypoint wiring.

## Decision
Split Streamlit presentation concerns into focused UI modules while keeping controller and domain responsibilities unchanged.

- Keep app.py as a lean entrypoint and section orchestrator.
- Move navigation and current work rendering to web_gui/ui/page.py.
- Move classification rendering and assignment field rendering to web_gui/ui/classification.py.
- Move sidebar dataset upload/reset rendering to web_gui/ui/sidebar.py.
- Move tag-management callbacks and rendering to web_gui/ui/tag_management.py.
- Expose UI modules through web_gui/ui/__init__.py for stable imports.

## Consequences
- Positive:
  - App startup flow is shorter and easier to understand.
  - UI sections are independently testable with cleaner monkeypatch targets.
  - Responsibilities align better with layered architecture in ADR 0002.
- Negative:
  - More modules increase import surface and require consistent package wiring.
  - Existing tests targeting private app.py functions must be migrated.
  - Legacy import paths may require compatibility shims in tests.

## Alternatives Considered
- Keep all UI code in app.py and only reorder functions.
- Move everything to one large ui.py module.
- Move UI logic into controller, blending presentation and orchestration concerns.

## Related
- Implementation: [src/app.py](../../src/app.py)
- Implementation: [src/web_gui/ui/page.py](../../src/web_gui/ui/page.py)
- Implementation: [src/web_gui/ui/sidebar.py](../../src/web_gui/ui/sidebar.py)
- Implementation: [src/web_gui/ui/classification.py](../../src/web_gui/ui/classification.py)
- Implementation: [src/web_gui/ui/tag_management.py](../../src/web_gui/ui/tag_management.py)
- Regression test: [tests/test_review_web_gui_app.py](../../tests/test_review_web_gui_app.py)
- Related ADR: [ADR 0002: Adopt Layered GUI Architecture](ADR-0002-layered-architecture.md)
- Related ADR: [ADR 0007: Render Adherence From a Fixed Option Set](ADR-0007-diagnostic-type-fixed-enum.md)
