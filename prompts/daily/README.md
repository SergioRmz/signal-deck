# Daily Prompt Contracts

These prompts are versioned operating contracts for the staggered signal-deck briefing flow. They are designed for Hermes cron jobs or manual agent runs that write auditable artifacts under `runs/YYYY-MM-DD/`.

The prompts do not replace the deterministic repo pipeline. They produce the editorial inputs that the pipeline validates, transforms, renders, deploys, and delivers.

## Phase order

```text
01-scout-broad.md
02-scout-update-dedupe.md
03-editorial-synthesis.md
04-build-deploy.md
05-final-delivery.md
```

## Required variables

Each prompt assumes the scheduler or operator supplies:

- `editionDate`: target edition date, `YYYY-MM-DD`
- `runDir`: `runs/YYYY-MM-DD`
- `publicUrl`: production/public briefing URL
- `readerProfile`: target roles and interests
- `deliverySlot`: final nominal delivery time

## Artifact rule

Every phase must write or update a date-scoped artifact. Intermediate phases should normally deliver locally only; the final delivery phase is the only phase that should produce the user-facing Telegram message.
