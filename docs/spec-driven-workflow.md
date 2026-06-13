# Spec-Driven Workflow for signal-deck

signal-deck now uses GitHub Spec Kit to make ambiguous product work explicit before implementation.

The goal is not bureaucracy. The goal is to protect the product from vague tasks becoming brittle code, generic UI, or recurring editorial workflows that cannot be audited.

## What was initialized

Spec Kit was initialized in the existing repository with:

```bash
uvx --from git+https://github.com/github/spec-kit.git specify init --here --force \
  --integration codex \
  --integration-options="--skills" \
  --script sh \
  --ignore-agent-tools
```

This installed:

- `.specify/` shared Spec Kit infrastructure;
- `.specify/memory/constitution.md` with signal-deck-specific principles;
- `.specify/templates/` for specs, plans, tasks, and checklists;
- `.specify/scripts/bash/` helper scripts;
- `.agents/skills/speckit-*` Codex skills;
- `AGENTS.md` as an agent context hook.

## Command model

In this repository, Spec Kit commands are exposed as Codex-style skills:

```text
$speckit-constitution
$speckit-specify
$speckit-clarify
$speckit-checklist
$speckit-plan
$speckit-tasks
$speckit-analyze
$speckit-implement
```

For meaningful product changes, use the full flow:

```text
$speckit-specify
  → $speckit-clarify
  → $speckit-checklist
  → $speckit-plan
  → $speckit-tasks
  → $speckit-analyze
  → $speckit-implement
```

## signal-deck adaptation

Before opening a spec, clarify with Sergio:

1. What capability or user-facing improvement are we specifying?
2. Which layer does it affect?
   - ingestion
   - transformation
   - visual composition
   - React renderer
   - scheduled publishing
   - deployment
   - delivery
   - docs/operations
3. What problem does it solve for the reader, publisher, or operator?
4. What is explicitly out of scope?
5. What contract/schema/data artifact changes are required?
6. What validation commands prove the change?
7. What public delivery checks are required, if any?
8. What failure modes must be handled?
9. How do we prevent sample/dry-run content from leaking into production?
10. What documentation must be updated?

## Quality gates

A spec should not move to implementation until it has:

- clear user stories or scenarios;
- measurable acceptance criteria;
- declared non-goals;
- contract/schema impacts identified;
- renderer/publishing/deploy impact identified;
- validation commands identified;
- stale/sample-content safeguards identified;
- alignment with `.specify/memory/constitution.md`.

## Suggested first spec families

Do not start these without Sergio choosing one. Candidate areas:

1. **Daily briefing run lifecycle** — formalize scout → update → synthesis → build/deploy → delivery as an auditable state machine.
2. **Editorial artifact contracts v2** — upgrade signal-input, briefing, and visual-composition contracts for richer teaching and personalization.
3. **Reader profile/lens model** — support multi-role readers and profile-specific translation without losing the central thesis.
4. **Renderer composition system** — evolve the React app into a true editorial module canvas instead of a fixed page template.
5. **Source integrity and anti-placeholder gate** — prevent weak sources, sample data, and dry-run artifacts from reaching public delivery.
6. **Public delivery pipeline** — specify deploy verification, Telegram copy, links, and run manifests.

## Current rule

Until Sergio names the first spec, do not open a speculative feature branch or implementation plan. The next step is to choose the first spec and clarify it.
