#!/usr/bin/env python3
"""Tests for Hermes cron job rendering."""

from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from render_hermes_cron_jobs import build_cron_jobs, render_cron_jobs  # noqa: E402


class RenderHermesCronJobsTest(unittest.TestCase):
    def test_build_cron_jobs_creates_five_staggered_phase_specs(self) -> None:
        jobs = build_cron_jobs(
            delivery_time="09:00",
            public_url="https://signal-deck.example.com/",
            workdir="/root/workspace/signal-deck",
        )

        self.assertEqual(len(jobs), 5)
        self.assertEqual([job["schedule"] for job in jobs], ["0 2 * * *", "30 4 * * *", "30 6 * * *", "0 8 * * *", "0 9 * * *"])
        self.assertEqual([job["deliver"] for job in jobs], ["local", "local", "local", "local", "origin"])
        self.assertEqual(jobs[0]["name"], "signal-deck daily 01 scout broad")
        self.assertEqual(jobs[-1]["name"], "signal-deck daily 05 final delivery")
        self.assertEqual(jobs[0]["expectedArtifact"], "runs/${EDITION_DATE}/scout-broad.json")
        self.assertEqual(jobs[-1]["expectedArtifact"], "runs/${EDITION_DATE}/telegram-message.md")

    def test_each_cron_prompt_is_self_contained_and_phase_specific(self) -> None:
        jobs = build_cron_jobs(
            delivery_time="09:00",
            public_url="https://signal-deck.example.com/",
            workdir="/root/workspace/signal-deck",
        )

        first_prompt = jobs[0]["prompt"]
        final_prompt = jobs[-1]["prompt"]

        for job in jobs:
            prompt = job["prompt"]
            self.assertIn("Do not create, update, remove, or recursively schedule cron jobs", prompt)
            self.assertIn("python3 scripts/prepare_daily_run.py", prompt)
            self.assertIn("runs/${EDITION_DATE}/phase-prompts/", prompt)
            self.assertIn(job["phasePrompt"], prompt)
            self.assertIn(job["expectedArtifact"], prompt)
            self.assertIn("/root/workspace/signal-deck", prompt)
            self.assertEqual(job["workdir"], "/root/workspace/signal-deck")
            self.assertEqual(job["enabledToolsets"], ["web", "terminal", "file"])

        self.assertIn("Do not send Telegram messages", first_prompt)
        self.assertIn("Return a compact completion note for local cron logs only", first_prompt)
        self.assertIn("This is the only phase allowed to produce the user-facing delivery", final_prompt)
        self.assertIn("If deployment verification failed", final_prompt)

    def test_render_cron_jobs_writes_preview_manifest(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir) / "cron-jobs.preview.json"
            manifest = render_cron_jobs(
                output_path=output_path,
                delivery_time="10:30",
                public_url="https://signal-deck.example.com/",
                workdir="/root/workspace/signal-deck",
            )

            written = json.loads(output_path.read_text())
            self.assertEqual(manifest["status"], "ok")
            self.assertEqual(written["deliveryTime"], "10:30")
            self.assertEqual([job["schedule"] for job in written["jobs"]], ["30 3 * * *", "0 6 * * *", "0 8 * * *", "30 9 * * *", "30 10 * * *"])
            self.assertEqual(written["jobs"][-1]["deliver"], "origin")


if __name__ == "__main__":
    unittest.main()
