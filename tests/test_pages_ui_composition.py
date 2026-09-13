#!/usr/bin/env python3
from pathlib import Path
import importlib.util
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))


def load_module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader
    spec.loader.exec_module(module)
    return module


story = load_module("weread_pages_story_ui", SCRIPTS / "pages_story_ui.py")
enrich = load_module("weread_pages_enrich_site", SCRIPTS / "pages_enrich_site.py")


class PagesUiCompositionTests(unittest.TestCase):
    def test_story_ui_includes_year_lens_and_career_views(self):
        self.assertIn('id="year-lens"', story.HTML)
        self.assertIn('id="career"', story.HTML)
        self.assertIn('id="depth-matrix"', story.HTML)
        self.assertIn('id="note-evolution"', story.HTML)
        self.assertIn("renderYearLens", story.JS)
        self.assertIn("drawCareer", story.JS)
        self.assertIn("drawScatter", story.JS)

    def test_enrichment_ui_keeps_explorer_and_rhythm_modules(self):
        self.assertIn('id="clock"', enrich.HTML)
        self.assertIn('id="progress"', enrich.HTML)
        self.assertIn('id="recall"', enrich.HTML)
        self.assertIn('id="shelf-explorer"', enrich.HTML)
        self.assertIn("drawClock", enrich.JS)
        self.assertIn("renderShelf", enrich.JS)
        self.assertIn("optionalSection", enrich.JS)


if __name__ == "__main__":
    unittest.main()
