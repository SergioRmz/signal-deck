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

## Candidate pool semantics

A normal `complete` run should contain **15-30 candidates**. If a run discovers fewer credible candidates, the package must set `run.status` to `underfilled` or `needs_review` and include a `qualityNotes` entry explaining the fallback. The validator also checks that run count fields match the actual array lengths.

For the core signal-deck editorial scope, a complete package must include candidate coverage across:

- `technology`
- `ai`
- `economy`

This is a coverage floor, not a forced equal split. The package may remain concentrated when the day genuinely demands it, but concentration must be auditable in `run.sourceDiversity` and later selection notes.

## Source metadata requirements

Every candidate must reference at least one known `sources[].sourceId`. Every source must include:

- `title`
- `publisher`
- `sourceType`
- `sourceRole`
- `credibilityNotes`
- either `publishedAt` or explicit access/publication limitations

Candidate `auditNotes` should preserve source or publication metadata caveats so a reviewer can distinguish verified facts from placeholders, paywalled context, or missing timestamps.

## Reader profile lens semantics

The package must contain exactly one canonical Sergio profile:

- `profileId: sergio-canonical`
- `canonical: true`
- `roles`: multiple roles are allowed and expected; profile modeling must not force Sergio or future readers into one exclusive role.

Every candidate must include `profileRelevance` for `sergio-canonical` with a non-empty rationale. Every selected signal must include `profileRationale`, which is the downstream-ready explanation of why the signal matters for Sergio's learning and competitive-advantage lens.

## Educational value assessment

Educational scoring is separate from factual relevance. A candidate can be timely and still weak if it cannot teach a reusable mechanism. Every candidate must provide:

- `editorialRationale`: why the item may matter for the briefing.
- `educationalValue.score`: numeric score from `0` to `1`.
- `educationalValue.teachingMechanisms`: at least one concrete teaching mechanism such as `causal_mechanism`, `incentive_structure`, `technical_moat`, or `risk_pattern`.
- `educationalValue.learningRationale`: what a reader should learn from the signal.
- `educationalValue.deepDivePotential`: `none`, `possible`, or `strong`.

A candidate with educational score below `0.4` is considered weak for the product's teaching mission. It must be downgraded to `watch_item`/`merged` or rejected; if rejected specifically for weak learning value, it should use `rejectionReason: low_educational_value`.

## Clustering, selection, and deep-dive rules

Clusters turn individual signals into reusable theses. Each cluster must reference known candidate `signalIds` and explain:

- `thesisCandidate`: the executive lesson the cluster could teach.
- `sharedMechanism`: the causal/economic/technical mechanism that binds the signals.
- `keyTension`: the contradiction or tradeoff a deep dive should not hide.
- `educationalRationale`: why the cluster deserves teaching time.

A normal `complete` run must promote **5-8 selected signals**. It must include **2-3 `deep_dive` selections**. Deep dives are not picked by hype: they require strong educational density. For a signal or cluster to serve as a deep dive, at least one underlying candidate must have:

- `educationalValue.score >= 0.75`
- `educationalValue.deepDivePotential: strong`
- a teaching mechanism such as `reusable_mental_model`, `causal_mechanism`, `second_order_effect`, `technical_moat`, or `market_structure`

`generate_briefing.py` now accepts either the legacy v1 `signal-input` packet or the v2 ingestion package. For v2 packages, it adapts selected signals and clusters into the existing v1 transformation layer so downstream renderer behavior remains compatible while the richer ingestion artifact matures.

## Validation

Run the validator from the repository root:

```bash
python3 scripts/validate_ingestion_package.py data/ingestion-package.sample.json
python3 -m unittest tests/test_validate_ingestion_package.py -v
```

The validator performs structural contract checks using `data/ingestion-package.schema.json` plus shared helper checks for object shape, unique IDs, cross references, candidate volume, domain coverage, and source metadata completeness. Additional story-specific semantic rules are added incrementally in later implementation groups.
