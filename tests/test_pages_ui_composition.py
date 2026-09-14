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
experience = load_module("weread_pages_experience_ui", SCRIPTS / "pages_experience_ui.py")


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

    def test_experience_layer_keeps_archive_chapters_and_controls(self):
        for chapter in (
            "chapter-life",
            "chapter-rhythm",
            "chapter-investment",
            "chapter-knowledge",
            "chapter-reflection",
            "chapter-shelf",
            "chapter-boundary",
        ):
            self.assertIn(chapter, experience.JS)
        self.assertIn("getElementById('rhythm')", experience.JS)
        self.assertIn("focus-mode", experience.CSS)
        self.assertIn("focusToggle", experience.JS)
        self.assertIn("shelfQuery", experience.JS)
        self.assertIn("e.key==='/'", experience.JS)
        self.assertIn("IntersectionObserver", experience.JS)
        self.assertIn("reading-progress", experience.CSS)

    def test_local_pin_queue_does_not_require_remote_writes(self):
        self.assertIn("wereadArchivePinsV1", experience.JS)
        self.assertIn("value='pinned'", experience.JS)
        self.assertIn("localStorage.setItem(pinKey", experience.JS)
        self.assertIn("shelf-pin", experience.CSS)
        self.assertIn("不修改微信读书", experience.JS)
        self.assertNotIn("/shelf/", experience.JS)
        self.assertNotIn("fetch(", experience.JS)

    def test_experience_enhancer_injects_css_and_js(self):
        base = "<html><head><style>BASE</style></head><body><script>BASEJS</script></body></html>"
        out = experience.enhance(base)
        self.assertIn("chapter-heading", out)
        self.assertIn("wereadArchiveFocus", out)
        self.assertIn("wereadArchivePinsV1", out)
        self.assertLess(out.index("BASE"), out.index("chapter-heading"))
        self.assertLess(out.index("BASEJS"), out.index("wereadArchiveFocus"))


if __name__ == "__main__":
    unittest.main()
