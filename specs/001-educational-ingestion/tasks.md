# Tasks: Educational Ingestion

**Input**: Design documents from `/specs/001-educational-ingestion/`

**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/ingestion-package-v2.schema.json, quickstart.md

**Tests**: Included because the spec and quickstart define independent tests and validation scenarios for every story.

**Organization**: Tasks are grouped by user story so each story can be implemented and validated independently.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel because it touches a different file and has no dependency on incomplete tasks.
- **[Story]**: User story label from `spec.md`.
- Every task includes an exact file path.

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Move the planned v2 ingestion package contract into canonical implementation locations without changing runtime behavior yet.

- [x] T001 Copy `specs/001-educational-ingestion/contracts/ingestion-package-v2.schema.json` to `data/ingestion-package.schema.json`
- [x] T002 [P] Create placeholder documentation shell for `docs/briefing-ingestion-v2.md` from `specs/001-educational-ingestion/data-model.md`
- [x] T003 [P] Create validation test skeleton in `tests/test_validate_ingestion_package.py`
- [x] T004 Create validator script skeleton in `scripts/validate_ingestion_package.py` with CLI argument parsing for `data/ingestion-package.sample.json`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Establish shared schema loading, semantic validation helpers, and fixture structure required by all user stories.

**⚠️ CRITICAL**: No user story work should begin until this phase is complete.

- [x] T005 Add JSON loading, object expectation, and schema validation helpers in `scripts/validate_ingestion_package.py`
- [x] T006 Add shared uniqueness and cross-reference helper functions in `scripts/validate_ingestion_package.py`
- [x] T007 [P] Add a minimal valid package fixture with 15 candidate shells in `data/ingestion-package.sample.json`
- [x] T008 [P] Add documentation for package top-level shape in `docs/briefing-ingestion-v2.md`
- [x] T009 Add base passing validation test for `data/ingestion-package.sample.json` in `tests/test_validate_ingestion_package.py`
- [x] T010 Run `python3 -m unittest tests/test_validate_ingestion_package.py -v` and confirm the base fixture validation passes

**Checkpoint**: Foundation ready — user story implementation can now begin.

---

## Phase 3: User Story 1 - Build a Broad Educational Signal Pool (Priority: P1) 🎯 MVP

**Goal**: A normal ingestion package contains 15-30 candidate signals across technology, AI, and economy with source metadata and enough factual context to evaluate each signal.

**Independent Test**: Run `python3 scripts/validate_ingestion_package.py data/ingestion-package.sample.json` and verify the package has 15-30 candidates, source references, timestamps when available, domain tags, factual summaries, and source notes.

### Tests for User Story 1

- [x] T011 [P] [US1] Add candidate count validation tests for underfilled and overfilled normal runs in `tests/test_validate_ingestion_package.py`
- [x] T012 [P] [US1] Add source reference cross-reference tests for missing `sourceIds` in `tests/test_validate_ingestion_package.py`
- [x] T013 [P] [US1] Add domain coverage test for technology, AI, and economy tags in `tests/test_validate_ingestion_package.py`

### Implementation for User Story 1

- [x] T014 [US1] Expand `data/ingestion-package.sample.json` to 15-30 realistic candidate signals with source metadata and factual summaries
- [x] T015 [US1] Implement candidate volume and underfilled-run validation in `scripts/validate_ingestion_package.py`
- [x] T016 [US1] Implement source ID existence validation for every candidate in `scripts/validate_ingestion_package.py`
- [x] T017 [US1] Implement required candidate metadata checks for domain tags, factual summary, source notes, and publication metadata notes in `scripts/validate_ingestion_package.py`
- [x] T018 [US1] Document candidate pool semantics and source metadata requirements in `docs/briefing-ingestion-v2.md`
- [x] T019 [US1] Run `python3 scripts/validate_ingestion_package.py data/ingestion-package.sample.json` and `python3 -m unittest tests/test_validate_ingestion_package.py -v`

**Checkpoint**: US1 is independently complete when broad candidate pool validation passes without changing briefing transformation.

---

## Phase 4: User Story 2 - Score Signals by Educational Relevance (Priority: P1)

**Goal**: Each candidate explains why it matters beyond recency and what reusable concept, mechanism, incentive, or strategic judgment it can teach.

