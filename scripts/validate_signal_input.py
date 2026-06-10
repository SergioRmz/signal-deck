#!/usr/bin/env python3
"""Validate a signal-deck ingestion packet against contract v1.

This validator uses only the Python standard library so it can run in minimal
execution environments.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

REQUIRED_TOP_LEVEL = [
    "meta",
    "brief",
    "sources",
    "signals",
    "synthesis",
    "editorialDecisions",
]

VALID_PRIORITIES = {"high", "medium", "low"}


def fail(message: str) -> None:
    print(f"ERROR: {message}", file=sys.stderr)
    raise SystemExit(1)


def expect_dict(value: Any, label: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        fail(f"{label} must be an object")
    return value


def expect_non_empty_string(value: Any, label: str) -> str:
    if not isinstance(value, str) or not value.strip():
        fail(f"{label} must be a non-empty string")
    return value


def expect_non_empty_list(value: Any, label: str) -> list[Any]:
    if not isinstance(value, list) or not value:
        fail(f"{label} must be a non-empty array")
    return value


def expect_unique_strings(values: list[Any], label: str) -> list[str]:
    normalized = []
    seen = set()
    for index, value in enumerate(values, start=1):
        item = expect_non_empty_string(value, f"{label}[{index}]")
        if item in seen:
            fail(f"{label} contains duplicate value: {item}")
        seen.add(item)
        normalized.append(item)
    return normalized


def validate_meta(meta: dict[str, Any]) -> None:
    expect_non_empty_string(meta.get("schemaVersion"), "meta.schemaVersion")
    expect_non_empty_string(meta.get("inputId"), "meta.inputId")
    expect_non_empty_string(meta.get("createdAt"), "meta.createdAt")
    expect_non_empty_string(meta.get("language"), "meta.language")
    if meta["schemaVersion"] != "1.0":
        fail("meta.schemaVersion must be '1.0' for the current validator")
    if "owners" in meta:
        expect_unique_strings(expect_non_empty_list(meta["owners"], "meta.owners"), "meta.owners")
    if "tags" in meta:
        expect_unique_strings(expect_non_empty_list(meta["tags"], "meta.tags"), "meta.tags")


def validate_brief(brief: dict[str, Any]) -> None:
    for field in ["topic", "objective", "audience", "timeHorizon"]:
        expect_non_empty_string(brief.get(field), f"brief.{field}")
    if "constraints" in brief:
        for index, value in enumerate(expect_non_empty_list(brief["constraints"], "brief.constraints"), start=1):
            expect_non_empty_string(value, f"brief.constraints[{index}]")


def validate_sources(sources: list[Any]) -> set[str]:
    source_ids = set()
    for index, item in enumerate(sources, start=1):
        source = expect_dict(item, f"sources[{index}]")
        source_id = expect_non_empty_string(source.get("sourceId"), f"sources[{index}].sourceId")
        if source_id in source_ids:
            fail(f"Duplicate sourceId: {source_id}")
        source_ids.add(source_id)
        for field in ["title", "sourceType", "publisher"]:
            expect_non_empty_string(source.get(field), f"sources[{index}].{field}")
    return source_ids


def validate_signals(signals: list[Any], source_ids: set[str]) -> set[str]:
    signal_ids = set()
    for index, item in enumerate(signals, start=1):
        signal = expect_dict(item, f"signals[{index}]")
        signal_id = expect_non_empty_string(signal.get("signalId"), f"signals[{index}].signalId")
        if signal_id in signal_ids:
            fail(f"Duplicate signalId: {signal_id}")
        signal_ids.add(signal_id)
        for field in ["statement", "category", "evidence"]:
            expect_non_empty_string(signal.get(field), f"signals[{index}].{field}")
        priority = expect_non_empty_string(signal.get("priority"), f"signals[{index}].priority")
        if priority not in VALID_PRIORITIES:
            fail(f"signals[{index}].priority must be one of {sorted(VALID_PRIORITIES)}")
        linked_sources = expect_unique_strings(
            expect_non_empty_list(signal.get("sourceIds"), f"signals[{index}].sourceIds"),
            f"signals[{index}].sourceIds",
        )
        for source_id in linked_sources:
            if source_id not in source_ids:
                fail(f"signals[{index}] references unknown sourceId: {source_id}")
        for label in ["implications", "counterpoints"]:
            if label in signal:
                for inner_index, value in enumerate(expect_non_empty_list(signal[label], f"signals[{index}].{label}"), start=1):
                    expect_non_empty_string(value, f"signals[{index}].{label}[{inner_index}]")
        expect_non_empty_list(signal.get("implications"), f"signals[{index}].implications")
    return signal_ids


def validate_synthesis(synthesis: dict[str, Any]) -> None:
    expect_non_empty_string(synthesis.get("workingThesis"), "synthesis.workingThesis")
    for label in ["supportingThemes", "openQuestions", "contradictions", "missingInformation"]:
        if label in synthesis:
            for index, value in enumerate(expect_non_empty_list(synthesis[label], f"synthesis.{label}"), start=1):
                expect_non_empty_string(value, f"synthesis.{label}[{index}]")
    expect_non_empty_list(synthesis.get("supportingThemes"), "synthesis.supportingThemes")
    expect_non_empty_list(synthesis.get("openQuestions"), "synthesis.openQuestions")


def validate_editorial_decisions(editorial: dict[str, Any], signal_ids: set[str]) -> None:
    for field in ["heroFrame", "topLineThesis"]:
        expect_non_empty_string(editorial.get(field), f"editorialDecisions.{field}")

    radar_order = expect_unique_strings(
        expect_non_empty_list(editorial.get("radarOrder"), "editorialDecisions.radarOrder"),
        "editorialDecisions.radarOrder",
    )
    deep_dive_ids = expect_unique_strings(
        expect_non_empty_list(editorial.get("deepDiveSignalIds"), "editorialDecisions.deepDiveSignalIds"),
        "editorialDecisions.deepDiveSignalIds",
    )

    for signal_id in radar_order + deep_dive_ids:
        if signal_id not in signal_ids:
            fail(f"editorialDecisions references unknown signalId: {signal_id}")

    for label in ["marketMapFrames", "watchlistSeeds"]:
        for index, value in enumerate(expect_non_empty_list(editorial.get(label), f"editorialDecisions.{label}"), start=1):
            expect_non_empty_string(value, f"editorialDecisions.{label}[{index}]")


def validate_input_packet(data: dict[str, Any]) -> None:
    for field in REQUIRED_TOP_LEVEL:
        if field not in data:
            fail(f"Missing top-level field: {field}")

    validate_meta(expect_dict(data["meta"], "meta"))
    validate_brief(expect_dict(data["brief"], "brief"))
    source_ids = validate_sources(expect_non_empty_list(data["sources"], "sources"))
    signal_ids = validate_signals(expect_non_empty_list(data["signals"], "signals"), source_ids)
    validate_synthesis(expect_dict(data["synthesis"], "synthesis"))
    validate_editorial_decisions(expect_dict(data["editorialDecisions"], "editorialDecisions"), signal_ids)


def main() -> None:
    path = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("apps/briefing-page/data/signal-input.sample.json")
    if not path.exists():
        fail(f"File not found: {path}")

    try:
        data = json.loads(path.read_text())
    except json.JSONDecodeError as exc:
        fail(f"Invalid JSON in {path}: {exc}")

    packet = expect_dict(data, "signal-input")
    validate_input_packet(packet)
    print(f"OK: {path} matches the signal-deck ingestion contract v1")


if __name__ == "__main__":
    main()
