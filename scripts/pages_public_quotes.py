#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Publish a bounded rotating sample of short WeRead highlight excerpts.

Every non-empty mark enters the build-time candidate pool, but the public static
artifact contains only a small attributed sample. This distinction matters:
GitHub Pages must not ship the complete raw highlight corpus merely to hide most
of it in client-side JavaScript.

Privacy authorization and copyright/distribution boundaries are separate:

- marks/highlights only; user reviews are never published here;
- every non-empty mark can be sampled, but at most one excerpt per book per build;
- a hard character cap per excerpt;
- a hard total-card cap;
- bibliographic attribution and a WeRead deep link;
- no full long highlight bodies;
- the public browser receives only the selected sample, never the full pool.

Enable at deploy time with ``WEREAD_PAGES_INCLUDE_PUBLIC_QUOTES=1``.
Use ``WEREAD_PUBLIC_QUOTES_SEED`` to reproduce a particular sample. Without it,
the UTC date is used so scheduled daily builds rotate naturally.
"""
from __future__ import annotations

from collections import Counter
from datetime import datetime, timezone
from hashlib import sha256
from pathlib import Path
import html
import json
import os
import random
import re

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
SITE = ROOT / "site"
MAX_CHARS = 90
MAX_TOTAL = 48
MAX_PER_BOOK = 1


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
    window = text[:max_chars]
    cut = max(window.rfind(p) for p in "。！？!?；;")
    if cut >= max(18, int(max_chars * 0.55)):
        window = window[: cut + 1]
    return window.rstrip() + "…", True


def sample_seed(explicit: str | None = None) -> str:
    if explicit:
        return explicit
    env_seed = clean_text(os.environ.get("WEREAD_PUBLIC_QUOTES_SEED"))
    if env_seed:
        return env_seed
    return datetime.now(timezone.utc).strftime("%Y-%m-%d")


def seeded_random(seed: str) -> random.Random:
    digest = sha256(seed.encode("utf-8")).digest()
    return random.Random(int.from_bytes(digest[:16], "big"))


def build_public_quotes(
    data_dir: Path = DATA,
    *,
    include_private: bool = False,
    max_chars: int = MAX_CHARS,
    max_total: int = MAX_TOTAL,
    seed: str | None = None,
) -> dict:
    shelf = load_json(data_dir / "weread_shelf.json", {})
    notes = load_json(data_dir / "weread_notes_export.json", [])
    shelf_books = list((shelf or {}).get("books") or [])
    shelf_by_id = {book_id(b): b for b in shelf_books if book_id(b)}
    secret_ids = {book_id(b) for b in shelf_books if book_id(b) and int(b.get("secret") or 0) == 1}

    candidates = []
    for note_book in notes if isinstance(notes, list) else []:
        if not isinstance(note_book, dict):
            continue
        bid = book_id(note_book)
        if not bid or (not include_private and bid in secret_ids):
            continue
        meta = shelf_by_id.get(bid) or note_book
        title = clean_text(meta.get("title") or note_book.get("title") or "未命名")
        author = clean_text(meta.get("author") or note_book.get("author") or "")
        for mark in note_book.get("marks") or []:
            if not isinstance(mark, dict):
                continue
            raw = clean_text(mark.get("text"))
            if not raw:
                continue
            chapter = clean_text(mark.get("chapter"))
            excerpt, truncated = excerpt_text(raw, max_chars=max_chars)
            candidates.append({
                "bookId": bid,
                "title": title,
                "author": author,
                "chapter": chapter,
                "excerpt": excerpt,
                "truncated": bool(truncated),
                "sourceKind": "mark",
                "deepLink": f"weread://reading?bId={bid}",
            })

    chosen_seed = sample_seed(seed)
    rng = seeded_random(chosen_seed)
    order = list(range(len(candidates)))
    rng.shuffle(order)

    items = []
    per_book = Counter()
    for index in order:
        row = candidates[index]
        if per_book[row["bookId"]] >= MAX_PER_BOOK:
            continue
        items.append(row)
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
            "allNonEmptyMarksMayBeSampled": True,
            "candidateCount": len(candidates),
            "sampleSeed": chosen_seed,
            "maxCharsPerExcerpt": int(max_chars),
            "maxPerBook": MAX_PER_BOOK,
            "maxTotal": int(max_total),
            "includePrivateBooks": bool(include_private),
            "note": "Every non-empty mark enters the build-time pool; only a bounded short attributed sample is shipped in each public artifact.",
        },
        "count": len(items),
        "items": items,
    }


CSS = r'''
.public-quote-stage{position:relative;border:1px solid var(--line);border-radius:24px;min-height:270px;overflow:hidden;background:color-mix(in srgb,var(--paper) 92%,var(--bg));display:grid;place-items:center;padding:28px}.public-quote-slide{max-width:820px;width:100%;text-align:center;transition:opacity .3s ease,transform .3s ease}.public-quote-slide.is-changing{opacity:.1;transform:translateY(5px)}.public-quote-slide blockquote{font-family:ui-serif,"Songti SC","STSong",serif;font-size:clamp(20px,2.5vw,34px);line-height:1.75;margin:0 0 24px}.public-quote-slide .q-meta{color:var(--muted);font-size:12px}.public-quote-slide .q-meta b{color:var(--ink);font-size:13px}.public-quote-slide a{color:var(--accent);text-decoration:none}.public-quote-controls{display:flex;align-items:center;justify-content:center;gap:8px;flex-wrap:wrap;margin-top:12px}.public-quote-controls button{border:1px solid var(--line);background:var(--paper);color:var(--ink);border-radius:999px;padding:7px 11px;cursor:pointer}.public-quote-counter{color:var(--muted);font-size:11px;min-width:72px;text-align:center}.public-quote-policy{border-left:4px solid var(--accent3);padding-left:13px;color:var(--muted);font-size:12px;margin:0 0 16px}@media(prefers-reduced-motion:reduce){.public-quote-slide{transition:none}}@media(max-width:560px){.public-quote-stage{min-height:235px;padding:20px}.public-quote-slide blockquote{font-size:20px}}
'''

JS = r'''
(()=>{const root=document.getElementById('publicQuotePlayer');if(!root)return;let rows=[];try{rows=JSON.parse(root.dataset.quotes||'[]')}catch(_){rows=[]}if(!rows.length)return;for(let i=rows.length-1;i>0;i--){const j=Math.floor(Math.random()*(i+1));[rows[i],rows[j]]=[rows[j],rows[i]]}const slide=document.getElementById('publicQuoteSlide'),counter=document.getElementById('publicQuoteCounter'),toggle=document.getElementById('publicQuoteToggle');let index=0,timer=null,playing=true;const esc=s=>String(s??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));function paint(){const q=rows[index];slide.classList.add('is-changing');setTimeout(()=>{const meta=[q.title?`<b>《${esc(q.title)}》</b>`:'',esc(q.author||''),esc(q.chapter||'')].filter(Boolean).join(' · ');slide.innerHTML=`<blockquote>“${esc(q.excerpt||'')}”</blockquote><div class="q-meta">${meta}${q.deepLink?`<br><a href="${esc(q.deepLink)}">在微信读书打开 ↗</a>`:''}</div>`;counter.textContent=`${index+1} / ${rows.length}`;slide.classList.remove('is-changing')},120)}function next(step=1){index=(index+step+rows.length)%rows.length;paint()}function stop(){if(timer)clearInterval(timer);timer=null}function start(){stop();if(playing)timer=setInterval(()=>next(1),7000)}document.getElementById('publicQuotePrev')?.addEventListener('click',()=>{next(-1);start()});document.getElementById('publicQuoteNext')?.addEventListener('click',()=>{next(1);start()});toggle?.addEventListener('click',()=>{playing=!playing;toggle.textContent=playing?'暂停':'播放';toggle.setAttribute('aria-pressed',String(!playing));playing?start():stop()});paint();start();})();
'''


def render_section(payload: dict) -> str:
    items = payload.get("items") or []
    encoded = html.escape(json.dumps(items, ensure_ascii=False, separators=(",", ":")), quote=True)
    policy = payload.get("policy") or {}
    candidates = int(policy.get("candidateCount") or 0)
    return (
        '<article class="card wide" id="public-quotes">'
        '<div class="title"><div><div class="section-kicker">Rotating public excerpts</div><h2>我的划线 · 随机轮播</h2></div>'
        f'<small>{candidates:,} 条候选 → 本轮 {len(items)} 条</small></div>'
        '<p class="public-quote-policy">所有非空 mark 都进入构建时候选池，但公开 artifact 只包含本轮抽中的短摘录；不会把完整划线库发送到浏览器。页面内每 7 秒随机轮播，可暂停或手动切换。review 仍不公开。</p>'
        f'<div class="public-quote-stage" id="publicQuotePlayer" data-quotes="{encoded}"><div class="public-quote-slide" id="publicQuoteSlide"></div></div>'
        '<div class="public-quote-controls"><button type="button" id="publicQuotePrev">上一条</button><button type="button" id="publicQuoteToggle" aria-pressed="false">暂停</button><span class="public-quote-counter" id="publicQuoteCounter"></span><button type="button" id="publicQuoteNext">下一条</button></div>'
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
        page = page.replace("</nav>", '<a href="#public-quotes">随机划线</a></nav>', 1)
        marker = '<article class="card wide privacy">'
        section = render_section(payload)
        if marker in page:
            page = page.replace(marker, section + "\n" + marker, 1)
        else:
            page = page.replace("</main>", section + "\n</main>", 1)
        page = page.replace("</script>", JS + "\n</script>", 1)
        index_path.write_text(page, encoding="utf-8")
    return {
        "enabled": True,
        "count": payload["count"],
        "candidateCount": int((payload.get("policy") or {}).get("candidateCount") or 0),
        "sampleSeed": (payload.get("policy") or {}).get("sampleSeed"),
        "includePrivateBooks": include_private,
    }


def main() -> None:
    result = augment_site()
    print(json.dumps({"pages-public-quotes": result}, ensure_ascii=False))


if __name__ == "__main__":
    main()
