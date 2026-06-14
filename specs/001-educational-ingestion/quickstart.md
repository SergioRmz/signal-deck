# Quickstart: Educational Ingestion

## Purpose

This guide defines how to validate the educational ingestion feature once implementation tasks are generated and completed. It is intentionally contract-first: the checks should prove that the package is auditable before the renderer is involved.

## Prerequisites

From the repository root:

```bash
python3 --version
cd apps/web && npm install && cd ../..
```

The implementation should remain standard-library only on the Python side unless a later task explicitly introduces and documents a dependency.

## Scenario 1: Validate the educational ingestion package contract

Expected implementation artifacts:

```text
data/ingestion-package.schema.json
data/ingestion-package.sample.json
scripts/validate_ingestion_package.py
tests/test_validate_ingestion_package.py
```

Run:

```bash
python3 scripts/validate_ingestion_package.py data/ingestion-package.sample.json
python3 -m unittest tests/test_validate_ingestion_package.py -v
```

Expected outcome:

- Sample package passes schema validation.
- Semantic validation confirms:
  - 15-30 candidates for a normal completed run.
  - 5-8 selected signals unless underfilled.
  - 2-3 deep dive candidates when sufficient educational depth exists.
  - every selected signal includes Sergio canonical relevance rationale.
  - every rejected signal has an explicit rejection reason.
  - watch items are not used as strong factual foundations.

## Scenario 2: Validate source-role coverage and concentration handling

Run the validator against a fixture containing concentrated but high-quality signals:

```bash
python3 scripts/validate_ingestion_package.py data/ingestion-package.sample.json
```

Expected outcome:

- Selected/deep-dive signals expose source-role coverage where available.
- Concentration risk is reported when one domain, actor, publisher, or narrative dominates.
- If the package remains concentrated, it includes an editorial justification.
- If alternatives are available but weak, the package explains why they were not used for artificial balance.

## Scenario 3: Generate a briefing from selected educational signals

Run:

```bash
python3 -m unittest tests/test_generate_briefing.py -v
python3 scripts/generate_briefing.py
python3 scripts/validate_briefing.py
```

Expected outcome:

- Transformation still produces a valid briefing payload.
- The final briefing uses selected signals rather than raw candidate volume.
- Deep dives reflect educational density and reusable thesis quality.
- Existing briefing schema remains valid.

## Scenario 4: Run the full local pipeline with auditable artifacts

Run:

```bash
python3 -m unittest tests/test_run_briefing_pipeline.py -v
python3 scripts/run_briefing_pipeline.py --run-date 2026-06-14
```

Expected outcome:

The run folder contains the existing artifacts plus the new ingestion package artifact:

```text
runs/2026-06-14/
├── ingestion-package.json
├── briefing.final.json
├── visual-composition.json
├── telegram-message.md
└── manifest.json
```

The manifest should reference the ingestion package path so a reviewer can trace the briefing back to candidate selection and rejection decisions.

## Scenario 5: Verify renderer compatibility without redesign

Run:

```bash
python3 scripts/run_briefing_pipeline.py --run-date 2026-06-14 --build-renderer
```

Expected outcome:

- Python validators pass.
- `apps/web` build passes.
- Renderer consumes the final briefing and visual-composition artifacts as before.
- No public renderer redesign is required by this ingestion feature.

## Failure modes to test

Implementation tasks should add fixtures or unit tests for:

- underfilled run with fewer than 15 credible candidates;
- rejected signal missing rejection reason;
- selected signal missing canonical Sergio rationale;
- watch item incorrectly included as a selected deep dive;
- source ID referenced by a candidate but absent from `sources`;
- cluster referencing an unknown signal;
- high concentration risk without concentration rationale;
- sample/dry-run package accidentally marked as live material.

## Completion criteria

This feature is ready for implementation review when:

- schema and docs are updated;
- validators reject malformed or unsafe packages;
- deterministic transformation consumes validated selected material;
- run artifacts are durable and traceable;
- all Python tests pass;
- optional renderer build passes without public-page redesign.
