# Feature Specification: Educational Ingestion

**Feature Branch**: `001-educational-ingestion`

**Created**: 2026-06-13

**Status**: Draft

**Input**: User description: "Improve signal-deck data ingestion so the system gathers multiple candidate signals across technology, AI, and economy; evaluates relevance and educational value for Sergio as the canonical reader while remaining extensible to multiple reader profiles; clusters related signals; rejects noise explicitly; and produces an auditable ingestion package with 15-30 candidate signals, 5-8 selected signals, and 2-3 potential deep dives focused on reusable mental models, causality, incentives, and strategic judgment."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Build a Broad Educational Signal Pool (Priority: P1)

As the publisher/reader, Sergio needs each briefing run to start from a broad enough set of candidate signals that the final briefing is not anchored to a single news item or shallow trend.

**Why this priority**: This fixes the current core failure mode: `1 noticia → 1 briefing`. Without a broader candidate pool, later editorial transformation cannot reliably educate or reveal patterns.

**Independent Test**: Run an ingestion cycle for the daily briefing domain and inspect the ingestion package. It should include 15-30 candidate signals across technology, AI, and economy, with source metadata and enough factual context to evaluate each signal.

**Acceptance Scenarios**:

1. **Given** a scheduled or manual daily ingestion run, **When** the system collects source material, **Then** it produces 15-30 candidate signals rather than a single selected news item.
2. **Given** the candidate pool, **When** each candidate is inspected, **Then** every candidate includes a source URL or source reference, publication timestamp when available, domain classification, factual summary, and initial rationale for why it might matter.
3. **Given** multiple sources covering the same event, **When** the system adds candidates, **Then** it preserves source diversity without treating duplicate coverage as separate editorial themes.

---

### User Story 2 - Score Signals by Educational Relevance (Priority: P1)

As Sergio, I want the ingestion layer to evaluate whether a signal can teach something reusable, not merely whether it is recent or trending.

**Why this priority**: signal-deck exists to keep the reader educated, not just informed. A signal should earn its place by revealing mechanisms, incentives, second-order effects, technical moats, market structure, strategic risk, or a reusable mental model.

**Independent Test**: Given the candidate pool, inspect each candidate's relevance evaluation. The system should distinguish factual importance from educational value and explain both in stakeholder-readable language.

**Acceptance Scenarios**:

1. **Given** a candidate signal about a product launch, **When** the system evaluates it, **Then** it must state whether the launch reveals a structural shift, incentive change, technical capability, market mechanism, or merely PR noise.
2. **Given** a candidate signal with high popularity but low learning value, **When** scoring is applied, **Then** the system can reject or downgrade it with an explicit reason.
3. **Given** a less viral signal with strong causal or strategic learning value, **When** scoring is applied, **Then** the system can elevate it above trendier but shallower stories.

---

### User Story 3 - Personalize Relevance for Sergio and Future Reader Profiles (Priority: P1)

As the product owner, Sergio needs the first relevance model to be grounded in his canonical profile while remaining extensible to multiple reader profiles and roles.

**Why this priority**: "Relevant" is not universal. The first system should optimize for Sergio as a professional ambitious about technology, AI, economy, labor-market advantage, and strategic understanding, while preserving the architecture for future multi-profile readers.

**Independent Test**: Review the ingestion package and verify that each selected or rejected signal includes a relevance explanation for the canonical Sergio profile and leaves room for future profile-specific scores.

**Acceptance Scenarios**:

1. **Given** the canonical reader profile, **When** the system evaluates a signal, **Then** it explains why the signal matters or does not matter for Sergio's learning and strategic advantage.
2. **Given** a candidate that matters differently to a founder, product operator, technical builder, investor, or executive, **When** the system evaluates it, **Then** it can record those profile lenses without forcing a single exclusive role.
3. **Given** future reader profiles, **When** the data contract is extended, **Then** profile-specific relevance can be added without rewriting the entire ingestion package shape.

---

### User Story 4 - Cluster Signals into Themes and Deep Dive Candidates (Priority: P2)

As the publisher, I want the ingestion layer to group related signals into themes so the briefing can explain patterns instead of listing isolated articles.

**Why this priority**: Education often emerges from comparing multiple signals and extracting the underlying mechanism. Clustering helps turn "news items" into teachable editorial themes.

**Independent Test**: Provide a candidate pool with related items. The ingestion output should identify clusters, explain their shared tension or mechanism, select 5-8 strong signals, and propose 2-3 potential deep dives.

**Acceptance Scenarios**:

1. **Given** multiple candidates about AI distribution, regulation, infrastructure, or enterprise adoption, **When** clustering runs, **Then** related candidates are grouped under a coherent theme rather than treated as unrelated fragments.
2. **Given** a cluster, **When** the system summarizes it, **Then** it states the thesis candidate, shared mechanism, key tension, and why the theme could educate the reader.
3. **Given** the full candidate pool, **When** selection completes, **Then** the system produces 5-8 selected signals and 2-3 potential deep dives with rationale.

