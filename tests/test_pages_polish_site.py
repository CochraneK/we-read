#!/usr/bin/env python3
from pathlib import Path
import importlib.util
import unittest

ROOT = Path(__file__).resolve().parents[1]


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader
    spec.loader.exec_module(module)
    return module


quotes = load("pages_public_quotes_polish_test", ROOT / "scripts" / "pages_public_quotes.py")
hidden = load("pages_hidden_search_polish_test", ROOT / "scripts" / "pages_hidden_search_ui.py")
polish = load("pages_polish_site_test", ROOT / "scripts" / "pages_polish_site.py")


class PagesPolishTests(unittest.TestCase):
    def test_quote_controls_include_random_resample_and_symbol_search(self):
        section = quotes.render_section({"items": [], "policy": {"candidateCount": 6099}})
        self.assertIn('id="publicQuoteRandom"', section)
        self.assertIn('id="publicQuoteResample"', section)
        self.assertIn('🎲 重新抽样', section)
        self.assertIn('id="publicQuoteSearchSymbol"', section)
        self.assertIn('aria-label="全量搜索"', section)
        self.assertIn('>🔎</button>', section)
        self.assertIn("sampleMarks(48,90)", quotes.JS)
        self.assertIn("open-weread-private-search", quotes.JS)
        self.assertIn("#publicQuoteResample", quotes.CSS)

    def test_we_read_links_use_https_search_not_app_scheme(self):
        self.assertTrue(quotes.web_search_link("测试书").startswith("https://weread.qq.com/web/search/books?keyword="))
        self.assertNotIn("weread://reading", quotes.JS)
        self.assertNotIn("weread://reading", hidden.JS)
        self.assertIn("https://weread.qq.com/web/search/books?keyword=", hidden.JS)

    def test_hidden_search_initializes_after_dom_and_exposes_api(self):
        self.assertIn("DOMContentLoaded", hidden.JS)
        self.assertIn("window.WeReadHiddenEvidenceSearch={open,close,sampleMarks,hydrate}", hidden.JS)
        self.assertIn("open-weread-private-search", hidden.JS)
        self.assertIn("indexedDB.open", hidden.JS)
        self.assertNotIn("fetch(", hidden.JS)
        self.assertNotIn("XMLHttpRequest", hidden.JS)

    def test_polish_keeps_views_in_chapters_and_cleans_placeholders(self):
        self.assertNotIn("annual-overview-cluster", polish.CSS)
        self.assertNotIn("appendChild(card)", polish.JS)
        self.assertIn("#annual-summary,#medals", polish.CSS)
        self.assertIn("#weekday,#season", polish.CSS)
        self.assertIn("#shift,#focus", polish.CSS)
        self.assertIn("cleanPreferenceGrid", polish.JS)
        self.assertIn("cleanTopTitle", polish.JS)
        self.assertIn("MutationObserver", polish.JS)

    def test_clock_peak_ranking_is_compact(self):
        self.assertIn("clock-peak-list", polish.CSS)
        self.assertIn("clock-peak-rank", polish.JS)
        self.assertNotIn("#1 活跃时段", polish.JS)


if __name__ == "__main__":
    unittest.main()
