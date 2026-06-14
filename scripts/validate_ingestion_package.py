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


def validate_shared_semantics(package: dict[str, Any]) -> None:
    sources = expect_non_empty_list(package.get("sources"), "sources")
    candidates = expect_non_empty_list(package.get("candidates"), "candidates")
    _validate_run_counts(package)
    _validate_domain_coverage(package)
    _validate_source_metadata(sources)
    _validate_candidate_metadata(candidates)

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
