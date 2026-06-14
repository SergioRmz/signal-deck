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

import run_briefing_pipeline  # noqa: E402
from run_briefing_pipeline import run_pipeline  # noqa: E402


class RunBriefingPipelineTest(unittest.TestCase):
    def test_pipeline_writes_run_artifacts_and_syncs_composition_identity(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            args = SimpleNamespace(
                input=(ROOT / "data" / "signal-input.sample.json"),
                ingestion_package=(ROOT / "data" / "ingestion-package.sample.json"),
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
            ingestion_package = json.loads((run_dir / "ingestion-package.json").read_text())
            telegram_message = (run_dir / "telegram-message.md").read_text()

            self.assertEqual(manifest["status"], "ok")
            self.assertEqual(manifest["rendererBuild"], "not-requested")
            self.assertTrue((run_dir / "manifest.json").exists())
            self.assertEqual(manifest["ingestionPackage"], str(run_dir / "ingestion-package.json"))
            self.assertEqual(ingestion_package["meta"]["packageId"], "ingestion-package-2026-06-14-foundation")
            self.assertEqual(composition["sourceBriefing"]["briefingId"], briefing["meta"]["briefingId"])
            self.assertEqual(composition["sourceBriefing"]["editionDate"], briefing["meta"]["editionDate"])
            self.assertIn(briefing["topLine"]["title"], telegram_message)
            self.assertIn("Señales para leer primero", telegram_message)
            self.assertIn("Lee el briefing completo: https://signal-deck.example.com/", telegram_message)

    def test_manifest_references_validated_ingestion_package_artifact(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            args = SimpleNamespace(
                input=(ROOT / "data" / "signal-input.sample.json"),
                ingestion_package=(ROOT / "data" / "ingestion-package.sample.json"),
                composition_template=(ROOT / "data" / "visual-composition.sample.json"),
                runs_dir=Path(tmpdir),
                run_date="2030-01-03",
                public_url=None,
                build_renderer=False,
            )

            manifest = run_pipeline(args)
            run_dir = Path(tmpdir) / "2030-01-03"
            manifest_on_disk = json.loads((run_dir / "manifest.json").read_text())

            self.assertEqual(manifest["ingestionPackage"], str(run_dir / "ingestion-package.json"))
            self.assertEqual(manifest_on_disk["ingestionPackage"], manifest["ingestionPackage"])
            self.assertTrue((run_dir / "ingestion-package.json").exists())

    def test_renderer_build_receives_final_briefing_and_composition_artifacts(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            captured_paths: list[tuple[Path, Path]] = []

            def fake_build(briefing_path: Path, composition_path: Path) -> None:
                captured_paths.append((briefing_path, composition_path))

            original_build = run_briefing_pipeline.run_renderer_build
            run_briefing_pipeline.run_renderer_build = fake_build
            try:
                args = SimpleNamespace(
                    input=(ROOT / "data" / "signal-input.sample.json"),
                    ingestion_package=(ROOT / "data" / "ingestion-package.sample.json"),
                    composition_template=(ROOT / "data" / "visual-composition.sample.json"),
                    runs_dir=Path(tmpdir),
                    run_date="2030-01-04",
                    public_url=None,
                    build_renderer=True,
                )

                manifest = run_pipeline(args)
            finally:
                run_briefing_pipeline.run_renderer_build = original_build

            run_dir = Path(tmpdir) / "2030-01-04"
            self.assertEqual(captured_paths, [(run_dir / "briefing.final.json", run_dir / "visual-composition.json")])
            self.assertEqual(manifest["rendererBuild"], "passed")


if __name__ == "__main__":
    unittest.main()
