#!/usr/bin/env python3
"""Render Hermes cron job specs for the staggered Signal Deck daily run.

This script does not install jobs. It writes an auditable preview manifest that
can be used by an operator, the Hermes cron CLI, or this agent's cronjob tool to
create the five recurring phase jobs.
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT = ROOT / "docs" / "operations" / "hermes-cron-jobs.preview.json"
DEFAULT_PUBLIC_URL = "https://signal-deck.sergio-ramirez-mtz.workers.dev/"
DEFAULT_WORKDIR = str(ROOT)

PHASES = [
    {
        "index": "01",
        "name": "scout broad",
        "offsetMinutes": -420,
        "phasePrompt": "01-scout-broad.md",
        "expectedArtifact": "scout-broad.json",
        "deliver": "local",
        "localOnly": True,
        "description": "Collect broad candidate signals and write the first scouting artifact.",
    },
    {
        "index": "02",
        "name": "scout update / dedupe",
        "offsetMinutes": -270,
        "phasePrompt": "02-scout-update-dedupe.md",
        "expectedArtifact": "scout-updated.json",
        "deliver": "local",
        "localOnly": True,
        "description": "Read broad scouting, dedupe, criticize sources, and promote/watch/reject candidates.",
    },
    {
        "index": "03",
        "name": "editorial synthesis",
        "offsetMinutes": -150,
        "phasePrompt": "03-editorial-synthesis.md",
        "expectedArtifact": "ingestion-package.json",
        "deliver": "local",
        "localOnly": True,
        "description": "Create the editorial plan and validated ingestion package for the deterministic pipeline.",
    },
    {
        "index": "04",
        "name": "build deploy",
        "offsetMinutes": -60,
        "phasePrompt": "04-build-deploy.md",
        "expectedArtifact": "deploy-result.json",
        "deliver": "local",
        "localOnly": True,
        "description": "Run the deterministic pipeline, build, deploy, and verify the public page.",
    },
    {
        "index": "05",
        "name": "final delivery",
        "offsetMinutes": 0,
        "phasePrompt": "05-final-delivery.md",
        "expectedArtifact": "telegram-message.md",
        "deliver": "origin",
        "localOnly": False,
        "description": "Read verified delivery artifacts and produce the single user-facing final message.",
    },
]


class CronRenderError(RuntimeError):
    """Raised when cron job specs cannot be rendered."""


def normalize_public_url(public_url: str) -> str:
    cleaned = public_url.strip()
    if not cleaned:
        raise CronRenderError("public URL cannot be empty")
    return cleaned.rstrip("/") + "/"


def parse_delivery_time(delivery_time: str) -> datetime:
    try:
        return datetime.strptime(delivery_time, "%H:%M")
    except ValueError as exc:
        raise CronRenderError(f"delivery time must use HH:MM format: {delivery_time}") from exc


def cron_schedule_for(delivery_anchor: datetime, offset_minutes: int) -> str:
    slot = delivery_anchor + timedelta(minutes=offset_minutes)
    return f"{slot.minute} {slot.hour} * * *"


def render_phase_runtime_prompt(*, phase: dict[str, Any], public_url: str, delivery_time: str, workdir: str) -> str:
    phase_prompt = str(phase["phasePrompt"])
    expected_artifact = f"runs/${{EDITION_DATE}}/{phase['expectedArtifact']}"
    local_only = bool(phase["localOnly"])
    local_delivery_rule = (
        "Do not send Telegram messages. Return a compact completion note for local cron logs only."
        if local_only
        else "This is the only phase allowed to produce the user-facing delivery after verification succeeds."
    )
    final_failure_rule = (
        "If deployment verification failed, return one honest blocker/status message instead of the normal briefing announcement."
        if not local_only
        else "If the phase is blocked, write the blocked artifact/status and return a compact local blocker note."
    )

    return f"""You are running Signal Deck daily phase {phase['index']} — {phase['name']}.

This is a durable Hermes cron job. Do not create, update, remove, or recursively schedule cron jobs from inside this run.

Repository/workdir:
{workdir}

