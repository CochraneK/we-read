#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Final presentation polish for the assembled WeRead Pages artifact.

This layer changes presentation only:
- keeps annual summary / seasonality / focus migration inside their original chapters;
- pairs them with nearby chapter modules so they do not sit alone on a row;
- removes empty official-preference placeholders and empty cover blocks;
- shortens display-only trailing edition/adaptation parentheticals in Reading Top;
- compacts the 24h-clock Top 3 activity display;
- keeps quote action buttons visually consistent while coloring only dice glyphs.
"""
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / "site"

CSS = r'''
/* Keep the three formerly-isolated annual views inside their original chapters. */
#annual-summary,#medals{grid-column:span 6!important}
#clock{grid-column:span 12!important}
#weekday,#season{grid-column:span 6!important}
#shift,#focus{grid-column:span 6!important}
#shift .shift-card{grid-template-columns:64px minmax(0,1fr);gap:11px;padding:12px}
#shift .shift-year{font-size:21px}
#focus .focus-list{gap:7px}
#focus .focus-row{grid-template-columns:54px 1fr;gap:9px;padding:8px 0}
#focus .focus-year{font-size:18px}
#focus .chips{gap:5px}
#focus .chip{padding:5px 7px;font-size:10px}
#annual-summary .table th,#annual-summary .table td{padding:8px 6px;font-size:11px}
#season .season-grid{grid-template-columns:repeat(6,1fr);gap:6px;row-gap:12px;min-height:158px}
#season .rhythm-bar-wrap{height:82px}
#season .rhythm-label,#season .rhythm-value{font-size:9px}
/* Compact clock peak ranking: one clear line per hour instead of stacked fragments. */
#clockPeak.clock-peak-list{display:grid;grid-template-columns:1fr;gap:7px}
#clockPeak.clock-peak-list .deep-card{min-height:0;padding:9px 11px;display:grid;grid-template-columns:28px 1fr auto;align-items:center;gap:10px;border-radius:12px}
.clock-peak-rank{width:25px;height:25px;border-radius:50%;display:grid;place-items:center;background:color-mix(in srgb,var(--accent3) 15%,var(--paper));color:var(--accent);font-size:11px;font-weight:800}
#clockPeak.clock-peak-list .deep-card b{margin:0;font-size:14px}
#clockPeak.clock-peak-list .deep-card p{margin:0;color:var(--muted);font-size:12px;font-variant-numeric:tabular-nums}
.pref-book.no-cover,.year-book-card.no-cover{padding-top:13px}.pref-book.no-cover .pref-book-cover,.year-book-card.no-cover .year-book-cover{display:none}.pref-book-grid.is-empty,.year-book-strip.is-empty{display:none!important}
@media(max-width:900px){#annual-summary,#medals,#weekday,#season,#shift,#focus{grid-column:span 12!important}#season .season-grid{grid-template-columns:repeat(12,1fr)}#season .rhythm-bar-wrap{height:92px}}
@media(max-width:560px){#season .season-grid{grid-template-columns:repeat(6,1fr)}}
'''

JS = r'''
(()=>{
  function cleanTopTitle(raw){let s=String(raw||'').trim(),prev='';const tail=/\s*(?:（[^（）]{1,60}）|\([^()]{1,60}\)|【[^【】]{1,60}】|\[[^\[\]]{1,60}\])\s*$/;while(s&&s!==prev){prev=s;s=s.replace(tail,'').trim()}return s||String(raw||'').trim()}
  document.querySelectorAll('#longest tr td:first-child').forEach(td=>{const full=td.textContent.trim(),short=cleanTopTitle(full);if(short&&short!==full){td.title=full;td.textContent=short}});

  function cleanPreferenceGrid(id,cardSelector,titleSelector){const grid=document.getElementById(id);if(!grid)return;const cards=[...grid.querySelectorAll(cardSelector)];cards.forEach(card=>{const title=card.querySelector(titleSelector)?.textContent?.trim()||'';if(!title||title==='—'||title==='未命名'){card.remove();return}const cover=card.querySelector('.pref-book-cover,.year-book-cover');if(cover&&!cover.querySelector('img'))card.classList.add('no-cover')});const valid=grid.querySelectorAll(cardSelector).length>0;grid.classList.toggle('is-empty',!valid);const head=grid.previousElementSibling;if(head?.classList?.contains('title'))head.style.display=valid?'':'none';if(!valid&&grid.textContent.trim())grid.textContent=''}
  const cleanOfficial=()=>cleanPreferenceGrid('preferBooks','.pref-book','b');
  const cleanYear=()=>cleanPreferenceGrid('yearBooks','.year-book-card','b');
  cleanOfficial();cleanYear();
  const officialGrid=document.getElementById('preferBooks'),yearGrid=document.getElementById('yearBooks');
  if(officialGrid)new MutationObserver(()=>cleanOfficial()).observe(officialGrid,{childList:true,subtree:true});
  if(yearGrid)new MutationObserver(()=>cleanYear()).observe(yearGrid,{childList:true,subtree:true});

  const peak=document.getElementById('clockPeak');
  if(peak){const cards=[...peak.querySelectorAll('.deep-card')];if(cards.length){peak.classList.add('clock-peak-list');cards.forEach((card,i)=>{const time=card.querySelector('b')?.textContent?.trim()||'—',hours=card.querySelector('p')?.textContent?.trim()||'';card.innerHTML=`<span class="clock-peak-rank">${i+1}</span><b>${time}</b><p>${hours}</p>`})}}

  const randomDice=document.querySelector('#publicQuoteRandom .dice'),resampleDice=document.querySelector('#publicQuoteResample .dice');
  if(randomDice)randomDice.textContent='⚄';
  if(resampleDice)resampleDice.textContent='⚅';
})();
'''


def polish(site_dir: Path = SITE) -> None:
    path = site_dir / "index.html"
    if not path.exists():
        raise SystemExit(f"ERROR: missing {path}; build Pages first")
    page = path.read_text(encoding="utf-8")
    marker = "clock-peak-list"
    if marker not in page:
        page = page.replace("</style>", CSS + "\n</style>", 1)
        page = page.replace("</script>", JS + "\n</script>", 1)
        path.write_text(page, encoding="utf-8")
    print("Pages polish: chapter-local annual views, clean preference cards, short top titles, compact clock peaks, dice-only color")


if __name__ == "__main__":
    polish()
