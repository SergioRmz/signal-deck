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

DEFAULT_INPUT = Path("apps/briefing-page/data/signal-input.sample.json")
DEFAULT_OUTPUT = Path("apps/briefing-page/data/briefing.sample.json")


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


def build_briefing_id(input_id: str, thesis: str, edition_date: str) -> tuple[str, str]:
    slug = slugify(thesis)
    return f"{edition_date}-{slug}", slug


def build_hero(packet: dict[str, Any]) -> dict[str, str]:
    brief = packet["brief"]
    synthesis = packet["synthesis"]
    editorial = packet["editorialDecisions"]
    lede = (
        f"{clean_sentence(brief['objective'])} "
        f"{clean_sentence(synthesis['workingThesis'])}"
    )
    return {
        "title": editorial["heroFrame"],
        "lede": lede,
    }


def build_top_line(signals_by_id: dict[str, dict[str, Any]], packet: dict[str, Any]) -> dict[str, str]:
    editorial = packet["editorialDecisions"]
    synthesis = packet["synthesis"]

    implication_sentences: list[str] = []
    for signal_id in editorial["radarOrder"]:
        signal = signals_by_id[signal_id]
        if signal["priority"] != "high":
            continue
        implication_sentences.extend(signal["implications"][:1])
        if len(implication_sentences) >= 2:
            break

    body_parts = [clean_sentence(synthesis["workingThesis"])]
    body_parts.extend(clean_sentence(item) for item in unique_preserving_order(implication_sentences)[:2])

    return {
        "title": editorial["topLineThesis"],
        "body": " ".join(body_parts),
    }


def build_radar(signals_by_id: dict[str, dict[str, Any]], ordered_ids: list[str]) -> dict[str, Any]:
    return {
        "title": "Radar",
        "items": [
            {
                "label": titleize_category(signals_by_id[signal_id]["category"]),
                "text": signals_by_id[signal_id]["statement"],
            }
            for signal_id in ordered_ids
        ],
    }


def build_deep_dives(signals_by_id: dict[str, dict[str, Any]], deep_dive_ids: list[str]) -> dict[str, Any]:
    items = []
    for index, signal_id in enumerate(deep_dive_ids, start=1):
        signal = signals_by_id[signal_id]
        body_parts = [clean_sentence(signal["evidence"])]
        body_parts.extend(clean_sentence(item) for item in signal["implications"][:2])
        for counterpoint in signal.get("counterpoints", [])[:1]:
            body_parts.append(f"Counterpoint: {clean_sentence(counterpoint)}")
        items.append(
            {
                "title": f"{index}. {signal['statement'].rstrip('.')}" ,
                "body": " ".join(body_parts),
            }
        )

    count = len(items)
    if count == 1:
        title = "One angle for reading the shift"
    else:
        title = f"{count} angles for reading the shift"

    return {
        "title": title,
        "items": items,
    }


def build_market_map(packet: dict[str, Any]) -> dict[str, Any]:
    frames = packet["editorialDecisions"]["marketMapFrames"]
    items = []
    for frame in frames:
        normalized = frame.strip().lower()
        if normalized == "winners":
            text = "Platforms and products that own distribution, recurring workflow, and durable user context."
        elif normalized == "pressured":
            text = "Vendors whose differentiation depends mainly on standalone access to a better model."
        elif normalized == "opportunity":
            text = "Vertical operators that can turn AI into embedded workflow and capture non-portable context over time."
        else:
            text = (
                "This frame should be interpreted through the packet's prioritized signals, "
                "implications, and stated editorial thesis."
            )
        items.append({"label": frame, "text": text})

    return {
        "title": "Who benefits if this thesis is right",
        "items": items,
    }


def build_watchlist(packet: dict[str, Any]) -> dict[str, Any]:
    synthesis = packet["synthesis"]
    editorial = packet["editorialDecisions"]
    questions = unique_preserving_order(editorial["watchlistSeeds"] + synthesis["openQuestions"])
    return {
        "title": "What to watch",
        "items": [{"text": question} for question in questions],
    }


def transform_packet(packet: dict[str, Any]) -> dict[str, Any]:
    meta = packet["meta"]
    editorial = packet["editorialDecisions"]
    signals = packet["signals"]
    signals_by_id = {signal["signalId"]: signal for signal in signals}

    edition_date = meta["createdAt"].split("T", 1)[0]
    briefing_id, slug = build_briefing_id(meta["inputId"], editorial["topLineThesis"], edition_date)

    briefing = {
        "meta": {
            "schemaVersion": "1.0",
            "briefingId": briefing_id,
            "editionDate": edition_date,
            "publishedAt": meta["createdAt"],
            "slug": slug,
            "language": meta["language"],
            "topics": meta.get("tags", []),
        },
        "hero": build_hero(packet),
        "topLine": build_top_line(signals_by_id, packet),
        "radar": build_radar(signals_by_id, editorial["radarOrder"]),
        "deepDives": build_deep_dives(signals_by_id, editorial["deepDiveSignalIds"]),
        "marketMap": build_market_map(packet),
        "watchlist": build_watchlist(packet),
    }
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
