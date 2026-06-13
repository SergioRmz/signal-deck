#!/usr/bin/env python3
"""Generate a signal-deck briefing from an ingestion packet.

This script intentionally uses only the Python standard library. It validates the
input packet, applies a deterministic transformation layer, validates the output
briefing, and writes the result to disk.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from typing import Any

from validate_briefing import validate_briefing
from validate_signal_input import expect_dict, validate_input_packet

DEFAULT_INPUT = Path("data/signal-input.sample.json")
DEFAULT_OUTPUT = Path("data/briefing.sample.json")
QUESTION_PREFIXES = ("which", "what", "where", "who", "how", "when", "why", "do", "does", "will", "can")


def slugify(value: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
    return slug or "briefing"


def clean_sentence(value: str) -> str:
    text = value.strip()
    if not text:
        return text
    if text[-1] not in ".!?":
        text += "."
    return text


def titleize_category(value: str) -> str:
    return value.replace("-", " ").replace("_", " ").strip().title()


def unique_preserving_order(values: list[str]) -> list[str]:
    seen: set[str] = set()
    output: list[str] = []
    for value in values:
        normalized = value.strip()
        if not normalized or normalized in seen:
            continue
        seen.add(normalized)
        output.append(normalized)
    return output


def build_briefing_id(thesis: str, edition_date: str) -> tuple[str, str]:
    slug = slugify(thesis)
    return f"{edition_date}-{slug}", slug


def build_meta(packet: dict[str, Any], thesis: str) -> dict[str, Any]:
    meta = packet["meta"]
    brief = packet["brief"]
    edition_date = meta["createdAt"].split("T", 1)[0]
    briefing_id, slug = build_briefing_id(thesis, edition_date)
    output = {
        "schemaVersion": "1.0",
        "briefingId": briefing_id,
        "editionDate": edition_date,
        "publishedAt": meta["createdAt"],
        "slug": slug,
        "language": meta["language"],
        "topics": meta.get("tags", []),
    }

    reader_profile = brief.get("readerProfile")
    if isinstance(reader_profile, dict):
        reader_context: dict[str, Any] = {}
        if isinstance(reader_profile.get("roles"), list) and reader_profile["roles"]:
            reader_context["roles"] = unique_preserving_order([str(item) for item in reader_profile["roles"]])
        if isinstance(reader_profile.get("interests"), list) and reader_profile["interests"]:
            reader_context["interests"] = unique_preserving_order([str(item) for item in reader_profile["interests"]])
        desired_upgrade = reader_profile.get("desiredUpgrade")
        if isinstance(desired_upgrade, str) and desired_upgrade.strip():
            reader_context["desiredUpgrade"] = desired_upgrade.strip()
        if reader_context:
            output["readerContext"] = reader_context

    return output


def build_hero(packet: dict[str, Any], ordered_signals: list[dict[str, Any]]) -> dict[str, str]:
    brief = packet["brief"]
    synthesis = packet["synthesis"]
    editorial = packet["editorialDecisions"]
    lead_signal = ordered_signals[0]
    contradictions = synthesis.get("contradictions", [])
    tension = contradictions[0] if contradictions else lead_signal.get("counterpoints", [""])[0]
    audience = brief.get("audience", "the reader")

    hero = {
        "title": editorial["heroFrame"],
        "lede": f"{clean_sentence(brief['objective'])} {clean_sentence(synthesis['workingThesis'])}",
        "signal": clean_sentence(lead_signal["statement"]),
        "thesis": clean_sentence(synthesis["workingThesis"]),
        "promise": clean_sentence(f"This briefing helps {audience} understand where leverage is moving and why it matters."),
    }
    if tension:
        hero["tension"] = clean_sentence(str(tension))
    return hero


def build_top_line(signals_by_id: dict[str, dict[str, Any]], packet: dict[str, Any]) -> dict[str, str]:
    editorial = packet["editorialDecisions"]
    synthesis = packet["synthesis"]

    first_order_implications: list[str] = []
    second_order_implications: list[str] = []
    for signal_id in editorial["radarOrder"]:
        signal = signals_by_id[signal_id]
        if signal["priority"] != "high":
            continue
        implications = signal["implications"]
        first_order_implications.extend(implications[:1])
        second_order_implications.extend(implications[1:2])
        if len(first_order_implications) >= 2:
            break

    body_parts = [clean_sentence(synthesis["workingThesis"])]
    body_parts.extend(clean_sentence(item) for item in unique_preserving_order(first_order_implications)[:2])
    if second_order_implications:
        body_parts.append(clean_sentence(f"Second-order effect: {second_order_implications[0]}"))
    if synthesis.get("openQuestions"):
        body_parts.append(clean_sentence(f"Question to track: {synthesis['openQuestions'][0]}"))
    stakes = (
        second_order_implications[-1]
        if second_order_implications
        else first_order_implications[0]
        if first_order_implications
        else brief_stakes_fallback(packet)
    )

    return {
        "title": editorial["topLineThesis"],
        "body": " ".join(body_parts),
        "stakes": clean_sentence(stakes),
    }


def brief_stakes_fallback(packet: dict[str, Any]) -> str:
    return packet["brief"]["objective"]


def infer_radar_role(signal: dict[str, Any]) -> str:
    if signal["priority"] == "high":
        return "supports-thesis"
    if signal.get("counterpoints"):
        return "complicates-thesis"
    return "monitor"


def build_radar(signals_by_id: dict[str, dict[str, Any]], ordered_ids: list[str]) -> dict[str, Any]:
    return {
        "title": "Evidence radar",
        "items": [
            {
                "label": titleize_category(signals_by_id[signal_id]["category"]),
                "text": clean_sentence(signals_by_id[signal_id]["statement"]),
                "role": infer_radar_role(signals_by_id[signal_id]),
            }
            for signal_id in ordered_ids
        ],
    }


def build_deep_dives(signals_by_id: dict[str, dict[str, Any]], deep_dive_ids: list[str]) -> dict[str, Any]:
    items = []
    for index, signal_id in enumerate(deep_dive_ids, start=1):
        signal = signals_by_id[signal_id]
        implications = signal["implications"]
        body_parts = [
            clean_sentence(f"Mechanism: {signal['evidence']}"),
            clean_sentence(f"Why it matters: {implications[0]}"),
        ]
        if len(implications) > 1:
            body_parts.append(clean_sentence(f"Second-order effect: {implications[1]}"))
        if signal.get("counterpoints"):
            body_parts.append(clean_sentence(f"Watch the tension: {signal['counterpoints'][0]}"))
        items.append(
            {
                "title": f"{index}. {signal['statement'].rstrip('.')}" ,
                "body": " ".join(body_parts),
                "mechanism": titleize_category(signal["category"]),
                "claim": clean_sentence(signal["statement"]),
                "explanation": clean_sentence(signal["evidence"]),
                "implication": clean_sentence(signal["implications"][0]),
            }
        )

    return {
        "title": "Mechanism breakdown",
        "items": items,
    }


def build_market_map(packet: dict[str, Any]) -> dict[str, Any]:
    frames = packet["editorialDecisions"]["marketMapFrames"]
    items = []
    for frame in frames:
        normalized = frame.strip().lower()
        if normalized == "winners":
            text = "Platforms and products that own distribution, recurring workflow, and durable user context."
            power_shift = "Leverage compounds where workflow and context accumulate."
        elif normalized == "pressured":
            text = "Vendors whose differentiation depends mainly on standalone access to a better model."
            power_shift = "Feature-level advantage erodes faster when access broadens."
        elif normalized == "opportunity":
            text = "Vertical operators that can turn AI into embedded workflow and capture non-portable context over time."
            power_shift = "Specialization wins when it becomes part of daily operating behavior."
        else:
            text = (
                "Interpret this frame through the packet's prioritized signals, implications, and editorial thesis."
            )
            power_shift = "Power moves toward the layer that owns repetition, context, or switching cost."
        items.append({"label": frame, "text": text, "powerShift": power_shift})

    return {
        "title": "Where leverage is moving",
        "items": items,
    }


def build_reader_translation(packet: dict[str, Any], high_priority_signals: list[dict[str, Any]]) -> dict[str, Any] | None:
    reader_profile = packet["brief"].get("readerProfile")
    if not isinstance(reader_profile, dict):
        return None
    roles = reader_profile.get("roles")
    if not isinstance(roles, list) or not roles:
        return None

    raw_role_weights = reader_profile.get("roleWeights")
    role_weights = raw_role_weights if isinstance(raw_role_weights, dict) else {}
    role_signal_index = {
        "software-engineer": 1 if len(high_priority_signals) > 1 else 0,
        "engineer": 1 if len(high_priority_signals) > 1 else 0,
        "founder": 0,
        "operator": 1 if len(high_priority_signals) > 1 else 0,
        "executive": 0,
    }
    role_lenses = {
        "software-engineer": "For a software engineer, the advantage is architecture: design products that capture workflow context, memory, and repeat usage instead of treating model calls as the moat.",
        "engineer": "For an engineer, the advantage is architecture: design products that capture workflow context, memory, and repeat usage instead of treating model calls as the moat.",
        "founder": "For a founder, the advantage is distribution: own the recurring user relationship before model access becomes a commodity input everyone can buy.",
        "operator": "For an operator, the advantage is operating cadence: find where AI becomes a repeated workflow dependency rather than an occasional productivity add-on.",
        "executive": "For an executive, the advantage is allocation discipline: move resources toward workflow ownership, context capture, and durable distribution.",
    }

    original_role_order = {str(role).strip(): index for index, role in enumerate(roles) if str(role).strip()}

    def role_weight(role: str) -> float | None:
        value = role_weights.get(role)
        if isinstance(value, (int, float)) and value > 0:
            return float(value)
        return None

    ordered_roles = sorted(
        original_role_order,
        key=lambda role: (-(role_weight(role) or 0), original_role_order[role]),
    )
    items = []
    for role_text in ordered_roles:
        normalized_role = role_text.lower()
        signal_index = role_signal_index.get(normalized_role, 0)
        source_signal = high_priority_signals[signal_index] if high_priority_signals else None
        fallback_body = source_signal["implications"][0] if source_signal else packet["brief"]["objective"]
        body = role_lenses.get(normalized_role, fallback_body)
        weight = role_weight(role_text)
        item = {
            "role": role_text,
            "headline": clean_sentence(f"What this means for {role_text}").rstrip("."),
            "body": clean_sentence(body),
        }
        if weight is not None:
            item["weight"] = weight
        items.append(item)

    if not items:
        return None
    return {
        "title": "What this changes for you",
        "items": items,
    }


def build_reusable_lesson(packet: dict[str, Any], high_priority_signals: list[dict[str, Any]]) -> dict[str, Any]:
    synthesis = packet["synthesis"]
    apply_when = synthesis.get("supportingThemes", [])[:3]
    takeaway = high_priority_signals[0]["implications"][0] if high_priority_signals else packet["brief"]["objective"]
    return {
        "title": "Reusable lesson",
        "pattern": clean_sentence(
            "When a base capability commoditizes, value often migrates toward the layer that owns workflow, distribution, or non-portable context."
        ),
        "applyWhen": [clean_sentence(theme) for theme in apply_when],
        "takeaway": clean_sentence(takeaway),
    }


def infer_watch_type(question: str) -> str:
    lowered = question.strip().lower()
    if any(lowered.startswith(prefix + " ") for prefix in QUESTION_PREFIXES):
        return "question"
    if "metric" in lowered or "correlat" in lowered:
        return "metric"
    if "invalidate" in lowered or "disprove" in lowered:
        return "invalidation"
    return "question"


def build_watchlist(packet: dict[str, Any]) -> dict[str, Any]:
    synthesis = packet["synthesis"]
    editorial = packet["editorialDecisions"]
    questions = unique_preserving_order(editorial["watchlistSeeds"] + synthesis["openQuestions"])
    return {
        "title": "Watch framework",
        "items": [{"text": clean_sentence(question), "type": infer_watch_type(question)} for question in questions],
    }


def transform_packet(packet: dict[str, Any]) -> dict[str, Any]:
    editorial = packet["editorialDecisions"]
    signals = packet["signals"]
    signals_by_id = {signal["signalId"]: signal for signal in signals}
    ordered_signals = [signals_by_id[signal_id] for signal_id in editorial["radarOrder"]]
    high_priority_signals = [signal for signal in ordered_signals if signal["priority"] == "high"]

    briefing = {
        "meta": build_meta(packet, editorial["topLineThesis"]),
        "hero": build_hero(packet, ordered_signals),
        "topLine": build_top_line(signals_by_id, packet),
        "radar": build_radar(signals_by_id, editorial["radarOrder"]),
        "deepDives": build_deep_dives(signals_by_id, editorial["deepDiveSignalIds"]),
        "marketMap": build_market_map(packet),
        "reusableLesson": build_reusable_lesson(packet, high_priority_signals),
        "watchlist": build_watchlist(packet),
    }

    reader_translation = build_reader_translation(packet, high_priority_signals)
    if reader_translation:
        briefing["readerTranslation"] = reader_translation

    return briefing


def main() -> None:
    input_path = Path(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_INPUT
    output_path = Path(sys.argv[2]) if len(sys.argv) > 2 else DEFAULT_OUTPUT

    if not input_path.exists():
        raise SystemExit(f"ERROR: File not found: {input_path}")

    try:
        data = json.loads(input_path.read_text())
    except json.JSONDecodeError as exc:
        raise SystemExit(f"ERROR: Invalid JSON in {input_path}: {exc}") from exc

    packet = expect_dict(data, "signal-input")
    validate_input_packet(packet)
    briefing = transform_packet(packet)
    validate_briefing(briefing)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(briefing, indent=2) + "\n")
    print(f"OK: generated briefing at {output_path} from {input_path}")


if __name__ == "__main__":
    main()
