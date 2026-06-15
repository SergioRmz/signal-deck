#!/usr/bin/env python3
"""Prepare auditable artifacts for a staggered daily signal-deck run.

This script does not schedule Hermes cron jobs by itself. It materializes the
run timeline and phase prompt copies that an operator or scheduler can use for a
real-flow run. The prompts are copied into the date-scoped run folder with the
run variables made explicit at the top of each file.
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_RUNS_DIR = ROOT / "runs"
DEFAULT_PROMPT_DIR = ROOT / "prompts" / "daily"
DEFAULT_PUBLIC_URL = "https://signal-deck.sergio-ramirez-mtz.workers.dev/"
SHARED_PROMPTS = [
    "product-philosophy.md",
    "reader-profile.md",
    "editorial-standards.md",
    "evidence-rules.md",
    "scoring-rubric.md",
    "artifact-discipline.md",
]

PHASES = [
    {
        "offsetMinutes": -420,
        "name": "scout broad",
        "artifact": "scout-broad.json",
        "prompt": "01-scout-broad.md",
    },
    {
        "offsetMinutes": -270,
        "name": "scout update / dedupe",
        "artifact": "scout-updated.json",
        "prompt": "02-scout-update-dedupe.md",
    },
    {
        "offsetMinutes": -150,
        "name": "editorial synthesis",
        "artifact": "ingestion-package.json",
        "prompt": "03-editorial-synthesis.md",
    },
    {
        "offsetMinutes": -60,
        "name": "build deploy",
        "artifact": "deploy-result.json",
        "prompt": "04-build-deploy.md",
    },
    {
        "offsetMinutes": 0,
        "name": "final delivery",
        "artifact": "telegram-message.md",
        "prompt": "05-final-delivery.md",
    },
]


class PrepareRunError(RuntimeError):
    """Raised when the daily run cannot be prepared."""


def normalize_public_url(public_url: str) -> str:
    cleaned = public_url.strip()
    if not cleaned:
        raise PrepareRunError("public URL cannot be empty")
    return cleaned.rstrip("/")


def parse_delivery_time(delivery_time: str) -> datetime:
    try:
        return datetime.strptime(delivery_time, "%H:%M")
    except ValueError as exc:
        raise PrepareRunError(f"delivery time must use HH:MM format: {delivery_time}") from exc


def slot_for(delivery_anchor: datetime, offset_minutes: int) -> str:
    return (delivery_anchor + timedelta(minutes=offset_minutes)).strftime("%H:%M")


def write_json(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2) + "\n")


def build_timeline(edition_date: str, delivery_time: str, public_url: str) -> dict[str, Any]:
    anchor = parse_delivery_time(delivery_time)
    normalized_url = normalize_public_url(public_url)
    phases = []
    for phase in PHASES:
        phases.append(
            {
                "slot": slot_for(anchor, int(phase["offsetMinutes"])),
                "name": phase["name"],
                "status": "pending",
                "artifact": f"runs/{edition_date}/{phase['artifact']}",
            }
        )
    return {
        "runDate": edition_date,
        "publicUrl": normalized_url,
        "mode": "staggered daily briefing run prepared from versioned prompt contracts",
        "phases": phases,
    }


def load_shared_prompt_context(prompt_dir: Path) -> str:
    shared_dir = prompt_dir / "shared"
    if not shared_dir.exists():
        raise PrepareRunError(f"shared prompt directory not found: {shared_dir}")
    sections: list[str] = []
    for filename in SHARED_PROMPTS:
        shared_path = shared_dir / filename
        if not shared_path.exists():
            raise PrepareRunError(f"shared prompt template not found: {shared_path}")
        sections.append(shared_path.read_text().rstrip())
    return "\n\n---\n\n".join(sections)


def render_phase_prompt(
    template_text: str,
    *,
    shared_context: str,
    edition_date: str,
    run_dir: str,
    public_url: str,
    delivery_time: str,
) -> str:
    normalized_with_slash = normalize_public_url(public_url) + "/"
    header = "\n".join(
        [
            "---",
            f"editionDate: {edition_date}",
            f"runDir: {run_dir}",
            f"publicUrl: {normalized_with_slash}",
            f"deliverySlot: {delivery_time}",
            "---",
            "",
        ]
    )
    return (
        header
        + "# Signal Deck Daily Agent Prompt\n\n"
        + "## Run Variables\n\n"
        + f"- editionDate: `{edition_date}`\n"
        + f"- runDir: `{run_dir}`\n"
        + f"- publicUrl: `{normalized_with_slash}`\n"
        + f"- deliverySlot: `{delivery_time}`\n\n"
        + "## Shared Operating Context\n\n"
        + shared_context.rstrip()
        + "\n\n---\n\n"
        + template_text.rstrip()
        + "\n"
    )


def copy_phase_prompts(prompt_dir: Path, run_dir: Path, edition_date: str, public_url: str, delivery_time: str) -> list[str]:
    if not prompt_dir.exists():
        raise PrepareRunError(f"prompt directory not found: {prompt_dir}")
    shared_context = load_shared_prompt_context(prompt_dir)
    output_dir = run_dir / "phase-prompts"
    output_dir.mkdir(parents=True, exist_ok=True)
    written: list[str] = []
    for phase in PHASES:
        template_path = prompt_dir / str(phase["prompt"])
        if not template_path.exists():
            raise PrepareRunError(f"prompt template not found: {template_path}")
        output_path = output_dir / template_path.name
        output_path.write_text(
            render_phase_prompt(
                template_path.read_text(),
                shared_context=shared_context,
                edition_date=edition_date,
                run_dir=f"runs/{edition_date}",
                public_url=public_url,
                delivery_time=delivery_time,
            )
        )
        written.append(str(output_path))
    return written


def prepare_daily_run(
    *,
    edition_date: str,
    delivery_time: str,
    public_url: str,
    runs_dir: Path = DEFAULT_RUNS_DIR,
    prompt_dir: Path = DEFAULT_PROMPT_DIR,
) -> dict[str, Any]:
    run_dir = runs_dir / edition_date
    run_dir.mkdir(parents=True, exist_ok=True)
    timeline = build_timeline(edition_date, delivery_time, public_url)
    timeline_path = run_dir / "run-timeline.json"
    write_json(timeline_path, timeline)
    phase_prompts = copy_phase_prompts(prompt_dir, run_dir, edition_date, public_url, delivery_time)
    manifest = {
        "status": "ok",
        "runDate": edition_date,
        "deliveryTime": delivery_time,
        "publicUrl": normalize_public_url(public_url) + "/",
        "timeline": str(timeline_path),
        "phasePrompts": phase_prompts,
    }
    write_json(run_dir / "daily-run-prep.json", manifest)
    return manifest


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Prepare a staggered signal-deck daily run folder.")
    parser.add_argument("--edition-date", required=True, help="Target edition date, YYYY-MM-DD.")
    parser.add_argument("--delivery-time", default="09:00", help="Nominal final delivery time, HH:MM.")
    parser.add_argument("--public-url", default=DEFAULT_PUBLIC_URL, help="Public briefing URL.")
    parser.add_argument("--runs-dir", type=Path, default=DEFAULT_RUNS_DIR, help="Runs directory.")
    parser.add_argument("--prompt-dir", type=Path, default=DEFAULT_PROMPT_DIR, help="Daily prompt template directory.")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> None:
    args = parse_args(argv or sys.argv[1:])
    try:
        manifest = prepare_daily_run(
            edition_date=args.edition_date,
            delivery_time=args.delivery_time,
            public_url=args.public_url,
            runs_dir=args.runs_dir,
            prompt_dir=args.prompt_dir,
        )
    except PrepareRunError as exc:
        raise SystemExit(f"ERROR: {exc}") from exc
    print("OK: daily briefing run prepared")
    for key, value in manifest.items():
        print(f"{key}: {value}")


if __name__ == "__main__":
    main()
