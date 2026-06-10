# Briefing Contract v1

## Purpose

This document defines the first stable editorial contract for a `signal-deck` briefing.

The contract exists to separate three concerns that should evolve independently:

1. **Editorial intelligence** — what the briefing says
2. **Presentation** — how the briefing is rendered
3. **Distribution** — where and how the briefing is published

Version 1 intentionally stays narrow. It is designed to be:

- easy to read
- easy to generate
- easy to validate
- stable enough for the static page to consume without UI-specific coupling

## Design goals

The v1 contract should support a briefing that feels:

- thesis-driven rather than summary-driven
- compact but information-dense
- reusable across topics in technology, AI, and the economy
- presentation-agnostic enough to survive future renderer changes

## Non-goals for v1

Version 1 does **not** attempt to model everything yet.

The following are explicitly deferred:

- per-claim source citations
- confidence scores
- historical archives and previous/next links
- asset embeds (charts, logos, images)
- multi-briefing collections
- user personalization
- workflow metadata for internal editorial tooling

Those can be added later in v2+ once the core briefing shape is stable.

## Top-level shape

A valid v1 briefing contains the following top-level objects:

- `meta`
- `hero`
- `topLine`
- `radar`
- `deepDives`
- `marketMap`
- `watchlist`

## Section semantics

### `meta`

Describes the identity and publication metadata of the briefing.

Required fields:

- `schemaVersion`: contract version string. For this version, always `"1.0"`
- `briefingId`: stable identifier for the briefing
- `editionDate`: human-readable edition label for display

Optional fields:

- `publishedAt`: ISO-8601 timestamp
- `slug`: URL-safe identifier
- `language`: content language, for example `"en"` or `"es"`
- `topics`: array of thematic tags

Notes:

- `meta` should contain editorial metadata, not renderer settings
- presentation details like dark mode, layout mode, or hosting concerns do not belong here

### `hero`

Defines the opening frame of the page.

Required fields:

- `title`: the main headline or framing statement
- `lede`: a short paragraph explaining the scope or promise of the edition

Notes:

- this is the narrative wrapper for the briefing, not the top thesis itself
- keep it readable and broad enough to orient the reader quickly

### `topLine`

Defines the primary thesis of the edition.

Required fields:

- `title`: the key claim in headline form
- `body`: a compact argument explaining why the thesis matters

Notes:

- this is the most important section in the artifact
- it should express a view, not just a topic label

### `radar`

Captures a concise scan of relevant signals.

Required fields:

- `title`: section heading
- `items`: array of radar entries

Each radar item requires:

- `label`: short category or lens
- `text`: one-line signal statement

Notes:

- radar items should be fast to scan
- each item should earn its place by adding a distinct angle

### `deepDives`

Expands the main thesis through a small number of structured arguments.

Required fields:

- `title`: section heading
- `items`: array of deep-dive entries

Each deep-dive item requires:

- `title`: sub-thesis or angle
- `body`: explanatory paragraph

Notes:

- keep the number of deep dives intentionally small
- each item should deepen the reader's model, not repeat the top line

### `marketMap`

Maps incentives, winners, losers, and strategic consequences.

Required fields:

- `title`: section heading
- `items`: array of market-map entries

Each market-map item requires:

- `label`: frame such as `Winners`, `Pressured`, or `Opportunity`
- `text`: consequence or explanation

Notes:

- this section should translate abstract change into strategic positioning
- labels may evolve per edition, but the structure should stay consistent

### `watchlist`

Defines what should be monitored next.

Required fields:

- `title`: section heading
- `items`: array of watchlist entries

Each watchlist item requires:

- `text`: a question, risk, or forward-looking checkpoint

Notes:

- entries should be specific enough to guide follow-up monitoring
- prefer concrete open questions over vague caution statements

## Editorial rules

Across all sections:

- prefer sharp declarative language over generic analyst phrasing
- avoid repeating the same idea across hero, top line, and deep dives
- optimize for strategic clarity, not maximum verbosity
- preserve a strong distinction between summary, argument, and implication

## Example outline

```json
{
  "meta": {
    "schemaVersion": "1.0",
    "briefingId": "2026-06-10-distribution-as-moat",
    "editionDate": "2026-06-10",
    "language": "en",
    "topics": ["ai", "distribution", "product-strategy"]
  },
  "hero": {
    "title": "Executive briefings with thesis, context, and consequences.",
    "lede": "A compact strategic read on technology, AI, and the economy."
  },
  "topLine": {
    "title": "Distribution is becoming as important as the model.",
    "body": "Control of interface, workflow, and user context is increasingly where capture happens."
  },
  "radar": {
    "title": "Radar",
    "items": [
      {
        "label": "Models",
        "text": "Raw model differentiation is narrowing."
      }
    ]
  },
  "deepDives": {
    "title": "Three angles to read the shift",
    "items": [
      {
        "title": "The battleground is moving",
        "body": "Product integration and workflow control matter more as models commoditize."
      }
    ]
  },
  "marketMap": {
    "title": "Who benefits if this thesis is right",
    "items": [
      {
        "label": "Winners",
        "text": "Platforms with distribution and daily user surface area."
      }
    ]
  },
  "watchlist": {
    "title": "What to watch",
    "items": [
      {
        "text": "Which layer owns the recurring user relationship?"
      }
    ]
  }
}
```

## Validation

The formal machine-readable schema for this contract lives at:

- `apps/briefing-page/data/briefing.schema.json`

Human-readable guidance lives in this document.

For lightweight local checks without external dependencies, use:

- `python3 scripts/validate_briefing.py`
- `python3 scripts/validate_briefing.py apps/briefing-page/data/briefing.sample.json`

Both the schema and the validator should evolve together with this document.
