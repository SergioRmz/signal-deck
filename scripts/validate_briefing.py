#!/usr/bin/env python3
"""Validate a signal-deck briefing against the v1 contract.

This validator intentionally uses only the Python standard library so it can run in
minimal environments. It performs structural checks for the current v1 contract.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

REQUIRED_TOP_LEVEL = [
    "meta",
    "hero",
    "topLine",
    "radar",
    "deepDives",
    "marketMap",
    "watchlist",
]

VALID_RADAR_ROLES = {"supports-thesis", "complicates-thesis", "contradiction", "monitor"}
VALID_WATCH_TYPES = {"confirmation", "invalidation", "metric", "question"}


def fail(message: str) -> None:
    print(f"ERROR: {message}", file=sys.stderr)
    raise SystemExit(1)


def expect_dict(value: Any, label: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        fail(f"{label} must be an object")
    return value


def expect_non_empty_string(value: Any, label: str) -> None:
    if not isinstance(value, str) or not value.strip():
        fail(f"{label} must be a non-empty string")


def expect_list(value: Any, label: str) -> list[Any]:
    if not isinstance(value, list) or not value:
        fail(f"{label} must be a non-empty array")
    return value


def expect_unique_strings(value: Any, label: str) -> list[str]:
    items = expect_list(value, label)
    seen = set()
    normalized: list[str] = []
    for index, item in enumerate(items, start=1):
        if not isinstance(item, str) or not item.strip():
            fail(f"{label}[{index}] must be a non-empty string")
        if item in seen:
            fail(f"{label} contains duplicate value: {item}")
        seen.add(item)
        normalized.append(item)
    return normalized


def validate_labeled_items(items: list[Any], label: str) -> None:
    for index, item in enumerate(items, start=1):
        obj = expect_dict(item, f"{label}[{index}]")
        expect_non_empty_string(obj.get("label"), f"{label}[{index}].label")
        expect_non_empty_string(obj.get("text"), f"{label}[{index}].text")
        if "role" in obj:
            expect_non_empty_string(obj.get("role"), f"{label}[{index}].role")
            if obj["role"] not in VALID_RADAR_ROLES:
                fail(f"{label}[{index}].role must be one of {sorted(VALID_RADAR_ROLES)}")


def validate_titled_items(items: list[Any], label: str) -> None:
    for index, item in enumerate(items, start=1):
        obj = expect_dict(item, f"{label}[{index}]")
        expect_non_empty_string(obj.get("title"), f"{label}[{index}].title")
        expect_non_empty_string(obj.get("body"), f"{label}[{index}].body")
        for field in ["mechanism", "claim", "explanation", "implication"]:
            if field in obj:
                expect_non_empty_string(obj.get(field), f"{label}[{index}].{field}")


def validate_text_items(items: list[Any], label: str) -> None:
    for index, item in enumerate(items, start=1):
        obj = expect_dict(item, f"{label}[{index}]")
        expect_non_empty_string(obj.get("text"), f"{label}[{index}].text")
        if "type" in obj:
            expect_non_empty_string(obj.get("type"), f"{label}[{index}].type")
            if obj["type"] not in VALID_WATCH_TYPES:
                fail(f"{label}[{index}].type must be one of {sorted(VALID_WATCH_TYPES)}")


def validate_reader_translation(block: dict[str, Any]) -> None:
    expect_non_empty_string(block.get("title"), "readerTranslation.title")
    items = expect_list(block.get("items"), "readerTranslation.items")
    for index, item in enumerate(items, start=1):
        obj = expect_dict(item, f"readerTranslation.items[{index}]")
        for field in ["role", "headline", "body"]:
            expect_non_empty_string(obj.get(field), f"readerTranslation.items[{index}].{field}")
        if "weight" in obj:
            if not isinstance(obj["weight"], (int, float)) or obj["weight"] <= 0:
                fail(f"readerTranslation.items[{index}].weight must be a positive number")


def validate_reusable_lesson(block: dict[str, Any]) -> None:
    for field in ["title", "pattern", "takeaway"]:
        expect_non_empty_string(block.get(field), f"reusableLesson.{field}")
    if "applyWhen" in block:
        for index, value in enumerate(expect_list(block["applyWhen"], "reusableLesson.applyWhen"), start=1):
            expect_non_empty_string(value, f"reusableLesson.applyWhen[{index}]")


def validate_briefing(data: dict[str, Any]) -> None:
    for field in REQUIRED_TOP_LEVEL:
        if field not in data:
            fail(f"Missing top-level field: {field}")

    meta = expect_dict(data["meta"], "meta")
    expect_non_empty_string(meta.get("schemaVersion"), "meta.schemaVersion")
    expect_non_empty_string(meta.get("briefingId"), "meta.briefingId")
    expect_non_empty_string(meta.get("editionDate"), "meta.editionDate")
    if meta["schemaVersion"] != "1.0":
        fail("meta.schemaVersion must be '1.0' for the current validator")
    if "readerContext" in meta:
        reader_context = expect_dict(meta["readerContext"], "meta.readerContext")
        if "roles" in reader_context:
            expect_unique_strings(reader_context["roles"], "meta.readerContext.roles")
        if "interests" in reader_context:
            expect_unique_strings(reader_context["interests"], "meta.readerContext.interests")
        if "desiredUpgrade" in reader_context:
            expect_non_empty_string(reader_context.get("desiredUpgrade"), "meta.readerContext.desiredUpgrade")

    hero = expect_dict(data["hero"], "hero")
    expect_non_empty_string(hero.get("title"), "hero.title")
    expect_non_empty_string(hero.get("lede"), "hero.lede")
    for field in ["signal", "thesis", "tension", "promise"]:
        if field in hero:
            expect_non_empty_string(hero.get(field), f"hero.{field}")

    top_line = expect_dict(data["topLine"], "topLine")
    expect_non_empty_string(top_line.get("title"), "topLine.title")
    expect_non_empty_string(top_line.get("body"), "topLine.body")
    if "stakes" in top_line:
        expect_non_empty_string(top_line.get("stakes"), "topLine.stakes")

    radar = expect_dict(data["radar"], "radar")
    expect_non_empty_string(radar.get("title"), "radar.title")
    validate_labeled_items(expect_list(radar.get("items"), "radar.items"), "radar.items")

    deep_dives = expect_dict(data["deepDives"], "deepDives")
    expect_non_empty_string(deep_dives.get("title"), "deepDives.title")
    validate_titled_items(expect_list(deep_dives.get("items"), "deepDives.items"), "deepDives.items")

    market_map = expect_dict(data["marketMap"], "marketMap")
    expect_non_empty_string(market_map.get("title"), "marketMap.title")
    validate_labeled_items(expect_list(market_map.get("items"), "marketMap.items"), "marketMap.items")
    for index, item in enumerate(expect_list(market_map.get("items"), "marketMap.items"), start=1):
        obj = expect_dict(item, f"marketMap.items[{index}]")
        if "powerShift" in obj:
            expect_non_empty_string(obj.get("powerShift"), f"marketMap.items[{index}].powerShift")

    if "readerTranslation" in data:
        validate_reader_translation(expect_dict(data["readerTranslation"], "readerTranslation"))
    if "reusableLesson" in data:
        validate_reusable_lesson(expect_dict(data["reusableLesson"], "reusableLesson"))

    watchlist = expect_dict(data["watchlist"], "watchlist")
    expect_non_empty_string(watchlist.get("title"), "watchlist.title")
    validate_text_items(expect_list(watchlist.get("items"), "watchlist.items"), "watchlist.items")


def main() -> None:
    path = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("apps/briefing-page/data/briefing.sample.json")
    if not path.exists():
        fail(f"File not found: {path}")

    try:
        data = json.loads(path.read_text())
    except json.JSONDecodeError as exc:
        fail(f"Invalid JSON in {path}: {exc}")

    briefing = expect_dict(data, "briefing")
    validate_briefing(briefing)
    print(f"OK: {path} matches the signal-deck briefing contract v1")


if __name__ == "__main__":
    main()