---

### User Story 5 - Reject Noise Explicitly and Auditably (Priority: P2)

As the operator, I want the ingestion layer to record why signals were rejected so the product can improve editorial judgment over time.

**Why this priority**: A strong editorial system is defined as much by what it excludes as by what it includes. Explicit rejection protects the briefing from PR, redundancy, weak sources, and low-learning-value noise.

**Independent Test**: Inspect the rejected-signal section of an ingestion package. Every rejected candidate should have a rejection reason that can be audited without reading the implementation.

**Acceptance Scenarios**:

1. **Given** a candidate that is only PR repetition, **When** evaluated, **Then** it can be rejected with reason `pr_or_marketing_noise` or equivalent.
2. **Given** a candidate already represented by a stronger source in a cluster, **When** evaluated, **Then** it can be rejected or merged with reason `duplicate_or_redundant_coverage`.
3. **Given** a candidate with weak sourcing, **When** evaluated, **Then** it can be rejected, downgraded, or marked as requiring corroboration.

---

### User Story 6 - Produce an Auditable Ingestion Package (Priority: P3)

As the operator, I need each ingestion run to produce a durable package that downstream transformation, validation, and debugging can inspect.

**Why this priority**: Daily publishing must be reproducible. If a briefing feels shallow, generic, or wrong, the team needs to trace whether the failure came from source discovery, scoring, clustering, selection, or transformation.

**Independent Test**: Run ingestion and verify that a dated run artifact captures candidates, scores, selected signals, rejected signals, clusters, source diversity, and recommended deep dive candidates.

**Acceptance Scenarios**:

1. **Given** a daily run, **When** ingestion finishes, **Then** the system writes a durable artifact linked to the run date or run ID.
2. **Given** a generated briefing, **When** the operator traces it backward, **Then** the selected signals and rejected alternatives are recoverable from the ingestion package.
3. **Given** a failed or low-quality run, **When** debugging starts, **Then** the package shows whether the failure was insufficient candidate volume, weak sources, poor scoring, poor clustering, or selection drift.

---

### Edge Cases

- If fewer than 15 credible candidate signals are available, the ingestion package must mark the run as underfilled, state how many candidates were found, and explain whether the run should continue, retry, or degrade gracefully.
- If many candidates are near-duplicates from syndicated coverage, the system must merge or cluster them rather than letting duplicate volume dominate selection.
- If a source is inaccessible, paywalled, incomplete, or missing publication metadata, the system must retain the limitation in source notes rather than inventing facts.
- If a candidate is interesting but outside the briefing's strategic/educational scope, the system must reject it with a scope reason instead of forcing it into the package.
- If selected signals over-concentrate in one domain, source type, vendor, or narrative, the package must flag concentration risk.
- If a signal has uncertain factual status, the package must label it as unconfirmed or requiring corroboration before it can become a deep dive.
- If a candidate is highly relevant to a future reader profile but weak for Sergio's canonical profile, the package may retain it as a profile-specific opportunity without selecting it for the default briefing.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The system MUST collect a broad candidate pool of 15-30 candidate signals for a normal daily ingestion run.
- **FR-002**: The system MUST support technology, artificial intelligence, and economy as first-class ingestion domains, while allowing candidates to belong to multiple domains.
- **FR-003**: Each candidate signal MUST include source reference, title or source-provided heading, publication timestamp when available, domain tags, factual summary, and source notes.
- **FR-004**: Each candidate signal MUST include an editorial relevance assessment explaining why it may matter beyond recency.
- **FR-005**: Each candidate signal MUST include an educational value assessment explaining what reusable concept, mechanism, incentive, causal chain, technical moat, market structure, or strategic judgment it could teach.
- **FR-006**: The system MUST evaluate relevance for the canonical reader profile: Sergio as an ambitious technology/AI/economy reader seeking labor-market advantage, strategic judgment, and deeper understanding.
- **FR-007**: The system MUST preserve an extensible profile-lens structure so future reader profiles can add relevance scores or rationale without replacing the canonical Sergio profile.
- **FR-008**: Reader profile modeling MUST allow multiple roles or interests per reader; it MUST NOT force one exclusive role.
- **FR-009**: The system MUST cluster related candidates into themes when they share an event, mechanism, market tension, technology shift, regulation, actor, or strategic implication.
- **FR-010**: The system MUST identify 5-8 selected signals from the candidate pool for downstream briefing transformation.
- **FR-011**: The system MUST identify 2-3 potential deep dive candidates when the candidate pool contains sufficient educational depth.
- **FR-012**: The system MUST record rejected or downgraded signals with explicit reasons.
- **FR-013**: Rejection reasons MUST distinguish at least: duplicate/redundant coverage, weak source or insufficient corroboration, PR/marketing noise, low educational value, outside scope, stale information, and excessive concentration.
- **FR-014**: The system MUST report source diversity across selected signals and flag concentration risk when selected signals depend too heavily on one source, actor, domain, or narrative.
- **FR-015**: The system MUST produce a durable ingestion package per run that downstream transformation can consume without scraping implementation logs.
- **FR-016**: The ingestion package MUST separate candidate signals, selected signals, rejected signals, clusters/themes, profile relevance, educational scoring, and run-level quality notes.
- **FR-017**: The system MUST mark underfilled runs when fewer than 15 credible candidates are available and explain the fallback decision.
- **FR-018**: The system MUST avoid treating sample fixtures, dry-run artifacts, or placeholder content as live source material.
- **FR-019**: The system MUST preserve enough audit information to explain why a final briefing was built from the chosen signals.
- **FR-020**: The system MUST be usable independently of renderer changes; improving ingestion quality MUST NOT require changing the public page design in this spec.

