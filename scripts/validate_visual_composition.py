#!/usr/bin/env python3
"""Validate a signal-deck visual composition payload against contract v1."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

REQUIRED_TOP_LEVEL = [
    "meta",
    "sourceBriefing",
    "experience",
    "designSystem",
    "page",
    "modules",
]

VALID_VISUAL_TONES = {"sharp", "playful", "cinematic", "dense", "electric", "sober", "hybrid"}
VALID_READING_MODES = {"scan", "guided", "explore", "mixed"}
VALID_INTERACTION_MODELS = {"static", "progressive", "tactile", "layered"}
VALID_THEMES = {"dark"}
VALID_DENSITIES = {"low", "medium", "high"}
VALID_CORNER_STYLES = {"soft", "rounded", "mixed", "sharp"}
VALID_SHADOW_STYLES = {"ambient", "crisp", "glow", "minimal"}
VALID_TEXTURES = {"none", "grid", "grain", "glowfield", "mixed"}
VALID_HERO_VARIANTS = {"thesis-wall", "split-hero", "manifesto", "signal-led", "dashboard-hero"}
VALID_RHYTHMS = {"linear", "modular", "asymmetric", "staged", "mosaic"}
VALID_EMPHASIS = {"topline", "radar", "deep-dives", "market-map", "watchlist", "balanced"}
VALID_MODULE_KINDS = {
    "hero",
    "topline",
    "reader-translation",
    "radar",
    "deep-dive-grid",
    "deep-dive-stack",
    "market-map",
    "reusable-lesson",
    "watchlist",
    "quote-band",
    "signal-strip",
    "comparison-panel",
}
VALID_PRIORITIES = {"primary", "secondary", "supporting"}
VALID_ACCENT_MODES = {"base", "accent", "contrast", "heat"}
VALID_SCROLL_MOODS = {"steady", "punctuated", "surprising"}


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


def expect_choice(value: Any, label: str, valid_values: set[str]) -> str:
    item = expect_non_empty_string(value, label)
    if item not in valid_values:
        fail(f"{label} must be one of {sorted(valid_values)}")
    return item


def validate_meta(meta: dict[str, Any]) -> None:
    expect_non_empty_string(meta.get("schemaVersion"), "meta.schemaVersion")
    expect_non_empty_string(meta.get("compositionId"), "meta.compositionId")
    expect_non_empty_string(meta.get("createdAt"), "meta.createdAt")
    expect_non_empty_string(meta.get("language"), "meta.language")
    if meta["schemaVersion"] != "1.0":
        fail("meta.schemaVersion must be '1.0' for the current validator")
    if "tags" in meta:
        expect_unique_strings(expect_non_empty_list(meta["tags"], "meta.tags"), "meta.tags")


def validate_source_briefing(source_briefing: dict[str, Any]) -> None:
    for field in ["briefingId", "editionDate", "slug"]:
        expect_non_empty_string(source_briefing.get(field), f"sourceBriefing.{field}")
    if "topics" in source_briefing:
        expect_unique_strings(expect_non_empty_list(source_briefing["topics"], "sourceBriefing.topics"), "sourceBriefing.topics")


def validate_experience(experience: dict[str, Any]) -> None:
    expect_choice(experience.get("visualTone"), "experience.visualTone", VALID_VISUAL_TONES)
    expect_choice(experience.get("readingMode"), "experience.readingMode", VALID_READING_MODES)
    expect_non_empty_string(experience.get("engagementGoal"), "experience.engagementGoal")
    expect_choice(experience.get("interactionModel"), "experience.interactionModel", VALID_INTERACTION_MODELS)
    for label in ["hooks", "learningPrompts"]:
        if label in experience:
            for index, value in enumerate(expect_non_empty_list(experience[label], f"experience.{label}"), start=1):
                expect_non_empty_string(value, f"experience.{label}[{index}]")


def validate_design_system(design_system: dict[str, Any]) -> None:
    expect_choice(design_system.get("theme"), "designSystem.theme", VALID_THEMES)
    palette = expect_dict(design_system.get("palette"), "designSystem.palette")
    for field in ["base", "surface", "text", "accent", "accentStrong"]:
        expect_non_empty_string(palette.get(field), f"designSystem.palette.{field}")
    expect_choice(design_system.get("density"), "designSystem.density", VALID_DENSITIES)
    expect_choice(design_system.get("cornerStyle"), "designSystem.cornerStyle", VALID_CORNER_STYLES)
    expect_choice(design_system.get("shadowStyle"), "designSystem.shadowStyle", VALID_SHADOW_STYLES)
    if "texture" in design_system:
        expect_choice(design_system.get("texture"), "designSystem.texture", VALID_TEXTURES)
    if "componentFamily" in design_system:
        expect_non_empty_string(design_system.get("componentFamily"), "designSystem.componentFamily")


def validate_page(page: dict[str, Any]) -> list[str]:
    expect_choice(page.get("heroVariant"), "page.heroVariant", VALID_HERO_VARIANTS)
    expect_choice(page.get("rhythm"), "page.rhythm", VALID_RHYTHMS)
    expect_choice(page.get("emphasis"), "page.emphasis", VALID_EMPHASIS)
    module_order = expect_unique_strings(expect_non_empty_list(page.get("moduleOrder"), "page.moduleOrder"), "page.moduleOrder")
    if "stickyElements" in page:
        expect_unique_strings(expect_non_empty_list(page["stickyElements"], "page.stickyElements"), "page.stickyElements")
    if "scrollMood" in page:
        expect_choice(page.get("scrollMood"), "page.scrollMood", VALID_SCROLL_MOODS)
    return module_order


def validate_modules(modules: list[Any], module_order: list[str]) -> None:
    module_ids = set()
    seen_kinds = set()
    for index, item in enumerate(modules, start=1):
        module = expect_dict(item, f"modules[{index}]")
        module_id = expect_non_empty_string(module.get("moduleId"), f"modules[{index}].moduleId")
        if module_id in module_ids:
            fail(f"Duplicate moduleId: {module_id}")
        module_ids.add(module_id)

        module_kind = expect_choice(module.get("kind"), f"modules[{index}].kind", VALID_MODULE_KINDS)
        seen_kinds.add(module_kind)
        expect_non_empty_string(module.get("variant"), f"modules[{index}].variant")
        expect_non_empty_string(module.get("sourceKey"), f"modules[{index}].sourceKey")
        expect_choice(module.get("priority"), f"modules[{index}].priority", VALID_PRIORITIES)

        for label in ["headline", "body", "interactionCue"]:
            if label in module:
                expect_non_empty_string(module[label], f"modules[{index}].{label}")
        if "layoutHints" in module:
            expect_unique_strings(expect_non_empty_list(module["layoutHints"], f"modules[{index}].layoutHints"), f"modules[{index}].layoutHints")
        if "accentMode" in module:
            expect_choice(module.get("accentMode"), f"modules[{index}].accentMode", VALID_ACCENT_MODES)
        if "dataRefs" in module:
            expect_unique_strings(expect_non_empty_list(module["dataRefs"], f"modules[{index}].dataRefs"), f"modules[{index}].dataRefs")

    if set(module_order) != module_ids:
        fail("page.moduleOrder must reference every moduleId exactly once")
    if "hero" not in seen_kinds:
        fail("modules must include at least one hero module")


def validate_visual_composition(data: dict[str, Any]) -> None:
    for field in REQUIRED_TOP_LEVEL:
        if field not in data:
            fail(f"Missing top-level field: {field}")

    validate_meta(expect_dict(data["meta"], "meta"))
    validate_source_briefing(expect_dict(data["sourceBriefing"], "sourceBriefing"))
    validate_experience(expect_dict(data["experience"], "experience"))
    validate_design_system(expect_dict(data["designSystem"], "designSystem"))
    module_order = validate_page(expect_dict(data["page"], "page"))
    validate_modules(expect_non_empty_list(data["modules"], "modules"), module_order)


def main() -> None:
    path = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("apps/briefing-page/data/visual-composition.sample.json")
    if not path.exists():
        fail(f"File not found: {path}")

    try:
        data = json.loads(path.read_text())
    except json.JSONDecodeError as exc:
        fail(f"Invalid JSON in {path}: {exc}")

    composition = expect_dict(data, "visual-composition")
    validate_visual_composition(composition)
    print(f"OK: {path} matches the signal-deck visual composition contract v1")


if __name__ == "__main__":
    main()
