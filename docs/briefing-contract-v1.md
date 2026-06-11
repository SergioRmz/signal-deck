# Briefing Contract v1

## Purpose

This document defines the stable editorial contract for a `signal-deck` briefing.

The contract separates three concerns that should evolve independently:

1. **Editorial intelligence** — what the briefing says
2. **Presentation** — how the briefing is rendered
3. **Distribution** — where and how the briefing is published

Version 1 stays intentionally lean, but it now supports a more pedagogical shape than a generic executive digest.

## Design goals

The v1 contract should support a briefing that feels:

- thesis-driven rather than summary-driven
- compact but information-dense
- reusable across technology, AI, and the economy
- pedagogical, not just informative
- presentation-agnostic enough to survive renderer changes

## Non-goals for v1

The following are still out of scope:

- per-claim source citations
- confidence scores
- historical archives and previous/next links
- asset embeds (charts, logos, images)
- multi-briefing collections
- internal workflow state for editorial tooling

## Top-level shape

A valid v1 briefing requires:

- `meta`
- `hero`
- `topLine`
- `radar`
- `deepDives`
- `marketMap`
- `watchlist`

It may also include:

- `readerTranslation`
- `reusableLesson`

These optional blocks let the artifact act more like a mini master class without forcing every renderer to support them immediately.

## Section semantics

### `meta`

Describes identity and publication metadata.

Required fields:

- `schemaVersion`: always `"1.0"`
- `briefingId`: stable identifier
- `editionDate`: human-readable edition label

Optional fields:

- `publishedAt`: ISO-8601 timestamp
- `slug`: URL-safe identifier
- `language`: content language such as `"en"` or `"es"`
- `topics`: thematic tags
- `readerContext`: lightweight reader-targeting context

#### `readerContext`

Optional fields:

- `roles`: reader roles relevant to this edition
- `interests`: domains to overweight
- `desiredUpgrade`: what kind of strategic upgrade the briefing should deliver

Notes:

- `meta` should contain editorial metadata, not renderer settings
- presentation details like theme, layout mode, or hosting do not belong here

### `hero`

Defines the opening frame.

Required fields:

- `title`: main headline or framing statement
- `lede`: short orientation paragraph

Optional fields:

- `signal`: trigger observation
- `thesis`: governing thesis in compressed form
- `tension`: what makes the thesis non-obvious or contested
- `promise`: what the reader should get from the piece

Notes:

- this block can operate as a signal-thesis hero, not just a decorative opening
- it should orient fast and establish the intellectual stakes

### `topLine`

Defines the core thesis.

Required fields:

- `title`: key claim in headline form
- `body`: compact argument

Optional fields:

- `stakes`: why the thesis matters strategically

Notes:

- this remains the most important section in the artifact
- it should express a view, not just a topic label

### `radar`

Captures the evidence scan around the thesis.

Required fields:

- `title`: section heading
- `items`: radar entries

Each radar item requires:

- `label`: short category or lens
- `text`: signal statement

Optional per item:

- `role`: one of `supports-thesis`, `complicates-thesis`, `contradiction`, `monitor`

Notes:

- this is better understood as an evidence radar than a novelty feed
- each item should add a distinct angle on the thesis

### `deepDives`

Expands the thesis through structured mechanisms.

Required fields:

- `title`: section heading
- `items`: deep-dive entries

Each deep-dive item requires:

- `title`: sub-thesis or angle
- `body`: explanatory paragraph

Optional per item:

- `mechanism`: named driver
- `claim`: compact causal claim
- `explanation`: why the mechanism works
- `implication`: reusable consequence

Notes:

- this block should deepen the reader's model, not repeat the top line
- mechanism-rich entries are preferred over generic commentary

### `marketMap`

Maps incentives, winners, losers, and strategic consequences.

Required fields:

- `title`: section heading
- `items`: market-map entries

Each market-map item requires:

- `label`: frame such as `Winners`, `Power gaining`, or `Opportunity`
- `text`: consequence or explanation

Optional per item:

- `powerShift`: explicit note on how leverage is moving

Notes:

- this section should translate abstract change into strategic positioning
- labels may evolve per edition, but the structure should stay consistent

### `readerTranslation`

Optional module that translates the thesis for specific reader roles.

Required fields:

- `title`: section heading
- `items`: translation entries

Each item requires:

- `role`: reader role being addressed
- `headline`: compressed implication for that role
- `body`: explanation for that reader

Optional per item:

- `weight`: positive numeric priority

Notes:

- this is where personalization becomes explicit in the final artifact
- it is especially useful when one thesis must serve multiple roles

### `reusableLesson`

Optional module that extracts the durable pattern from the edition.

Required fields:

- `title`: section heading
- `pattern`: reusable strategic pattern
- `takeaway`: operational takeaway

Optional fields:

- `applyWhen`: situations where the pattern should be reused

Notes:

- this block turns a good briefing into a compounding learning asset

### `watchlist`

Defines what should be monitored next.

Required fields:

- `title`: section heading
- `items`: watchlist entries

Each watchlist item requires:

- `text`: question, risk, checkpoint, or metric prompt

Optional per item:

- `type`: one of `confirmation`, `invalidation`, `metric`, `question`

Notes:

- this block should behave like a watch framework, not generic caution
- prefer monitorable prompts over vague warnings

## Editorial rules

Across all sections:

- prefer sharp declarative language over generic analyst phrasing
- avoid repeating the same idea across hero, top line, and deep dives
- optimize for strategic clarity, not verbosity
- preserve a clear distinction between signal, argument, mechanism, implication, and monitoring
- aim to leave the reader with a reusable model, not only an updated opinion

## Validation

Machine-readable schema:

- `apps/briefing-page/data/briefing.schema.json`

Canonical sample:

- `apps/briefing-page/data/briefing.sample.json`

Lightweight validator:

- `python3 scripts/validate_briefing.py`
- `python3 scripts/validate_briefing.py apps/briefing-page/data/briefing.sample.json`

The schema, sample, validator, and this document should evolve together.
