#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""微信读书数据增强抓取：readdata/detail + getprogress + info。
复用 export_notes.py 的调用/重试/落盘模式。后台运行，带进度日志。
"""
import json, os, sys, time, datetime, urllib.request, urllib.error

BASE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(BASE)                        # 项目根目录
DATA = os.path.join(ROOT, "data")                   # 数据统一放在 data/
KEY = os.environ.get("WEREAD_API_KEY")
URL = "https://i.weread.qq.com/api/agent/gateway"
SV = "1.0.4"
OUT_READ = os.path.join(DATA, "weread_readdata.json")
OUT_PROG = os.path.join(DATA, "weread_progress.json")
OUT_INFO = os.path.join(DATA, "weread_bookinfo.json")
LOG = os.path.join(DATA, "enrich_progress.log")

NOTES = os.path.join(DATA, "weread_notes_export.json")
SHELF = os.path.join(DATA, "weread_shelf.json")

def log(msg):
    ts = datetime.datetime.now().strftime("%H:%M:%S")
    line = f"[{ts}] {msg}"
    print(line, flush=True)
    with open(LOG, "a", encoding="utf-8") as f:
        f.write(line + "\n")

def call(body, retries=5):
    last = None
    for i in range(retries):
        try:
            req = urllib.request.Request(URL, data=json.dumps(body).encode(),
                headers={"Authorization": f"Bearer {KEY}", "Content-Type": "application/json"}, method="POST")
            with urllib.request.urlopen(req, timeout=30) as r:
                data = json.loads(r.read().decode())
            if data.get("upgrade_info"):
                log(f"  !! 需要升级 skill: {data['upgrade_info']}")
            if data.get("errcode", 0) != 0:
                last = data.get("errmsg")
                log(f"  errcode={data.get('errcode')} {last}, retry {i+1}")
                time.sleep(1.5)
                continue
            return data
        except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError, ConnectionError) as e:
            last = str(e)
            log(f"  network err: {last[:80]}, retry {i+1}")
            time.sleep(2)
    log(f"  FAILED after retries: {body.get('api_name')} {last}")
    return None

# ---------- 1. readdata/detail ----------
def fetch_readdata():
    log("=== 抓取 readdata/detail ===")
    result = {"overall": None, "annually": {}, "monthly": {}}

    # overall
    d = call({"api_name": "/readdata/detail", "skill_version": SV, "mode": "overall"})
    if d: result["overall"] = d
    log("  overall done: totalReadTime=%s readDays=%s" % (
        d.get("totalReadTime") if d else None, d.get("readDays") if d else None))
    time.sleep(0.2)

    # annually per year 2023..2026
    for y in range(2023, 2027):
        bt = int(datetime.datetime(y, 6, 1).timestamp())
        d = call({"api_name": "/readdata/detail", "skill_version": SV, "mode": "annually", "baseTime": bt})
        if d: result["annually"][str(y)] = d
        t = d.get("totalReadTime") if d else None
        log(f"  annually {y}: totalReadTime={t} readDays={d.get('readDays') if d else None}")
        time.sleep(0.2)

    # monthly per month 2023-01 .. 2026-08
    ym_list = []
    y, m = 2023, 1
    while (y, m) <= (2026, 8):
        ym_list.append((y, m))
        m += 1
        if m > 12:
            m = 1; y += 1
    for (y, m) in ym_list:
        bt = int(datetime.datetime(y, m, 1).timestamp())
        d = call({"api_name": "/readdata/detail", "skill_version": SV, "mode": "monthly", "baseTime": bt})
        if d: result["monthly"][f"{y}-{m:02d}"] = d
        time.sleep(0.12)
    log(f"  monthly done: {len(result['monthly'])} months")

    json.dump(result, open(OUT_READ, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    log(f"  saved -> {OUT_READ}")
    return result

# ---------- 2/3. getprogress + info per book ----------
def load_bookids():
    books = json.load(open(NOTES, encoding="utf-8"))
    ids = [b["bookId"] for b in books if b.get("bookId")]
    log(f"笔记书总数: {len(ids)}")
    return ids

def fetch_per_book(ids):
    progress = {}
    info = {}
    total = len(ids)
    for i, bid in enumerate(ids, 1):
        # getprogress
        d = call({"api_name": "/book/getprogress", "bookId": bid, "skill_version": SV})
        if d and d.get("book"):
            bk = d["book"]
            progress[bid] = {
                "progress": bk.get("progress"),
                "recordReadingTime": bk.get("recordReadingTime"),
                "finishTime": bk.get("finishTime"),
                "updateTime": bk.get("updateTime"),
                "isStartReading": bk.get("isStartReading"),
            }
        # info
        di = call({"api_name": "/book/info", "bookId": bid, "skill_version": SV})
        if di:
            info[bid] = {
                "publishTime": di.get("publishTime"),
                "wordCount": di.get("wordCount"),
                "publisher": di.get("publisher"),
                "newRating": di.get("newRating"),
                "newRatingCount": di.get("newRatingCount"),
                "translator": di.get("translator"),
                "category": di.get("category"),
                "intro": (di.get("intro") or "")[:200],
            }
        time.sleep(0.12)
        if i % 40 == 0 or i == total:
            json.dump(progress, open(OUT_PROG, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
            json.dump(info, open(OUT_INFO, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
            log(f"  进度 {i}/{total}  进度书={len(progress)} info书={len(info)}")
    json.dump(progress, open(OUT_PROG, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    json.dump(info, open(OUT_INFO, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    log(f"=== 抓取完成: progress={len(progress)} info={len(info)} ===")

if __name__ == "__main__":
    if not KEY:
        log("ERROR: WEREAD_API_KEY 未设置"); sys.exit(1)
    # 清日志
    open(LOG, "w", encoding="utf-8").close()
    ids = load_bookids()
    fetch_readdata()
    fetch_per_book(ids)
    log("ALL DONE")