**Independent Test**: Inspect candidate validation output and fixture data to confirm editorial relevance and educational value are separate, structured, and testable.

### Tests for User Story 2

- [x] T020 [P] [US2] Add tests requiring `editorialRationale` and `educationalValue.learningRationale` for every candidate in `tests/test_validate_ingestion_package.py`
- [x] T021 [P] [US2] Add tests rejecting candidates whose `educationalValue.teachingMechanisms` is empty in `tests/test_validate_ingestion_package.py`
- [x] T022 [P] [US2] Add tests for valid `deepDivePotential` and educational score range in `tests/test_validate_ingestion_package.py`

### Implementation for User Story 2

- [x] T023 [US2] Populate `data/ingestion-package.sample.json` with educational value scores, teaching mechanisms, and learning rationales for every candidate
- [x] T024 [US2] Implement educational value semantic validation in `scripts/validate_ingestion_package.py`
- [x] T025 [US2] Implement weak-learning rejection/downgrade checks in `scripts/validate_ingestion_package.py`
- [x] T026 [US2] Document educational value assessment semantics in `docs/briefing-ingestion-v2.md`
- [x] T027 [US2] Run `python3 -m unittest tests/test_validate_ingestion_package.py -v`

**Checkpoint**: US2 is independently complete when the validator distinguishes factual relevance from educational value.

---

## Phase 5: User Story 3 - Personalize Relevance for Sergio and Future Reader Profiles (Priority: P1)

**Goal**: The package includes canonical Sergio relevance while allowing future reader profiles with multiple roles or interests.

**Independent Test**: Validate that every selected or rejected signal can explain relevance for the canonical Sergio profile and that profile modeling allows multiple roles.

### Tests for User Story 3

- [ ] T028 [P] [US3] Add test requiring one canonical Sergio profile in `tests/test_validate_ingestion_package.py`
- [ ] T029 [P] [US3] Add test requiring canonical Sergio relevance on every selected signal in `tests/test_validate_ingestion_package.py`
- [ ] T030 [P] [US3] Add test allowing multiple roles in a reader profile in `tests/test_validate_ingestion_package.py`

### Implementation for User Story 3

- [ ] T031 [US3] Populate `readerProfiles` and `profileRelevance` in `data/ingestion-package.sample.json`
- [ ] T032 [US3] Implement canonical profile and multi-role validation in `scripts/validate_ingestion_package.py`
- [ ] T033 [US3] Ensure selected signals expose `profileRationale` for Sergio in `data/ingestion-package.sample.json`
- [ ] T034 [US3] Document reader profile lens semantics in `docs/briefing-ingestion-v2.md`
- [ ] T035 [US3] Run `python3 -m unittest tests/test_validate_ingestion_package.py -v`

**Checkpoint**: US3 is independently complete when canonical Sergio relevance is enforced without blocking future multi-role profiles.

---

## Phase 6: User Story 4 - Cluster Signals into Themes and Deep Dive Candidates (Priority: P2)

**Goal**: Related candidates are clustered into themes, selected signals are promoted, and 2-3 deep dive candidates are chosen by educational density and reusable thesis quality.

**Independent Test**: Validate clusters, 5-8 selected signals, and 2-3 deep dive candidates with rationales tied to mechanisms and reusable theses.

### Tests for User Story 4

- [ ] T036 [P] [US4] Add cluster cross-reference tests for unknown `signalIds` in `tests/test_validate_ingestion_package.py`
- [ ] T037 [P] [US4] Add selected-signal count tests for normal completed runs in `tests/test_validate_ingestion_package.py`
- [ ] T038 [P] [US4] Add deep dive educational density tests in `tests/test_validate_ingestion_package.py`
- [ ] T039 [P] [US4] Add transformation tests proving selected/deep-dive package signals can feed `generate_briefing.py` in `tests/test_generate_briefing.py`

### Implementation for User Story 4

- [ ] T040 [US4] Populate `clusters` in `data/ingestion-package.sample.json` with thesis candidates, shared mechanisms, and key tensions
- [ ] T041 [US4] Populate `selectedSignals` in `data/ingestion-package.sample.json` with 5-8 selected signals and 2-3 deep dive roles
- [ ] T042 [US4] Implement cluster and selected-signal semantic validation in `scripts/validate_ingestion_package.py`
- [ ] T043 [US4] Add package-to-v1 transformation adapter in `scripts/generate_briefing.py` without breaking existing `signal-input.sample.json` flow
- [ ] T044 [US4] Document clustering, selection, and deep dive rules in `docs/briefing-ingestion-v2.md`
- [ ] T045 [US4] Run `python3 -m unittest tests/test_generate_briefing.py -v` and `python3 -m unittest tests/test_validate_ingestion_package.py -v`

