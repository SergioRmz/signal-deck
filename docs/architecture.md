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

At this layer, the important output is not HTML. It is a content artifact with a stable contract.

The current v1 contract is defined in:

- `docs/briefing-contract-v1.md`
- `apps/briefing-page/data/briefing.schema.json`

### 2. Presentation

Responsible for:

- rendering the briefing as a single page
- maintaining a sober and readable design system
- transforming a structured artifact into a premium reading experience

In the current prototype, presentation is a static HTML/CSS/JS page with no framework.

The presentation layer should consume the contract, not invent it.

### 3. Distribution

Responsible for:

- publishing externally
- versioning releases
- linking the artifact from Telegram or other channels

Cloudflare Pages remains a strong fit here because of its simplicity, low maintenance burden, and static hosting model.

## Current contract boundary

The current repository boundary is:

- **input to presentation**: `apps/briefing-page/data/briefing.sample.json`
- **machine-readable schema**: `apps/briefing-page/data/briefing.schema.json`
- **human-readable contract**: `docs/briefing-contract-v1.md`

This is the most important architectural decision in the current phase.

It means the renderer can evolve without redefining the briefing shape, and the editorial pipeline can evolve without coupling itself to page markup.

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

- stable briefing schema
- automatically generated intermediate artifacts
- real briefing content injected into the page

### Phase 3

- briefing history
- thematic views
- navigation or reading metrics if they prove useful

## Repository structure

- `apps/briefing-page/`: main visual artifact
- `apps/briefing-page/data/`: briefing payloads and schema
- `docs/`: vision, decisions, contracts, and operations

## Conventions

The repository should continue to prefer:

- obvious names
- few nesting levels
- clear separation between content, app, and deployment
- contracts that are explicit before they become automated
