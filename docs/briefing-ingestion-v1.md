# Briefing Ingestion Contract v1

## Purpose

This document defines the first stable contract for the **input side** of `signal-deck`.

If the briefing contract answers **what the final artifact must look like**, the ingestion contract answers **what structured editorial material must exist before a briefing can be produced well**.

The goal is to stop treating upstream editorial work as invisible intuition.

## Why this contract exists

A strong executive briefing does not begin with page rendering.
It begins with:

- raw developments worth tracking
- candidate interpretations of those developments
- explicit relevance and priority signals
- a visible path from evidence to thesis

Without that layer, the system risks producing polished output with weak editorial discipline.

## Design goals

Version 1 is designed to be:

- expressive enough to capture real editorial inputs
- simple enough to author by hand
- structured enough to validate automatically
- clearly mappable to the briefing output contract

## Non-goals for v1

The following are intentionally deferred:

- full source-text storage
- automatic deduplication of source URLs
- granular confidence scoring
- collaborative edit history
- token-budget metadata for model orchestration
- citation rendering rules in the final page

Version 1 is about stabilizing the shape of upstream editorial material, not building the entire newsroom stack.

## Top-level shape

A valid ingestion payload contains the following top-level objects:

- `meta`
- `brief`
- `sources`
- `signals`
- `synthesis`
- `editorialDecisions`

## Section semantics

### `meta`

Describes the identity of the ingestion artifact.

Required fields:

- `schemaVersion`: for this version, always `"1.0"`
- `inputId`: stable identifier for the ingestion artifact
- `createdAt`: ISO-8601 timestamp for when the input packet was assembled
- `language`: content language such as `"en"` or `"es"`

Optional fields:

- `owners`: array of editors, agents, or processes that assembled the packet
- `tags`: freeform thematic tags

### `brief`

Defines what this ingestion packet is trying to produce.

Required fields:

- `topic`: the domain or subject under study
- `objective`: what the packet is supposed to help the briefing accomplish
- `audience`: who the resulting briefing is for
- `timeHorizon`: short label such as `"current"`, `"daily"`, `"quarterly"`, or `"structural"`

Optional fields:

- `deliverable`: expected artifact, for example `"executive briefing"`
- `constraints`: array of explicit editorial constraints

### `sources`

Captures the source objects from which signals were derived.

Each source requires:

- `sourceId`: stable local identifier
- `title`: human-readable source title
- `sourceType`: for example `article`, `earnings-call`, `paper`, `thread`, `dataset`, or `internal-note`
- `publisher`: origin or institution behind the source

Optional source fields:

- `url`
- `publishedAt`
- `summary`

Notes:

- `sources` stores provenance, not the fully transformed editorial judgment
- a source may be low-value by itself and still support a high-value signal when combined with others

### `signals`

Captures the developments that matter enough to compete for inclusion in the briefing.

Each signal requires:

- `signalId`: stable local identifier
- `statement`: concise statement of what changed or what matters
- `category`: lens such as `models`, `product`, `distribution`, `regulation`, `market`, or `labor`
- `priority`: one of `high`, `medium`, or `low`
- `sourceIds`: non-empty array of source identifiers supporting the signal
- `evidence`: short explanation of why the signal is credible or relevant
- `implications`: non-empty array of second-order or strategic implications

Optional signal fields:

- `counterpoints`: array of reasons the signal may be overstated or incomplete
- `notes`: extra editorial context

Notes:

- `statement` should describe the signal, not the final thesis
- `implications` should move the packet from observation toward interpretation

### `synthesis`

Holds the provisional editorial interpretation before the final briefing is written.

Required fields:

- `workingThesis`: best current explanation of what the packet suggests
- `supportingThemes`: non-empty array of reinforcing angles
- `openQuestions`: non-empty array of unresolved questions

Optional fields:

- `contradictions`: tensions inside the packet that deserve caution
- `missingInformation`: what evidence would most improve the next draft

Notes:

- this is the bridge between signal collection and final narrative framing
- it should remain revisable and may still contain uncertainty

### `editorialDecisions`

Makes the intended transformation toward the briefing output visible.

Required fields:

- `heroFrame`: opening frame for the final briefing
- `topLineThesis`: candidate top-line claim
- `radarOrder`: ordered array of signal IDs for scan priority
- `deepDiveSignalIds`: array of signal IDs most likely to justify expansion
- `marketMapFrames`: non-empty array of labels likely to structure the market map
- `watchlistSeeds`: non-empty array of monitorable questions or risks

Notes:

- this object is intentionally output-adjacent
- it records the editorial path from packet to artifact without yet writing the final artifact itself

## Mapping from ingestion to briefing v1

The expected transformation is:

- `brief.topic`, `brief.objective`, and `synthesis.workingThesis` help inform `hero`
- `editorialDecisions.topLineThesis` becomes the basis for `topLine`
- `editorialDecisions.radarOrder` determines which `signals` feed `radar.items`
- `editorialDecisions.deepDiveSignalIds` indicate which `signals` and themes should expand into `deepDives.items`
- `editorialDecisions.marketMapFrames` guide the framing of `marketMap.items`
- `synthesis.openQuestions` and `editorialDecisions.watchlistSeeds` feed `watchlist.items`

This contract does **not** require a one-to-one field copy. It requires a traceable editorial path.

## Editorial rules

Across the packet:

- prefer observations that can support strategic interpretation
- distinguish evidence from conclusion
- make priority explicit instead of implied
- surface uncertainty where it materially changes the thesis
- capture second-order implications early, not only in the final artifact

## Example outline

```json
{
  "meta": {
    "schemaVersion": "1.0",
    "inputId": "2026-06-11-distribution-shift-input",
    "createdAt": "2026-06-11T09:00:00Z",
    "language": "en"
  },
  "brief": {
    "topic": "AI distribution and product capture",
    "objective": "Assess where value is concentrating as model quality converges.",
    "audience": "executives and operators",
    "timeHorizon": "structural"
  },
  "sources": [
    {
      "sourceId": "src-1",
      "title": "Example source",
      "sourceType": "article",
      "publisher": "Example publisher"
    }
  ],
  "signals": [
    {
      "signalId": "sig-1",
      "statement": "Distribution is carrying more strategic weight as raw model differentiation narrows.",
      "category": "distribution",
      "priority": "high",
      "sourceIds": ["src-1"],
      "evidence": "Several product and market moves point in the same direction.",
      "implications": [
        "Workflow ownership matters more.",
        "Interface control becomes economically meaningful."
      ]
    }
  ],
  "synthesis": {
    "workingThesis": "The battle is moving up the stack from raw model quality to control of user context and workflow.",
    "supportingThemes": ["distribution", "workflow", "context capture"],
    "openQuestions": ["Which layer keeps the recurring user relationship?"]
  },
  "editorialDecisions": {
    "heroFrame": "The strategic surface is shifting from model access to packaging and workflow capture.",
    "topLineThesis": "Distribution is becoming as important as the model.",
    "radarOrder": ["sig-1"],
    "deepDiveSignalIds": ["sig-1"],
    "marketMapFrames": ["Winners", "Pressured", "Opportunity"],
    "watchlistSeeds": ["Which layer owns the recurring user relationship?"]
  }
}
```

## Validation

The formal machine-readable schema for this contract lives at:

- `apps/briefing-page/data/signal-input.schema.json`

For lightweight local checks without external dependencies, use:

- `python3 scripts/validate_signal_input.py`
- `python3 scripts/validate_signal_input.py apps/briefing-page/data/signal-input.sample.json`

The schema, sample, validator, and this document should evolve together.
