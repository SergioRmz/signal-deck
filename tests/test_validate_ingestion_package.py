from __future__ import annotations

import importlib.util
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT_PATH = ROOT / "scripts" / "validate_ingestion_package.py"
SAMPLE_PATH = ROOT / "data" / "ingestion-package.sample.json"
SCHEMA_PATH = ROOT / "data" / "ingestion-package.schema.json"


def load_validator_module():
    spec = importlib.util.spec_from_file_location("validate_ingestion_package", SCRIPT_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Unable to load {SCRIPT_PATH}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class ValidateIngestionPackageTests(unittest.TestCase):
    def test_canonical_schema_is_available(self) -> None:
        self.assertTrue(SCHEMA_PATH.exists(), "canonical v2 ingestion schema should exist under data/")

    def test_sample_package_passes_validator_function(self) -> None:
        validator = load_validator_module()
        data = validator.load_json(SAMPLE_PATH)
        validator.validate_ingestion_package(data)

    def test_sample_package_passes_cli(self) -> None:
        result = subprocess.run(
            [sys.executable, str(SCRIPT_PATH), str(SAMPLE_PATH)],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("OK:", result.stdout)


if __name__ == "__main__":
    unittest.main()
