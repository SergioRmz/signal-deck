# Prompt: Scout Broad

## Use when
Run this as the first staggered editorial phase for a target edition date.

## Inputs

- `editionDate`: target date, `YYYY-MM-DD`
- `runDir`: `runs/YYYY-MM-DD`
- `readerProfile`: target roles and interests
- `topicBoundaries`: technology, AI, economy, infrastructure, regulation, and adjacent strategic signals

## Goal
Collect a wide but curated candidate set before the delivery window becomes urgent.

Do not draft the briefing. This phase is for discovery, source capture, early scoring, and verification questions.

## Instructions

1. Search for current, consequential signals across primary sources and credible secondary coverage.
2. Prefer signals that can teach a structural lesson, not merely fill a daily digest.
3. Separate fact, interpretation, and open questions.
4. Score candidates using:
   - source quality
   - novelty
   - executive relevance
   - second-order consequence potential
   - pedagogical value
   - evidence robustness
5. Mark items as `candidate`, `watch`, or `reject` with reasons.
6. Write the artifact to `runs/YYYY-MM-DD/scout-broad.json`.
7. Update `runs/YYYY-MM-DD/run-timeline.json` phase `scout broad` to `completed` or `blocked`.

## Output contract

Write JSON with this shape:

```json
{
  "editionDate": "YYYY-MM-DD",
  "phase": "scout broad",
  "status": "completed",
  "generatedAt": "ISO-8601 timestamp",
  "readerProfile": {
    "roles": ["software-engineer", "founder", "operator"],
    "interests": ["ai", "infrastructure", "economy"]
  },
  "candidates": [
    {
      "id": "stable-kebab-id",
      "title": "Candidate title",
      "summary": "What changed and why it may matter.",
      "status": "candidate",
      "sources": [
        {
          "title": "Source title",
          "url": "https://...",
          "sourceType": "primary|secondary|market-data|regulatory|company|analysis",
          "confidence": "high|medium|low"
        }
      ],
      "scores": {
        "sourceQuality": 0,
        "novelty": 0,
        "executiveRelevance": 0,
        "secondOrderPotential": 0,
        "pedagogicalValue": 0,
        "evidenceRobustness": 0
      },
      "whyItCouldMatter": "Strategic implication.",
      "verificationQuestions": ["Question still unresolved."],
      "riskNotes": ["What could be overstated?"]
    }
  ],
  "blockedReason": null
}
```

If no credible candidates exist, write `status: "blocked"` with a specific `blockedReason`.
