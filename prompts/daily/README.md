# Daily Prompt Contracts

These prompts are versioned operating contracts for the staggered Signal Deck briefing flow. They are designed for Hermes cron jobs or manual agent runs that write auditable artifacts under `runs/YYYY-MM-DD/`.

The prompts do not replace the deterministic repo pipeline. They produce the editorial inputs that the pipeline validates, transforms, renders, deploys, and delivers.

## Prompt architecture

Daily prompts now use a two-layer structure with XML-like semantic boundaries. The tags are prompt contracts, not presentation markup: they tell the model which instructions are identity, mission, input scope, reasoning posture, constraints, failure behavior, and output requirements.

1. **Shared operating context** under `shared/`
   - `<product_philosophy>`
   - `<reader_profile>`
   - `<editorial_standards>`
   - `<evidence_rules>`
   - `<scoring_rubric>`
   - `<artifact_discipline>`
2. **Phase-specific expert role prompts** at the daily prompt root
   - each phase has a distinct professional identity
   - each phase uses `<role>`, `<mission>`, `<inputs>`, `<reasoning_posture>`, `<instructions>`, `<anti_patterns>`, `<failure_behavior>`, and `<output_contract>`
   - optional operational details may use extra tags such as `<core_command>` or `<ingestion_package_rule>`

`prepare_daily_run.py` assembles these into self-contained phase prompts under `runs/YYYY-MM-DD/phase-prompts/` so Hermes cron sessions do not depend on hidden conversational context.

## Shared modules

```text
shared/product-philosophy.md
shared/reader-profile.md
shared/editorial-standards.md
shared/evidence-rules.md
shared/scoring-rubric.md
shared/artifact-discipline.md
```

## Phase order

```text
01-scout-broad.md                 — Strategic Intelligence Scout
02-scout-update-dedupe.md         — Source Critic and Dedupe Editor
03-editorial-synthesis.md         — Strategic Synthesis Editor
04-build-deploy.md                — Release Engineer and Editorial QA Operator
05-final-delivery.md              — Executive Delivery Editor
```

## Required variables

Each prompt assumes the scheduler or operator supplies:

- `editionDate`: target edition date, `YYYY-MM-DD`
- `runDir`: `runs/YYYY-MM-DD`
- `publicUrl`: production/public briefing URL
- `readerProfile`: target roles and interests
- `deliverySlot`: final nominal delivery time

## Artifact rule

Every phase must write or update a date-scoped artifact. Intermediate phases should normally deliver locally only; the final delivery phase is the only phase that should produce the user-facing Telegram message.

## Quality rule

The goal is not to automate a generic news digest. The goal is to preserve expert editorial judgment inside an auditable system: strong role, clear mission, explicit evidence boundaries, anti-patterns, and failure behavior for every phase.