**Checkpoint**: US4 is independently complete when package-selected signals can drive downstream briefing transformation.

---

## Phase 7: User Story 5 - Reject Noise Explicitly and Auditably (Priority: P2)

**Goal**: Rejected, merged, downgraded, and watch signals are recorded with explicit reasons and audit notes.

**Independent Test**: Inspect rejected-signal and watch-item sections and confirm every exclusion has a reason understandable without reading implementation logs.

### Tests for User Story 5

- [ ] T046 [P] [US5] Add test requiring `rejectionReason` for every rejected candidate in `tests/test_validate_ingestion_package.py`
- [ ] T047 [P] [US5] Add test requiring `duplicateOfSignalId` or `mergedIntoSignalId` for merged/redundant coverage in `tests/test_validate_ingestion_package.py`
- [ ] T048 [P] [US5] Add test preventing watch items from being selected as factual deep dives in `tests/test_validate_ingestion_package.py`

### Implementation for User Story 5

- [ ] T049 [US5] Populate `rejectedSignals` and `watchItems` in `data/ingestion-package.sample.json`
- [ ] T050 [US5] Implement rejection reason, merged-signal, and watch-item validation in `scripts/validate_ingestion_package.py`
- [ ] T051 [US5] Add CLI failure messages that identify the exact invalid signal ID in `scripts/validate_ingestion_package.py`
- [ ] T052 [US5] Document rejection reasons and watch-item semantics in `docs/briefing-ingestion-v2.md`
- [ ] T053 [US5] Run `python3 scripts/validate_ingestion_package.py data/ingestion-package.sample.json` and `python3 -m unittest tests/test_validate_ingestion_package.py -v`

**Checkpoint**: US5 is independently complete when noise rejection and watch-item retention are auditable.

---

## Phase 8: User Story 6 - Produce an Auditable Ingestion Package (Priority: P3)

**Goal**: Each local pipeline run writes a durable ingestion package artifact and manifest link that downstream transformation, validation, and debugging can inspect.

**Independent Test**: Run the local pipeline and verify `runs/YYYY-MM-DD/ingestion-package.json` exists, validates, and is referenced by `manifest.json`.

### Tests for User Story 6

- [ ] T054 [P] [US6] Add pipeline test requiring `ingestion-package.json` in run artifacts in `tests/test_run_briefing_pipeline.py`
- [ ] T055 [P] [US6] Add pipeline test requiring `manifest.json` to reference the ingestion package in `tests/test_run_briefing_pipeline.py`
- [ ] T056 [P] [US6] Add pipeline test proving renderer build still consumes final briefing and composition artifacts in `tests/test_run_briefing_pipeline.py`

### Implementation for User Story 6

- [ ] T057 [US6] Add `--ingestion-package` CLI argument and default path in `scripts/run_briefing_pipeline.py`
- [ ] T058 [US6] Validate and snapshot the ingestion package into `runs/YYYY-MM-DD/ingestion-package.json` in `scripts/run_briefing_pipeline.py`
- [ ] T059 [US6] Add `ingestionPackage` to the run manifest in `scripts/run_briefing_pipeline.py`
- [ ] T060 [US6] Update `README.md` validation commands and run artifact list for the v2 ingestion package
- [ ] T061 [US6] Run `python3 -m unittest tests/test_run_briefing_pipeline.py -v` and `python3 scripts/run_briefing_pipeline.py --run-date 2026-06-14 --build-renderer`

**Checkpoint**: US6 is independently complete when a dated run is fully traceable from ingestion package to briefing output.

---

## Final Phase: Polish & Cross-Cutting Concerns

**Purpose**: Validate the full feature, update docs, and prepare the PR for review.

