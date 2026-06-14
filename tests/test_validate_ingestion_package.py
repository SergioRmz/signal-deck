from __future__ import annotations

import copy
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
    def setUp(self) -> None:
        self.validator = load_validator_module()
        self.sample = self.validator.load_json(SAMPLE_PATH)

    def assert_validation_error(self, package: dict, expected: str) -> None:
        with self.assertRaisesRegex(self.validator.ValidationError, expected):
            self.validator.validate_ingestion_package(package)

    def test_canonical_schema_is_available(self) -> None:
        self.assertTrue(SCHEMA_PATH.exists(), "canonical v2 ingestion schema should exist under data/")

    def test_sample_package_passes_validator_function(self) -> None:
        self.validator.validate_ingestion_package(self.sample)

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

    def test_complete_run_rejects_underfilled_candidate_pool(self) -> None:
        package = copy.deepcopy(self.sample)
        package["candidates"] = package["candidates"][:14]
        package["run"]["candidateCount"] = 14

        self.assert_validation_error(package, "complete run must contain 15-30 candidates")

    def test_complete_run_rejects_overfilled_candidate_pool(self) -> None:
        package = copy.deepcopy(self.sample)
        extra = copy.deepcopy(package["candidates"][-1])
        for index in range(16, 32):
            clone = copy.deepcopy(extra)
            clone["signalId"] = f"sig-{index:02d}"
            clone["title"] = f"Candidate signal {index:02d}"
            package["candidates"].append(clone)
        package["run"]["candidateCount"] = len(package["candidates"])

        self.assert_validation_error(package, "complete run must contain 15-30 candidates")

    def test_underfilled_run_allows_smaller_pool_with_quality_note(self) -> None:
        package = copy.deepcopy(self.sample)
        package["candidates"] = package["candidates"][:12]
        package["run"]["candidateCount"] = 12
        package["run"]["status"] = "underfilled"
        package["qualityNotes"] = [{"code": "UNDERFILLED", "message": "Only 12 credible candidates found.", "severity": "warning"}]

        self.validator.validate_ingestion_package(package)

    def test_missing_candidate_source_reference_is_rejected(self) -> None:
        package = copy.deepcopy(self.sample)
        package["candidates"][0]["sourceIds"] = ["src-does-not-exist"]

        self.assert_validation_error(package, "unknown sourceId: src-does-not-exist")

    def test_complete_run_requires_technology_ai_and_economy_domain_coverage(self) -> None:
        package = copy.deepcopy(self.sample)
        for candidate in package["candidates"]:
            candidate["domainTags"] = ["technology"]
        package["run"]["sourceDiversity"]["domainCounts"] = {"technology": 15}

        self.assert_validation_error(package, "domain coverage must include")


if __name__ == "__main__":
    unittest.main()
