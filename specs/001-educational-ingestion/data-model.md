# Data Model: Educational Ingestion

## Overview

The educational ingestion package is a durable run artifact that sits upstream of the existing briefing transformation. It records the full editorial scouting decision: what was discovered, how it was evaluated, which themes emerged, which signals were selected, what was rejected, and what should be watched later.

## Entity: IngestionRun

**Purpose**: Represents one execution of the ingestion process for a briefing date or run ID.

**Fields**:

- `runId` string, required, stable local identifier.
- `runDate` string, required, `YYYY-MM-DD`.
- `createdAt` string, required, ISO-8601 date-time.
- `language` string, required; default publication language remains Spanish for signal-deck output.
- `domains` array of strings, required; expected to include technology, AI, and/or economy.
- `status` enum, required: `complete`, `underfilled`, `needs_review`, `failed`.
- `candidateCount` integer, required.
- `selectedCount` integer, required.
- `rejectedCount` integer, required.
- `watchItemCount` integer, required.
- `qualityNotes` array of RunQualityNote, optional.
- `sourceDiversity` SourceDiversitySummary, required.

**Validation rules**:

- A normal complete run should contain 15-30 candidate signals.
- If fewer than 15 credible candidates exist, `status` must be `underfilled` or `needs_review`, with a quality note explaining the fallback.
- `selectedCount` should be 5-8 unless the run is underfilled.

## Entity: SourceReference

**Purpose**: Records provenance and evidence role for source material.

**Fields**:

- `sourceId` string, required.
- `title` string, required.
- `publisher` string, required.
- `sourceType` string, required; examples: `article`, `press_release`, `paper`, `filing`, `dataset`, `official_blog`, `earnings_call`, `expert_analysis`.
- `sourceRole` enum, required: `primary`, `source_of_record`, `technical_analysis`, `economic_analysis`, `market_context`, `regulatory_context`, `critical_contrast`, `secondary_coverage`.
- `url` string, optional.
- `publishedAt` string, optional ISO-8601 date-time.
- `accessLimitations` array of strings, optional.
- `credibilityNotes` string, optional.

**Validation rules**:

- Every `sourceId` must be unique.
- Selected or deep-dive signals should include source-role coverage where available, especially primary/source-of-record plus context or contrast.
- Missing publication metadata must be noted rather than invented.

## Entity: ReaderProfileLens

**Purpose**: Captures how a signal matters for Sergio's canonical profile and future multi-role profiles.

**Fields**:

- `profileId` string, required.
- `displayName` string, required.
- `roles` array of strings, required and non-empty.
- `interests` array of strings, optional.
- `advantageTargets` array of strings, optional.
- `relevanceRationale` string, required when attached to a selected signal.
- `relevanceScore` number, optional, 0-1.

**Validation rules**:

- The package must include a canonical Sergio lens.
- Reader profiles may have multiple roles; no exclusive single-role constraint is allowed.
- Every selected signal must include the canonical Sergio relevance rationale.

## Entity: CandidateSignal

**Purpose**: Represents a discovered item competing for inclusion in the briefing.

**Fields**:

- `signalId` string, required.
- `title` string, required.
- `factualSummary` string, required.
- `domainTags` array of strings, required and non-empty.
- `sourceIds` array of source IDs, required and non-empty.
- `status` enum, required: `candidate`, `selected`, `rejected`, `watch_item`, `merged`.
- `editorialRationale` string, required.
- `educationalValue` EducationalValueAssessment, required.
- `profileRelevance` array of ReaderProfileLens references/assessments, required.
- `confidence` number, required, 0-1.
- `clusterId` string, optional.
- `duplicateOfSignalId` string, optional when status is `merged`.
- `rejectionReason` enum, optional when rejected or downgraded.
- `corroborationStatus` enum, required: `corroborated`, `partially_corroborated`, `uncertain`, `requires_follow_up`.
- `auditNotes` array of strings, optional.

