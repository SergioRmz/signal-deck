# Daily Briefing Runbook

This runbook defines the operational shape for a recurring signal-deck briefing. It exists because the product is not only a renderer or a deterministic transformation script: it is an editorial system where research, judgment, QA, composition, deployment, and delivery must leave auditable artifacts.

The default operating model is **staggered execution with slack**. The final Telegram delivery should depend on already-built and verified artifacts, not on a long chain of just-in-time web requests and model calls.

## Operating principles

- **One final notification**: Telegram is the activation layer, not the full reading experience.
- **Public page first**: the single-page briefing must be deployed and verified before the final message is sent.
- **Artifacts over vibes**: each phase writes date-scoped files under `runs/YYYY-MM-DD/` so the run can be inspected after the fact.
- **Editorial judgment is explicit**: scouting, verification, synthesis, contrarian review, and visual routing are not hidden inside the renderer.
- **Failure is honest**: if public URL verification fails, the delivery phase sends a blocker/status message instead of pretending the briefing is live.

## Default timeline

For a 09:00 delivery, use this nominal schedule:

```text
02:00 — scout broad
04:30 — scout update / dedupe
06:30 — editorial synthesis
08:00 — build deploy
09:00 — final delivery
```

The exact times can move, but the spacing matters. The system should gather, verify, synthesize, build, and deploy with enough margin that the final slot is mostly a verification and send step.

## Phase contracts

### 1. Scout broad

**Purpose**: collect a wide candidate set before the delivery window becomes urgent.

**Primary questions**:

- What changed in technology, AI, markets, infrastructure, or regulation?
- Which signals could teach a reusable strategic lesson?
- Which stories have enough source quality to survive later verification?

**Input**:

- current date
- reader profile / role mix
- topic boundaries
- known source preferences

**Output**:

```text
runs/YYYY-MM-DD/scout-broad.json
```

**Expected contents**:

- candidate signals
- source URLs
- source type and confidence notes
- early relevance scores
- open verification questions
- rejection/watch candidates when appropriate

### 2. Scout update / dedupe

**Purpose**: reduce the candidate set and update it after a meaningful gap.

**Primary questions**:

- Which candidates are duplicates of the same underlying shift?
- Which candidates have improved or weakened after more source checks?
- Which items should be rejected, watched, or promoted?

**Input**:

```text
runs/YYYY-MM-DD/scout-broad.json
```

**Output**:

```text
runs/YYYY-MM-DD/scout-updated.json
```

**Expected contents**:

- promoted candidates
- rejected candidates with reasons
- watch items that are interesting but not publication-ready
- dedupe decisions
- unresolved source-risk notes

### 3. Editorial synthesis

**Purpose**: convert verified candidates into the editorial packet consumed by the deterministic pipeline.

**Primary questions**:

- What is the briefing thesis?
- Which signals are evidence, and which are only context?
- What is fact, inference, and speculation?
- What reader advantage should the issue deliver?
- What visual/pedagogical shape should the briefing take?

**Input**:

```text
runs/YYYY-MM-DD/scout-updated.json
```

**Outputs**:

```text
runs/YYYY-MM-DD/editorial-plan.json
runs/YYYY-MM-DD/ingestion-package.json
```

`editorial-plan.json` captures the reasoning path. `ingestion-package.json` is the machine-facing packet validated by the repo pipeline.

### 4. Build deploy

**Purpose**: run the deterministic repo pipeline, build the renderer, deploy the page, and verify the public surface.

**Input**:

```text
runs/YYYY-MM-DD/ingestion-package.json
```

**Core command**:

```bash
python3 scripts/run_briefing_pipeline.py \
  --run-date YYYY-MM-DD \
  --ingestion-package runs/YYYY-MM-DD/ingestion-package.json \
  --public-url https://signal-deck.sergio-ramirez-mtz.workers.dev/ \
  --build-renderer
```

**Outputs**:

```text
runs/YYYY-MM-DD/briefing.final.json
runs/YYYY-MM-DD/visual-composition.json
runs/YYYY-MM-DD/telegram-message.md
runs/YYYY-MM-DD/manifest.json
runs/YYYY-MM-DD/deploy-result.json
```

