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

The repository starts with two tightly connected layers:

1. **Editorial intelligence**
   - selecting relevant signals
   - synthesizing them into a coherent thesis
   - structuring context, implications, and follow-up questions

2. **Delivery**
   - presenting the briefing as a high-clarity, dark-theme single page
   - keeping the output externally accessible
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
│           └── briefing.sample.json
└── docs/
    ├── architecture.md
    ├── product-brief.md
    └── deployment/
        └── cloudflare-pages.md
```

## What is already in place

This first foundation includes:

- a **dark-theme single-page briefing prototype**
- a **static renderer** that reads briefing content from a local JSON file
- a **clean separation** between content structure and presentation
- initial documentation for **product direction**, **architecture**, and **deployment**

That may sound modest, but it is an important strategic choice: the project is starting from a lean, legible base rather than prematurely committing to framework complexity.

## Why this foundation matters

The hard part of a product like this is not just page design or automation.
It is building a system that can consistently transform scattered developments into a readable strategic artifact.

That requires a workflow where:

- the editorial layer can evolve independently
- the presentation layer stays polished and reusable
- deployment remains friction-light
- the output can eventually support recurring publication and external distribution

This repository is the beginning of that system.

## Running the prototype locally

From the repository root:

```bash
cd apps/briefing-page
python3 -m http.server 4173
```

Then open:

```text
http://localhost:4173
```

## Near-term roadmap

1. Define a stable editorial input/output schema
2. Formalize the structure of a briefing as a reusable content contract
3. Connect the page to generated or real briefing artifacts
4. Prepare external deployment through Cloudflare Pages
5. Move from a static prototype toward a repeatable publishing workflow

## Project status

The repository is now initialized with a deliberate first version:

- simple enough to move quickly
- structured enough to scale
- opinionated enough to feel like the beginning of a real product

The next step is not to add complexity blindly.
It is to make the editorial contract strong enough that the rest of the system can be built around it.
