# Briefing Transformation Layer v1

## Purpose

This document defines the first explicit transformation layer in `signal-deck`.

If the ingestion contract describes the structured editorial packet and the briefing contract describes the final structured artifact, the transformation layer defines **how the system moves from one to the other**.

Version 1 is still deterministic by design, but it now targets a more pedagogical briefing shape rather than a plain executive recap.

## Why this layer matters

Without a visible transformation layer, the most valuable part of the system stays hidden inside prompts, manual intuition, or renderer-side assumptions.

That is dangerous because it makes it hard to:

- explain why a briefing says what it says
- test whether the output follows the intended rules
- improve editorial quality without breaking downstream consumers
- compare different transformation strategies over time

The goal of v1 is not to solve editorial judgment completely.
The goal is to make the first transformation rules explicit, runnable, and debuggable.

## Inputs and outputs

### Input

The transformation layer consumes a payload that matches:

- `docs/briefing-ingestion-v1.md`
- `apps/briefing-page/data/signal-input.schema.json`

### Output

It emits a payload that matches:

- `docs/briefing-contract-v1.md`
- `apps/briefing-page/data/briefing.schema.json`

## Current implementation

The current transformation entry point is:

- `scripts/generate_briefing.py`

Default paths:

- input: `apps/briefing-page/data/signal-input.sample.json`
- output: `apps/briefing-page/data/briefing.sample.json`

## Design goals for v1

Version 1 is designed to be:

- deterministic
- easy to inspect
- lightweight to run locally
- good enough to prove the architecture
- honest about where editorial heuristics still remain crude

## Non-goals for v1

The following are intentionally deferred:

- claim-level citation rendering
- scoring functions for source confidence
- multiple output shapes from a single run
- historical comparisons across editions
- agent orchestration inside the transformation step
- model-based rewriting and ranking pipelines

Version 1 is a transparent baseline, not the finished editorial engine.

## Core transformation rules

### 1. Validate the ingestion packet first

The generator must reject malformed input before attempting any editorial transformation.

### 2. Promote editorial intent into briefing structure

The transformation treats `editorialDecisions` as the strongest explicit signal for shaping the final artifact.

Examples:

- `heroFrame` becomes `hero.title`
- `topLineThesis` becomes `topLine.title`
- `radarOrder` determines the order of `radar.items`
- `deepDiveSignalIds` determines which signals expand into `deepDives.items`
- `watchlistSeeds` contributes directly to `watchlist.items`

### 3. Use synthesis as the narrative bridge

The transformation uses `synthesis.workingThesis`, `supportingThemes`, `openQuestions`, and `contradictions` to move from observation toward argument.

This means:

- `workingThesis` informs `hero.thesis` and `topLine.body`
- `contradictions` can become `hero.tension`
- `supportingThemes` can inform `reusableLesson.applyWhen`
- `openQuestions` contributes to `watchlist.items`

### 4. Convert signals into pedagogical modules

Signals should not only populate a recap list.
They should be turned into modules that help the reader learn something reusable.

This means:

- the first ordered signal can become `hero.signal`
- radar entries become an **evidence radar** with simple semantic roles
- deep dives become a **mechanism breakdown** with `mechanism`, `claim`, `explanation`, and `implication`
- market-map frames produce explicit `powerShift` descriptions
- the transformation should emit a `reusableLesson` block even when personalization is absent

### 5. Keep the generated briefing compact

The transformation should not dump the full ingestion packet into the final artifact.

Instead it should:

- compress repeated ideas
- preserve high-signal observations
- surface implications that help an executive reader reason quickly
- keep each section legible inside the one-page format

### 6. Preserve traceability

The output does not need to be a literal field-for-field copy.
It does need to preserve a visible path from:

- input packet identity
- prioritized signals
- working thesis
- editorial decisions

into the final briefing payload.

## Field mapping guidance

### `meta`

Generated from the ingestion packet:

- `schemaVersion` → always `"1.0"`
- `briefingId` → derived from the edition date plus a slugified thesis
- `editionDate` → date derived from `meta.createdAt`
- `publishedAt` → defaults to `meta.createdAt`
- `slug` → derived from the thesis
- `language` → copied from `meta.language`
- `topics` → copied from `meta.tags` when present
- `readerContext` → copied from `brief.readerProfile` when that richer input is available

### `hero`

Generated from:

- `editorialDecisions.heroFrame`
- first prioritized signal in `radarOrder`
- `brief.objective`
- `synthesis.workingThesis`
- `synthesis.contradictions` or signal counterpoints when present

The hero should orient the reader to the edition's strategic frame, not merely repeat the top-line claim.

### `topLine`

Generated from:

- `editorialDecisions.topLineThesis`
- `synthesis.workingThesis`
- strongest implications from the highest-priority signals

The goal is to express the thesis, the argument, and the stakes.

### `radar`

Generated from:

- ordered signals referenced by `editorialDecisions.radarOrder`

Each item stays concise:

- `label` comes from the signal category
- `text` comes from the signal statement
- `role` is inferred heuristically from signal priority and whether the signal mainly supports or complicates the thesis

### `deepDives`

Generated from:

- signals referenced by `editorialDecisions.deepDiveSignalIds`

Each deep dive should combine:

- the signal statement as the local claim
- the signal evidence as the explanation layer
- one implication worth carrying forward
- optional counterpoints when they materially change the reading

### `marketMap`

Generated from:

- `editorialDecisions.marketMapFrames`
- the aggregate direction of the packet's implications

Version 1 still uses deterministic heuristics rather than a full market-modeling engine.
That is acceptable as long as the output remains coherent and inspectable.

### `readerTranslation`

Optional.
Generated only when the input packet already includes structured `brief.readerProfile.roles`.

This keeps the transformation forward-compatible with personalization work without forcing fake role-specific output when the input is generic.

### `reusableLesson`

Generated from:

- the packet's central thesis
- `synthesis.supportingThemes`
- the strongest implications from high-priority signals

This block should extract a reusable strategic pattern from the edition.

### `watchlist`

Generated from:

- `editorialDecisions.watchlistSeeds`
- `synthesis.openQuestions`

Duplicate questions should be removed while preserving order.
The generator may also assign a lightweight `type` heuristic such as `question` or `metric`.

## Validation and local usage

Generate the sample briefing:

```bash
python3 scripts/validate_signal_input.py
python3 scripts/generate_briefing.py
python3 scripts/validate_briefing.py
```

Generate from an explicit input path:

```bash
python3 scripts/generate_briefing.py path/to/input.json path/to/output.json
```

## What v1 proves

This layer proves that the repository now has an explicit editorial path:

1. structured ingestion packet
2. deterministic transformation
3. validated briefing payload
4. a clean handoff into the visual composition layer
5. presentation that can render from structured inputs rather than ad hoc assumptions

That is the minimum viable backbone for turning agent-collected material into a repeatable editorial artifact.

## What should improve next

The next iterations should likely focus on:

- stronger ranking and compression logic
- richer market-map generation
- explicit source traces or citations
- multiple renderer targets from the same briefing payload
- an auditable distinction between deterministic rules and model-authored prose
- tighter integration with future React + Vite component rendering
