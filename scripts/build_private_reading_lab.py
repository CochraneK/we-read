#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Build the local/private WeRead Reading Lab.

This is the integration entry point for the user's original highlight-card work
and the newer evidence-first WeRead Intelligence modules. It intentionally writes
outside `site/` so raw evidence can never be published by the Pages workflow.
"""
from __future__ import annotations

from datetime import date
from pathlib import Path
import argparse
import html
import json
import os
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
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


def render_index(out_dir: Path, *, with_text: bool, topic: str, book_id: str) -> str:
    items = [
        ("Advisor Context", "advisor_context.json", "真读/浅尝/隐藏深读/最近活动与推荐证据底座"),
        ("Blindspot Context", "blindspot_context.json", "阅读集中度、投入落差与反向阅读证据"),
        ("Recall Queue", "recall_queue.json", "旧证据重新激活与费曼式回顾候选"),
        ("Deep Notes Context", "deep_notes_context.json", "重复划线、章节位置、划线↔想法错位、想法密度"),
        ("Narrative Review Context", "narrative_review_context.json", "周期事实包、完成/在读/浅尝/重读与叙事候选"),
    ]
    if with_text:
        items.insert(0, ("划线卡片", "quote_cards.html", "从个人划线筛选、去重、三主题卡片化；可搜索/翻转/打印"))
        items.append(("金句库", "quotes/金句库_top60.md", "划线金句候选 Top 60；仅个人学习/复核"))
        if topic:
            items.append((f"Alchemy · {topic}", "alchemy_topic_context.json", "跨书主题证据包；marks 与 reviews 明确分离"))
        if book_id:
            items.append(("Alchemy · 单书", "alchemy_book_context.json", "单书章节级划线/想法证据包"))
    cards = "".join(
        f'<a class="item" href="{html.escape(path, quote=True)}"><strong>{html.escape(name)}</strong><span>{html.escape(desc)}</span></a>'
        for name, path, desc in items
    )
    return f'''<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="robots" content="noindex,nofollow,noarchive"><title>WeRead Private Reading Lab</title><style>
:root{{--bg:#f4f0e8;--paper:#fffdf8;--ink:#292621;--muted:#756e65;--line:#ded6ca;--accent:#a9523c}}*{{box-sizing:border-box}}body{{margin:0;background:var(--bg);color:var(--ink);font-family:Inter,"PingFang SC",sans-serif}}main{{max-width:980px;margin:auto;padding:48px 24px}}h1{{font-family:"Songti SC",serif;font-size:38px;margin:0 0 8px}}p{{color:var(--muted);line-height:1.8}}.warning{{border:1px dashed var(--line);padding:14px;border-radius:14px;margin:22px 0}}.grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(260px,1fr));gap:14px}}.item{{display:flex;flex-direction:column;gap:8px;background:var(--paper);border:1px solid var(--line);border-radius:16px;padding:18px;text-decoration:none;color:var(--ink)}}.item:hover{{border-color:var(--accent)}}.item strong{{font-size:17px}}.item span{{color:var(--muted);font-size:13px;line-height:1.6}}code{{background:var(--paper);padding:2px 5px;border-radius:5px}}</style></head><body><main><h1>WeRead Private Reading Lab</h1><p>把最初的划线卡片、深度笔记分析，与 Search / Recall / Blindspot / Advisor / Alchemy / Review 统一到一个本地入口。</p><div class="warning"><strong>隐私边界：</strong>此目录可能包含原始划线和本人想法，只用于本地阅读研究。它不属于 <code>site/</code>，不得接入公开 Pages artifact。</div><section class="grid">{cards}</section></main></body></html>'''


def parse_args():
    today = date.today()
    parser = argparse.ArgumentParser(description="Build the local/private WeRead Reading Lab.")
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUT)
    parser.add_argument("--include-private", action="store_true", help="Include secret=1 books in the unified context. Off by default.")
    parser.add_argument("--with-text", action="store_true", help="Also build raw-text private assets: quote library/cards and optional Alchemy contexts.")
    parser.add_argument("--topic", default="", help="Optional Alchemy topic; requires --with-text.")
    parser.add_argument("--book-id", default="", help="Optional single-book Alchemy context; requires --with-text.")
    parser.add_argument("--review-start", default=f"{today.year}-01-01")
    parser.add_argument("--review-end", default=today.isoformat())
    parser.add_argument("--review-platform", choices=["", "朋友圈", "公众号", "小红书", "视频脚本", "个人日记"], default="")
    return parser.parse_args()


def main():
    args = parse_args()
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
        write_private_text_assets(out_dir, context_path)
    index = render_index(out_dir, with_text=args.with_text, topic=args.topic.strip(), book_id=args.book_id.strip())
    (out_dir / "index.html").write_text(index, encoding="utf-8")
    manifest = {
        "version": 1,
        "private": True,
        "publicPageSafe": False,
        "outputDir": str(out_dir),
        "includePrivateBooks": bool(args.include_private),
        "includesRawTextAssets": bool(args.with_text),
        "topicAlchemy": args.topic.strip() or None,
        "bookAlchemy": args.book_id.strip() or None,
        "entry": "index.html",
    }
    (out_dir / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"private-reading-lab: {out_dir / 'index.html'} | raw_text={args.with_text} public_page_safe=false")


if __name__ == "__main__":
    main()
