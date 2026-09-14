#!/usr/bin/env python3
from pathlib import Path
import importlib.util
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
MODULE = ROOT / "scripts" / "build_private_reading_lab.py"
spec = importlib.util.spec_from_file_location("build_private_reading_lab", MODULE)
lab = importlib.util.module_from_spec(spec)
assert spec.loader
spec.loader.exec_module(lab)


class PrivateReadingLabTests(unittest.TestCase):
    def test_filtered_notes_follows_unified_context_privacy(self):
        raw = [
            {"bookId": "public", "title": "公开"},
            {"bookId": "secret", "title": "私密"},
        ]
        context = {"books": [{"bookId": "public"}]}
        self.assertEqual(lab.filtered_notes(raw, context), [raw[0]])

    def test_core_steps_unify_modern_analysis_modules(self):
        with tempfile.TemporaryDirectory() as td:
            out = Path(td)
            steps = lab.build_steps(
                out,
                include_private=False,
                with_text=False,
                topic="",
                book_id="",
                review_start="2026-01-01",
                review_end="2026-09-14",
                review_platform="",
            )
        labels = [label for label, _ in steps]
        self.assertIn("统一事实层", labels)
        self.assertIn("Advisor Context", labels)
        self.assertIn("Blindspot Context", labels)
        self.assertIn("Recall Queue", labels)
        self.assertIn("Search Index", labels)
        self.assertIn("Deep Notes Context", labels)
        self.assertIn("Narrative Review Context", labels)
        flattened = "\n".join(" ".join(cmd) for _, cmd in steps)
        self.assertIn("build_visualization_context.py", flattened)
        self.assertIn("build_deep_notes_context.py", flattened)
        self.assertNotIn("analysis.py", flattened)

    def test_text_mode_adds_alchemy_and_private_hub_links(self):
        with tempfile.TemporaryDirectory() as td:
            out = Path(td)
            steps = lab.build_steps(
                out,
                include_private=True,
                with_text=True,
                topic="认知科学",
                book_id="book-1",
                review_start="2026-01-01",
                review_end="2026-09-14",
                review_platform="公众号",
            )
            page = lab.render_index(out, with_text=True, topic="认知科学", book_id="book-1")
        labels = [label for label, _ in steps]
        self.assertIn("Alchemy Topic Context", labels)
        self.assertIn("Alchemy Book Context", labels)
        self.assertIn("划线卡片", page)
        self.assertIn("quote_cards.html", page)
        self.assertIn("Deep Notes Context", page)
        self.assertIn("不得接入公开 Pages", page)


if __name__ == "__main__":
    unittest.main()
