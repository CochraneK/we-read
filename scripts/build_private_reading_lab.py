#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Build the local/private WeRead Reading Lab.

This is the integration entry point for the user's original highlight-card work
and the newer evidence-first WeRead Intelligence modules. It intentionally writes
outside `site/` so raw evidence can never be published by the Pages workflow.

Important: the core lab already contains private raw evidence because Search,
Recall and Deep Notes operate on mark/review text. `--with-text` means “also
build browsable quote-card and optional Alchemy assets”, not “turn privacy on”.
"""
from __future__ import annotations

from datetime import date
from pathlib import Path
import argparse
import json
import os
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
DATA = Path(os.environ.get("WEREAD_DATA_DIR", ROOT / "data")).expanduser().resolve()
DEFAULT_OUT = DATA / "analysis" / "private_lab"


def run_step(args: list[str]) -> None:
    subprocess.run([sys.executable, *args], cwd=ROOT, check=True)


def filtered_notes(raw_notes: list, context: dict) -> list[dict]:
    allowed = {str(b.get("bookId") or "") for b in (context.get("books") or []) if isinstance(b, dict)}
    return [
        row for row in raw_notes
        if isinstance(row, dict) and str(row.get("bookId") or "") in allowed
    ]


def build_steps(out_dir: Path, *, include_private: bool, with_text: bool, topic: str, book_id: str,
                review_start: str, review_end: str, review_platform: str) -> list[tuple[str, list[str]]]:
    context = out_dir / "visualization_context.json"
    steps: list[tuple[str, list[str]]] = []
    context_cmd = ["scripts/build_visualization_context.py", "--output", str(context)]
    if include_private:
        context_cmd.append("--include-private")
    steps.append(("统一事实层", context_cmd))
    steps.extend([
        ("Advisor Context", ["scripts/build_advisor_context.py", "--context", str(context), "--output", str(out_dir / "advisor_context.json")]),
        ("Blindspot Context", ["scripts/build_blindspot_context.py", "--context", str(context), "--output", str(out_dir / "blindspot_context.json")]),
        ("Recall Queue", ["scripts/build_recall_queue.py", "--context", str(context), "--output", str(out_dir / "recall_queue.json"), "--min-age-days", "30", "--limit", "40", "--max-per-book", "2"]),
        ("Search Index", ["scripts/build_search_index.py", "--context", str(context), "--db", str(out_dir / "search.sqlite"), "--rebuild"]),
        ("Deep Notes Context", ["scripts/build_deep_notes_context.py", "--context", str(context), "--output", str(out_dir / "deep_notes_context.json")]),
    ])
    review = [
        "scripts/build_narrative_review_context.py", "--context", str(context),
        "--readdata", str(DATA / "weread_readdata.json"), "--start", review_start,
        "--end", review_end, "--output", str(out_dir / "narrative_review_context.json"),
    ]
    if review_platform:
        review.extend(["--platform", review_platform])
    steps.append(("Narrative Review Context", review))

    if with_text:
        if topic:
            steps.append(("Alchemy Topic Context", [
                "scripts/build_alchemy_context.py", "--context", str(context), "--topic", topic,
                "--output", str(out_dir / "alchemy_topic_context.json"),
            ]))
        if book_id:
            steps.append(("Alchemy Book Context", [
                "scripts/build_alchemy_context.py", "--context", str(context), "--book-id", book_id,
                "--output", str(out_dir / "alchemy_book_context.json"),
            ]))
    return steps


def write_private_text_assets(out_dir: Path, context_path: Path) -> None:
    """Build the historical highlight-card branch through the unified privacy allowlist."""
    raw_path = DATA / "weread_notes_export.json"
    if not raw_path.exists():
        raise SystemExit(f"ERROR: missing {raw_path}; run scripts/export_notes.py first")
    context = json.loads(context_path.read_text(encoding="utf-8"))
    raw_notes = json.loads(raw_path.read_text(encoding="utf-8"))
    notes = filtered_notes(raw_notes if isinstance(raw_notes, list) else [], context)
    filtered = out_dir / "filtered_notes_private.json"
    filtered.write_text(json.dumps(notes, ensure_ascii=False, indent=2), encoding="utf-8")
    quote_dir = out_dir / "quotes"
    run_step(["scripts/build_quote_lib.py", "--input", str(filtered), "--output-dir", str(quote_dir)])
    run_step(["scripts/renderers/quote_cards.py", "--input", str(quote_dir / "金句库.json"), "--output", str(out_dir / "quote_cards.html")])


def render_dashboard(out_dir: Path) -> None:
    args = [
        "scripts/renderers/private_lab.py",
        "--context", str(out_dir / "visualization_context.json"),
        "--deep", str(out_dir / "deep_notes_context.json"),
        "--recall", str(out_dir / "recall_queue.json"),
        "--advisor", str(out_dir / "advisor_context.json"),
        "--blindspot", str(out_dir / "blindspot_context.json"),
        "--review", str(out_dir / "narrative_review_context.json"),
        "--quote-cards", str(out_dir / "quote_cards.html"),
        "--output", str(out_dir / "index.html"),
    ]
    run_step(args)


def parse_args():
    today = date.today()
    parser = argparse.ArgumentParser(description="Build the local/private WeRead Reading Lab.")
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUT)
    parser.add_argument("--include-private", action="store_true", help="Include secret=1 books in the private lab context. Off by default.")
    parser.add_argument(
        "--with-text",
        action="store_true",
        help="Also build quote library/cards and optional Alchemy assets. Core Search/Recall already contain private evidence text.",
    )
    parser.add_argument("--topic", default="", help="Optional Alchemy topic; requires --with-text.")
    parser.add_argument("--book-id", default="", help="Optional single-book Alchemy context; requires --with-text.")
    parser.add_argument("--review-start", default=f"{today.year}-01-01")
    parser.add_argument("--review-end", default=today.isoformat())
    parser.add_argument("--review-platform", choices=["", "朋友圈", "公众号", "小红书", "视频脚本", "个人日记"], default="")
    return parser.parse_args()


def main():
    args = parse_args()
    if (args.topic.strip() or args.book_id.strip()) and not args.with_text:
        raise SystemExit("ERROR: --topic/--book-id require --with-text because Alchemy contains raw evidence")

    out_dir = args.output_dir.expanduser().resolve()
    out_dir.mkdir(parents=True, exist_ok=True)
    steps = build_steps(
        out_dir,
        include_private=args.include_private,
        with_text=args.with_text,
        topic=args.topic.strip(),
        book_id=args.book_id.strip(),
        review_start=args.review_start,
        review_end=args.review_end,
        review_platform=args.review_platform,
    )
    for label, command in steps:
        print(f"==> {label}")
        run_step(command)

    context_path = out_dir / "visualization_context.json"
    if args.with_text:
        print("==> Quote Library + Cards")
        write_private_text_assets(out_dir, context_path)

    print("==> Interactive Private Lab")
    render_dashboard(out_dir)

    manifest = {
        "version": 2,
        "private": True,
        "publicPageSafe": False,
        "containsRawEvidence": True,
        "outputDir": str(out_dir),
        "includePrivateBooks": bool(args.include_private),
        "includesQuoteCards": bool(args.with_text),
        "includesAlchemyRawEvidence": bool(args.with_text and (args.topic.strip() or args.book_id.strip())),
        "topicAlchemy": args.topic.strip() or None,
        "bookAlchemy": args.book_id.strip() or None,
        "entry": "index.html",
        "privacyNote": "Search/Recall/context artifacts contain mark/review text even without --with-text; keep the entire directory private.",
    }
    (out_dir / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    print(
        f"private-reading-lab: {out_dir / 'index.html'} | quote_cards={args.with_text} "
        f"raw_evidence=true public_page_safe=false"
    )


if __name__ == "__main__":
    main()
