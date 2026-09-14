#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Compose the Private Reading Lab base renderer with experience modules."""
from __future__ import annotations

from pathlib import Path
import argparse
import sys

HERE = Path(__file__).resolve().parent
SCRIPTS = HERE.parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

import private_lab as base
import private_lab_recall_ui
import private_lab_action_ui


def render_final(data: dict, *, assets: dict[str, bool] | None = None) -> str:
    page = base.render(data)
    page = private_lab_recall_ui.augment(page)
    page = private_lab_action_ui.augment(page, assets or {})
    return page


def parse_args():
    parser = argparse.ArgumentParser(description="Render composed local-only WeRead Private Reading Lab.")
    parser.add_argument("--context", type=Path, default=base.LAB / "visualization_context.json")
    parser.add_argument("--deep", type=Path, default=base.LAB / "deep_notes_context.json")
    parser.add_argument("--recall", type=Path, default=base.LAB / "recall_queue.json")
    parser.add_argument("--advisor", type=Path, default=base.LAB / "advisor_context.json")
    parser.add_argument("--blindspot", type=Path, default=base.LAB / "blindspot_context.json")
    parser.add_argument("--review", type=Path, default=base.LAB / "narrative_review_context.json")
    parser.add_argument("--quote-cards", type=Path, default=base.LAB / "quote_cards.html")
    parser.add_argument("--alchemy-topic-report", type=Path, default=base.LAB / "alchemy_topic.html")
    parser.add_argument("--alchemy-book-report", type=Path, default=base.LAB / "alchemy_book.html")
    parser.add_argument("--advisor-report", type=Path, default=base.LAB / "advisor.html")
    parser.add_argument("--path-discovery-report", type=Path, default=base.LAB / "reading_path_discovery.html")
    parser.add_argument("--path-plan-report", type=Path, default=base.LAB / "reading_path.html")
    parser.add_argument("--output", type=Path, default=base.LAB / "index.html")
    return parser.parse_args()


def main():
    args = parse_args()
    context = base.read_json(args.context, {})
    if not context:
        raise SystemExit(f"ERROR: missing/invalid context: {args.context}")
    data = base.payload(
        context,
        base.read_json(args.deep, {}),
        base.read_json(args.recall, {}),
        base.read_json(args.advisor, {}),
        base.read_json(args.blindspot, {}),
        base.read_json(args.review, {}),
        quote_cards_exists=args.quote_cards.exists(),
    )
    assets = {
        "alchemyTopic": args.alchemy_topic_report.exists(),
        "alchemyBook": args.alchemy_book_report.exists(),
        "advisor": args.advisor_report.exists(),
        "pathDiscovery": args.path_discovery_report.exists(),
        "pathPlan": args.path_plan_report.exists(),
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(render_final(data, assets=assets), encoding="utf-8")
    print(
        f"private-lab-final: {args.output} | books={len(data['books'])} "
        f"evidence={len(data['evidence'])} recall={len((data['recall'] or {}).get('items') or [])} "
        f"actions={sum(1 for x in assets.values() if x)} private=true"
    )


if __name__ == "__main__":
    main()