### Key Entities *(include if feature involves data)*

- **IngestionRun**: A single execution of the ingestion process for a briefing date or run ID. Contains run metadata, candidate counts, selected counts, quality notes, source diversity, and links to candidate/cluster records.
- **CandidateSignal**: A potentially relevant item discovered during ingestion. Contains source metadata, factual summary, domain tags, novelty/context notes, educational value, relevance assessments, and status.
- **SourceReference**: The origin of a candidate signal, including URL or citation, publisher/source name, publication timestamp when available, source type, access limitations, and credibility notes.
- **ReaderProfileLens**: A profile-specific perspective used to evaluate relevance. The canonical lens is Sergio; future lenses may represent roles such as founder, product operator, technical builder, investor, executive, or other multi-role combinations.
- **RelevanceAssessment**: A structured explanation of why a signal matters, for whom, across what horizon, and through which strategic or educational mechanism.
- **EducationalValueAssessment**: A structured explanation of what the reader can learn from a signal: model mental, causal mechanism, incentive map, technical concept, market dynamic, risk pattern, or second-order effect.
- **SignalCluster**: A group of related candidate signals representing a shared theme, tension, mechanism, actor, or market/technical shift.
- **SelectedSignal**: A candidate or cluster promoted for downstream briefing transformation, with rationale and expected role in the briefing.
- **RejectedSignal**: A candidate that is excluded or downgraded, with explicit rejection reason and audit note.
- **DeepDiveCandidate**: A selected theme or signal with enough depth to become a major explanatory section in the briefing.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: A normal ingestion run produces 15-30 candidate signals, or explicitly marks the run as underfilled with a reason and count.
- **SC-002**: At least 90% of candidate signals in a completed run include source reference, domain tags, factual summary, editorial relevance assessment, and educational value assessment.
- **SC-003**: A completed run selects 5-8 signals for downstream transformation unless the run is explicitly marked underfilled.
- **SC-004**: A completed run proposes 2-3 deep dive candidates when sufficient material exists, each with a stated learning mechanism or strategic thesis candidate.
- **SC-005**: 100% of rejected signals include an explicit rejection or downgrade reason.
- **SC-006**: The ingestion package identifies duplicate/redundant coverage and prevents near-duplicate source items from filling more than one selected-signal slot unless they contribute distinct evidence to a cluster.
- **SC-007**: The canonical Sergio reader profile is present in every selected signal's relevance rationale.
- **SC-008**: The package supports adding additional profile lenses without changing the meaning of the canonical Sergio profile.
- **SC-009**: A reviewer can inspect the ingestion package and understand why each selected signal was chosen without reading code or prompt logs.
- **SC-010**: The ingestion package can be consumed by the existing transformation layer as an upstream artifact without requiring public renderer redesign in this spec.

## Assumptions

- Sergio is the canonical initial reader profile: an ambitious reader focused on technology, AI, economy, strategic judgment, labor-market advantage, and deep learning.
- The feature should remain extensible to multiple reader profiles from the beginning, but it does not need a full user account or profile-management UI in this spec.
- The target normal run volume is 15-30 candidate signals, 5-8 selected signals, and 2-3 potential deep dives.
- "Educate" means producing reusable mental models, causal understanding, incentive awareness, technical/economic context, and strategic judgment—not merely adding background paragraphs.
- This spec covers the ingestion layer and its contract/output artifacts. It does not redesign the React renderer, public page layout, deployment pipeline, or final editorial prose generation.
- Source discovery may use whatever mechanisms are later selected in planning, but the specification intentionally avoids choosing implementation tools.
- Existing signal-deck validators, run artifacts, and briefing contracts are relevant constraints and should be updated only as needed to support this ingestion package.
- The system should favor source quality, relevance, and educational density over raw trend popularity.