- [ ] T062 [P] Update `specs/001-educational-ingestion/quickstart.md` if implementation paths differ from the plan
- [ ] T063 [P] Add any missing validator edge-case notes to `docs/briefing-ingestion-v2.md`
- [ ] T064 Run `python3 -m unittest tests/test_validate_ingestion_package.py -v`
- [ ] T065 Run `python3 -m unittest tests/test_generate_briefing.py -v`
- [ ] T066 Run `python3 -m unittest tests/test_run_briefing_pipeline.py -v`
- [ ] T067 Run `python3 scripts/validate_ingestion_package.py data/ingestion-package.sample.json`
- [ ] T068 Run `python3 scripts/run_briefing_pipeline.py --run-date 2026-06-14 --build-renderer`
- [ ] T069 Run `git diff --check` from repository root
- [ ] T070 Commit all completed implementation work and push `001-educational-ingestion`
- [ ] T071 Update PR #25 summary and validation notes using `specs/001-educational-ingestion/tasks.md` as the implementation checklist source

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies; can start immediately.
- **Foundational (Phase 2)**: Depends on Setup; blocks all user stories.
- **P1 User Stories**: US1, US2, and US3 depend on Phase 2 and should be completed before P2 stories because they define the package's core candidate/evaluation/profile contract.
- **P2 User Stories**: US4 and US5 depend on US1-US3 because clustering, selection, rejection, and watch items require candidate and profile semantics.
- **P3 User Story**: US6 depends on US1-US5 because the pipeline should snapshot a complete package.
- **Polish**: Depends on all desired user stories being complete.

### User Story Dependencies

- **US1 (P1)**: Starts after Foundational; no dependency on other stories.
- **US2 (P1)**: Starts after Foundational; can be developed alongside US1 but final validation needs populated candidates.
- **US3 (P1)**: Starts after Foundational; can be developed alongside US1/US2.
- **US4 (P2)**: Depends on US1-US3.
- **US5 (P2)**: Depends on US1-US3; can run in parallel with US4 after candidate/profile semantics are stable.
- **US6 (P3)**: Depends on US4-US5.

### Parallel Opportunities

- Setup tasks T002-T004 can be split once T001 is complete.
- Foundational tasks T007 and T008 can run in parallel with validator helper work.
- Test-writing tasks inside each user story are parallelizable where marked `[P]`.
- US2 and US3 can run in parallel after Phase 2 if both coordinate on `data/ingestion-package.sample.json` edits.
- US4 and US5 can run in parallel after US1-US3 if they coordinate fixture edits.

---

## Parallel Example: User Story 1

```bash
# Parallel test-design tasks for US1
Task: "T011 Add candidate count validation tests in tests/test_validate_ingestion_package.py"
Task: "T012 Add source reference cross-reference tests in tests/test_validate_ingestion_package.py"
Task: "T013 Add domain coverage test in tests/test_validate_ingestion_package.py"
```

## Parallel Example: User Story 4

```bash
# Parallel validation and transformation tests for US4
Task: "T036 Add cluster cross-reference tests in tests/test_validate_ingestion_package.py"
Task: "T038 Add deep dive educational density tests in tests/test_validate_ingestion_package.py"
Task: "T039 Add transformation tests in tests/test_generate_briefing.py"
```

---

## Implementation Strategy

### MVP First

1. Complete Phase 1 and Phase 2.
2. Complete US1 only.
3. Validate that a broad candidate pool exists and passes `scripts/validate_ingestion_package.py`.
4. Stop and review the package shape before adding scoring, profiles, clustering, or pipeline integration.

### Incremental Delivery

1. US1: candidate pool and source references.
2. US2: educational scoring.
3. US3: Sergio canonical relevance and multi-role profile support.
4. US4: clusters, selection, and deep dives.
5. US5: rejection/watch audit trail.
6. US6: durable run artifact and manifest integration.

### Final Validation

Before closing the implementation section, run:

```bash
python3 -m unittest tests/test_validate_ingestion_package.py -v
python3 -m unittest tests/test_generate_briefing.py -v
python3 -m unittest tests/test_run_briefing_pipeline.py -v
python3 scripts/validate_ingestion_package.py data/ingestion-package.sample.json
python3 scripts/run_briefing_pipeline.py --run-date 2026-06-14 --build-renderer
git diff --check
```

### Save/PR Rule

At the end of this task-generation section and every later implementation section:

1. Commit scoped changes.
2. Push `001-educational-ingestion`.
3. Ensure PR #25 reflects the latest branch state.
4. Report commit SHA, validation, and PR URL.
