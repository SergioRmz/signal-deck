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

2. **Presentation**
   - rendering the briefing as a high-clarity, dark-theme single page
   - keeping the output legible, premium, and reusable

3. **Delivery**
   - keeping the final artifact externally accessible
   - staying simple enough to deploy and maintain without unnecessary overhead

The goal is not complexity for its own sake. The goal is a system that can produce premium insight with operational discipline.

## Design principles

- **Signal over volume**  
  The product should elevate consequential information, not merely compress more of it.

- **Thesis-driven output**  
  Every strong briefing should do more than summarize. It should make an argument.

- **Executive readability**  
  The final artifact should feel fast to scan, dense with meaning, and useful under time pressure.

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
- a **visual composition contract** between editorial output and final page rendering
- a **dark-theme single-page briefing prototype**
- a **composition-aware renderer** that reads both briefing content and visual-composition intent from local JSON files
- an **interaction layer** with guided reading progress and section-to-section navigation
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
- the composition layer can decide how each edition should feel and flow
- the presentation layer stays polished and reusable
- deployment remains friction-light
- the output can eventually support recurring publication and external distribution

This repository is the beginning of that system.

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

## Near-term roadmap

1. Strengthen the transformation heuristics from ingestion packets to briefing payloads
2. Prepare external deployment through Cloudflare Pages
3. Introduce briefing history and recurring publication workflows

## Project status

The repository is now initialized with a deliberate first version:

- simple enough to move quickly
- structured enough to scale
- opinionated enough to feel like the beginning of a real product

The next step is not to add complexity blindly.
It is to make the transformation between upstream signals and final briefings strong enough that the rest of the system can be built around it.
