# Product Brief

## Thesis

`signal-deck` is designed to turn informational noise into an executive read that creates competitive advantage.

It is not meant to become a generic digest. It should help answer questions such as:

- what actually matters
- what changed structurally in the market
- who is gaining leverage, who is losing it, and why
- which second-order effects deserve attention before they become obvious

## Target user

The target reader is an executive, operator, founder, or ambitious professional who needs:

- reading speed
- conceptual density
- strategic clarity
- strong editorial taste

## First product artifact

The first deliverable is a **single page** with clear sections for a daily or thematic briefing:

1. **Hero**
   - the framing promise of the edition
2. **Top line**
   - the thesis of the day
3. **Radar**
   - relevant signals, ordered for scanning
4. **Deep dives**
   - developments that deserve more context
5. **Market map**
   - actors, incentives, and strategic consequences
6. **What to watch**
   - questions, risks, and monitoring checkpoints

## Explicit constraints

- dark theme only
- externally accessible delivery
- simple, maintainable stack
- clean, logical, scalable repository structure

## Quality bar

The output should feel:

- sharp, not bureaucratic
- informed, not inflated
- reusable, not anecdotal
- visually restrained, not overloaded

## Editorial contracts

The repository now treats both the input side and the output side of the briefing as structured artifacts.

### Ingestion side

- `docs/briefing-ingestion-v1.md`
- `data/signal-input.schema.json`

### Briefing side

- `docs/briefing-contract-v1.md`
- `data/briefing.schema.json`

Together, those contracts define the current editorial surface of the product.

## Why this matters

The long-term value of the project is not only in visual polish or automation.
It is in building a system that can repeatedly transform scattered developments into a strategic briefing with a clear point of view.

That means the product must preserve a strong distinction between:

- raw inputs
- structured editorial packets
- structured briefing content
- rendered experience
- external distribution
