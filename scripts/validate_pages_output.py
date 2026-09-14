#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Validate the fully assembled GitHub Pages artifact before deployment.

Checks the HTML/report contract, required UX markers, bookshelf count consistency,
and a sample of source mark/review bodies to catch accidental raw-text leaks.
It also writes concatenated inline JavaScript so CI can run ``node --check`` on
exactly the script that will be deployed.
"""
from __future__ import annotations

import argparse
import json
from html.parser import HTMLParser
from pathlib import Path
from typing import Iterable


REQUIRED_HTML_MARKERS = (
    "chapter-life",
    "chapter-shelf",
    "shelf-explorer",
    "archiveCommand",
    "daily-recall",
    "wereadArchivePinsV1",
    "wereadArchiveShelfStateV1",
    "we-read-local-pins",
)
RAW_KEYS = {"text", "content", "markText", "reviewText"}


class InlineScriptParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=False)
        self._inline = False
        self._parts: list[str] = []
        self.scripts: list[str] = []

    def handle_starttag(self, tag: str, attrs) -> None:
        if tag.lower() != "script":
            return
        attr_map = dict(attrs)
        self._inline = not bool(attr_map.get("src"))
        self._parts = []

    def handle_data(self, data: str) -> None:
        if self._inline:
            self._parts.append(data)

    def handle_endtag(self, tag: str) -> None:
        if tag.lower() == "script" and self._inline:
            self.scripts.append("".join(self._parts))
            self._inline = False
            self._parts = []


def load_json(path: Path, default):
    try:
        return json.loads(path.read_text(encoding="utf-8-sig"))
    except (FileNotFoundError, json.JSONDecodeError):
        return default


def iter_raw_bodies(value) -> Iterable[str]:
    """Yield likely user/source body strings, not titles/authors/metadata."""
    if isinstance(value, dict):
        for key, item in value.items():
            if key in RAW_KEYS and isinstance(item, str):
                text = " ".join(item.split()).strip()
                if len(text) >= 24:
                    yield text
            else:
                yield from iter_raw_bodies(item)
    elif isinstance(value, list):
        for item in value:
            yield from iter_raw_bodies(item)


def validate(site: Path, data: Path, js_out: Path, sample_limit: int = 240) -> dict:
    index_path = site / "index.html"
    report_path = site / "report-data.json"
    if not index_path.exists():
        raise ValueError(f"missing {index_path}")
    if not report_path.exists():
        raise ValueError(f"missing {report_path}")

    html = index_path.read_text(encoding="utf-8")
    report_text = report_path.read_text(encoding="utf-8")
    report = json.loads(report_text)

    missing = [marker for marker in REQUIRED_HTML_MARKERS if marker not in html]
    if missing:
        raise ValueError("missing required Page markers: " + ", ".join(missing))

    summary = report.get("summary") or {}
    insights = report.get("insights") or {}
    scope = insights.get("scope") or {}
    enrichment = insights.get("enrichment") or {}
    bookshelf = enrichment.get("bookshelf") or []

    shelf_books = int(summary.get("shelfBooks") or 0)
    if shelf_books <= 0:
        raise ValueError("summary.shelfBooks must be positive")
    if len(bookshelf) != shelf_books:
        raise ValueError(
            f"bookshelf count mismatch: summary={shelf_books} enrichment={len(bookshelf)}"
        )
    if scope.get("rawTextPublished") is not False:
        raise ValueError("insights.scope.rawTextPublished must be false")

    serialized_enrichment = json.dumps(enrichment, ensure_ascii=False)
    for forbidden_key in ("markText", "reviewText"):
        if f'"{forbidden_key}"' in serialized_enrichment:
            raise ValueError(f"forbidden raw-text field in enrichment: {forbidden_key}")

    notes = load_json(data / "weread_notes_export.json", [])
    checked = 0
    for body in iter_raw_bodies(notes):
        # Long exact substrings are a high-signal accidental-publication check.
        needle = body[:160]
        if needle in html or needle in report_text:
            raise ValueError("raw mark/review body leaked into Pages output")
        checked += 1
        if checked >= sample_limit:
            break

    parser = InlineScriptParser()
    parser.feed(html)
    inline = "\n".join(parser.scripts).strip()
    if not inline:
        raise ValueError("no inline JavaScript found in final Page")
    js_out.parent.mkdir(parents=True, exist_ok=True)
    js_out.write_text(inline + "\n", encoding="utf-8")

    return {
        "shelfBooks": shelf_books,
        "notes": int(summary.get("notes") or 0),
        "inlineScripts": len(parser.scripts),
        "inlineJsChars": len(inline),
        "rawBodiesChecked": checked,
        "privateIncluded": int(summary.get("privateIncluded") or 0),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--site", type=Path, default=Path("site"))
    parser.add_argument("--data", type=Path, default=Path("data"))
    parser.add_argument("--js-out", type=Path, default=Path("/tmp/we-read-pages-inline.js"))
    parser.add_argument("--sample-limit", type=int, default=240)
    args = parser.parse_args()
    result = validate(args.site, args.data, args.js_out, max(0, args.sample_limit))
    print(json.dumps(result, ensure_ascii=False))


if __name__ == "__main__":
    main()
