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
