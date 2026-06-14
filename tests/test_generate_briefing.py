#!/usr/bin/env python3
"""Behavior tests for the deterministic briefing transformation layer."""

from __future__ import annotations

import copy
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from generate_briefing import transform_ingestion_package, transform_packet  # noqa: E402


class EditorialTransformationV2Test(unittest.TestCase):
    def setUp(self) -> None:
        self.packet = json.loads((ROOT / "data" / "signal-input.sample.json").read_text())

    def test_reader_translation_uses_role_weights_and_role_specific_advantage(self) -> None:
        packet = copy.deepcopy(self.packet)
        packet["brief"]["readerProfile"]["roleWeights"] = {
            "operator": 0.7,
            "founder": 0.2,
            "software-engineer": 0.1,
        }

        briefing = transform_packet(packet)
        items = briefing["readerTranslation"]["items"]

        self.assertEqual([item["role"] for item in items], ["operator", "founder", "software-engineer"])
        self.assertEqual([item["weight"] for item in items], [0.7, 0.2, 0.1])
        bodies_by_role = {item["role"]: item["body"] for item in items}
        self.assertIn("sistema crítico", bodies_by_role["operator"])
        self.assertIn("unit economics", bodies_by_role["founder"])
        self.assertIn("restricciones reales", bodies_by_role["software-engineer"])

    def test_deep_dives_explain_mechanism_implication_and_tension_explicitly(self) -> None:
        briefing = transform_packet(self.packet)
        first = briefing["deepDives"]["items"][0]

        self.assertIn("Mecanismo:", first["body"])
        self.assertIn("Por qué importa:", first["body"])
        self.assertIn("Efecto de segundo orden:", first["body"])
        self.assertIn("Tensión a vigilar:", first["body"])

    def test_top_line_surfaces_stakes_second_order_effect_and_open_question(self) -> None:
        briefing = transform_packet(self.packet)
        top_line = briefing["topLine"]

        self.assertIn("Efecto de segundo orden:", top_line["body"])
        self.assertIn("Pregunta a vigilar:", top_line["body"])
        self.assertIn("Switching costs may rise", top_line["stakes"])

    def test_ingestion_package_selected_signals_feed_briefing_transformation(self) -> None:
        package = json.loads((ROOT / "data" / "ingestion-package.sample.json").read_text())

        briefing = transform_ingestion_package(package)

        self.assertEqual(briefing["meta"]["language"], "es")
        self.assertGreaterEqual(len(briefing["radar"]["items"]), 5)
        self.assertEqual(len(briefing["deepDives"]["items"]), 2)
        self.assertIn("Mecanismo:", briefing["deepDives"]["items"][0]["body"])
        self.assertIn("Qué cambia para ti", briefing["readerTranslation"]["title"])


if __name__ == "__main__":
    unittest.main()
