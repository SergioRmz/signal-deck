# signal-deck Constitution

## Core Principles

### I. Thesis-Driven Editorial Product

signal-deck is not a news digest, dashboard, or generic AI summary surface. Every meaningful feature MUST preserve the product thesis: turn technology, AI, and economic noise into a sharp executive briefing that teaches the reader how to think better. Specs must state the reader value, the editorial job-to-be-done, and the structural insight the feature enables.

### II. Contracts Before Presentation

Editorial ingestion, transformation, visual composition, and rendered output MUST remain separated by explicit contracts. A feature that changes content shape, source handling, reader profiles, briefing payloads, or composition metadata must update the relevant schema/docs before implementation. Presentation code should consume validated artifacts, not hidden assumptions or ad hoc sample data.

### III. React as Editorial Canvas

The briefing UI is a dark-theme editorial canvas composed from reusable modules, not a fixed template that makes every story feel identical. Features affecting the renderer MUST favor composable editorial primitives, precise Spanish UI copy, and visual structure that encodes meaning. Avoid generic SaaS cards, decorative gradients, placeholder charts, meaningless numeric labels, and boolean-prop sprawl.

### IV. Recurring Publishing Must Be Auditable

Daily briefing workflows MUST be reproducible and inspectable. Each run should produce durable artifacts under a dated run directory or equivalent store: scout/research inputs, editorial plan, generated briefing, visual composition, deploy result, and delivery copy when applicable. Scheduled phases should be separated enough to avoid brittle bursts and should fail loudly rather than silently shipping stale or sample content.

### V. Personalization Without Losing Editorial Quality

Reader personalization is part of the architecture, but it must not flatten the briefing into shallow role-specific blurbs. Reader profiles may contain multiple roles/interests, and specs must define how lenses alter emphasis, examples, or interpretation while preserving the central thesis and pedagogical quality of the piece.

### VI. Public Delivery Requires Real Verification

When a feature affects external delivery, completion requires real verification: validators, tests/builds, deployment status, and public URL checks where applicable. A local render or plausible description is not enough. Any user-facing page must avoid placeholders, sample content leaks, broken Spanish copy, and visible implementation scaffolding.

### VII. Configuration Over Hardcoding

Operational configuration belongs in documented environment variables or structured config, not hardcoded application paths or hidden script constants. This includes data paths, deployment targets, feed/source settings, feature flags, delivery channels, and provider credentials. Specs must distinguish product defaults from configurable deployment/runtime choices.

### VIII. Spec-Driven Development Before Material Changes

Material product, architecture, workflow, or renderer changes MUST follow the Spec Kit workflow. Ambiguous ideas are not implementation requests. Before implementation, create or update a spec, clarify scope with Sergio, validate requirements, plan the technical approach, generate tasks, and analyze alignment.

Recommended flow:

```text
$speckit-specify → $speckit-clarify → $speckit-checklist → $speckit-plan → $speckit-tasks → $speckit-analyze → $speckit-implement
```

Small typo fixes or emergency production corrections may skip the full flow only when the change is explicitly low-risk and documented in the final response.

## Product Constraints

- The public briefing surface is Spanish-first and dark-theme by default.
- The system should teach through mechanisms, incentives, second-order effects, technical moats, market structure, and reusable mental models.
- The README is the project entry point and must stay current when structure, setup, deployment, or workflows change.
- Existing contracts and validators are product assets; do not bypass them for speed.
- Scheduled daily runs should use phased, auditable execution rather than one monolithic opaque prompt.
- Real source material must be distinguished from sample fixtures and dry-run artifacts.
- External delivery must include a verified public link when the user asks for a deliverable page.

## Development Workflow

Before starting each spec, capture explicit clarifications for:

1. feature/capability name and user-facing goal;
2. target reader/operator and reader profile impact;
3. affected layer: ingestion, transformation, composition, renderer, scheduling, deployment, delivery, or docs;
4. acceptance criteria and validation commands;
5. content contract or schema changes;
6. configuration/env surface;
7. run artifact and audit requirements;
8. failure modes and stale/sample-content protections;
9. public delivery requirements, if any;
10. non-goals for this spec.

Specs should be narrow enough to implement safely without redesigning the whole product at once.

## Governance

This constitution supersedes informal implementation preferences for signal-deck. If a spec or plan violates a MUST principle, the plan must include an explicit justification and a safer alternative. Amendments require updating this file, documenting the reason in the relevant spec/plan, and checking active specs for impact.

**Version**: 0.1.0 | **Ratified**: 2026-06-13 | **Last Amended**: 2026-06-13
