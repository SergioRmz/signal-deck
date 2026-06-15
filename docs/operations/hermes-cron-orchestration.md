# Hermes Cron Orchestration

This document defines how Signal Deck moves from a prepared daily run folder to actual scheduled Hermes agents.

The core rule is simple: **cron owns time; the repo owns judgment and artifacts**. Hermes cron wakes the right phase at the right hour, but the editorial contract lives in `prompts/daily/`, the run folder, and the deterministic pipeline.

## Installed job shape

For the default 09:00 delivery slot, the recurring jobs are:

```text
0 2 * * *     signal-deck daily 01 scout broad        deliver=local
30 4 * * *    signal-deck daily 02 scout update dedupe deliver=local
30 6 * * *    signal-deck daily 03 editorial synthesis deliver=local
0 8 * * *     signal-deck daily 04 build deploy        deliver=local
0 9 * * *     signal-deck daily 05 final delivery      deliver=origin
```

Intermediate phases deliver to `local` so they do not spam the reader. The final phase is the only user-facing delivery phase.

## Runtime contract

Each cron job runs in the repository workdir and receives a self-contained runtime prompt. The prompt requires the agent to:

1. compute `EDITION_DATE` from the live system date;
2. run `scripts/prepare_daily_run.py` for that date if the run folder is missing or stale;
3. read the relevant self-contained phase prompt under `runs/YYYY-MM-DD/phase-prompts/`;
4. read prior artifacts if the phase depends on them;
5. write the expected phase artifact;
6. update `runs/YYYY-MM-DD/run-timeline.json`;
7. avoid recursive cron scheduling;
8. avoid user-facing delivery unless it is phase 05.

## Preview manifest

Render the auditable cron preview with:

```bash
python3 scripts/render_hermes_cron_jobs.py \
  --delivery-time 09:00 \
  --public-url https://signal-deck.sergio-ramirez-mtz.workers.dev/ \
  --workdir /root/workspace/signal-deck \
  --output docs/operations/hermes-cron-jobs.preview.json
```

The preview file is:

```text
docs/operations/hermes-cron-jobs.preview.json
```

It contains the job names, cron schedules, delivery targets, expected artifacts, enabled toolsets, and full runtime prompts used to install the real Hermes jobs.

## Phase artifact map

```text
01 scout broad
  prompt:   runs/YYYY-MM-DD/phase-prompts/01-scout-broad.md
  output:   runs/YYYY-MM-DD/scout-broad.json
  delivery: local

02 scout update / dedupe
  prompt:   runs/YYYY-MM-DD/phase-prompts/02-scout-update-dedupe.md
  input:    runs/YYYY-MM-DD/scout-broad.json
  output:   runs/YYYY-MM-DD/scout-updated.json
  delivery: local

03 editorial synthesis
  prompt:   runs/YYYY-MM-DD/phase-prompts/03-editorial-synthesis.md
  input:    runs/YYYY-MM-DD/scout-updated.json
  outputs:  runs/YYYY-MM-DD/editorial-plan.json
            runs/YYYY-MM-DD/ingestion-package.json
  delivery: local

04 build deploy
  prompt:   runs/YYYY-MM-DD/phase-prompts/04-build-deploy.md
  input:    runs/YYYY-MM-DD/ingestion-package.json
  outputs:  runs/YYYY-MM-DD/briefing.final.json
            runs/YYYY-MM-DD/visual-composition.json
            runs/YYYY-MM-DD/telegram-message.md
            runs/YYYY-MM-DD/deploy-result.json
  delivery: local

05 final delivery
  prompt:   runs/YYYY-MM-DD/phase-prompts/05-final-delivery.md
  inputs:   runs/YYYY-MM-DD/telegram-message.md
            runs/YYYY-MM-DD/deploy-result.json
  output:   final Telegram message or honest blocker
  delivery: origin
```

## Failure behavior

A phase must not fabricate upstream work. If a required prior artifact is missing, invalid, or under-verified, the phase should mark itself blocked in `run-timeline.json` and write a clear blocker note.

The final delivery phase must not announce a normal briefing unless deployment verification succeeded. If verification failed, it should send one concise blocker/status message.

## Installation note

The repo preview does not install jobs by itself. Installation is performed by Hermes cron using the manifest fields:

- `name`
- `schedule`
- `prompt`
- `deliver`
- `workdir`
- `enabledToolsets`

This separation keeps the repository auditable while allowing the live Hermes scheduler to own execution.
