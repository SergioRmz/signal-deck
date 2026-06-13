# signal-deck

**signal-deck** is an editorial system for turning noise in technology, AI, and the economy into sharp executive briefings.

This project is not trying to become another news digest.
It is being built to produce a higher-value artifact: a briefing that identifies what matters, explains why it matters, and surfaces the second-order consequences busy operators should be paying attention to.

At its best, signal-deck should help answer questions like:

- What changed structurally, not just tactically?
- Which signals are actually worth escalating?
- Where are incentives shifting beneath the surface?
- Who is gaining leverage, and who is quietly losing it?

## What this repository is building

The repository currently distinguishes three tightly connected layers:

1. **Editorial intelligence**
   - collecting and structuring inputs
   - selecting relevant signals
   - synthesizing them into a coherent thesis
   - structuring context, implications, and follow-up questions

2. **Transformation**
   - converting validated ingestion packets into validated briefing payloads
   - keeping editorial logic inspectable and deterministic
   - preserving a visible path from signals to thesis to final artifact

3. **Presentation**
   - rendering the briefing as a high-clarity, dark-theme single page
   - keeping the output legible, premium, and reusable

The goal is not complexity for its own sake. The goal is a system that can produce premium insight with operational discipline.

## Design principles

- **Signal over volume**  
  The product should elevate consequential information, not merely compress more of it.

- **Thesis-driven output**  
  Every strong briefing should do more than summarize. It should make an argument.

- **Pedagogy over recap**  
  The output should leave the reader with a sharper model, not just a fresher memory.

- **Operational simplicity**  
  Fewer moving parts, lower maintenance burden, cleaner iteration loops.

- **Scalable editorial structure**  
  The repository should grow cleanly as the system evolves from prototype to repeatable publishing workflow.

## Current repository structure

```text
signal-deck/
├── README.md
├── .gitignore
├── data/
│   ├── briefing.sample.json
│   ├── briefing.schema.json
│   ├── signal-input.sample.json
│   ├── signal-input.schema.json
│   ├── visual-composition.sample.json
│   └── visual-composition.schema.json
├── apps/
│   └── web/
│       ├── src/
│       ├── components/
│       ├── lib/
│       ├── scripts/
│       ├── .env.example
│       └── package.json
├── scripts/
│   ├── validate_briefing.py
│   ├── validate_visual_composition.py
│   ├── validate_signal_input.py
│   ├── generate_briefing.py
│   └── run_briefing_pipeline.py
└── docs/
    ├── architecture.md
    ├── briefing-contract-v1.md
    ├── briefing-ingestion-v1.md
    ├── briefing-transformation-v1.md
    ├── visual-composition-contract-v1.md
    ├── product-brief.md
    └── deployment/
        └── cloudflare-pages.md
```

## What is already in place

This first foundation includes:

- a **formal ingestion contract** for upstream editorial packets
- an **explicit transformation layer** from ingestion packets to briefing payloads
- a **formal briefing contract** for the final briefing artifact
- a briefing contract that supports richer pedagogical fields and optional learning modules
- a **dark-theme React + Vite single-page renderer**
- a component renderer foundation that keeps shadcn/ui-compatible primitives available
- a **composition-aware renderer** that reads both briefing content and visual-composition intent from local JSON files
- a **ported Radar + Deep Dives layer** in React + Vite that already renders real evidence signals and mechanism cards from the briefing payload
- a **ported Reader Translation layer** in React + Vite that renders role-specific takeaways from the real briefing + composition artifacts
- a **ported closing layer** in React + Vite that renders Market Map, Reusable Lesson, and Watchlist modules from the real briefing + composition artifacts
- environment-based data paths for the Vite app so payload locations are not hardcoded into the renderer
- an **interaction layer** with guided reading progress and section-to-section navigation
- a **scroll choreography base** that keeps active focus, cue text, and module emphasis in sync
- a **viewport-aware choreography layer** that scrolls between modules and re-syncs focus from real section intersections
- a **sticky reading dock** that keeps navigation state visible while the briefing moves
- a **jump navigation strip** that lets the reader move directly to any module in the composition path
- an **entrance choreography layer** that stages modules with per-section motion metadata and smoother queued → entered → active transitions
- a **module-depth layer** that surfaces composition metadata like priority, accent mode, variant, and layout hints inside each section
- a **clean separation** between content structure and presentation
- lightweight local validators for both input packets and briefing payloads
- a validator for composition payloads that encode visual intent, hooks, and module sequencing
- a tested deterministic generator that turns a validated input packet into a validated briefing payload with explicit second-order effects, mechanism framing, watch questions, and weighted reader translations
- a local briefing pipeline runner that writes auditable `runs/YYYY-MM-DD/` artifacts and can build the renderer against them
- initial documentation for **product direction**, **architecture**, **contracts**, and **deployment**

That may sound modest, but it is an important strategic choice: the project now has one active renderer, canonical data contracts, and a lightweight static deployment path without losing contract clarity.

## Why this foundation matters

The hard part of a product like this is not just page design or automation.
It is building a system that can consistently transform scattered developments into a readable strategic artifact.

