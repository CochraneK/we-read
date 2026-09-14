#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Publish a bounded set of short WeRead highlight excerpts to GitHub Pages.

This module is intentionally separate from the raw-evidence/private-lab path.
User authorization controls privacy, while this publisher keeps an independent
copyright/distribution boundary:

- marks/highlights only; user reviews are never published here;
- at most one excerpt per book;
- a hard character cap per excerpt;
- a hard total-card cap;
- bibliographic attribution and a WeRead deep link;
- no full long highlight bodies.

Enable at deploy time with ``WEREAD_PAGES_INCLUDE_PUBLIC_QUOTES=1``.
"""
from __future__ import annotations

from collections import Counter
from pathlib import Path
import html
import json
import os
import re

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
SITE = ROOT / "site"
MAX_CHARS = 90
MAX_TOTAL = 48
MAX_PER_BOOK = 1
MIN_CHARS = 12


def env_true(name: str, default: bool = False) -> bool:
    raw = os.environ.get(name)
    if raw is None:
        return default
    return raw.strip().lower() in {"1", "true", "yes", "on"}


def load_json(path: Path, default):
    try:
        return json.loads(path.read_text(encoding="utf-8-sig"))
    except (FileNotFoundError, json.JSONDecodeError):
        return default


def book_id(row: dict) -> str:
    return str(row.get("bookId") or (row.get("book") or {}).get("bookId") or "")


def clean_text(value) -> str:
    return re.sub(r"\s+", " ", str(value or "")).strip()


def excerpt_text(text: str, max_chars: int = MAX_CHARS) -> tuple[str, bool]:
    text = clean_text(text)
    if len(text) <= max_chars:
        return text, False
    # Prefer a natural sentence boundary near the cap, but never exceed it.
    window = text[:max_chars]
    cut = max(window.rfind(p) for p in "。！？!?；;")
    if cut >= max(18, int(max_chars * 0.55)):
        window = window[: cut + 1]
    return window.rstrip() + "…", True


def quote_score(text: str, chapter: str, created_at: int) -> tuple[int, int, int]:
    """Deterministic display heuristic, not a literary-quality judgment."""
    length = len(text)
    ideal = 62
    length_score = max(0, 80 - abs(min(length, MAX_CHARS) - ideal))
    punctuation = 8 if any(p in text for p in "。！？!?；;") else 0
    chapter_bonus = 4 if clean_text(chapter) else 0
    return length_score + punctuation + chapter_bonus, int(created_at or 0), length


def build_public_quotes(data_dir: Path = DATA, *, include_private: bool = False,
                        max_chars: int = MAX_CHARS, max_total: int = MAX_TOTAL) -> dict:
    shelf = load_json(data_dir / "weread_shelf.json", {})
    notes = load_json(data_dir / "weread_notes_export.json", [])
    shelf_books = list((shelf or {}).get("books") or [])
    shelf_by_id = {book_id(b): b for b in shelf_books if book_id(b)}
    secret_ids = {book_id(b) for b in shelf_books if book_id(b) and int(b.get("secret") or 0) == 1}

    candidates = []
    seen_text = set()
    for note_book in notes if isinstance(notes, list) else []:
        if not isinstance(note_book, dict):
            continue
        bid = book_id(note_book)
        if not bid or (not include_private and bid in secret_ids):
            continue
        meta = shelf_by_id.get(bid) or note_book
        title = clean_text(meta.get("title") or note_book.get("title") or "未命名")
        author = clean_text(meta.get("author") or note_book.get("author") or "")
        best = None
        for mark in note_book.get("marks") or []:
            if not isinstance(mark, dict):
                continue
            raw = clean_text(mark.get("text"))
            if len(raw) < MIN_CHARS or raw in seen_text:
                continue
            chapter = clean_text(mark.get("chapter"))
            created = int(mark.get("createTime") or 0)
            score = quote_score(raw, chapter, created)
            excerpt, truncated = excerpt_text(raw, max_chars=max_chars)
            row = {
                "bookId": bid,
                "title": title,
                "author": author,
                "chapter": chapter,
                "excerpt": excerpt,
                "truncated": bool(truncated),
                "sourceKind": "mark",
                "deepLink": f"weread://reading?bId={bid}",
                "_score": score,
                "_raw": raw,
            }
            if best is None or row["_score"] > best["_score"]:
                best = row
        if best is not None:
            seen_text.add(best["_raw"])
            candidates.append(best)

    candidates.sort(key=lambda x: x["_score"], reverse=True)
    items = []
    per_book = Counter()
    for row in candidates:
        if per_book[row["bookId"]] >= MAX_PER_BOOK:
            continue
        public = {k: v for k, v in row.items() if not k.startswith("_")}
        items.append(public)
        per_book[row["bookId"]] += 1
        if len(items) >= max(0, max_total):
            break

    return {
        "policy": {
            "enabled": True,
            "userAuthorized": True,
            "source": "marks_only",
            "reviewsPublished": False,
            "fullRawPublished": False,
            "maxCharsPerExcerpt": int(max_chars),
            "maxPerBook": MAX_PER_BOOK,
            "maxTotal": int(max_total),
            "includePrivateBooks": bool(include_private),
            "note": "Short attributed excerpts only. Original long highlight bodies remain outside the public artifact.",
        },
        "count": len(items),
        "items": items,
    }


CSS = r'''
.public-quotes{display:grid;grid-template-columns:repeat(3,1fr);gap:12px}.public-quote{border:1px solid var(--line);border-radius:18px;padding:17px;background:color-mix(in srgb,var(--paper) 92%,var(--bg));display:flex;flex-direction:column;min-height:210px}.public-quote blockquote{font-family:ui-serif,"Songti SC","STSong",serif;font-size:16px;line-height:1.8;margin:0 0 16px}.public-quote .q-meta{margin-top:auto;color:var(--muted);font-size:11px}.public-quote .q-meta b{color:var(--ink);font-size:12px}.public-quote a{color:var(--accent);text-decoration:none}.public-quote-policy{border-left:4px solid var(--accent3);padding-left:13px;color:var(--muted);font-size:12px;margin:0 0 16px}@media(max-width:900px){.public-quotes{grid-template-columns:repeat(2,1fr)}}@media(max-width:560px){.public-quotes{grid-template-columns:1fr}.public-quote{min-height:0}}
'''


def render_section(payload: dict) -> str:
    items = payload.get("items") or []
    cards = []
    for item in items:
        excerpt = html.escape(str(item.get("excerpt") or ""))
        title = html.escape(str(item.get("title") or "未命名"))
        author = html.escape(str(item.get("author") or ""))
        chapter = html.escape(str(item.get("chapter") or ""))
        link = html.escape(str(item.get("deepLink") or ""), quote=True)
        meta = f"<b>《{title}》</b>"
        if author:
            meta += f" · {author}"
        if chapter:
            meta += f"<br>{chapter}"
        open_link = f'<br><a href="{link}">在微信读书打开 ↗</a>' if link else ""
        cards.append(
            '<article class="public-quote">'
            f'<blockquote>“{excerpt}”</blockquote>'
            f'<div class="q-meta">{meta}{open_link}</div>'
            '</article>'
        )
    return (
        '<article class="card wide" id="public-quotes">'
        '<div class="title"><div><div class="section-kicker">Public excerpts</div><h2>我的划线 · 公开摘录</h2></div>'
        f'<small>{len(items)} 条 · 每本最多 1 条</small></div>'
        '<p class="public-quote-policy">这些是经本人授权公开的短划线摘录。这里只发布 mark，不发布本人 review；长划线自动裁剪，原始全文仍留在 Private Reading Lab。</p>'
        f'<div class="public-quotes">{"".join(cards)}</div>'
        '</article>'
    )


def augment_site(site_dir: Path = SITE, data_dir: Path = DATA, *, enabled: bool | None = None) -> dict:
    if enabled is None:
        enabled = env_true("WEREAD_PAGES_INCLUDE_PUBLIC_QUOTES", False)
    report_path = site_dir / "report-data.json"
    index_path = site_dir / "index.html"
    if not report_path.exists() or not index_path.exists():
        raise SystemExit("ERROR: build Pages with scripts/pages_runtime.py before publishing quotes")

    report = load_json(report_path, {})
    if not enabled:
        report.pop("publicQuotes", None)
        report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
        return {"enabled": False, "count": 0}

    include_private = str(report.get("privacyMode") or "") == "full"
    payload = build_public_quotes(data_dir, include_private=include_private)
    report["publicQuotes"] = payload
    report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")

    page = index_path.read_text(encoding="utf-8")
    if 'id="public-quotes"' not in page:
        page = page.replace("</style>", CSS + "\n</style>", 1)
        page = page.replace("</nav>", '<a href="#public-quotes">公开划线</a></nav>', 1)
        marker = '<article class="card wide privacy">'
        section = render_section(payload)
        if marker in page:
            page = page.replace(marker, section + "\n" + marker, 1)
        else:
            page = page.replace("</main>", section + "\n</main>", 1)
        index_path.write_text(page, encoding="utf-8")
    return {"enabled": True, "count": payload["count"], "includePrivateBooks": include_private}


def main() -> None:
    result = augment_site()
    print(json.dumps({"pages-public-quotes": result}, ensure_ascii=False))


if __name__ == "__main__":
    main()
