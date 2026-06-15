# Prompt: Scout Update / Dedupe

## Use when
Run this after `scout-broad` and before editorial synthesis.

## Inputs

- `editionDate`: target date, `YYYY-MM-DD`
- `runDir`: `runs/YYYY-MM-DD`
- `runs/YYYY-MM-DD/scout-broad.json`

## Goal
Reduce the broad candidate set into a smaller, cleaner set of publishable signals, watch items, and rejected items.

## Instructions

1. Read `scout-broad.json`.
2. Re-check the strongest candidates for updated source quality and duplicate coverage.
3. Merge duplicate candidates that are really the same structural signal.
4. Reject weak candidates explicitly; do not silently drop them.
5. Keep watch items out of the final factual evidence stack unless their uncertainty is clear.
6. Promote only candidates that can support a thesis without overclaiming.
7. Write `runs/YYYY-MM-DD/scout-updated.json`.
8. Update `runs/YYYY-MM-DD/run-timeline.json` phase `scout update / dedupe` to `completed` or `blocked`.

## Output contract

Write JSON with this shape:

```json
{
  "editionDate": "YYYY-MM-DD",
  "phase": "scout update / dedupe",
  "status": "completed",
  "generatedAt": "ISO-8601 timestamp",
  "promoted": [
    {
      "id": "stable-kebab-id",
      "title": "Signal title",
      "summary": "Why this signal survived.",
      "sourceConfidence": "high|medium|low",
      "evidenceRole": "primary-signal|supporting-signal|context",
      "sources": [
        {
          "title": "Source title",
          "url": "https://...",
          "sourceType": "primary|secondary|market-data|regulatory|company|analysis",
          "confidence": "high|medium|low"
        }
      ],
      "verifiedFacts": ["Fact that can be stated."],
      "inferences": ["Inference that must be framed as interpretation."],
      "sourceRisks": ["Risk or caveat."],
      "thesisPotential": "How this could support the issue thesis."
    }
  ],
  "watch": [
    {
      "id": "stable-kebab-id",
      "reason": "Why it is interesting but not publication-ready."
    }
  ],
  "rejected": [
    {
      "id": "stable-kebab-id",
      "reason": "Why it was rejected."
    }
  ],
  "dedupeDecisions": [
    {
      "kept": "candidate-id",
      "mergedOrRejected": ["candidate-id-2"],
      "reason": "Why these belong together."
    }
  ],
  "blockedReason": null
}
```

If fewer than two credible promoted signals remain, write `status: "blocked"` unless there is a strong reason to publish a single-signal issue.
