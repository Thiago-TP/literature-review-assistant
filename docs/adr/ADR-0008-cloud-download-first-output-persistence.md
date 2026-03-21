# ADR 0008: Cloud Download-First Output Persistence

## Status
Accepted

## Context
ADR 0003 established an output compatibility contract that assumed server-side persistence of temp and final review files. In Streamlit cloud environments, filesystem writes are ephemeral and not a reliable user-facing storage mechanism. Users need a deterministic way to retain outputs from Export and Save and Quit actions regardless of host lifecycle.

## Decision
Adopt a download-first persistence model for Streamlit cloud execution and supersede ADR 0003.

- Keep output schema and naming compatibility expectations for generated artifacts.
- Shift persistence responsibility for Export and Save and Quit to user-initiated browser downloads.
- Do not rely on server-side temp/final file persistence as the primary retention path in cloud environments.
- Treat successful browser download initiation as the canonical completion path for output retention.

## Consequences
- Positive:
  - Output retention no longer depends on ephemeral cloud filesystem state.
  - Export and Save and Quit become explicit user-controlled save actions.
  - Compatibility of artifact structure can be preserved while changing persistence transport.
- Negative:
  - Users must complete browser download interactions to retain outputs.
  - Server-side inspection of temp/final artifacts is reduced in cloud-only runs.
  - Flows that assumed durable local server files require operational adjustment.

## Alternatives Considered
- Keep ADR 0003 server-side temp/final persistence model unchanged in all environments.
- Add optional cloud object storage as default persistence backend.
- Maintain dual-write behavior (server files plus browser download) as a hard requirement.

## Related
- Supersedes: [ADR 0003: Preserve Output Compatibility Contract](ADR-0003-output-compatibility-contract.md)
- Related ADR: [ADR 0001: Python 3.11 + Streamlit + Pandas](ADR-0001-framework-selection.md)
- Related ADR: [ADR 0002: Adopt Layered GUI Architecture](ADR-0002-layered-architecture.md)
