# Visual Composition Contract v1

## Purpose

This document defines the first stable contract for the **visual composition layer** in `signal-deck`.

If the briefing contract defines **what the editorial artifact says**, the visual composition contract defines **how that artifact should be staged, sequenced, and embodied on the page**.

Version 1 exists to prevent the final experience from collapsing into a single rigid template while still keeping the system coherent and reusable.

## Why this contract exists

A premium briefing product cannot rely on only two modes:

- a fixed template that makes every edition feel identical
- unconstrained improvisation that makes every edition feel noisy or inconsistent

`signal-deck` needs a middle layer: a composition system that allows strong visual variation inside a disciplined design grammar.

That layer is what turns a readable briefing into a piece with:

- attraction
- rhythm
- surprise
- clarity
- replay value
- daily habit potential

The product goal is not decoration. It is a visual reading experience that makes the user want to **touch, play, and learn**.

## Position in the architecture

The intended flow is now:

1. ingestion packet
2. briefing transformation
3. structured briefing payload
4. visual composition payload
5. rendered one-page experience
6. external delivery

The visual composition contract sits **between** editorial structure and renderer implementation.

## Design goals for v1

Version 1 should be:

- expressive enough to support meaningful visual variation
- constrained enough to keep the system recognizable
- machine-readable and easy to validate
- compatible with a dark-theme-only product direction
- capable of encoding engagement intentionally rather than leaving it to ad hoc styling

## Non-goals for v1

The following are intentionally deferred:

- per-user personalization
- animation timelines
- A/B testing metadata
- accessibility scoring beyond structural preparation
- device-specific layout trees
- renderer-specific CSS tokens
- freeform design prompts with no controlled vocabulary

Version 1 is a stable composition language, not a full creative engine.

## Top-level shape

A valid visual composition payload contains these top-level objects:

- `meta`
- `sourceBriefing`
- `experience`
- `designSystem`
- `page`
- `modules`

## Section semantics

### `meta`

Describes the identity of the composition payload.

Required fields:

- `schemaVersion`: always `"1.0"` for this contract
- `compositionId`: stable identifier for the composition artifact
- `createdAt`: ISO-8601 timestamp
- `language`: content language

Optional fields:

- `tags`: thematic tags

### `sourceBriefing`

Identifies the briefing that this composition is staging.

Required fields:

- `briefingId`
- `editionDate`
- `slug`

Optional fields:

- `topics`: array of briefing topics

### `experience`

Captures the intended emotional and cognitive posture of the page.

Required fields:

- `visualTone`: one of `sharp`, `playful`, `cinematic`, `dense`, `electric`, `sober`, or `hybrid`
- `readingMode`: one of `scan`, `guided`, `explore`, or `mixed`
- `engagementGoal`: short phrase describing what should make the page compelling
- `interactionModel`: one of `static`, `progressive`, `tactile`, or `layered`

Optional fields:

- `hooks`: array of short cues that describe the intended draw of the experience
- `learningPrompts`: array of cues that reinforce the "touch, play, learn" behavior

Notes:

- this object makes the product ambition explicit
- the page should not only look good; it should invite attention and structured curiosity

### `designSystem`

Defines the reusable visual basis.

Required fields:

- `theme`: for v1, always `"dark"`
- `palette`: object with required keys `base`, `surface`, `text`, `accent`, `accentStrong`
- `density`: one of `low`, `medium`, or `high`
- `cornerStyle`: one of `soft`, `rounded`, `mixed`, or `sharp`
- `shadowStyle`: one of `ambient`, `crisp`, `glow`, or `minimal`

Optional fields:

- `texture`: one of `none`, `grid`, `grain`, `glowfield`, or `mixed`
- `componentFamily`: short label for the dominant component system

Notes:

- this is the stable base layer: background, color logic, and visual physics
- it should support variety without losing product identity

### `page`

Defines whole-page composition choices.

Required fields:

