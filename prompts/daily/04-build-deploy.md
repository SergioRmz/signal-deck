# Prompt: Build Deploy

## Use when
Run this after `runs/YYYY-MM-DD/ingestion-package.json` exists.

## Inputs

- `editionDate`: target date, `YYYY-MM-DD`
- `runDir`: `runs/YYYY-MM-DD`
- `publicUrl`: production/public briefing URL
- `runs/YYYY-MM-DD/ingestion-package.json`

## Goal
Run the deterministic pipeline, build the renderer, deploy the public page, and verify that the public artifact serves the target edition.

## Instructions

1. Validate the ingestion package.
2. Run the local pipeline with renderer build:

```bash
python3 scripts/run_briefing_pipeline.py \
  --run-date YYYY-MM-DD \
  --ingestion-package runs/YYYY-MM-DD/ingestion-package.json \
  --public-url PUBLIC_URL \
  --build-renderer
```

3. Deploy using the repository's current deployment path.
4. Verify `PUBLIC_URL` resolves.
5. Verify `PUBLIC_URL/data/briefing.json` serves `meta.editionDate == YYYY-MM-DD`.
6. Verify the deployed payload has multiple real signals and no scaffold terms.
7. Write `runs/YYYY-MM-DD/deploy-result.json`.
8. Update `runs/YYYY-MM-DD/run-timeline.json` phase `build deploy` to `completed` or `blocked`.

## Deploy result contract

Write JSON with this shape:

```json
{
  "editionDate": "YYYY-MM-DD",
  "phase": "build deploy",
  "status": "completed",
  "generatedAt": "ISO-8601 timestamp",
  "publicUrl": "https://.../",
  "briefingJsonUrl": "https://.../data/briefing.json",
  "localArtifacts": {
    "briefing": "runs/YYYY-MM-DD/briefing.final.json",
    "visualComposition": "runs/YYYY-MM-DD/visual-composition.json",
    "telegramMessage": "runs/YYYY-MM-DD/telegram-message.md",
    "manifest": "runs/YYYY-MM-DD/manifest.json"
  },
  "checks": {
    "ingestionValidation": "passed",
    "briefingValidation": "passed",
    "compositionValidation": "passed",
    "rendererBuild": "passed",
    "publicUrl": "passed",
    "editionDate": "passed",
    "scaffoldTerms": "passed"
  },
  "blockedReason": null
}
```

If deployment or public verification fails, write `status: "blocked"` with a specific `blockedReason`. Do not let the final delivery phase send a normal briefing if this phase is blocked.
