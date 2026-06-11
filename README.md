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
├── apps/
│   └── briefing-page/
│       ├── index.html
│       ├── styles.css
│       ├── app.js
│       └── data/
│           ├── briefing.sample.json
│           ├── briefing.schema.json
│           ├── signal-input.sample.json
│           ├── signal-input.schema.json
│           ├── visual-composition.sample.json
│           └── visual-composition.schema.json
├── scripts/
│   ├── validate_briefing.py
│   ├── validate_visual_composition.py
│   ├── validate_signal_input.py
│   └── generate_briefing.py
└── docs/
│   ├── architecture.md
│   ├── briefing-contract-v1.md
│   ├── briefing-ingestion-v1.md
│   ├── briefing-transformation-v1.md
│   ├── visual-composition-contract-v1.md
│   ├── product-brief.md
│   └── deployment/
│       └── cloudflare-pages.md
```

## What is already in place

This first foundation includes:

- a **formal ingestion contract** for upstream editorial packets
- an **explicit transformation layer** from ingestion packets to briefing payloads
- a **formal briefing contract** for the final briefing artifact
- a briefing contract that supports richer pedagogical fields and optional learning modules
- a **dark-theme single-page briefing prototype**
- a **composition-aware renderer** that reads both briefing content and visual-composition intent from local JSON files
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
- a deterministic generator that turns a validated input packet into a validated briefing payload
- initial documentation for **product direction**, **architecture**, **contracts**, and **deployment**

That may sound modest, but it is an important strategic choice: the project is starting from a lean, legible base rather than prematurely committing to framework complexity.

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
  - `python3 scripts/validate_signal_input.py`
  - `python3 scripts/generate_briefing.py`
  - `python3 scripts/validate_briefing.py`
  - `python3 scripts/validate_visual_composition.py`
  - `node --test tests/briefing-page.test.mjs`

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

## Running the prototype locally

From the repository root:

```bash
python3 scripts/validate_signal_input.py
python3 scripts/generate_briefing.py
python3 scripts/validate_briefing.py
python3 scripts/validate_visual_composition.py
node --test tests/briefing-page.test.mjs
cd apps/briefing-page
python3 -m http.server 4173
```

Then open:

```text
http://localhost:4173
```

## Key contract documents

- `docs/briefing-ingestion-v1.md` — editorial contract for upstream signal packets
- `apps/briefing-page/data/signal-input.schema.json` — ingestion schema
- `docs/briefing-contract-v1.md` — editorial contract for final briefings
- `apps/briefing-page/data/briefing.schema.json` — briefing schema
- `docs/briefing-transformation-v1.md` — deterministic mapping rules from ingestion to briefing
- `scripts/validate_signal_input.py` — ingestion validator
- `scripts/validate_briefing.py` — briefing validator
- `scripts/generate_briefing.py` — briefing generator

## Near-term roadmap

1. Strengthen the transformation heuristics from ingestion packets to briefing payloads
2. Connect the page to generated or real briefing artifacts more systematically
3. Prepare external deployment through Cloudflare Pages
4. Introduce briefing history and recurring publication workflows
5. Migrate the frontend to a component system that better matches the editorial engine

## Project status

The repository is now initialized with a deliberate first version:

- simple enough to move quickly
- structured enough to scale
- opinionated enough to feel like the beginning of a real product

The next step is not to add complexity blindly.
It is to make the transformation between upstream signals and final briefings strong enough that the rest of the system can be built around it.
