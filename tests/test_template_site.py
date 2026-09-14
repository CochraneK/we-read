#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]


class TemplateSiteTests(unittest.TestCase):
    def run_python(self, *args: str) -> subprocess.CompletedProcess:
        return subprocess.run(
            [sys.executable, *args],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=True,
        )

    def test_full_template_reuses_production_chain_without_touching_site(self):
        canonical = ROOT / "site" / "index.html"
        before = canonical.read_bytes() if canonical.exists() else None

        with tempfile.TemporaryDirectory() as tmp:
            tmp = Path(tmp)
            data = tmp / "data"
            site = tmp / "site"
            js = tmp / "inline.js"

            self.run_python("template/demo_data.py", "--output", str(data))
            self.run_python(
                "scripts/build_template_site.py",
                "--data", str(data),
                "--output", str(site),
                "--include-private",
                "--publish-marks",
            )
            validated = self.run_python(
                "scripts/validate_pages_output.py",
                "--site", str(site),
                "--data", str(data),
                "--js-out", str(js),
            )

            result = json.loads(validated.stdout.strip().splitlines()[-1])
            self.assertEqual(result["shelfBooks"], 6)
            self.assertEqual(result["privateIncluded"], 1)
            self.assertGreater(result["publicQuotes"], 0)
            self.assertGreater(result["publicMarkIndex"], 0)

            html = (site / "index.html").read_text(encoding="utf-8")
            self.assertIn('id="chapter-life"', html)
            self.assertIn('id="shelf-explorer"', html)
            self.assertIn('id="public-quotes"', html)
            self.assertIn("clock-peak-list", html)
            self.assertTrue((site / "public-marks-index.js").is_file())
            self.assertTrue((site / ".nojekyll").is_file())

            meta = json.loads((site / "template-build.json").read_text(encoding="utf-8"))
            self.assertEqual(meta["builder"], "weread-template")
            self.assertTrue(meta["includePrivate"])
            self.assertTrue(meta["publishMarks"])

        after = canonical.read_bytes() if canonical.exists() else None
        self.assertEqual(before, after, "template build must never mutate the canonical site/index.html")

    def test_template_builder_refuses_canonical_site_output(self):
        with tempfile.TemporaryDirectory() as tmp:
            data = Path(tmp) / "data"
            self.run_python("template/demo_data.py", "--output", str(data))
            proc = subprocess.run(
                [
                    sys.executable,
                    "scripts/build_template_site.py",
                    "--data", str(data),
                    "--output", str(ROOT / "site"),
                ],
                cwd=ROOT,
                text=True,
                capture_output=True,
            )
            self.assertNotEqual(proc.returncode, 0)
            self.assertIn("refuses to overwrite ./site", proc.stderr + proc.stdout)


if __name__ == "__main__":
    unittest.main()
