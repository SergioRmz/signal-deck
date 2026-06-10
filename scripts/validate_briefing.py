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


def validate_labeled_items(items: list[Any], label: str) -> None:
    for index, item in enumerate(items, start=1):
        obj = expect_dict(item, f"{label}[{index}]")
        expect_non_empty_string(obj.get("label"), f"{label}[{index}].label")
        expect_non_empty_string(obj.get("text"), f"{label}[{index}].text")


def validate_titled_items(items: list[Any], label: str) -> None:
    for index, item in enumerate(items, start=1):
        obj = expect_dict(item, f"{label}[{index}]")
        expect_non_empty_string(obj.get("title"), f"{label}[{index}].title")
        expect_non_empty_string(obj.get("body"), f"{label}[{index}].body")


def validate_text_items(items: list[Any], label: str) -> None:
    for index, item in enumerate(items, start=1):
        obj = expect_dict(item, f"{label}[{index}]")
        expect_non_empty_string(obj.get("text"), f"{label}[{index}].text")


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

    hero = expect_dict(data["hero"], "hero")
    expect_non_empty_string(hero.get("title"), "hero.title")
    expect_non_empty_string(hero.get("lede"), "hero.lede")

    top_line = expect_dict(data["topLine"], "topLine")
    expect_non_empty_string(top_line.get("title"), "topLine.title")
    expect_non_empty_string(top_line.get("body"), "topLine.body")

    radar = expect_dict(data["radar"], "radar")
    expect_non_empty_string(radar.get("title"), "radar.title")
    validate_labeled_items(expect_list(radar.get("items"), "radar.items"), "radar.items")

    deep_dives = expect_dict(data["deepDives"], "deepDives")
    expect_non_empty_string(deep_dives.get("title"), "deepDives.title")
    validate_titled_items(expect_list(deep_dives.get("items"), "deepDives.items"), "deepDives.items")

    market_map = expect_dict(data["marketMap"], "marketMap")
    expect_non_empty_string(market_map.get("title"), "marketMap.title")
    validate_labeled_items(expect_list(market_map.get("items"), "marketMap.items"), "marketMap.items")

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
