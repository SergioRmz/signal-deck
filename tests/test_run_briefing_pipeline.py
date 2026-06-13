#!/usr/bin/env python3
"""Tests for the local briefing pipeline runner."""

from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from run_briefing_pipeline import run_pipeline  # noqa: E402


class RunBriefingPipelineTest(unittest.TestCase):
    def test_pipeline_writes_run_artifacts_and_syncs_composition_identity(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            args = SimpleNamespace(
                input=(ROOT / "data" / "signal-input.sample.json"),
                composition_template=(ROOT / "data" / "visual-composition.sample.json"),
                runs_dir=Path(tmpdir),
                run_date="2030-01-02",
                public_url="https://signal-deck.example.com/",
                build_renderer=False,
            )

            manifest = run_pipeline(args)
            run_dir = Path(tmpdir) / "2030-01-02"
            briefing = json.loads((run_dir / "briefing.final.json").read_text())
            composition = json.loads((run_dir / "visual-composition.json").read_text())
            telegram_message = (run_dir / "telegram-message.md").read_text()

            self.assertEqual(manifest["status"], "ok")
            self.assertEqual(manifest["rendererBuild"], "not-requested")
            self.assertTrue((run_dir / "signal-input.json").exists())
            self.assertTrue((run_dir / "manifest.json").exists())
            self.assertEqual(composition["sourceBriefing"]["briefingId"], briefing["meta"]["briefingId"])
            self.assertEqual(composition["sourceBriefing"]["editionDate"], briefing["meta"]["editionDate"])
            self.assertIn(briefing["topLine"]["title"], telegram_message)
            self.assertIn("Signals to read first", telegram_message)
            self.assertIn("Read the full briefing: https://signal-deck.example.com/", telegram_message)


if __name__ == "__main__":
    unittest.main()
