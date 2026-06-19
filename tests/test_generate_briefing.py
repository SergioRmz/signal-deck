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

from generate_briefing import (  # noqa: E402
    detect_meta_editorial_voice,
    transform_ingestion_package,
    transform_packet,
)


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
        self.assertIn("economía unitaria", bodies_by_role["founder"])
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

    def test_ingestion_package_public_briefing_is_spanish_and_not_personalized_meta_copy(self) -> None:
        package = json.loads((ROOT / "runs" / "2026-06-15" / "ingestion-package.json").read_text())

        briefing = transform_ingestion_package(package)
        serialized = json.dumps(briefing, ensure_ascii=False)

        self.assertEqual(briefing["meta"]["language"], "es")
        banned_fragments = [
            "Shows Sergio",
            "Teaches readers",
            "Gives Sergio",
            "Helps Sergio",
            "Evidence radar",
            "Mechanism breakdown",
            "executive learner",
            "para Sergio",
        ]
        for fragment in banned_fragments:
            self.assertNotIn(fragment, serialized)
        self.assertIn("La competencia en IA de frontera", serialized)


class MetaEditorialVoiceGuardTest(unittest.TestCase):
    """Verify the generator strips meta-editorial voice from reader-facing fields.

    Meta-editorial voice describes the briefing or editorial process in third
    person instead of speaking as the analyst. Examples:
    - "El briefing del 18 de junio muestra..."
    - "Promover como la primera señal: ..."
    - "Tiene anclaje primario en Reuters y Banxico"
    - "Enseña a leer señales..."
    - "Da a el lector un marco..."
    """

    def test_detector_flags_third_person_briefing_patterns(self) -> None:
        cases = [
            "El briefing del 18 de junio muestra tres capas distintas de un mismo fenómeno.",
            "Este briefing muestra cómo cambia la ventaja.",
            "El briefing traduce una decisión en una lección.",
            "Este análisis revela el mecanismo estructural.",
            "Promover como la primera señal: cambia el régimen monetario.",
            "Tiene anclaje primario en Reuters y Banxico.",
            "Enseña a leer señales de dominios distintos.",
            "Da a el lector un marco reutilizable.",
            "Da al lector una lente para leer mercados.",
        ]
        for text in cases:
            matches = detect_meta_editorial_voice(text)
            self.assertGreater(len(matches), 0, f"Expected to flag: {text!r}")

    def test_detector_does_not_flag_expert_voice(self) -> None:
        clean_cases = [
            "Banxico cerró el ciclo de recortes a 6.50% con inflación arriba del 4%.",
            "El cuello de botella de la IA ya no es el silicio: es el empaque CoWoS.",
            "NVIDIA bloquea 50% de la capacidad de empaque avanzado de TSMC.",
            "La pausa elimina el viento de cola sobre crédito PyME.",
            "China suspendió por un año el régimen de exportación de tierras raras.",
        ]
        for text in clean_cases:
            matches = detect_meta_editorial_voice(text)
            self.assertEqual(matches, [], f"Should not flag expert voice: {text!r}")

    def test_deduplicate_strips_meta_editorial_from_briefing_fields(self) -> None:
        """When phase 03 leaks meta-editorial voice, the generator must clean it."""
        import scripts.generate_briefing as gb

        briefing = {
            "hero": {
                "title": "La ventaja se mueve hacia quien controla el mecanismo, no solo la noticia",
                "lede": "Convertir señales en una mini master class. El briefing del 18 de junio muestra tres capas.",
                "signal": "El briefing del 18 de junio muestra tres capas distintas de un mismo fenómeno.",
                "thesis": "El briefing del 18 de junio muestra tres capas distintas de un mismo fenómeno.",
                "promise": "Esta edición enseña a ubicar dónde se mueve la ventaja.",
                "tension": "El sesgo del consenso todavía asume apertura.",
            },
            "topLine": {
                "title": "El briefing del 18 de junio muestra tres capas distintas.",
                "body": "El briefing del 18 de junio muestra tres capas. Promover como primera señal: Banxico. Tiene anclaje primario en Reuters. Enseña a leer señales. Da a el lector un marco.",
                "stakes": "Traduce una decisión de política monetaria en una lección de operador sobre crédito.",
            },
            "radar": {
                "title": "Radar",
                "items": [
                    {
                        "label": "Estructura de mercado",
                        "text": "El briefing del 18 de junio muestra tres capas distintas.",
                        "role": "supports-thesis",
                    },
                    {
                        "label": "Economía",
                        "text": "Banxico cerró el ciclo de recortes a 6.50% con inflación arriba del 4%.",
                        "role": "supports-thesis",
                    },
                ],
            },
            "deepDives": {
                "title": "Despiece",
                "items": [
                    {
                        "title": "1. El briefing del 18 de junio muestra tres capas.",
                        "body": "Mecanismo: El briefing muestra tres capas distintas. Enseña a leer señales.",
                        "mechanism": "Estructura",
                        "claim": "El briefing del 18 de junio muestra tres capas.",
                        "explanation": "El briefing del 18 de junio muestra tres capas.",
                        "implication": "Enseña a leer señales de dominios distintos.",
                    }
                ],
            },
            "marketMap": {
                "title": "Mapa",
                "items": [
                    {
                        "label": "Ganan",
                        "text": "El briefing muestra cómo cambia la ventaja.",
                        "powerShift": "Da a el lector un marco para evaluar.",
                    }
                ],
            },
            "reusableLesson": {
                "title": "Lección",
                "pattern": "Enseña a leer señales de dominios distintos.",
                "applyWhen": ["AI infrastructure"],
                "takeaway": "El briefing del 18 de junio muestra tres capas distintas.",
            },
            "watchlist": {"title": "Vigilancia", "items": []},
            "readerTranslation": {
                "title": "Qué cambia",
                "items": [
                    {
                        "role": "operador",
                        "headline": "Para un operador",
                        "body": "El briefing del 18 de junio muestra tres capas distintas. Para un operador mexicano, eso redefine el mapa.",
                    }
                ],
            },
        }

        cleaned = gb.deduplicate_briefing_fields(briefing)

        # Check that all forbidden patterns are gone from every reader-facing field
        serialized = json.dumps(cleaned, ensure_ascii=False)
        forbidden = [
            "El briefing del 18 de junio muestra",
            "El briefing del 18 de junio",
            "Promover como",
            "Tiene anclaje primario",
            "Enseña a leer",
            "Da a el lector",
            "Da al lector",
        ]
        for fragment in forbidden:
            self.assertNotIn(fragment, serialized, f"Meta-editorial fragment survived: {fragment!r}")

    def test_ingestion_package_2026_06_18_yields_clean_briefing(self) -> None:
        """Regression: the leaked ingestion package from 2026-06-18 must produce a clean briefing."""
        path = ROOT / "runs" / "2026-06-18" / "ingestion-package.json"
        if not path.exists():
            self.skipTest(f"Sample ingestion package not found at {path}")
        package = json.loads(path.read_text())
        briefing = transform_ingestion_package(package)
        serialized = json.dumps(briefing, ensure_ascii=False)
        forbidden = [
            "El briefing del 18 de junio muestra",
            "El briefing del 18 de junio",
            "Promover como",
            "Tiene anclaje primario",
            "Enseña a leer",
            "Da a el lector",
            "Da al lector",
        ]
        for fragment in forbidden:
            self.assertNotIn(fragment, serialized, f"Meta-editorial fragment survived: {fragment!r}")


if __name__ == "__main__":
    unittest.main()
