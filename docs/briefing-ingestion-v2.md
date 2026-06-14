# Briefing Ingestion Package v2

`data/ingestion-package.sample.json` is the canonical local example for the educational ingestion package. The package sits upstream of the existing briefing transformation and records the complete editorial scouting decision: discovered candidates, source provenance, educational evaluation, reader-profile relevance, clustering, selections, rejections, watch items, and quality notes.

The machine-readable contract lives at `data/ingestion-package.schema.json`; the planning source remains in `specs/001-educational-ingestion/contracts/ingestion-package-v2.schema.json`.

## Top-level shape

A v2 package contains these required sections:

- `meta`: schema version, package ID, creation timestamp, language, and package domains.
- `run`: run identity, date, status, counts, and source-diversity summary.
- `readerProfiles`: one or more reader lenses; the canonical Sergio profile is added in the profile story.
- `sources`: provenance records with publisher, source type, source role, optional URL/timestamp, and credibility notes.
- `candidates`: discovered signal candidates with factual summaries, domain tags, source references, editorial rationale, educational value, profile relevance, confidence, and corroboration status.
- `clusters`: thematic groupings used later for thesis and deep-dive selection.
- `selectedSignals`: promoted signals or clusters for downstream briefing transformation.
- `rejectedSignals`: auditable exclusions.
- `watchItems`: uncertain but potentially useful signals to revisit.
- `qualityNotes`: run-level notes for underfilled runs, concentration risk, or other quality caveats.

## Validation

Run the validator from the repository root:

```bash
python3 scripts/validate_ingestion_package.py data/ingestion-package.sample.json
python3 -m unittest tests/test_validate_ingestion_package.py -v
```

The validator performs structural contract checks using `data/ingestion-package.schema.json` plus shared helper checks for object shape, unique IDs, and cross references. User-story-specific semantic rules are added incrementally in the implementation tasks.
