# Architecture

## Goal of this phase

Establish a clean separation between product thinking, editorial content, and deployment from day one.

The immediate purpose of this phase is to make the repository legible enough that future automation can plug into it without rewriting the visual layer every time the content shape changes.

## Layers

### 1. Editorial intelligence

Responsible for:

- receiving inputs
- prioritizing signals
- forming a thesis
- producing structured briefing artifacts

At this layer, the important output is not HTML. It is a sequence of structured editorial artifacts with stable contracts.

The current contracts are:

- **ingestion contract v1**
  - `docs/briefing-ingestion-v1.md`
  - `apps/briefing-page/data/signal-input.schema.json`
- **transformation layer v1**
  - `docs/briefing-transformation-v1.md`
  - `scripts/generate_briefing.py`
- **briefing contract v1**
  - `docs/briefing-contract-v1.md`
  - `apps/briefing-page/data/briefing.schema.json`
- **visual composition contract v1**
  - `docs/visual-composition-contract-v1.md`
  - `apps/briefing-page/data/visual-composition.schema.json`

### 2. Presentation

Responsible for:

- translating composition intent into a concrete page layout
- rendering the briefing as a single page
- maintaining a sober and readable design system
- transforming structured editorial + composition artifacts into a premium reading experience
- giving the page a guided interaction model with progress and section sequencing

In the current prototype, presentation is a static HTML/CSS/JS page with no framework, but it now consumes both a briefing payload and a visual-composition payload.

The presentation layer should consume the briefing and composition contracts, not invent them.

### 3. Distribution

Responsible for:

- publishing externally
- versioning releases
- linking the artifact from Telegram or other channels

Cloudflare Pages remains a strong fit here because of its simplicity, low maintenance burden, and static hosting model.

## Current contract boundary

The current repository boundary is:

- **input packet to editorial layer**: `apps/briefing-page/data/signal-input.sample.json`
- **machine-readable ingestion schema**: `apps/briefing-page/data/signal-input.schema.json`
- **human-readable ingestion contract**: `docs/briefing-ingestion-v1.md`
- **deterministic transformation entry point**: `scripts/generate_briefing.py`
- **human-readable transformation rules**: `docs/briefing-transformation-v1.md`
- **machine-readable visual composition schema**: `apps/briefing-page/data/visual-composition.schema.json`
- **human-readable visual composition contract**: `docs/visual-composition-contract-v1.md`
- **input to presentation**: `apps/briefing-page/data/visual-composition.sample.json`
- **machine-readable briefing schema**: `apps/briefing-page/data/briefing.schema.json`
- **human-readable briefing contract**: `docs/briefing-contract-v1.md`

This is the most important architectural decision in the current phase.

It means:

- upstream collection can evolve without rewriting the final page
- transformation logic can become explicit instead of remaining invisible editorial intuition
- the renderer can evolve without redefining either the briefing shape or the composition language

## Editorial flow

The intended flow is now:

1. collect and normalize source material into an ingestion packet
2. derive prioritized signals and a working thesis
3. record editorial decisions that map input material toward the output artifact
4. transform the packet into a validated briefing payload
5. stage the briefing through a validated visual composition payload
6. render and distribute the final page

The system is still early, but the contracts now define the intended path.

## Initial technical decision

The prototype uses a static page because it:

- reduces unnecessary complexity
- accelerates editorial feedback loops
- avoids choosing a framework too early
- leaves room to migrate later to a more sophisticated renderer if needed

## Planned evolution

### Phase 1

- reference single page
- mock content
- simple external deployment

### Phase 2

- stable ingestion schema
- stable briefing schema
- explicit transformation from input packets to briefing payloads
- real briefing content injected into the page
- composition-aware rendering driven by visual-composition payloads

### Phase 3

- briefing history
- thematic views
- navigation or reading metrics if they prove useful
- recurring delivery workflows

## Repository structure

- `apps/briefing-page/`: main visual artifact
- `apps/briefing-page/data/`: briefing payloads, ingestion payloads, and schemas
- `docs/`: vision, decisions, contracts, and operations
- `scripts/`: lightweight local validators and future utilities

## Conventions

The repository should continue to prefer:

- obvious names
- few nesting levels
- clear separation between content, app, and deployment
- contracts that are explicit before they become automated
- transform steps that are inspectable instead of hidden inside prompts