- `heroVariant`: one of `thesis-wall`, `split-hero`, `manifesto`, `signal-led`, or `dashboard-hero`
- `rhythm`: one of `linear`, `modular`, `asymmetric`, `staged`, or `mosaic`
- `emphasis`: one of `topline`, `radar`, `deep-dives`, `market-map`, `watchlist`, or `balanced`
- `moduleOrder`: non-empty ordered array of module IDs

Optional fields:

- `stickyElements`: array of labels for persistent UI anchors
- `scrollMood`: one of `steady`, `punctuated`, or `surprising`

### `modules`

Defines the reusable components selected for this edition.

Each module requires:

- `moduleId`: stable local identifier
- `kind`: one of `hero`, `topline`, `reader-translation`, `radar`, `deep-dive-grid`, `deep-dive-stack`, `market-map`, `reusable-lesson`, `watchlist`, `quote-band`, `signal-strip`, or `comparison-panel`
- `variant`: short controlled label for the component style
- `sourceKey`: which briefing section this module stages
- `priority`: one of `primary`, `secondary`, or `supporting`

Optional module fields:

- `headline`
- `body`
- `layoutHints`: array of short layout cues
- `interactionCue`: short phrase describing what the user should feel invited to do
- `accentMode`: one of `base`, `accent`, `contrast`, or `heat`
- `dataRefs`: array of references into the briefing payload, such as `radar.items` or `deepDives.items`

Notes:

- modules are semantically meaningful, not decorative fragments
- a future renderer should be able to choose component implementations from `kind` + `variant`
- `interactionCue` is important because the product wants engagement, not passive reading alone

## Editorial-to-visual mapping guidance

A composition payload should encode judgments like:

- whether the edition should feel more exploratory or more thesis-first
- whether the radar deserves quick-strip treatment or denser list treatment
- whether the deep dives should read as cards, stacks, or spotlight modules
- whether the market map should feel analytical, dramatic, or tactile
- where the main visual hook should live

This contract does not store every CSS detail.
It stores the compositional intent the renderer should honor.

## Example outline

```json
{
  "meta": {
    "schemaVersion": "1.0",
    "compositionId": "2026-06-11-distribution-composition",
    "createdAt": "2026-06-11T09:05:00Z",
    "language": "en"
  },
  "sourceBriefing": {
    "briefingId": "2026-06-11-distribution-is-becoming-as-important-as-the-model",
    "editionDate": "2026-06-11",
    "slug": "distribution-is-becoming-as-important-as-the-model"
  },
  "experience": {
    "visualTone": "electric",
    "readingMode": "mixed",
    "engagementGoal": "Make the briefing feel like a strategic object you want to explore, not only scan.",
    "interactionModel": "layered"
  },
  "designSystem": {
    "theme": "dark",
    "palette": {
      "base": "#07111f",
      "surface": "#0f1d33",
      "text": "#e9eef8",
      "accent": "#78a4ff",
      "accentStrong": "#8df0d3"
    },
    "density": "medium",
    "cornerStyle": "rounded",
    "shadowStyle": "glow"
  },
  "page": {
    "heroVariant": "thesis-wall",
    "rhythm": "staged",
    "emphasis": "topline",
    "moduleOrder": ["mod-hero", "mod-topline", "mod-reader-translation", "mod-radar", "mod-deep-dives", "mod-market-map", "mod-reusable-lesson", "mod-watchlist"]
  },
  "modules": [
    {
      "moduleId": "mod-hero",
      "kind": "hero",
      "variant": "thesis-wall-glow",
      "sourceKey": "hero",
      "priority": "primary",
      "interactionCue": "Land fast, create curiosity, and establish the mood.",
      "dataRefs": ["hero.title", "hero.lede"]
    }
  ]
}
```

## Validation

The formal machine-readable schema for this contract lives at:

- `apps/briefing-page/data/visual-composition.schema.json`

For lightweight local checks without external dependencies, use:

- `python3 scripts/validate_visual_composition.py`
- `python3 scripts/validate_visual_composition.py apps/briefing-page/data/visual-composition.sample.json`

## What v1 proves

This contract proves that `signal-deck` can distinguish three visual responsibilities clearly:

1. editorial meaning
2. composition intent
3. final rendering

That separation is what enables a daily product to feel fresh without becoming arbitrary.