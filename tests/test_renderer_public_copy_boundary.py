#!/usr/bin/env python3
"""Static guardrails for reader-facing renderer copy boundaries."""

from __future__ import annotations

import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
APP = ROOT / "apps" / "web" / "src" / "App.tsx"


class RendererPublicCopyBoundaryTest(unittest.TestCase):
    def test_renderer_does_not_expose_editorial_planning_fields(self) -> None:
        source = APP.read_text()

        forbidden_snippets = [
            "module?.interactionCue",
            "topLineModule?.interactionCue",
            "readerTranslationModule?.interactionCue",
            "radarModule?.interactionCue",
            "deepDivesModule?.interactionCue",
            "module?.headline",
            "module.priority",
            "module.variant",
            "module.accentMode",
            "Ruta ensamblada",
            "La página se arma como una clase, no como un feed",
            "Pausar en el cambio estructural",
            "primary: 'principal'",
            "secondary: 'secundario'",
            "supporting: 'soporte'",
        ]
        for snippet in forbidden_snippets:
            self.assertNotIn(snippet, source)

    def test_renderer_uses_reader_facing_topline_module(self) -> None:
        source = APP.read_text()

        self.assertIn("function TopLineSpotlight", source)
        self.assertIn("Tesis operativa", source)
        self.assertIn("briefing.topLine.body", source)
        self.assertNotIn("function StrategyPath", source)


if __name__ == "__main__":
    unittest.main()
