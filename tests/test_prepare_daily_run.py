#!/usr/bin/env python3
"""Tests for daily run preparation."""

from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from prepare_daily_run import prepare_daily_run  # noqa: E402


class PrepareDailyRunTest(unittest.TestCase):
    def test_prepare_daily_run_writes_timeline_and_phase_prompts(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            manifest = prepare_daily_run(
                edition_date="2030-01-05",
                delivery_time="09:00",
                public_url="https://signal-deck.example.com/",
                runs_dir=Path(tmpdir),
                prompt_dir=ROOT / "prompts" / "daily",
            )

            run_dir = Path(tmpdir) / "2030-01-05"
            timeline = json.loads((run_dir / "run-timeline.json").read_text())
            phase_prompt = (run_dir / "phase-prompts" / "01-scout-broad.md").read_text()

            self.assertEqual(manifest["status"], "ok")
            self.assertEqual(manifest["runDate"], "2030-01-05")
            self.assertEqual(timeline["runDate"], "2030-01-05")
            self.assertEqual(timeline["publicUrl"], "https://signal-deck.example.com")
            self.assertEqual([phase["slot"] for phase in timeline["phases"]], ["02:00", "04:30", "06:30", "08:00", "09:00"])
            self.assertEqual([phase["status"] for phase in timeline["phases"]], ["pending"] * 5)
            self.assertEqual(timeline["phases"][-1]["name"], "final delivery")
            self.assertIn("editionDate: 2030-01-05", phase_prompt)
            self.assertIn("runDir: runs/2030-01-05", phase_prompt)
            self.assertIn("publicUrl: https://signal-deck.example.com/", phase_prompt)

    def test_prepared_phase_prompts_include_expert_shared_context(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            prepare_daily_run(
                edition_date="2030-01-05",
                delivery_time="09:00",
                public_url="https://signal-deck.example.com/",
                runs_dir=Path(tmpdir),
                prompt_dir=ROOT / "prompts" / "daily",
            )

            run_dir = Path(tmpdir) / "2030-01-05"
            scout_prompt = (run_dir / "phase-prompts" / "01-scout-broad.md").read_text()
            synthesis_prompt = (run_dir / "phase-prompts" / "03-editorial-synthesis.md").read_text()

            required_shared_markers = [
                "Signal Deck produces a functional morning briefing",
                "A signal must reveal a mechanism",
                "Separate fact, inference, and speculation",
                "source quality",
                "educational density",
                "If the phase fails for any reason",
            ]
            for marker in required_shared_markers:
                self.assertIn(marker, scout_prompt)
                self.assertIn(marker, synthesis_prompt)

            self.assertIn("You are a strategic intelligence analyst", scout_prompt)
            self.assertIn("You are the strategic synthesis editor", synthesis_prompt)
            self.assertIn("Do not optimize for virality or recency", scout_prompt)
            self.assertIn("Do not invent sources, metrics, quotes, or companies", synthesis_prompt)

    def test_daily_prompt_templates_have_expert_role_sections(self) -> None:
        expected_role_markers = {
            "01-scout-broad.md": "You are a strategic intelligence analyst",
            "02-scout-update-dedupe.md": "You are a source critic and dedupe editor",
            "03-editorial-synthesis.md": "You are the strategic synthesis editor",
            "04-build-deploy.md": "You are the release engineer and editorial QA operator",
            "05-final-delivery.md": "You are the executive delivery editor",
        }
        for filename, role_marker in expected_role_markers.items():
            prompt = (ROOT / "prompts" / "daily" / filename).read_text()
            self.assertIn("## Role", prompt)
            self.assertIn("## Mission", prompt)
            self.assertIn("## Anti-patterns", prompt)
            self.assertIn("## Failure behavior", prompt)
            self.assertIn(role_marker, prompt)

    def test_prepare_daily_run_offsets_slots_from_delivery_time(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            prepare_daily_run(
                edition_date="2030-01-06",
                delivery_time="10:30",
                public_url="https://signal-deck.example.com/",
                runs_dir=Path(tmpdir),
                prompt_dir=ROOT / "prompts" / "daily",
            )

            timeline = json.loads((Path(tmpdir) / "2030-01-06" / "run-timeline.json").read_text())
            self.assertEqual([phase["slot"] for phase in timeline["phases"]], ["03:30", "06:00", "08:00", "09:30", "10:30"])


if __name__ == "__main__":
    unittest.main()