**Verification before this phase is complete**:

- local validators pass
- renderer build passes
- public URL resolves
- `/data/briefing.json` serves the target `meta.editionDate`
- deployed payload has no scaffold terms such as `placeholder`, `sample`, `example.com`, `Vite renderer`, `composition cue`, or `migration status`

### 5. Final delivery

**Purpose**: send exactly one Telegram-ready message after the public page has been verified.

**Inputs**:

```text
runs/YYYY-MM-DD/telegram-message.md
runs/YYYY-MM-DD/deploy-result.json
runs/YYYY-MM-DD/run-timeline.json
```

**Output**:

The final assistant response / Telegram message.

**Rules**:

- include the public URL
- keep the message compact but useful even if the reader does not open the link
- do not send intermediate phase chatter to the user
- if verification fails, send one honest blocker/status message

## Run timeline artifact

Every real-flow run should write:

```text
runs/YYYY-MM-DD/run-timeline.json
```

Prepare the run folder and phase prompt copies with:

```bash
python3 scripts/prepare_daily_run.py \
  --edition-date YYYY-MM-DD \
  --delivery-time 09:00 \
  --public-url https://signal-deck.sergio-ramirez-mtz.workers.dev/
```

The prepared phase prompts are self-contained. The script combines XML-like shared daily context from `prompts/daily/shared/` with the phase-specific expert prompt so a fresh Hermes cron session receives bounded sections such as `<product_philosophy>`, `<reader_profile>`, `<evidence_rules>`, `<scoring_rubric>`, `<artifact_discipline>`, `<role>`, `<mission>`, `<anti_patterns>`, `<failure_behavior>`, and `<output_contract>` in one file.

Minimum shape:

```json
{
  "runDate": "YYYY-MM-DD",
  "publicUrl": "https://signal-deck.sergio-ramirez-mtz.workers.dev",
  "mode": "one-shot real-flow trial preserving scheduled phase order and nominal slots",
  "phases": [
    {
      "slot": "02:00",
      "name": "scout broad",
      "status": "pending",
      "artifact": "runs/YYYY-MM-DD/scout-broad.json"
    },
    {
      "slot": "04:30",
      "name": "scout update / dedupe",
      "status": "pending",
      "artifact": "runs/YYYY-MM-DD/scout-updated.json"
    },
    {
      "slot": "06:30",
      "name": "editorial synthesis",
      "status": "pending",
      "artifact": "runs/YYYY-MM-DD/ingestion-package.json"
    },
    {
      "slot": "08:00",
      "name": "build deploy",
      "status": "pending",
      "artifact": "runs/YYYY-MM-DD/deploy-result.json"
    },
    {
      "slot": "09:00",
      "name": "final delivery",
      "status": "pending",
      "artifact": "runs/YYYY-MM-DD/telegram-message.md"
    }
  ]
}
```

## What belongs in code vs. prompts

The deterministic repo should own:

- JSON schema validation
- deterministic transformation from ingestion package to briefing payload
- visual composition validation
- renderer build
- local artifact generation
- public delivery checks that can be scripted reliably

Prompted/editorial jobs should own:

- source discovery
- source criticism
- candidate rejection and watch-listing
- synthesis and thesis formation
- contrarian pressure-testing
- pedagogical routing
- final editorial judgment

The boundary matters: prompts create auditable artifacts; code validates and renders them.

## Recurring scheduling rule

A recurring daily setup should create staggered jobs rather than one large just-in-time job. Intermediate jobs should write artifacts locally. The final job should be the only one delivered to the user.

The concrete Hermes cron contract is documented in:

```text
docs/operations/hermes-cron-orchestration.md
```

Generate the auditable job preview with:

```bash
python3 scripts/render_hermes_cron_jobs.py \
  --delivery-time 09:00 \
  --public-url https://signal-deck.sergio-ramirez-mtz.workers.dev/ \
  --workdir /root/workspace/signal-deck \
  --output docs/operations/hermes-cron-jobs.preview.json
```

The final delivery job must not assume success. It should verify the public URL and edition date before sending the normal briefing message.
