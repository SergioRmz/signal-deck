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
                "Signal Deck is not a news digest",
                "executive learning surface",
                "Separate fact, inference, and speculation",
                "source quality",
                "educational density",
                "Do not send intermediate Telegram messages",
            ]
            for marker in required_shared_markers:
                self.assertIn(marker, scout_prompt)
                self.assertIn(marker, synthesis_prompt)

            for tag in ["product_philosophy", "reader_profile", "evidence_rules", "scoring_rubric", "artifact_discipline"]:
                self.assertIn(f"<{tag}>", scout_prompt)
                self.assertIn(f"</{tag}>", scout_prompt)
                self.assertIn(f"<{tag}>", synthesis_prompt)
                self.assertIn(f"</{tag}>", synthesis_prompt)

            for tag in ["role", "mission", "reasoning_posture", "anti_patterns", "failure_behavior", "output_contract"]:
                self.assertIn(f"<{tag}>", scout_prompt)
                self.assertIn(f"</{tag}>", scout_prompt)
                self.assertIn(f"<{tag}>", synthesis_prompt)
                self.assertIn(f"</{tag}>", synthesis_prompt)

            self.assertIn("You are a senior strategic intelligence scout", scout_prompt)
            self.assertIn("You are the strategic synthesis editor", synthesis_prompt)
            self.assertIn("not merely popular stories", scout_prompt)
            self.assertIn("issue thesis", synthesis_prompt)

    def test_daily_prompt_templates_have_xml_like_expert_sections(self) -> None:
        expected_role_markers = {
            "01-scout-broad.md": "You are a senior strategic intelligence scout",
            "02-scout-update-dedupe.md": "You are a source critic and dedupe editor",
            "03-editorial-synthesis.md": "You are the strategic synthesis editor",
            "04-build-deploy.md": "You are a release engineer and editorial QA operator",
            "05-final-delivery.md": "You are the executive delivery editor",
        }
        required_tags = [
            "role",
            "mission",
            "inputs",
            "reasoning_posture",
            "instructions",
            "anti_patterns",
            "failure_behavior",
            "output_contract",
        ]
        for filename, role_marker in expected_role_markers.items():
            prompt = (ROOT / "prompts" / "daily" / filename).read_text()
            for tag in required_tags:
                self.assertIn(f"<{tag}>", prompt, f"{filename} missing <{tag}>")
                self.assertIn(f"</{tag}>", prompt, f"{filename} missing </{tag}>")
            self.assertIn(role_marker, prompt)

    def test_shared_prompt_modules_have_xml_like_boundaries(self) -> None:
        required_shared_tags = {
            "product-philosophy.md": "product_philosophy",
            "reader-profile.md": "reader_profile",
            "editorial-standards.md": "editorial_standards",
            "evidence-rules.md": "evidence_rules",
            "scoring-rubric.md": "scoring_rubric",
            "artifact-discipline.md": "artifact_discipline",
        }
        for filename, tag in required_shared_tags.items():
            prompt = (ROOT / "prompts" / "daily" / "shared" / filename).read_text()
            self.assertIn(f"<{tag}>", prompt, f"{filename} missing <{tag}>")
            self.assertIn(f"</{tag}>", prompt, f"{filename} missing </{tag}>")

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