That requires a workflow where:

- the editorial layer can evolve independently
- the transformation layer stays inspectable
- the presentation layer stays polished and reusable
- the output can eventually support recurring publication and external distribution

This repository is the beginning of that system.

## Built with Hermes Agent

This repository is also intentionally a visible example of **agent-native product development**.

The current implementation work is being advanced with **Hermes Agent** as a real execution layer, not as a marketing label added after the fact.
In practice, Hermes is being used to:

- inspect the codebase and architecture
- patch application files directly
- run validators and renderer tests
- manage branch-by-branch iteration
- push changes and open pull requests

That matters for two reasons:

1. **signal-deck** is a product prototype
2. **signal-deck** is also evidence of an emerging workflow where software, editorial systems, and agent orchestration are developed together

For potential employers, that means this repository is not only showing frontend or content-structure decisions.
It is also showing how the project is being executed with an agentic delivery loop.

### Hermes-relevant workflows already visible in this repo

- **Primary implementation agent**  
  Hermes Agent is driving the live repo iteration loop: inspect → patch → validate → commit → push → PR.

- **Test-and-validation loop**  
  The repo is structured so Hermes can run deterministic checks repeatedly while the presentation system evolves:
  - `python3 -m unittest tests/test_generate_briefing.py -v`
  - `python3 scripts/validate_signal_input.py`
  - `python3 scripts/generate_briefing.py`
  - `python3 scripts/validate_briefing.py`
  - `python3 scripts/validate_visual_composition.py`
  - `python3 scripts/run_briefing_pipeline.py --build-renderer`
  - `cd apps/web && npm run build`

- **Agent-friendly repository shape**  
  The project is being kept legible on purpose: explicit contracts, predictable folders, and a renderer that can be evolved safely by an autonomous coding agent.

### Hermes workflows relevant to the roadmap

Hermes Agent is especially relevant to where this repository is going next, because the platform supports patterns that map directly onto the product ambition:

- **delegated specialist agents** for parallel subtasks and research workflows
- **scheduled cron jobs** for recurring briefing generation and monitoring
- **messaging/gateway delivery** for distribution into channels like Telegram
- **persistent skills and memory** for evolving repeatable editorial + engineering workflows over time

In other words, Hermes is not incidental to this project.
It is part of the operational thesis behind how a system like **signal-deck** can eventually move from prototype to recurring high-value editorial production.

## Validating the editorial artifacts

From the repository root:

```bash
python3 -m unittest tests/test_generate_briefing.py -v
python3 scripts/validate_signal_input.py
python3 scripts/generate_briefing.py
python3 scripts/validate_briefing.py
python3 scripts/validate_visual_composition.py
python3 scripts/run_briefing_pipeline.py
```

To execute a full local trial run and build the renderer from generated run artifacts:

```bash
python3 scripts/run_briefing_pipeline.py --run-date 2026-06-11 --build-renderer
```

The pipeline writes local-only artifacts under `runs/YYYY-MM-DD/`:

- `signal-input.json`
- `briefing.final.json`
- `visual-composition.json`
- `telegram-message.md`
- `manifest.json`

## Running the React + Vite renderer locally

From the repository root:

```bash
cd apps/web
cp .env.example .env
npm install
npm run dev
```

Then open:

```text
http://localhost:5173
```

The current env variables are:

- `SIGNAL_DECK_BRIEFING_PATH`
- `SIGNAL_DECK_COMPOSITION_PATH`

Both paths are resolved relative to `apps/web/`.

Before `npm run dev` and `npm run build`, the renderer runs `apps/web/scripts/sync-renderer-data.mjs`, which copies the configured briefing and composition JSON files into `apps/web/public/data/` so the Vite build stays fully static.

## Key contract documents

- `docs/briefing-ingestion-v1.md` — editorial contract for upstream signal packets
- `data/signal-input.schema.json` — ingestion schema
- `docs/briefing-contract-v1.md` — editorial contract for final briefings
- `data/briefing.schema.json` — briefing schema
- `docs/briefing-transformation-v1.md` — deterministic mapping rules from ingestion to briefing
- `scripts/validate_signal_input.py` — ingestion validator
- `scripts/validate_briefing.py` — briefing validator
- `scripts/generate_briefing.py` — briefing generator
- `scripts/run_briefing_pipeline.py` — local run orchestrator for generated briefing, composition, Telegram draft, and optional renderer build

## Near-term roadmap

1. Strengthen market-map generation and source-trace handling beyond the current deterministic transformation v2 baseline
2. Run the first end-to-end editorial trial with a fresh input packet and inspect the generated Telegram draft plus rendered page
3. Prepare and validate external deployment through Cloudflare Workers static assets
4. Introduce briefing history and recurring publication workflows
5. Continue moving operational renderer configuration behind explicit environment variables as deployment needs become clearer

## Project status

The repository is now initialized with a deliberate first version:

- simple enough to move quickly
- structured enough to scale
- opinionated enough to feel like the beginning of a real product

The next step is not to add complexity blindly.
It is to make the transformation between upstream signals and final briefings strong enough that the rest of the system can be built around it.
