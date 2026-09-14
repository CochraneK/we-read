#!/usr/bin/env python3
from pathlib import Path
import importlib.util
import json
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
MODULE = ROOT / "scripts" / "pages_public_quotes.py"
spec = importlib.util.spec_from_file_location("pages_public_quotes", MODULE)
quotes = importlib.util.module_from_spec(spec)
assert spec.loader
spec.loader.exec_module(quotes)


class PublicQuotesTests(unittest.TestCase):
    def make_data(self, root: Path):
        (root / "weread_shelf.json").write_text(json.dumps({"books": [
            {"bookId": "pub", "title": "公开书", "author": "甲", "secret": 0},
            {"bookId": "sec", "title": "私密书", "author": "乙", "secret": 1},
        ]}, ensure_ascii=False), encoding="utf-8")
        (root / "weread_notes_export.json").write_text(json.dumps([
            {
                "bookId": "pub", "title": "公开书", "author": "甲",
                "marks": [
                    {"chapter": "第一章", "text": "这是一个足够长、可以被选择为公开短摘录的划线。", "createTime": 10},
                    {"chapter": "第二章", "text": "这是另一条同一本书的划线，因此同一轮不应该同时公开。", "createTime": 20},
                ],
                "reviews": [{"chapter": "第一章", "text": "这是用户自己的想法，绝对不应进入公开摘录。", "createTime": 30}],
            },
            {
                "bookId": "sec", "title": "私密书", "author": "乙",
                "marks": [{"chapter": "秘密章", "text": "私密书中的划线在 include_private 开启后也可进入授权公开候选。", "createTime": 40}],
                "reviews": [],
            },
        ], ensure_ascii=False), encoding="utf-8")

    def test_filtered_mode_uses_all_public_marks_as_candidates_but_one_per_book(self):
        with tempfile.TemporaryDirectory() as td:
            data = Path(td); self.make_data(data)
            result = quotes.build_public_quotes(data, include_private=False, seed="fixed")
        self.assertEqual(result["policy"]["candidateCount"], 2)
        self.assertEqual(result["count"], 1)
        self.assertEqual(result["items"][0]["bookId"], "pub")
        self.assertEqual(result["items"][0]["sourceKind"], "mark")
        self.assertNotIn("用户自己的想法", json.dumps(result, ensure_ascii=False))
        self.assertFalse(result["policy"]["reviewsPublished"])
        self.assertTrue(result["policy"]["allEligibleMarksMayBeSampled"])

    def test_full_mode_adds_secret_candidates_and_is_seed_reproducible(self):
        with tempfile.TemporaryDirectory() as td:
            data = Path(td); self.make_data(data)
            first = quotes.build_public_quotes(data, include_private=True, seed="same-day")
            second = quotes.build_public_quotes(data, include_private=True, seed="same-day")
        self.assertEqual(first, second)
        self.assertEqual(first["policy"]["candidateCount"], 3)
        self.assertEqual({x["bookId"] for x in first["items"]}, {"pub", "sec"})
        self.assertTrue(first["policy"]["includePrivateBooks"])

    def test_long_highlight_is_hard_truncated(self):
        raw = "很长的划线内容" * 40
        excerpt, truncated = quotes.excerpt_text(raw, max_chars=90)
        self.assertTrue(truncated)
        self.assertLessEqual(len(excerpt.rstrip("…")), 90)
        self.assertNotEqual(excerpt.rstrip("…"), raw)

    def test_augment_site_renders_random_player_not_full_pool(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td); data, site = root / "data", root / "site"
            data.mkdir(); site.mkdir(); self.make_data(data)
            (site / "report-data.json").write_text(json.dumps({"privacyMode": "full"}), encoding="utf-8")
            (site / "index.html").write_text('<html><head><style></style></head><body><nav></nav><main><article class="card wide privacy">privacy</article></main><script></script></body></html>', encoding="utf-8")
            result = quotes.augment_site(site, data, enabled=True)
            page = (site / "index.html").read_text(encoding="utf-8")
            report = json.loads((site / "report-data.json").read_text(encoding="utf-8"))
        self.assertTrue(result["enabled"])
        self.assertIn('id="public-quotes"', page)
        self.assertIn('id="publicQuotePlayer"', page)
        self.assertIn("随机轮播", page)
        self.assertIn("setInterval", page)
        self.assertTrue(report["publicQuotes"]["policy"]["userAuthorized"])
        self.assertEqual(report["publicQuotes"]["policy"]["source"], "marks_only")
        self.assertEqual(report["publicQuotes"]["policy"]["candidateCount"], 3)


if __name__ == "__main__":
    unittest.main()
