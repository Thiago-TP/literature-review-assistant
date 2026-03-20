# ADR 0002: Adopt Layered GUI Architecture

## Status
Accepted

## Context
The existing GUI is monolithic and repetitive, making maintenance and testing harder. The new GUI must be leaner and easier to evolve while preserving behavior.

## Decision
Adopt a layered architecture with clear boundaries:
- UI composition layer
- Application/controller layer
- Domain services (pure functions where possible)
- Persistence adapters for JSON/XLSX I/O

## Consequences
- Positive:
  - Better unit-testability through isolated domain and persistence logic.
  - Clear responsibilities reduce duplication and improve maintainability.
  - Safer future UI improvements without changing core behavior.
- Negative:
  - Initial refactor overhead and more files to navigate.
  - Requires discipline to keep boundaries clean over time.

## Alternatives Considered
- Option A: Keep monolithic file and only do superficial cleanup.
- Option B: Extract small utilities without explicit layering.

## Related
- Spec: Tech Lead YAML spec approved in chat (2026-03-19)
- Supersedes: ADR-XXXX (if any)
