#!/usr/bin/env python3
from pathlib import Path
from unittest import mock
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

    def test_text_mode_adds_both_alchemy_modes(self):
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
        labels = [label for label, _ in steps]
        self.assertIn("Alchemy Topic Context", labels)
        self.assertIn("Alchemy Book Context", labels)

    def test_dashboard_renderer_is_the_final_entrypoint(self):
        with tempfile.TemporaryDirectory() as td:
            out = Path(td)
            captured = []
            with mock.patch.object(lab, "run_step", side_effect=lambda args: captured.append(args)):
                lab.render_dashboard(out)
        self.assertEqual(len(captured), 1)
        cmd = captured[0]
        self.assertIn("scripts/renderers/private_lab.py", cmd)
        self.assertIn(str(out / "visualization_context.json"), cmd)
        self.assertIn(str(out / "deep_notes_context.json"), cmd)
        self.assertIn(str(out / "recall_queue.json"), cmd)
        self.assertIn(str(out / "index.html"), cmd)


if __name__ == "__main__":
    unittest.main()