Daily schedule context:
- final delivery slot: {delivery_time}
- public URL: {public_url}
- phase prompt file: runs/${{EDITION_DATE}}/phase-prompts/{phase_prompt}
- expected artifact: {expected_artifact}

Runtime date rule:
1. Compute EDITION_DATE as today's date in YYYY-MM-DD using the live system date.
2. Work inside `{workdir}`.
3. Ensure the run folder and self-contained phase prompts exist by running:

```bash
python3 scripts/prepare_daily_run.py \\
  --edition-date ${{EDITION_DATE}} \\
  --delivery-time {delivery_time} \\
  --public-url {public_url}
```

Phase execution:
1. Read `runs/${{EDITION_DATE}}/phase-prompts/{phase_prompt}`.
2. Follow that prompt exactly, including its Role, Mission, Reasoning posture, Anti-patterns, Failure behavior, and Output contract.
3. Read any prior artifacts required by that phase from `runs/${{EDITION_DATE}}/`.
4. Write or update `{expected_artifact}`.
5. Update `runs/${{EDITION_DATE}}/run-timeline.json` for phase `{phase['name']}` to `completed` or `blocked`.
6. If possible, verify the artifact exists and is non-empty before finishing.

Delivery rule:
{local_delivery_rule}
{final_failure_rule}

Operational note:
Use tools only as needed to complete this phase. Preserve artifact discipline over conversational verbosity.
"""


def build_cron_jobs(*, delivery_time: str, public_url: str, workdir: str) -> list[dict[str, Any]]:
    anchor = parse_delivery_time(delivery_time)
    normalized_url = normalize_public_url(public_url)
    jobs: list[dict[str, Any]] = []
    for phase in PHASES:
        phase_prompt = str(phase["phasePrompt"])
        expected_artifact = f"runs/${{EDITION_DATE}}/{phase['expectedArtifact']}"
        jobs.append(
            {
                "name": f"signal-deck daily {phase['index']} {phase['name'].replace(' / ', ' ')}",
                "phase": phase["name"],
                "schedule": cron_schedule_for(anchor, int(phase["offsetMinutes"])),
                "deliver": phase["deliver"],
                "workdir": workdir,
                "enabledToolsets": ["web", "terminal", "file"],
                "phasePrompt": phase_prompt,
                "expectedArtifact": expected_artifact,
                "description": phase["description"],
                "prompt": render_phase_runtime_prompt(
                    phase=phase,
                    public_url=normalized_url,
                    delivery_time=delivery_time,
                    workdir=workdir,
                ),
            }
        )
    return jobs


def render_cron_jobs(*, output_path: Path, delivery_time: str, public_url: str, workdir: str) -> dict[str, Any]:
    manifest = {
        "status": "ok",
        "deliveryTime": delivery_time,
        "publicUrl": normalize_public_url(public_url),
        "workdir": workdir,
        "jobs": build_cron_jobs(delivery_time=delivery_time, public_url=public_url, workdir=workdir),
    }
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(manifest, indent=2) + "\n")
    return manifest


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Render Hermes cron job specs for Signal Deck daily operations.")
    parser.add_argument("--delivery-time", default="09:00", help="Nominal final delivery time, HH:MM.")
    parser.add_argument("--public-url", default=DEFAULT_PUBLIC_URL, help="Public briefing URL.")
    parser.add_argument("--workdir", default=DEFAULT_WORKDIR, help="Absolute repository workdir for Hermes cron jobs.")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT, help="Preview manifest output path.")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> None:
    args = parse_args(argv or sys.argv[1:])
    try:
        manifest = render_cron_jobs(
            output_path=args.output,
            delivery_time=args.delivery_time,
            public_url=args.public_url,
            workdir=args.workdir,
        )
    except CronRenderError as exc:
        raise SystemExit(f"ERROR: {exc}") from exc
    print("OK: Hermes cron job preview rendered")
    print(f"output: {args.output}")
    print(f"jobs: {len(manifest['jobs'])}")
    for job in manifest["jobs"]:
        print(f"- {job['schedule']} | {job['name']} | deliver={job['deliver']}")


if __name__ == "__main__":
    main()
