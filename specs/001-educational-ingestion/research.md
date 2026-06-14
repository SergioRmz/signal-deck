# Research: Educational Ingestion

## Decision: Add an ingestion package v2 artifact instead of overloading the current v1 signal input

**Rationale**: The existing `signal-input` contract is a compact upstream packet designed for hand-authored editorial material and deterministic transformation. The new feature needs candidate pools, clustering, rejection logs, source-role coverage, watch items, source diversity, concentration flags, and per-signal audit records. Adding all of that directly to v1 would blur compatibility and make existing fixtures harder to reason about.

**Alternatives considered**:

- Extend `data/signal-input.schema.json` in place: rejected because it risks breaking the current validator and sample pipeline too early.
- Replace v1 entirely: rejected because downstream transformation and renderer validation already depend on the current stable path.
- Keep everything in prompt logs: rejected because the constitution requires durable, inspectable run artifacts.

## Decision: Keep source discovery provider-agnostic in the contract

**Rationale**: The spec requires hybrid discovery and source roles, but does not choose a feed provider, search API, crawler, model provider, or database. The package should record what was discovered and how it was judged: source type, source role, credibility notes, access limitations, and evidence depth. Implementation tasks can later wire discovery mechanisms without changing the editorial contract.

**Alternatives considered**:

- Encode specific providers in the schema: rejected as premature and contrary to configuration-over-hardcoding.
- Require fully automated discovery before supporting the contract: rejected because contract-first fixtures and validators can be built now.
- Use freeform source notes only: rejected because selected signals need auditable source-role coverage.

## Decision: Represent signal status explicitly

**Rationale**: The product needs to know not only which signals were selected, but also why other signals were rejected, merged, downgraded, or retained as watch items. Explicit statuses make the package debuggable and prevent weak/uncorroborated material from contaminating the final briefing.

**Chosen statuses**:

- `candidate`: discovered and evaluated but not necessarily selected.
- `selected`: promoted into the 5-8 downstream signal set.
- `rejected`: excluded with an explicit reason.
- `watch_item`: uncertain but potentially valuable; tracked without becoming a strong factual basis.
- `merged`: represented by another candidate or cluster because coverage is redundant.

**Alternatives considered**:

- Boolean `selected`: rejected because it cannot distinguish rejection, redundancy, and watch states.
- Separate arrays only: rejected unless each item also has a status, because status simplifies semantic validation and audit queries.

## Decision: Use structured, bounded audit fields rather than exhaustive reasoning traces

**Rationale**: The clarification selected structured/debbugable auditability. Each signal should preserve editorial rationale, educational value, confidence/score, source references, cluster relationship, rejection reason when applicable, and concentration/corroboration notes. Full internal deliberation traces are unnecessary and would make artifacts noisy and brittle.

**Alternatives considered**:

- Minimal reason strings: rejected because feedback and debugging need more structure.
- Exhaustive reasoning logs: rejected because the spec explicitly avoids full internal deliberation traces.

## Decision: Validate with both JSON schema and Python semantic checks

**Rationale**: JSON schema can enforce artifact shape, required fields, enums, and counts. Python semantic validation is still needed for cross-reference checks: source IDs exist, selected signals reference known candidates, cluster members exist, deep dives are selected or cluster-backed, rejection reasons match rejected status, watch items are not used as strong factual foundations, and concentration flags are consistent with selected signals.

**Alternatives considered**:

- JSON schema only: rejected because cross-reference integrity is difficult to fully express and maintain.
- Python only: rejected because schema files are already a project convention and are easier to document/review.

## Decision: Continue file-based run artifacts for this feature

**Rationale**: The current repository writes auditable local run folders and does not yet need a database. A file-based ingestion package keeps the implementation small, testable, and aligned with existing validators and pipeline commands.

**Alternatives considered**:

- Add SQLite/Postgres now: rejected as premature for this spec.
- Store only generated briefing output: rejected because the feature is explicitly about upstream auditability.

## Decision: Keep renderer changes out of scope

**Rationale**: The spec says improving ingestion quality must not require changing the public page design. The transformation layer may consume the new selected signals, but the React app should continue rendering validated briefing and visual-composition artifacts.

**Alternatives considered**:

- Add a UI for candidate inspection now: rejected as a separate future operator-console spec.
- Redesign the briefing page to expose all audit data: rejected because auditability is a run artifact requirement, not a public presentation requirement.
