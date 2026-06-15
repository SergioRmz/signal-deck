# Prompt: Editorial Synthesis

## Use when
Run this after `scout-updated.json` exists and before the deterministic build/deploy phase.

## Inputs

- `editionDate`: target date, `YYYY-MM-DD`
- `runDir`: `runs/YYYY-MM-DD`
- `runs/YYYY-MM-DD/scout-updated.json`
- current ingestion package schema in `data/ingestion-package.schema.json`

## Goal
Turn promoted signals into an editorial plan and a valid ingestion package that the deterministic pipeline can consume.

This is the strategic center of the daily run. It must make the reasoning path explicit before the generator turns the packet into the final briefing payload.

## Instructions

1. Read `scout-updated.json`.
2. Identify the issue thesis.
3. Decide which promoted signals are evidence, context, or watch material.
4. Separate facts, inferences, and speculation.
5. Run a contrarian pass:
   - strongest alternative explanation
   - likely overclaim
   - missing evidence
   - what would change the conclusion
6. Choose the dominant pedagogical function:
   - market map
   - strategy lesson
   - career lesson
   - tools/workflow lesson
   - early signal to monitor
   - technical paradigm shift
   - winners-vs-losers arbitrage
7. Write `runs/YYYY-MM-DD/editorial-plan.json`.
8. Write `runs/YYYY-MM-DD/ingestion-package.json` that conforms to the current ingestion package schema.
9. Update `runs/YYYY-MM-DD/run-timeline.json` phase `editorial synthesis` to `completed` or `blocked`.

## Editorial plan contract

Write JSON with this shape:

```json
{
  "editionDate": "YYYY-MM-DD",
  "phase": "editorial synthesis",
  "status": "completed",
  "generatedAt": "ISO-8601 timestamp",
  "thesis": "The structural argument of the issue.",
  "dominantPedagogicalFunction": "strategy lesson",
  "readerAdvantage": "What the reader should understand or do better after reading.",
  "evidenceStack": [
    {
      "signalId": "stable-kebab-id",
      "role": "primary|supporting|context",
      "facts": ["Verified fact."],
      "inferences": ["Interpretive claim."],
      "riskBoundary": "How to avoid overclaiming."
    }
  ],
  "contrarianReview": {
    "alternativeExplanation": "A credible competing interpretation.",
    "overclaimRisk": "Where the thesis could be too strong.",
    "missingEvidence": ["Evidence that would improve confidence."],
    "confidence": "high|medium|low"
  },
  "compositionRouting": {
    "primaryMode": "mechanism-map|power-shift-map|market-map|role-lens|watch-sensors",
    "reason": "Why this visual/pedagogical shape fits the issue."
  },
  "blockedReason": null
}
```

## Ingestion package rule

The ingestion package is the machine-facing artifact. It must validate before the build/deploy phase begins.

Do not invent sources, quotes, or facts. If evidence is insufficient, block the run honestly.
