#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Build a privacy-aware GitHub Pages report from the repository's real WeRead data.

The public report intentionally excludes shelf entries marked `secret=1` and never
publishes raw highlights/reviews. It is deterministic and uses only the Python
standard library plus the shared metrics module.
"""
from __future__ import annotations

import datetime as dt
import html
import json
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
SITE = ROOT / "site"
sys.path.insert(0, str(ROOT / "scripts"))

from metrics import category_participation  # noqa: E402


def load_json(path: Path, default):
    try:
        return json.loads(path.read_text(encoding="utf-8-sig"))
    except (FileNotFoundError, json.JSONDecodeError):
        return default


def book_id(item: dict) -> str:
    return str(item.get("bookId") or (item.get("book") or {}).get("bookId") or "")


def note_count(item: dict) -> int:
    return int(item.get("noteCount") or 0) + int(item.get("reviewCount") or 0) + int(item.get("bookmarkCount") or 0)


def fmt_hours(seconds: float) -> float:
    return round(float(seconds or 0) / 3600, 1)


def safe_date(ts) -> str:
    try:
        if not ts:
            return "—"
        return dt.datetime.fromtimestamp(int(ts), tz=dt.timezone.utc).strftime("%Y-%m-%d")
    except (TypeError, ValueError, OSError):
        return "—"


def build_report() -> dict:
    shelf = load_json(DATA / "weread_shelf.json", {})
    notebooks = load_json(DATA / "weread_notebooks.json", [])
    readdata = load_json(DATA / "weread_readdata.json", {})

    shelf_books = list(shelf.get("books") or [])
    secret_ids = {book_id(b) for b in shelf_books if int(b.get("secret") or 0) == 1 and book_id(b)}
    public_shelf = [b for b in shelf_books if book_id(b) not in secret_ids]
    public_notebooks = [n for n in notebooks if book_id(n) not in secret_ids]

    cat = category_participation(public_shelf, public_notebooks)
    categories = [row for row in cat["rows"] if row["category"] != "未知"][:12]

    author_notes = Counter()
    author_books = Counter()
    for n in public_notebooks:
        book = n.get("book") or {}
        author = str(book.get("author") or "未知").strip() or "未知"
        author_notes[author] += note_count(n)
        author_books[author] += 1
    authors = [
        {"author": a, "notes": author_notes[a], "books": author_books[a]}
        for a, _ in author_notes.most_common(12)
        if a != "未知"
    ]

    overall = readdata.get("overall") or {}
    read_times = overall.get("readTimes") or {}
    total_seconds = sum(float(v or 0) for v in read_times.values())
    read_days = int(overall.get("readDays") or 0)

    monthly = []
    for month, payload in sorted((readdata.get("monthly") or {}).items()):
        monthly.append({
            "month": month,
            "hours": fmt_hours((payload or {}).get("totalReadTime") or 0),
        })

    # Note creation counts are already materialized by the legacy deterministic analysis.
    monthly_csv = DATA / "analysis" / "B5_monthly.csv"
    if monthly_csv.exists():
        note_by_month = {}
        for line in monthly_csv.read_text(encoding="utf-8-sig").splitlines()[1:]:
            if not line.strip():
                continue
            parts = line.split(",")
            if len(parts) >= 3:
                try:
                    note_by_month[parts[0]] = int(float(parts[2]))
                except ValueError:
                    pass
        for row in monthly:
            row["notes"] = note_by_month.get(row["month"], 0)
    else:
        for row in monthly:
            row["notes"] = 0

    peak = max(monthly, key=lambda x: x["hours"], default={"month": "—", "hours": 0, "notes": 0})
    active_months = sum(1 for x in monthly if x["hours"] > 0)

    longest = []
    for item in overall.get("readLongest") or []:
        book = item.get("book") or {}
        bid = str(book.get("bookId") or "")
        if bid and bid in secret_ids:
            continue
        longest.append({
            "title": book.get("title") or "未命名",
            "author": book.get("author") or "",
            "hours": fmt_hours(item.get("readTime") or 0),
        })
    longest = longest[:8]

    recent = []
    for book in sorted(public_shelf, key=lambda b: int(b.get("readUpdateTime") or 0), reverse=True):
        if not book.get("readUpdateTime"):
            continue
        recent.append({
            "title": book.get("title") or "未命名",
            "author": book.get("author") or "",
            "category": book.get("category") or "未分类",
            "cover": book.get("cover") or "",
            "date": safe_date(book.get("readUpdateTime")),
        })
        if len(recent) >= 10:
            break

    return {
        "generatedAt": dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%d %H:%M UTC"),
        "summary": {
            "publicShelfBooks": len(public_shelf),
            "privateExcluded": len(secret_ids),
            "notebookBooks": len(public_notebooks),
            "notes": sum(note_count(n) for n in public_notebooks),
            "readDays": read_days,
            "totalHours": round(total_seconds / 3600, 1),
            "activeMonths": active_months,
            "peakMonth": peak["month"],
            "peakHours": peak["hours"],
        },
        "monthly": monthly,
        "categories": categories,
        "authors": authors,
        "longest": longest,
        "recent": recent,
    }


TEMPLATE = r'''<!doctype html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="color-scheme" content="light dark">
<title>我的微信读书 · 数据报告</title>
<style>
:root{--bg:#f5f1e8;--paper:#fffdf7;--ink:#25231f;--muted:#777166;--line:#dfd7c8;--accent:#b4573f;--accent2:#708b77;--accent3:#c4953c;--shadow:0 18px 50px rgba(54,45,34,.08)}
@media(prefers-color-scheme:dark){:root{--bg:#171613;--paper:#211f1b;--ink:#f2ede4;--muted:#a8a095;--line:#3a352d;--accent:#dd7a61;--accent2:#91ab95;--accent3:#ddb25a;--shadow:none}}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--ink);font-family:ui-sans-serif,-apple-system,BlinkMacSystemFont,"Segoe UI","PingFang SC","Microsoft YaHei",sans-serif;line-height:1.55}.wrap{max-width:1180px;margin:auto;padding:44px 22px 70px}.hero{display:grid;grid-template-columns:1.5fr .7fr;gap:24px;align-items:end;margin-bottom:28px}.eyebrow{font-size:13px;letter-spacing:.18em;text-transform:uppercase;color:var(--accent);font-weight:800}.hero h1{font-family:ui-serif,"Songti SC","STSong",serif;font-size:clamp(38px,6vw,78px);line-height:1.02;margin:8px 0 14px;font-weight:650}.hero p{max-width:740px;color:var(--muted);font-size:17px}.stamp{text-align:right;color:var(--muted);font-size:13px}.grid{display:grid;grid-template-columns:repeat(12,1fr);gap:16px}.card{background:var(--paper);border:1px solid var(--line);border-radius:22px;padding:22px;box-shadow:var(--shadow)}.stat{grid-column:span 2;min-height:128px}.stat b{font-size:30px;display:block;margin-top:12px}.stat span{font-size:13px;color:var(--muted)}.wide{grid-column:span 12}.half{grid-column:span 6}.third{grid-column:span 4}.title{display:flex;justify-content:space-between;gap:12px;align-items:baseline;margin-bottom:16px}.title h2{font-size:20px;margin:0}.title small{color:var(--muted)}#hoursChart,#notesChart{width:100%;height:auto;display:block}.bars{display:grid;gap:10px}.barrow{display:grid;grid-template-columns:minmax(130px,220px) 1fr 74px;gap:12px;align-items:center;font-size:13px}.track{height:10px;border-radius:999px;background:color-mix(in srgb,var(--line) 70%,transparent);overflow:hidden}.fill{height:100%;border-radius:999px;background:var(--accent2)}.fill.notes{background:var(--accent3)}.value{text-align:right;color:var(--muted);font-variant-numeric:tabular-nums}.books{display:grid;grid-template-columns:repeat(5,1fr);gap:14px}.book{min-width:0}.cover{aspect-ratio:2/3;border-radius:12px;background:var(--line);overflow:hidden;margin-bottom:8px}.cover img{width:100%;height:100%;object-fit:cover}.book h3{font-size:13px;margin:0 0 4px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}.book p{margin:0;color:var(--muted);font-size:11px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}.table{width:100%;border-collapse:collapse}.table th,.table td{text-align:left;padding:10px 8px;border-bottom:1px solid var(--line);font-size:13px}.table th{color:var(--muted);font-weight:600}.privacy{border-left:4px solid var(--accent2)}footer{color:var(--muted);font-size:12px;margin-top:24px;text-align:center}@media(max-width:900px){.hero{grid-template-columns:1fr}.stamp{text-align:left}.stat{grid-column:span 4}.half,.third{grid-column:span 12}.books{grid-template-columns:repeat(3,1fr)}}@media(max-width:560px){.wrap{padding:28px 14px 50px}.stat{grid-column:span 6}.books{grid-template-columns:repeat(2,1fr)}.barrow{grid-template-columns:110px 1fr 58px}.card{padding:17px}}
</style>
</head>
<body>
<div class="wrap">
<section class="hero"><div><div class="eyebrow">WeRead · Personal Data Report</div><h1>我的微信读书</h1><p>这不是工具介绍，而是直接由仓库中的真实微信读书数据重新计算并生成的结果页。阅读时长、书架、笔记量、作者与类别均来自真实数据；公开页面自动排除私密书和原始划线全文。</p></div><div class="stamp" id="generated"></div></section>
<section class="grid" id="stats"></section>
<section class="grid" style="margin-top:16px">
  <article class="card wide"><div class="title"><h2>月度阅读时长</h2><small id="range"></small></div><svg id="hoursChart" viewBox="0 0 1040 310" role="img" aria-label="月度阅读时长趋势"></svg></article>
  <article class="card wide"><div class="title"><h2>月度笔记量</h2><small>笔记创建时间代理</small></div><svg id="notesChart" viewBox="0 0 1040 260" role="img" aria-label="月度笔记量"></svg></article>
  <article class="card half"><div class="title"><h2>阅读类别</h2><small>按唯一 bookId 去重</small></div><div class="bars" id="categories"></div></article>
  <article class="card half"><div class="title"><h2>笔记最多的作者</h2><small>公开书目</small></div><div class="bars" id="authors"></div></article>
  <article class="card half"><div class="title"><h2>阅读时长 Top</h2><small>官方 readLongest</small></div><table class="table"><thead><tr><th>书名</th><th>作者</th><th>小时</th></tr></thead><tbody id="longest"></tbody></table></article>
  <article class="card half"><div class="title"><h2>最近阅读</h2><small>按 readUpdateTime</small></div><div class="books" id="recent"></div></article>
  <article class="card wide privacy"><div class="title"><h2>公开边界</h2><small>privacy-aware</small></div><p id="privacyText" style="margin:0;color:var(--muted)"></p></article>
</section>
<footer>Generated from CochraneK/we-read · deterministic build · raw highlights/reviews are not published</footer>
</div>
<script>
const D=__REPORT_JSON__;
const $=id=>document.getElementById(id);
$('generated').textContent='生成于 '+D.generatedAt;
const S=D.summary;
const stats=[['累计阅读',S.totalHours+' h'],['阅读天数',S.readDays+' 天'],['公开书架',S.publicShelfBooks+' 本'],['有笔记书',S.notebookBooks+' 本'],['标注/想法',S.notes.toLocaleString()+' 条'],['峰值月份',S.peakMonth+' · '+S.peakHours+'h']];
$('stats').innerHTML=stats.map(([k,v])=>`<article class="card stat"><span>${k}</span><b>${v}</b></article>`).join('');
if(D.monthly.length){$('range').textContent=D.monthly[0].month+' → '+D.monthly[D.monthly.length-1].month+' · '+S.activeMonths+' 个活跃月';}
function esc(s){return String(s??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));}
function drawLine(svgId,key,stroke){const svg=$(svgId),data=D.monthly,W=1040,H=310,p={l:48,r:18,t:18,b:40};const max=Math.max(1,...data.map(d=>+d[key]||0));let out='';for(let i=0;i<5;i++){const y=p.t+(H-p.t-p.b)*i/4;const val=(max*(1-i/4)).toFixed(key==='hours'?0:0);out+=`<line x1="${p.l}" y1="${y}" x2="${W-p.r}" y2="${y}" stroke="var(--line)"/><text x="6" y="${y+4}" fill="var(--muted)" font-size="11">${val}</text>`;}const pts=data.map((d,i)=>{const x=p.l+(W-p.l-p.r)*(data.length===1?0:i/(data.length-1));const y=p.t+(H-p.t-p.b)*(1-(+d[key]||0)/max);return [x,y];});out+=`<polyline fill="none" stroke="${stroke}" stroke-width="3" stroke-linejoin="round" stroke-linecap="round" points="${pts.map(p=>p.join(',')).join(' ')}"/>`;pts.forEach((pt,i)=>{if(i%6===0||i===pts.length-1)out+=`<text x="${pt[0]}" y="${H-12}" text-anchor="middle" fill="var(--muted)" font-size="10">${esc(data[i].month)}</text>`;});svg.innerHTML=out;}
function drawBars(svgId,key,fill){const svg=$(svgId),data=D.monthly,W=1040,H=260,p={l:48,r:18,t:16,b:38};const max=Math.max(1,...data.map(d=>+d[key]||0));const gap=3,bw=(W-p.l-p.r)/Math.max(1,data.length);let out='';data.forEach((d,i)=>{const v=+d[key]||0,h=(H-p.t-p.b)*v/max,x=p.l+i*bw+gap/2,y=H-p.b-h;out+=`<rect x="${x}" y="${y}" width="${Math.max(1,bw-gap)}" height="${h}" rx="2" fill="${fill}"><title>${esc(d.month)} · ${v}</title></rect>`;if(i%6===0||i===data.length-1)out+=`<text x="${x+bw/2}" y="${H-12}" text-anchor="middle" fill="var(--muted)" font-size="10">${esc(d.month)}</text>`;});svg.innerHTML=out;}
drawLine('hoursChart','hours','var(--accent)');drawBars('notesChart','notes','var(--accent3)');
function barList(rows,labelKey,valueKey,unit,cls=''){const max=Math.max(1,...rows.map(r=>+r[valueKey]||0));return rows.map(r=>`<div class="barrow"><div title="${esc(r[labelKey])}">${esc(r[labelKey])}</div><div class="track"><div class="fill ${cls}" style="width:${((+r[valueKey]||0)/max*100).toFixed(1)}%"></div></div><div class="value">${(+r[valueKey]||0).toLocaleString()}${unit}</div></div>`).join('');}
$('categories').innerHTML=barList(D.categories,'category','bookCount',' 本');$('authors').innerHTML=barList(D.authors,'author','notes',' 条','notes');
$('longest').innerHTML=D.longest.map(x=>`<tr><td>${esc(x.title)}</td><td>${esc(x.author)}</td><td>${x.hours}</td></tr>`).join('');
$('recent').innerHTML=D.recent.map(x=>`<div class="book"><div class="cover">${x.cover?`<img loading="lazy" referrerpolicy="no-referrer" src="${esc(x.cover)}" alt="">`:''}</div><h3 title="${esc(x.title)}">${esc(x.title)}</h3><p>${esc(x.author||x.category)} · ${esc(x.date)}</p></div>`).join('');
$('privacyText').textContent=`公开报告已自动排除 ${S.privateExcluded} 本 secret=1 私密书，并且不发布任何原始划线、想法正文或搜索索引。页面展示的是聚合统计和公开书目信息。`;
</script>
</body></html>'''


def main() -> None:
    report = build_report()
    SITE.mkdir(parents=True, exist_ok=True)
    payload = json.dumps(report, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")
    output = TEMPLATE.replace("__REPORT_JSON__", payload)
    (SITE / "index.html").write_text(output, encoding="utf-8")
    (SITE / "report-data.json").write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Generated {SITE / 'index.html'}")
    print(json.dumps(report["summary"], ensure_ascii=False))


if __name__ == "__main__":
    main()
