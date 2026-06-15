# Prompt: Final Delivery

## Use when
Run this at the nominal delivery slot after build/deploy is complete.

## Inputs

- `editionDate`: target date, `YYYY-MM-DD`
- `runDir`: `runs/YYYY-MM-DD`
- `publicUrl`: production/public briefing URL
- `runs/YYYY-MM-DD/telegram-message.md`
- `runs/YYYY-MM-DD/deploy-result.json`
- `runs/YYYY-MM-DD/run-timeline.json`

## Goal
Send exactly one Telegram-ready final message, but only after public URL verification succeeds.

## Instructions

1. Read `deploy-result.json`.
2. Re-verify `PUBLIC_URL/data/briefing.json` serves `meta.editionDate == YYYY-MM-DD`.
3. Re-verify the public page resolves.
4. Read `telegram-message.md`.
5. Ensure the message includes the public URL.
6. Update `run-timeline.json` phase `final delivery` to `completed` or `blocked`.
7. Final response must be exactly one of:
   - the Telegram-ready briefing message, if verification passes
   - one honest blocker/status message, if verification fails

## Rules

- Do not schedule new cron jobs from this phase.
- Do not send multiple Telegram fragments.
- Do not include local file paths as the user-facing link.
- Do not claim the page is live unless the public URL resolves and serves the target edition date.
- Do not expose implementation scaffolding in the user-facing message.

## Blocker message contract

If blocked, the final message should include:

- what failed
- which artifact exists locally
- whether the issue is content, build, deployment, or verification
- what must be fixed next

Keep it compact and honest.
