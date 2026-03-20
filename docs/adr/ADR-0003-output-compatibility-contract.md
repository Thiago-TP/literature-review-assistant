# ADR 0003: Preserve Output Compatibility Contract

## Status
Accepted

## Context
Current downstream workflow depends on result artifacts in results/, including labels JSON and review Excel files. A rewrite must not break file naming patterns, merge behavior, or output column expectations.

## Decision
Treat output behavior as a compatibility contract:
- Preserve labels JSON, temp review XLSX, and final review XLSX naming patterns.
- Preserve merge strategy (work_id-first with fallback behavior compatibility).
- Preserve source input columns plus classification columns in exports.

## Consequences
- Positive:
  - Existing user workflows keep working without migration.
  - Lower rollout risk and easier adoption of the new GUI.
  - Enables regression tests against concrete compatibility rules.
- Negative:
  - Constrains redesign freedom for storage/output schemas.
  - Legacy quirks may need to be retained intentionally.

## Alternatives Considered
- Option A: Redesign output schema and provide migration scripts.
- Option B: Partial compatibility with documented breaking changes.

## Related
- Spec: Tech Lead YAML spec approved in chat (2026-03-19)
- Supersedes: ADR-XXXX (if any)