**Validation rules**:

- A selected signal must not have `corroborationStatus` of `uncertain` unless explicitly marked as not used as a strong factual foundation.
- Rejected signals must include `rejectionReason`.
- Merged signals must reference `duplicateOfSignalId` or a cluster that explains redundancy.
- Watch items must not appear in the final selected signal list or deep dive list until corroborated.

## Entity: EducationalValueAssessment

**Purpose**: Explains what the signal can teach beyond recency.

**Fields**:

- `score` number, required, 0-1.
- `teachingMechanisms` array of enums, required and non-empty: `causal_mechanism`, `incentive_structure`, `reusable_mental_model`, `second_order_effect`, `technical_moat`, `market_structure`, `strategic_judgment`, `risk_pattern`.
- `learningRationale` string, required.
- `deepDivePotential` enum, required: `none`, `possible`, `strong`.

**Validation rules**:

- Deep dive candidates require `deepDivePotential` of `strong` or an explicit cluster-level rationale.
- Popularity alone is not a valid teaching mechanism.

## Entity: SignalCluster

**Purpose**: Groups related signals into a coherent theme.

**Fields**:

- `clusterId` string, required.
- `title` string, required.
- `signalIds` array of signal IDs, required and non-empty.
- `thesisCandidate` string, required.
- `sharedMechanism` string, required.
- `keyTension` string, optional.
- `educationalRationale` string, required.
- `concentrationNotes` array of strings, optional.

**Validation rules**:

- Every `signalId` must exist.
- A cluster selected for deep dive must explain its reusable thesis or mechanism.

## Entity: SelectedSignal

**Purpose**: Records a signal or cluster promoted for downstream transformation.

**Fields**:

- `selectionId` string, required.
- `signalId` string, optional.
- `clusterId` string, optional.
- `roleInBriefing` enum, required: `radar`, `deep_dive`, `market_map`, `reader_translation`, `watchlist_seed`.
- `selectionRationale` string, required.
- `sourceCoverageSummary` string, required.
- `profileRationale` string, required for Sergio canonical profile.

**Validation rules**:

- Must reference either a known signal or known cluster.
- Normal completed runs should have 5-8 selected signals.
- Deep dive selections require educational density and reusable thesis quality.

## Entity: RejectedSignal

**Purpose**: Makes exclusions auditable.

**Fields**:

- `signalId` string, required.
- `reason` enum, required: `duplicate_or_redundant_coverage`, `weak_source_or_insufficient_corroboration`, `pr_or_marketing_noise`, `low_educational_value`, `outside_scope`, `stale_information`, `excessive_concentration`.
- `auditNote` string, required.
- `mergedIntoSignalId` string, optional.

**Validation rules**:

- Every rejected signal must correspond to a candidate signal.
- Rejection reasons must be understandable without reading implementation logs.

## Entity: WatchItem

**Purpose**: Retains uncertain but potentially valuable signals for future follow-up.

**Fields**:

- `signalId` string, required.
- `watchReason` string, required.
- `neededCorroboration` array of strings, required.
- `potentialFutureUse` enum, required: `future_deep_dive`, `contextual_follow_up`, `discard_if_unconfirmed`.

**Validation rules**:

- Watch items must not be treated as selected factual foundations in the final briefing.
- Each watch item must state what would make it usable later.

## Entity: SourceDiversitySummary

**Purpose**: Audits concentration risk across selections.

**Fields**:

- `domainCounts` object, required.
- `publisherCounts` object, required.
- `actorCounts` object, optional.
- `narrativeCounts` object, optional.
- `concentrationRisk` enum, required: `low`, `medium`, `high`.
- `concentrationRationale` string, required when risk is `medium` or `high`.
- `alternativeSearchNotes` string, optional.

**Validation rules**:

- If concentration risk is detected, the package must record whether strong alternatives were found.
- Diversification should happen only when alternatives meet the educational value threshold.
