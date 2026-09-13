#!/usr/bin/env python3
from pathlib import Path
import datetime as dt
import importlib.util
import json
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]


def load_module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader
    spec.loader.exec_module(module)
    return module


pages = load_module("weread_pages_report", ROOT / "scripts" / "build_pages_report.py")


def write_json(root: Path, name: str, value):
    (root / name).write_text(json.dumps(value, ensure_ascii=False), encoding="utf-8")


class PagesReportTests(unittest.TestCase):
    def test_public_report_filters_secret_books_and_raw_text(self):
        with tempfile.TemporaryDirectory() as tmp:
            data = Path(tmp)
            public_id = "public"
            secret_id = "secret"
            ts = int(dt.datetime(2026, 1, 3, tzinfo=dt.timezone.utc).timestamp())

            write_json(data, "weread_shelf.json", {
                "books": [
                    {"bookId": public_id, "title": "公开书", "author": "公开作者", "category": "历史", "secret": 0, "readUpdateTime": ts},
                    {"bookId": secret_id, "title": "私密书", "author": "私密作者", "category": "私密分类", "secret": 1, "readUpdateTime": ts},
                ]
            })
            write_json(data, "weread_notebooks.json", [
                {"bookId": public_id, "book": {"bookId": public_id, "title": "公开书", "author": "公开作者"}, "noteCount": 1, "reviewCount": 1},
                {"bookId": secret_id, "book": {"bookId": secret_id, "title": "私密书", "author": "私密作者"}, "noteCount": 99, "reviewCount": 99},
            ])
            write_json(data, "weread_notes_export.json", [
                {"bookId": public_id, "title": "公开书", "author": "公开作者", "marks": [{"text": "不应公开的原文", "createTime": ts}], "reviews": [{"content": "不应公开的想法", "createTime": ts}]},
                {"bookId": secret_id, "title": "私密书", "author": "私密作者", "marks": [{"text": "秘密", "createTime": ts}], "reviews": []},
            ])
            write_json(data, "weread_readdata.json", {
                "overall": {
                    "readTimes": {str(ts): 7200},
                    "readDays": 1,
                    "readLongest": [
                        {"book": {"bookId": secret_id, "title": "私密书", "author": "私密作者"}, "readTime": 99999},
                        {"book": {"bookId": public_id, "title": "公开书", "author": "公开作者"}, "readTime": 7200},
                    ],
                },
                "monthly": {"2026-01": {"totalReadTime": 7200}},
                "annually": {"2026": {"dailyReadTimes": {str(ts): 7200}, "totalReadTime": 7200, "readDays": 1}},
            })

            report = pages.build_report(data)

            self.assertEqual(report["summary"]["privateExcluded"], 1)
            self.assertEqual(report["summary"]["publicShelfBooks"], 1)
            self.assertEqual(report["summary"]["marks"], 1)
            self.assertEqual(report["summary"]["reviews"], 1)
            self.assertEqual(report["summary"]["notes"], 2)
            self.assertEqual(report["summary"]["investedRate"], 100.0)
            self.assertEqual(report["longest"][0]["title"], "公开书")
            self.assertEqual(report["focus"][0]["top"][0]["category"], "历史")
            self.assertEqual(report["daily"][0]["level"], 4)
            self.assertEqual(report["network"]["authors"][0]["name"], "公开作者")

            serialized = json.dumps(report, ensure_ascii=False)
            self.assertNotIn("私密书", serialized)
            self.assertNotIn("秘密", serialized)
            self.assertNotIn("不应公开的原文", serialized)
            self.assertNotIn("不应公开的想法", serialized)


if __name__ == "__main__":
    unittest.main()
