#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Generate a fully synthetic WeRead dataset for template smoke tests and demos."""
from __future__ import annotations

import argparse
import datetime as dt
import json
from pathlib import Path

UTC = dt.timezone.utc


def ts(year: int, month: int, day: int, hour: int = 12) -> int:
    return int(dt.datetime(year, month, day, hour, tzinfo=UTC).timestamp())


def write_json(root: Path, name: str, value) -> None:
    (root / name).write_text(json.dumps(value, ensure_ascii=False, indent=2), encoding="utf-8")


def build_demo(root: Path) -> None:
    root.mkdir(parents=True, exist_ok=True)

    books = [
        {"bookId": "demo-history", "title": "示例书·时间的纹理", "author": "示例作者甲", "category": "历史", "secret": 0, "readUpdateTime": ts(2026, 8, 15), "cover": ""},
        {"bookId": "demo-psy", "title": "示例书·心智地图", "author": "示例作者乙", "category": "心理学", "secret": 0, "readUpdateTime": ts(2026, 9, 1), "cover": ""},
        {"bookId": "demo-lit", "title": "示例书·夜航札记", "author": "示例作者丙", "category": "文学", "secret": 0, "readUpdateTime": ts(2025, 12, 21), "cover": ""},
        {"bookId": "demo-science", "title": "示例书·复杂世界", "author": "示例作者甲", "category": "科学", "secret": 0, "readUpdateTime": ts(2024, 7, 9), "cover": ""},
        {"bookId": "demo-design", "title": "示例书·看见结构", "author": "示例作者丁", "category": "设计", "secret": 0, "readUpdateTime": ts(2026, 6, 2), "cover": ""},
        {"bookId": "demo-secret", "title": "示例私密书", "author": "示例作者戊", "category": "私人收藏", "secret": 1, "readUpdateTime": ts(2026, 9, 8), "cover": ""},
    ]
    write_json(root, "weread_shelf.json", {"books": books})

    notebooks = [
        {"bookId": "demo-history", "book": books[0], "noteCount": 3, "reviewCount": 1, "readingProgress": 100},
        {"bookId": "demo-psy", "book": books[1], "noteCount": 4, "reviewCount": 2, "readingProgress": 72},
        {"bookId": "demo-lit", "book": books[2], "noteCount": 2, "reviewCount": 1, "readingProgress": 48},
        {"bookId": "demo-science", "book": books[3], "noteCount": 2, "reviewCount": 0, "readingProgress": 34},
        {"bookId": "demo-secret", "book": books[5], "noteCount": 1, "reviewCount": 1, "readingProgress": 21},
    ]
    write_json(root, "weread_notebooks.json", notebooks)

    notes = [
        {
            "bookId": "demo-history", "title": books[0]["title"], "author": books[0]["author"],
            "marks": [
                {"bookmarkId": "h1", "text": "示例划线：历史并不是静止的目录，而是持续被重新解释的证据链。", "chapter": "第一章", "createTime": ts(2024, 3, 4)},
                {"bookmarkId": "h2", "text": "示例划线：比较不同年代的问题意识，比只记住结论更重要。", "chapter": "第二章", "createTime": ts(2024, 5, 11)},
                {"bookmarkId": "h3", "text": "示例划线：阅读记录可以成为后来判断变化的时间坐标。", "chapter": "第三章", "createTime": ts(2025, 1, 7)},
            ],
            "reviews": [{"content": "示例想法：我开始把时间线当作问题变化线来读。", "createTime": ts(2025, 1, 8)}],
        },
        {
            "bookId": "demo-psy", "title": books[1]["title"], "author": books[1]["author"],
            "marks": [
                {"bookmarkId": "p1", "text": "示例划线：一个解释模型的价值，在于它能否提出可检验的新问题。", "chapter": "模型", "createTime": ts(2025, 9, 2)},
                {"bookmarkId": "p2", "text": "示例划线：区分观察、解释与推断，可以减少把印象当作事实。", "chapter": "证据", "createTime": ts(2026, 2, 16)},
                {"bookmarkId": "p3", "text": "示例划线：改变观点并不等于前后矛盾，关键在于新增了什么证据。", "chapter": "更新", "createTime": ts(2026, 4, 6)},
                {"bookmarkId": "p4", "text": "示例划线：把模糊感受转成可以比较的维度，讨论才真正开始。", "chapter": "测量", "createTime": ts(2026, 8, 28)},
            ],
            "reviews": [
                {"content": "示例想法：我要把证据和解释分开记录。", "createTime": ts(2026, 4, 7)},
                {"content": "示例想法：同一问题可以保留多个竞争解释。", "createTime": ts(2026, 8, 29)},
            ],
        },
        {
            "bookId": "demo-lit", "title": books[2]["title"], "author": books[2]["author"],
            "marks": [
                {"bookmarkId": "l1", "text": "示例划线：有些夜晚并不提供答案，只让问题的轮廓变得更清楚。", "chapter": "夜", "createTime": ts(2025, 11, 3)},
                {"bookmarkId": "l2", "text": "示例划线：叙事让同一个事实拥有了时间、视角和重量。", "chapter": "航线", "createTime": ts(2025, 12, 11)},
            ],
            "reviews": [{"content": "示例想法：文学的作用也许是改变我注意什么。", "createTime": ts(2025, 12, 12)}],
        },
        {
            "bookId": "demo-science", "title": books[3]["title"], "author": books[3]["author"],
            "marks": [
                {"bookmarkId": "s1", "text": "示例划线：复杂系统里，局部最优并不保证整体结果更好。", "chapter": "系统", "createTime": ts(2024, 7, 10)},
                {"bookmarkId": "s2", "text": "示例划线：反馈回路比单向因果更接近很多真实问题的结构。", "chapter": "反馈", "createTime": ts(2024, 7, 12)},
            ],
            "reviews": [],
        },
        {
            "bookId": "demo-secret", "title": books[5]["title"], "author": books[5]["author"],
            "marks": [{"bookmarkId": "x1", "text": "示例私密划线：这只是用于验证 secret=1 模式的合成文本。", "chapter": "私密", "createTime": ts(2026, 9, 8)}],
            "reviews": [{"content": "示例私密想法：模板测试不包含任何真实个人数据。", "createTime": ts(2026, 9, 9)}],
        },
    ]
    write_json(root, "weread_notes_export.json", notes)

    monthly_points = [
        (2024, 3, 4, 2400), (2024, 5, 11, 3600), (2024, 7, 10, 4200),
        (2025, 1, 7, 3000), (2025, 9, 2, 5400), (2025, 11, 3, 4800), (2025, 12, 11, 6000),
        (2026, 2, 16, 5100), (2026, 4, 6, 5700), (2026, 6, 2, 3300), (2026, 8, 28, 6900), (2026, 9, 8, 2700),
    ]
    monthly = {}
    annual_daily: dict[str, dict[str, int]] = {}
    for year, month, day, seconds in monthly_points:
        raw = str(ts(year, month, day))
        key = f"{year:04d}-{month:02d}"
        payload = monthly.setdefault(key, {"totalReadTime": 0, "readTimes": {}})
        payload["totalReadTime"] += seconds
        payload["readTimes"][raw] = seconds
        annual_daily.setdefault(str(year), {})[raw] = seconds

    annually = {}
    for year, daily in annual_daily.items():
        annually[year] = {
            "dailyReadTimes": daily,
            "totalReadTime": sum(daily.values()),
            "readDays": len(daily),
        }

    total_seconds = sum(seconds for *_, seconds in monthly_points)
    write_json(root, "weread_readdata.json", {
        "overall": {
            "readTimes": {"reading": total_seconds},
            "readDays": len(monthly_points),
            "preferTime": [0, 0, 0, 0, 0, 0, 180, 240, 420, 360, 120, 90, 60, 80, 100, 160, 260, 420, 660, 780, 540, 360, 220, 140],
            "readLongest": [
                {"book": books[1], "readTime": 14400},
                {"book": books[0], "readTime": 12600},
                {"book": books[2], "readTime": 10800},
            ],
        },
        "monthly": monthly,
        "annually": annually,
    })

    write_json(root, "weread_progress.json", {
        "demo-history": {"progress": 100},
        "demo-psy": {"progress": 72},
        "demo-lit": {"progress": 48},
        "demo-science": {"progress": 34},
        "demo-design": {"progress": 0},
        "demo-secret": {"progress": 21},
    })
    write_json(root, "weread_bookinfo.json", {
        row["bookId"]: {"bookId": row["bookId"], "title": row["title"], "author": row["author"], "category": row["category"], "publisher": "示例出版社"}
        for row in books
    })


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    build_demo(args.output.expanduser().resolve())
    print(args.output.expanduser().resolve())


if __name__ == "__main__":
    main()
