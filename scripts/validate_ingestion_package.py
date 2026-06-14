#!/usr/bin/env python3
"""Validate a signal-deck educational ingestion package v2.

The validator intentionally uses only the Python standard library so local runs do
not depend on optional JSON Schema packages. It supports the subset of JSON
Schema used by `data/ingestion-package.schema.json` and layers shared semantic
checks on top.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_PACKAGE_PATH = ROOT / "data" / "ingestion-package.sample.json"
DEFAULT_SCHEMA_PATH = ROOT / "data" / "ingestion-package.schema.json"


class ValidationError(ValueError):
    """Raised when an ingestion package violates the v2 contract."""


def fail(message: str) -> None:
    raise ValidationError(message)


def load_json(path: Path | str) -> Any:
    json_path = Path(path)
    if not json_path.exists():
        fail(f"File not found: {json_path}")
    try:
        return json.loads(json_path.read_text())
    except json.JSONDecodeError as exc:
        fail(f"Invalid JSON in {json_path}: {exc}")


def expect_dict(value: Any, label: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        fail(f"{label} must be an object")
    return value


def expect_list(value: Any, label: str) -> list[Any]:
    if not isinstance(value, list):
        fail(f"{label} must be an array")
    return value


def expect_non_empty_list(value: Any, label: str) -> list[Any]:
    items = expect_list(value, label)
    if not items:
        fail(f"{label} must be a non-empty array")
    return items


def expect_non_empty_string(value: Any, label: str) -> str:
    if not isinstance(value, str) or not value.strip():
        fail(f"{label} must be a non-empty string")
    return value


def expect_unique_strings(values: list[Any], label: str) -> list[str]:
    normalized: list[str] = []
    seen: set[str] = set()
    for index, value in enumerate(values, start=1):
        item = expect_non_empty_string(value, f"{label}[{index}]")
        if item in seen:
            fail(f"{label} contains duplicate value: {item}")
        seen.add(item)
        normalized.append(item)
    return normalized


def _schema_type_matches(value: Any, expected_type: str) -> bool:
    if expected_type == "object":
        return isinstance(value, dict)
    if expected_type == "array":
        return isinstance(value, list)
    if expected_type == "string":
        return isinstance(value, str)
    if expected_type == "integer":
        return isinstance(value, int) and not isinstance(value, bool)
    if expected_type == "number":
        return isinstance(value, (int, float)) and not isinstance(value, bool)
    if expected_type == "boolean":
        return isinstance(value, bool)
    return True


def _resolve_ref(schema: dict[str, Any], ref: str) -> dict[str, Any]:
    if not ref.startswith("#/"):
        fail(f"Unsupported schema ref: {ref}")
    current: Any = schema
    for part in ref.removeprefix("#/").split("/"):
        current = current[part]
    return expect_dict(current, ref)


def validate_against_schema(value: Any, node: dict[str, Any], root_schema: dict[str, Any], label: str) -> None:
    if "$ref" in node:
        validate_against_schema(value, _resolve_ref(root_schema, node["$ref"]), root_schema, label)
        return

    if "oneOf" in node:
        matches = 0
        messages = []
        for option in node["oneOf"]:
            try:
                validate_against_schema(value, option, root_schema, label)
                matches += 1
            except ValidationError as exc:
                messages.append(str(exc))
        if matches != 1:
            fail(f"{label} must match exactly one schema branch; matched {matches}. {'; '.join(messages)}")

    if "const" in node and value != node["const"]:
        fail(f"{label} must be {node['const']!r}")

    if "enum" in node and value not in node["enum"]:
        fail(f"{label} must be one of {node['enum']}")

    expected_type = node.get("type")
    if expected_type and not _schema_type_matches(value, expected_type):
        fail(f"{label} must be a {expected_type}")

    if isinstance(value, str):
        if node.get("minLength") is not None and len(value) < node["minLength"]:
            fail(f"{label} must be at least {node['minLength']} characters")

    if isinstance(value, (int, float)) and not isinstance(value, bool):
        if "minimum" in node and value < node["minimum"]:
            fail(f"{label} must be >= {node['minimum']}")
        if "maximum" in node and value > node["maximum"]:
            fail(f"{label} must be <= {node['maximum']}")

    if isinstance(value, list):
        if "minItems" in node and len(value) < node["minItems"]:
            fail(f"{label} must contain at least {node['minItems']} items")
        if node.get("uniqueItems") and len(value) != len({json.dumps(item, sort_keys=True) for item in value}):
            fail(f"{label} must contain unique items")
        if "items" in node:
            for index, item in enumerate(value, start=1):
                validate_against_schema(item, node["items"], root_schema, f"{label}[{index}]")

    if isinstance(value, dict):
        required = node.get("required", [])
        for field in required:
            if field not in value:
                fail(f"{label} missing required field: {field}")
        properties = node.get("properties", {})
        if node.get("additionalProperties") is False:
            for field in value:
                if field not in properties:
                    fail(f"{label} has unsupported field: {field}")
        for field, child in properties.items():
            if field in value:
                validate_against_schema(value[field], child, root_schema, f"{label}.{field}")
        additional = node.get("additionalProperties")
        if isinstance(additional, dict):
            for field, child_value in value.items():
                if field not in properties:
                    validate_against_schema(child_value, additional, root_schema, f"{label}.{field}")


def _collect_unique_ids(items: list[Any], id_field: str, label: str) -> set[str]:
    ids: set[str] = set()
    for index, item in enumerate(items, start=1):
        obj = expect_dict(item, f"{label}[{index}]")
        item_id = expect_non_empty_string(obj.get(id_field), f"{label}[{index}].{id_field}")
        if item_id in ids:
            fail(f"Duplicate {id_field}: {item_id}")
        ids.add(item_id)
    return ids


def _validate_run_counts(package: dict[str, Any]) -> None:
    run = expect_dict(package.get("run"), "run")
    candidates = expect_list(package.get("candidates"), "candidates")
    selected = expect_list(package.get("selectedSignals"), "selectedSignals")
    rejected = expect_list(package.get("rejectedSignals"), "rejectedSignals")
    watch_items = expect_list(package.get("watchItems"), "watchItems")

    expected_counts = {
        "candidateCount": len(candidates),
        "selectedCount": len(selected),
        "rejectedCount": len(rejected),
        "watchItemCount": len(watch_items),
    }
    for field, expected in expected_counts.items():
        if run.get(field) != expected:
            fail(f"run.{field} must equal actual {field.removesuffix('Count')} count {expected}")

    if run.get("status") == "complete" and not 15 <= len(candidates) <= 30:
        fail("complete run must contain 15-30 candidates")

    if len(candidates) < 15 and run.get("status") not in {"underfilled", "needs_review"}:
        fail("runs with fewer than 15 candidates must be underfilled or needs_review")

    if len(candidates) < 15 and not package.get("qualityNotes"):
        fail("underfilled candidate pools require a quality note")


def _validate_domain_coverage(package: dict[str, Any]) -> None:
    candidates = expect_list(package.get("candidates"), "candidates")
    domains = {
        tag
        for candidate in candidates
        for tag in expect_non_empty_list(candidate.get("domainTags"), f"candidate {candidate.get('signalId', '<unknown>')}.domainTags")
    }
    required_domains = {"technology", "ai", "economy"}
    missing = sorted(required_domains - domains)
    if expect_dict(package.get("run"), "run").get("status") == "complete" and missing:
        fail(f"domain coverage must include technology, ai, and economy; missing: {missing}")


def _validate_source_metadata(sources: list[Any]) -> None:
    for index, item in enumerate(sources, start=1):
        source = expect_dict(item, f"sources[{index}]")
        source_id = expect_non_empty_string(source.get("sourceId"), f"sources[{index}].sourceId")
        expect_non_empty_string(source.get("credibilityNotes"), f"sources[{index}].credibilityNotes")
        if "publishedAt" not in source and "accessLimitations" not in source:
            fail(f"source {source_id} missing publication metadata notes")


def _validate_candidate_metadata(candidates: list[Any]) -> None:
    for index, item in enumerate(candidates, start=1):
        candidate = expect_dict(item, f"candidates[{index}]")
        signal_id = expect_non_empty_string(candidate.get("signalId"), f"candidates[{index}].signalId")
        expect_non_empty_string(candidate.get("factualSummary"), f"candidate {signal_id}.factualSummary")
        expect_non_empty_string(candidate.get("editorialRationale"), f"candidate {signal_id}.editorialRationale")
        expect_non_empty_list(candidate.get("domainTags"), f"candidate {signal_id}.domainTags")
        if not candidate.get("auditNotes"):
            fail(f"candidate {signal_id} must include source or publication metadata audit notes")


def _validate_educational_value(candidates: list[Any]) -> None:
    for index, item in enumerate(candidates, start=1):
        candidate = expect_dict(item, f"candidates[{index}]")
        signal_id = expect_non_empty_string(candidate.get("signalId"), f"candidates[{index}].signalId")
        value = expect_dict(candidate.get("educationalValue"), f"candidate {signal_id}.educationalValue")
        score = value.get("score")
        if not isinstance(score, (int, float)) or isinstance(score, bool) or not 0 <= score <= 1:
            fail(f"candidate {signal_id}.educationalValue.score must be between 0 and 1")
        expect_non_empty_list(value.get("teachingMechanisms"), f"candidate {signal_id}.educationalValue.teachingMechanisms")
        expect_non_empty_string(value.get("learningRationale"), f"candidate {signal_id}.educationalValue.learningRationale")
        deep_dive = expect_non_empty_string(value.get("deepDivePotential"), f"candidate {signal_id}.educationalValue.deepDivePotential")
        if deep_dive not in {"none", "possible", "strong"}:
            fail(f"candidate {signal_id}.educationalValue.deepDivePotential must be none, possible, or strong")
        if score < 0.4 and candidate.get("status") not in {"rejected", "watch_item", "merged"}:
            fail(f"candidate {signal_id} has weak educational value and must be downgraded or rejected")
        if score < 0.4 and candidate.get("status") == "rejected" and candidate.get("rejectionReason") != "low_educational_value":
            fail(f"candidate {signal_id} rejected for weak educational value must use rejectionReason low_educational_value")


def _validate_reader_profiles(package: dict[str, Any]) -> str:
    profiles = expect_non_empty_list(package.get("readerProfiles"), "readerProfiles")
    canonical_true_profiles = [
        expect_dict(profile, "readerProfile")
        for profile in profiles
        if profile.get("canonical") is True
    ]
    canonical_profiles = [profile for profile in canonical_true_profiles if profile.get("profileId") == "sergio-canonical"]
    if len(canonical_true_profiles) != 1 or len(canonical_profiles) != 1:
        fail("package must include exactly one canonical Sergio profile with profileId sergio-canonical")
    roles = expect_non_empty_list(canonical_profiles[0].get("roles"), "canonical Sergio profile roles")
    if len(roles) < 2:
        fail("canonical Sergio profile must support multiple roles")
    return "sergio-canonical"


def _validate_profile_relevance(candidates: list[Any], canonical_profile_id: str) -> None:
    for index, candidate in enumerate(candidates, start=1):
        signal_id = expect_non_empty_string(candidate.get("signalId"), f"candidates[{index}].signalId")
        relevance = expect_non_empty_list(candidate.get("profileRelevance"), f"candidate {signal_id}.profileRelevance")
        if not any(expect_dict(item, f"candidate {signal_id}.profileRelevance[]").get("profileId") == canonical_profile_id for item in relevance):
            fail(f"candidate {signal_id} must include canonical Sergio relevance")
        for rel_index, item in enumerate(relevance, start=1):
            rel = expect_dict(item, f"candidate {signal_id}.profileRelevance[{rel_index}]")
            expect_non_empty_string(rel.get("relevanceRationale"), f"candidate {signal_id}.profileRelevance[{rel_index}].relevanceRationale")


def _validate_selected_profile_rationales(selected_signals: list[Any]) -> None:
    for index, selected in enumerate(selected_signals, start=1):
        expect_non_empty_string(
            expect_dict(selected, f"selectedSignals[{index}]").get("profileRationale"),
            f"selectedSignals[{index}].profileRationale",
        )


def _candidate_by_id(candidates: list[Any]) -> dict[str, dict[str, Any]]:
    return {expect_dict(candidate, "candidate")["signalId"]: candidate for candidate in candidates}


def _validate_rejection_and_watch_semantics(package: dict[str, Any], candidates: list[Any]) -> None:
    candidates_by_id = _candidate_by_id(candidates)
    rejected_entries = expect_list(package.get("rejectedSignals"), "rejectedSignals")
    watch_entries = expect_list(package.get("watchItems"), "watchItems")
    rejected_entry_ids = {expect_dict(entry, "rejectedSignal").get("signalId") for entry in rejected_entries}
    watch_entry_ids = {expect_dict(entry, "watchItem").get("signalId") for entry in watch_entries}

    for candidate in candidates:
        signal_id = expect_non_empty_string(candidate.get("signalId"), "candidate.signalId")
        status = candidate.get("status")
        if status == "rejected":
            expect_non_empty_string(candidate.get("rejectionReason"), f"candidate {signal_id}.rejectionReason")
            if signal_id not in rejected_entry_ids:
                fail(f"candidate {signal_id} is rejected but missing from rejectedSignals")
        if status == "merged":
            expect_non_empty_string(candidate.get("duplicateOfSignalId"), f"candidate {signal_id}.duplicateOfSignalId")
            if candidate["duplicateOfSignalId"] not in candidates_by_id:
                fail(f"candidate {signal_id} references unknown duplicateOfSignalId: {candidate['duplicateOfSignalId']}")
            if signal_id not in rejected_entry_ids:
                fail(f"candidate {signal_id} is merged but missing from rejectedSignals")
        if status == "watch_item" and signal_id not in watch_entry_ids:
            fail(f"candidate {signal_id} is watch_item but missing from watchItems")

    for index, rejected in enumerate(rejected_entries, start=1):
        entry = expect_dict(rejected, f"rejectedSignals[{index}]")
        signal_id = expect_non_empty_string(entry.get("signalId"), f"rejectedSignals[{index}].signalId")
        reason = expect_non_empty_string(entry.get("reason"), f"rejectedSignals[{index}].reason")
        if signal_id not in candidates_by_id:
            fail(f"rejectedSignals[{index}] references unknown signalId: {signal_id}")
        if reason == "duplicate_or_redundant_coverage" and not entry.get("mergedIntoSignalId"):
            fail(f"rejectedSignals[{index}] for {signal_id} requires mergedIntoSignalId")
        if entry.get("mergedIntoSignalId") and entry["mergedIntoSignalId"] not in candidates_by_id:
            fail(f"rejectedSignals[{index}] references unknown mergedIntoSignalId: {entry['mergedIntoSignalId']}")

    for index, item in enumerate(watch_entries, start=1):
        entry = expect_dict(item, f"watchItems[{index}]")
        signal_id = expect_non_empty_string(entry.get("signalId"), f"watchItems[{index}].signalId")
        if signal_id not in candidates_by_id:
            fail(f"watchItems[{index}] references unknown signalId: {signal_id}")
        if candidates_by_id[signal_id].get("status") != "watch_item":
            fail(f"watch item {signal_id} must reference a candidate with status watch_item")


def _validate_selection_semantics(package: dict[str, Any], candidates: list[Any]) -> None:
    run = expect_dict(package.get("run"), "run")
    selected_signals = expect_list(package.get("selectedSignals"), "selectedSignals")
    clusters = expect_list(package.get("clusters"), "clusters")
    candidates_by_id = _candidate_by_id(candidates)
    clusters_by_id = {expect_dict(cluster, "cluster")["clusterId"]: cluster for cluster in clusters}
    watch_signal_ids = {candidate["signalId"] for candidate in candidates if candidate.get("status") == "watch_item"}

    if run.get("status") == "complete" and not 5 <= len(selected_signals) <= 8:
        fail("complete run must contain 5-8 selected signals")

    deep_dives = [selected for selected in selected_signals if expect_dict(selected, "selectedSignal").get("roleInBriefing") == "deep_dive"]
    if run.get("status") == "complete" and not 2 <= len(deep_dives) <= 3:
        fail("complete run must contain 2-3 deep dive selections")

    for index, selected in enumerate(selected_signals, start=1):
        item = expect_dict(selected, f"selectedSignals[{index}]")
        if item.get("signalId"):
            signal_id = item["signalId"]
            if signal_id not in candidates_by_id:
                fail(f"selectedSignals[{index}] references unknown signalId: {signal_id}")
            candidate_ids = [signal_id]
        else:
            cluster_id = item.get("clusterId")
            if cluster_id not in clusters_by_id:
                fail(f"selectedSignals[{index}] references unknown clusterId: {cluster_id}")
            candidate_ids = clusters_by_id[cluster_id]["signalIds"]

        if item.get("roleInBriefing") != "deep_dive":
            continue

        watch_candidates = [signal_id for signal_id in candidate_ids if signal_id in watch_signal_ids]
        if watch_candidates:
            fail(f"watch item {watch_candidates[0]} cannot be selected as a deep dive")

        dense_candidates = []
        for signal_id in candidate_ids:
            if signal_id not in candidates_by_id:
                fail(f"selectedSignals[{index}] references cluster with unknown signalId: {signal_id}")
            candidate = candidates_by_id[signal_id]
            value = expect_dict(candidate.get("educationalValue"), f"candidate {signal_id}.educationalValue")
            mechanisms = set(expect_non_empty_list(value.get("teachingMechanisms"), f"candidate {signal_id}.educationalValue.teachingMechanisms"))
            if (
                value.get("score", 0) >= 0.75
                and value.get("deepDivePotential") == "strong"
                and mechanisms.intersection({"reusable_mental_model", "causal_mechanism", "second_order_effect", "technical_moat", "market_structure"})
            ):
                dense_candidates.append(signal_id)
        if not dense_candidates:
            fail(f"deep dive {item.get('selectionId', index)} requires strong educational density")


def validate_shared_semantics(package: dict[str, Any]) -> None:
    sources = expect_non_empty_list(package.get("sources"), "sources")
    candidates = expect_non_empty_list(package.get("candidates"), "candidates")
    canonical_profile_id = _validate_reader_profiles(package)
    _validate_run_counts(package)
    _validate_domain_coverage(package)
    _validate_source_metadata(sources)
    _validate_candidate_metadata(candidates)
    _validate_educational_value(candidates)
    _validate_rejection_and_watch_semantics(package, candidates)
    _validate_profile_relevance(candidates, canonical_profile_id)
    _validate_selected_profile_rationales(expect_list(package.get("selectedSignals"), "selectedSignals"))

    source_ids = _collect_unique_ids(sources, "sourceId", "sources")
    candidate_ids = _collect_unique_ids(candidates, "signalId", "candidates")
    cluster_ids = _collect_unique_ids(expect_list(package.get("clusters"), "clusters"), "clusterId", "clusters")

    profile_ids = _collect_unique_ids(
        expect_non_empty_list(package.get("readerProfiles"), "readerProfiles"),
        "profileId",
        "readerProfiles",
    )

    for index, candidate in enumerate(candidates, start=1):
        linked_sources = expect_unique_strings(
            expect_non_empty_list(candidate.get("sourceIds"), f"candidates[{index}].sourceIds"),
            f"candidates[{index}].sourceIds",
        )
        for source_id in linked_sources:
            if source_id not in source_ids:
                fail(f"candidates[{index}] references unknown sourceId: {source_id}")

        relevance = expect_non_empty_list(candidate.get("profileRelevance"), f"candidates[{index}].profileRelevance")
        for rel_index, item in enumerate(relevance, start=1):
            profile_id = expect_non_empty_string(
                expect_dict(item, f"candidates[{index}].profileRelevance[{rel_index}]").get("profileId"),
                f"candidates[{index}].profileRelevance[{rel_index}].profileId",
            )
            if profile_id not in profile_ids:
                fail(f"candidates[{index}] references unknown profileId: {profile_id}")

        if candidate.get("clusterId") and candidate["clusterId"] not in cluster_ids:
            fail(f"candidates[{index}] references unknown clusterId: {candidate['clusterId']}")
        if candidate.get("duplicateOfSignalId") and candidate["duplicateOfSignalId"] not in candidate_ids:
            fail(f"candidates[{index}] references unknown duplicateOfSignalId: {candidate['duplicateOfSignalId']}")

    for index, cluster in enumerate(package.get("clusters", []), start=1):
        for signal_id in expect_unique_strings(
            expect_non_empty_list(cluster.get("signalIds"), f"clusters[{index}].signalIds"),
            f"clusters[{index}].signalIds",
        ):
            if signal_id not in candidate_ids:
                fail(f"clusters[{index}] references unknown signalId: {signal_id}")

    for index, selected in enumerate(package.get("selectedSignals", []), start=1):
        if selected.get("signalId") and selected["signalId"] not in candidate_ids:
            fail(f"selectedSignals[{index}] references unknown signalId: {selected['signalId']}")
        if selected.get("clusterId") and selected["clusterId"] not in cluster_ids:
            fail(f"selectedSignals[{index}] references unknown clusterId: {selected['clusterId']}")

    _validate_selection_semantics(package, candidates)

    for index, rejected in enumerate(package.get("rejectedSignals", []), start=1):
        signal_id = rejected.get("signalId")
        if signal_id not in candidate_ids:
            fail(f"rejectedSignals[{index}] references unknown signalId: {signal_id}")
        if rejected.get("mergedIntoSignalId") and rejected["mergedIntoSignalId"] not in candidate_ids:
            fail(f"rejectedSignals[{index}] references unknown mergedIntoSignalId: {rejected['mergedIntoSignalId']}")

    for index, item in enumerate(package.get("watchItems", []), start=1):
        signal_id = item.get("signalId")
        if signal_id not in candidate_ids:
            fail(f"watchItems[{index}] references unknown signalId: {signal_id}")


def validate_ingestion_package(data: dict[str, Any], schema_path: Path | str = DEFAULT_SCHEMA_PATH) -> None:
    package = expect_dict(data, "ingestion-package")
    schema = expect_dict(load_json(schema_path), "schema")
    validate_against_schema(package, schema, schema, "ingestion-package")
    validate_shared_semantics(package)


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validate a signal-deck educational ingestion package v2")
    parser.add_argument("package", nargs="?", type=Path, default=DEFAULT_PACKAGE_PATH)
    parser.add_argument("--schema", type=Path, default=DEFAULT_SCHEMA_PATH)
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    try:
        data = load_json(args.package)
        validate_ingestion_package(data, args.schema)
    except ValidationError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    print(f"OK: {args.package} matches the signal-deck educational ingestion package v2 contract")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
