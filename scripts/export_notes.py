#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
微信读书 - 全量笔记/划线导出
- 先拉 /user/notebooks 拿到所有有笔记的书
- 对每本书调 /book/bookmarklist（划线）+ /review/list/mine（想法/点评，含翻页）
- 产出 weread_notes_export.json（完整结构化）+ weread_notes_export.md（按书/章节分组的可读版）
- 带重试、进度日志、每 20 本落盘一次（断点保护）
"""
import json, urllib.request, os, time, datetime, sys

KEY = os.environ["WEREAD_API_KEY"]
URL = "https://i.weread.qq.com/api/agent/gateway"
SV = "1.0.4"
BASE = r"D:/workbuddy/微信读书"
DATA = os.path.join(BASE, "data")                 # 数据统一放在 data/
NB_PATH = os.path.join(DATA, "weread_notebooks.json")
JSON_PATH = os.path.join(DATA, "weread_notes_export.json")
MD_PATH = os.path.join(DATA, "weread_notes_export.md")
LOG_PATH = os.path.join(DATA, "export_progress.log")

def log(msg):
    ts = datetime.datetime.now().strftime("%H:%M:%S")
    line = f"[{ts}] {msg}"
    print(line, flush=True)
    with open(LOG_PATH, "a", encoding="utf-8") as f:
        f.write(line + "\n")

def call(body, tries=3):
    last = None
    for i in range(tries):
        try:
            req = urllib.request.Request(URL, data=json.dumps(body).encode(),
                headers={"Authorization": f"Bearer {KEY}", "Content-Type": "application/json"}, method="POST")
            with urllib.request.urlopen(req, timeout=30) as r:
                return json.load(r)
        except Exception as e:
            last = e
            time.sleep(1.0 + i)
    raise last

def fetch_notebooks():
    if os.path.exists(NB_PATH):
        log("复用已拉取的 notebooks 列表")
        return json.load(open(NB_PATH, encoding="utf-8"))
    books = []
    last = None
    while True:
        b = {"api_name": "/user/notebooks", "count": 100, "skill_version": SV}
        if last is not None:
            b["lastSort"] = last
        d = call(b)
        if "upgrade_info" in d:
            log(f"需要升级: {d['upgrade_info']}")
            raise SystemExit("UPGRADE_REQUIRED")
        page = d.get("books", [])
        books += page
        if d.get("hasMore") != 1 or not page:
            break
        last = page[-1].get("sort")
    json.dump(books, open(NB_PATH, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    log(f"notebooks 拉取完成: {len(books)} 本")
    return books

def chapter_map(chapters):
    return {c.get("chapterUid"): c.get("title", "") for c in (chapters or [])}

def export_book(bk):
    bid = bk.get("bookId") or (bk.get("book") or {}).get("bookId")
    title = (bk.get("book") or {}).get("title", "?")
    author = (bk.get("book") or {}).get("author", "")
    out = {"bookId": bid, "title": title, "author": author,
           "noteCount": bk.get("noteCount", 0), "reviewCount": bk.get("reviewCount", 0),
           "bookmarkCount": bk.get("bookmarkCount", 0),
           "marks": [], "reviews": []}
    # 划线
    try:
        d = call({"api_name": "/book/bookmarklist", "bookId": bid, "skill_version": SV})
        chs = chapter_map(d.get("chapters"))
        for m in (d.get("updated") or []):
            out["marks"].append({
                "chapter": chs.get(m.get("chapterUid"), ""),
                "text": m.get("markText", ""),
                "createTime": m.get("createTime", 0),
            })
    except Exception as e:
        log(f"  ! 划线失败 {title}: {e}")
    # 想法/点评（翻页）
    try:
        synckey = 0
        while True:
            d = call({"api_name": "/review/list/mine", "bookid": bid, "count": 500,
                      "synckey": synckey, "skill_version": SV})
            for rv in (d.get("reviews") or []):
                r = rv.get("review", {}) if isinstance(rv, dict) else {}
                out["reviews"].append({
                    "chapter": r.get("chapterName", "") or "",
                    "abstract": r.get("abstract", ""),
                    "content": r.get("content", ""),
                    "createTime": r.get("createTime", 0),
                    "star": r.get("star", -1),
                })
            if d.get("hasMore") != 1:
                break
            nk = d.get("synckey")
            if not nk or nk == synckey:
                break
            synckey = nk
    except Exception as e:
        log(f"  ! 想法失败 {title}: {e}")
    return out

def main():
    log("=== 开始全量导出 ===")
    books = fetch_notebooks()
    results = []
    done = 0
    for i, bk in enumerate(books, 1):
        try:
            res = export_book(bk)
            results.append(res)
            done += 1
            if i % 20 == 0:
                json.dump(results, open(JSON_PATH, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
                log(f"进度 {i}/{len(books)} 已落盘 (本本笔记 {len(res['marks'])} 想法 {len(res['reviews'])})")
        except Exception as e:
            log(f"  !! 整本失败跳过 {bk.get('book',{}).get('title','?')}: {e}")
        time.sleep(0.12)
    # 最终 JSON
    json.dump(results, open(JSON_PATH, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    total_marks = sum(len(r["marks"]) for r in results)
    total_reviews = sum(len(r["reviews"]) for r in results)
    log(f"全部完成: {len(results)} 本 / 划线 {total_marks} / 想法点评 {total_reviews}")
    # 生成 Markdown
    build_md(results, total_marks, total_reviews, len(results))
    log("Markdown 生成完毕")

def build_md(results, total_marks, total_reviews, nbooks):
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    L = []
    L.append(f"# 微信读书 全量笔记/划线导出\n")
    L.append(f"> 导出时间：{now}　|　含笔记的书：**{nbooks}** 本　|　划线：**{total_marks}** 条　|　想法/点评：**{total_reviews}** 条\n")
    L.append("\n---\n")
    for r in results:
        L.append(f"\n## {r['title']}　*{r['author']}*\n")
        L.append(f"- 划线 {len(r['marks'])} 条 · 想法/点评 {len(r['reviews'])} 条 · 书签 {r['bookmarkCount']} 个（书签仅计数，不可导出内容）\n")
        if r["marks"]:
            L.append("\n### 划线\n")
            for m in r["marks"]:
                ch = f"〔{m['chapter']}〕 " if m["chapter"] else ""
                L.append(f"> {ch}{m['text']}\n")
        if r["reviews"]:
            L.append("\n### 想法 / 点评\n")
            for rv in r["reviews"]:
                ch = f"〔{rv['chapter']}〕 " if rv["chapter"] else ""
                if rv["abstract"]:
                    L.append(f"- {ch}原文：_{rv['abstract']}_")
                    L.append(f"  - 想法：{rv['content']}\n")
                else:
                    L.append(f"- {ch}{rv['content']}\n")
    open(MD_PATH, "w", encoding="utf-8").write("".join(L))
    log(f"MD 写入: {MD_PATH}")

if __name__ == "__main__":
    main()
