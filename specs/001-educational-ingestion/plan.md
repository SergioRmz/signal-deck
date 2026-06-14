# Implementation Plan: Educational Ingestion

**Branch**: `001-educational-ingestion` | **Date**: 2026-06-14 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `/specs/001-educational-ingestion/spec.md`

## Summary

Build a richer upstream ingestion package for signal-deck so each daily briefing starts from 15-30 candidate signals, evaluates educational relevance for Sergio's canonical reader profile, clusters related signals into themes, records explicit rejection/watch decisions, and exposes 5-8 selected signals plus 2-3 deep dive candidates to the existing deterministic transformation layer.

The technical approach is contract-first: introduce an ingestion package v2 schema and documentation, add validated sample fixtures, extend Python validators/tests before changing transformation behavior, then adapt the existing local pipeline so downstream generation consumes the selected signal set without requiring renderer redesign.

## Technical Context

**Language/Version**: Python 3 standard library for pipeline, validation, and deterministic transformation; TypeScript/React/Vite renderer remains downstream and unchanged by this feature.

**Primary Dependencies**: Existing Python scripts under `scripts/`; existing JSON contracts under `data/`; existing Vite app under `apps/web/`. No new runtime dependency is planned for this feature.

**Storage**: File-based JSON artifacts. Source fixtures live under `data/`; per-run artifacts live under `runs/YYYY-MM-DD/`; this feature adds an ingestion package artifact to the run folder.

**Testing**: Python `unittest`; existing validators (`scripts/validate_signal_input.py`, `scripts/validate_briefing.py`, `scripts/validate_visual_composition.py`); optional renderer build via `npm run build` from `apps/web`.

**Target Platform**: Local/CI Linux execution and static renderer build; no backend service or database in scope.

**Project Type**: Editorial data pipeline plus static React presentation app.

**Performance Goals**: Normal local run should validate and transform 15-30 candidate signals quickly enough for recurring daily publishing; correctness and auditability matter more than throughput.

**Constraints**: Must keep ingestion, transformation, visual composition, and renderer contracts separated; must not use sample/dry-run fixtures as live source material; must preserve Spanish-first public output; must not redesign public renderer in this spec.

**Scale/Scope**: One daily briefing run at a time with 15-30 candidate signals, 5-8 selected signals, 2-3 deep dive candidates, rejected/downranked signals, watch items, clusters, source diversity, and run-level quality notes.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- **I. Thesis-Driven Editorial Product**: PASS — feature explicitly optimizes for educational signal selection, reusable mental models, causality, incentives, and strategic judgment.
- **II. Contracts Before Presentation**: PASS — plan starts with schema/docs and keeps renderer changes out of scope.
- **III. React as Editorial Canvas**: PASS — no renderer redesign in this feature; downstream public page remains contract-consuming.
- **IV. Recurring Publishing Must Be Auditable**: PASS — ingestion package and run artifacts become inspectable, dated, and debuggable.
- **V. Personalization Without Losing Editorial Quality**: PASS — canonical Sergio profile is required while preserving future multi-profile lenses.
- **VI. Public Delivery Requires Real Verification**: PASS — no public delivery change in this spec; validation commands cover generated artifacts and optional renderer build.
- **VII. Configuration Over Hardcoding**: PASS — plan uses existing file-based defaults and identifies future configurable source discovery without hardcoding provider choices.
- **VIII. Spec-Driven Development Before Material Changes**: PASS — spec and clarifications exist before planning.

No constitutional violations require justification.

## Project Structure

### Documentation (this feature)

```text
specs/001-educational-ingestion/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   └── ingestion-package-v2.schema.json
└── tasks.md              # Created later by speckit-tasks, not this plan step
```

### Source Code (repository root)

```text
data/
├── signal-input.schema.json              # Existing v1 contract; may remain for compatibility
├── signal-input.sample.json              # Existing sample; may be migrated or joined by v2 sample
├── ingestion-package.schema.json         # Likely new canonical v2 schema during implementation
└── ingestion-package.sample.json         # Likely new fixture for educational ingestion

scripts/
├── validate_signal_input.py              # Existing validator; may delegate or stay v1-compatible
├── validate_ingestion_package.py         # Likely new v2 validator
├── generate_briefing.py                  # Consume selected signals from package while keeping output contract
└── run_briefing_pipeline.py              # Write ingestion package artifact into run folder

tests/
├── test_generate_briefing.py             # Extend transformation behavior coverage
├── test_run_briefing_pipeline.py         # Extend run artifact coverage
└── test_validate_ingestion_package.py    # Likely new schema/semantic validation tests

docs/
├── briefing-ingestion-v1.md              # Existing contract reference
└── briefing-ingestion-v2.md              # Likely new contract documentation
```

**Structure Decision**: Keep the feature inside the existing file-based editorial pipeline. Add a v2 ingestion package contract and validator instead of replacing the renderer or introducing a database/service. Preserve compatibility with the current transformation layer until tasks define the exact migration sequence.

## Phase 0 Research Output

See [research.md](./research.md). Key decisions:

- Use a v2 ingestion package rather than overloading the existing v1 `signal-input` shape.
- Keep discovery provider-agnostic; represent source roles and evidence depth in the package.
- Model selection statuses explicitly: candidate, selected, rejected, watch item, and merged/redundant.
- Validate the artifact structurally with JSON schema and semantically with Python checks.

## Phase 1 Design Output

- [data-model.md](./data-model.md) defines ingestion run, source references, candidate signals, clusters, selected signals, rejected signals, watch items, and quality notes.
- [contracts/ingestion-package-v2.schema.json](./contracts/ingestion-package-v2.schema.json) captures the proposed artifact shape for implementation.
- [quickstart.md](./quickstart.md) defines validation scenarios and commands.

## Post-Design Constitution Check

- **Contracts Before Presentation** remains satisfied because contract artifacts exist before implementation tasks.
- **Auditable Publishing** remains satisfied because run-level quality notes, source diversity, and decision records are first-class data-model entities.
- **Configuration Over Hardcoding** remains satisfied because source discovery implementation remains provider-agnostic in this plan; source roles are represented as data rather than hardcoded provider rules.
- **Public Delivery Requires Real Verification** remains satisfied because final validation includes deterministic pipeline checks and renderer build only as downstream verification, not as the implementation target.

No gate failures remain.

## Complexity Tracking

No constitutional violations or complexity exceptions are required for this plan.
