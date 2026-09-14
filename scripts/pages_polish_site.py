#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Final presentation polish for the assembled WeRead Pages artifact.

This layer changes presentation only:
- groups annual summary / seasonality / focus migration into one compact row;
- removes empty official-preference placeholders and empty cover blocks;
- shortens display-only trailing edition/adaptation parentheticals in Reading Top.
"""
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / "site"

CSS = r'''
.annual-overview-cluster{grid-column:1/-1;display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:16px;align-items:stretch}.annual-overview-cluster>.card{grid-column:auto!important;min-width:0;height:100%}.annual-overview-cluster #annual-summary .table th,.annual-overview-cluster #annual-summary .table td{padding:8px 6px;font-size:11px}.annual-overview-cluster #season .season-grid{grid-template-columns:repeat(6,1fr);gap:5px;row-gap:11px;min-height:150px}.annual-overview-cluster #season .rhythm-bar-wrap{height:72px}.annual-overview-cluster #season .rhythm-label,.annual-overview-cluster #season .rhythm-value{font-size:9px}.annual-overview-cluster #focus .focus-list{gap:5px}.annual-overview-cluster #focus .focus-row{grid-template-columns:48px 1fr;gap:8px;padding:7px 0}.annual-overview-cluster #focus .focus-year{font-size:16px}.annual-overview-cluster #focus .chips{gap:5px}.annual-overview-cluster #focus .chip{padding:4px 6px;font-size:9px}.pref-book.no-cover,.year-book-card.no-cover{padding-top:13px}.pref-book.no-cover .pref-book-cover,.year-book-card.no-cover .year-book-cover{display:none}.pref-book-grid.is-empty,.year-book-strip.is-empty{display:none!important}
@media(max-width:980px){.annual-overview-cluster{grid-template-columns:1fr}.annual-overview-cluster #season .season-grid{grid-template-columns:repeat(12,1fr)}.annual-overview-cluster #season .rhythm-bar-wrap{height:92px}}
@media(max-width:560px){.annual-overview-cluster #season .season-grid{grid-template-columns:repeat(6,1fr)}}
'''

JS = r'''
(()=>{
  const annual=document.getElementById('annual-summary'),season=document.getElementById('season'),focus=document.getElementById('focus'),heatmap=document.getElementById('heatmap');
  if(annual&&season&&focus&&heatmap&&!document.getElementById('annual-overview-cluster')){
    const cluster=document.createElement('div');cluster.id='annual-overview-cluster';cluster.className='annual-overview-cluster';
    heatmap.insertAdjacentElement('afterend',cluster);[annual,season,focus].forEach(card=>cluster.appendChild(card));
  }

  function cleanTopTitle(raw){let s=String(raw||'').trim(),prev='';const tail=/\s*(?:（[^（）]{1,60}）|\([^()]{1,60}\)|【[^【】]{1,60}】|\[[^\[\]]{1,60}\])\s*$/;while(s&&s!==prev){prev=s;s=s.replace(tail,'').trim()}return s||String(raw||'').trim()}
  document.querySelectorAll('#longest tr td:first-child').forEach(td=>{const full=td.textContent.trim(),short=cleanTopTitle(full);if(short&&short!==full){td.title=full;td.textContent=short}});

  function cleanPreferenceGrid(id,cardSelector,titleSelector){const grid=document.getElementById(id);if(!grid)return;const cards=[...grid.querySelectorAll(cardSelector)];cards.forEach(card=>{const title=card.querySelector(titleSelector)?.textContent?.trim()||'';if(!title||title==='—'||title==='未命名'){card.remove();return}const cover=card.querySelector('.pref-book-cover,.year-book-cover');if(cover&&!cover.querySelector('img'))card.classList.add('no-cover')});const valid=grid.querySelectorAll(cardSelector).length>0;grid.classList.toggle('is-empty',!valid);const head=grid.previousElementSibling;if(head?.classList?.contains('title'))head.style.display=valid?'':'none';if(!valid&&grid.textContent.trim())grid.textContent=''}
  const cleanOfficial=()=>cleanPreferenceGrid('preferBooks','.pref-book','b');
  const cleanYear=()=>cleanPreferenceGrid('yearBooks','.year-book-card','b');
  cleanOfficial();cleanYear();
  const officialGrid=document.getElementById('preferBooks'),yearGrid=document.getElementById('yearBooks');
  if(officialGrid)new MutationObserver(()=>cleanOfficial()).observe(officialGrid,{childList:true,subtree:true});
  if(yearGrid)new MutationObserver(()=>cleanYear()).observe(yearGrid,{childList:true,subtree:true});
})();
'''


def polish(site_dir: Path = SITE) -> None:
    path = site_dir / "index.html"
    if not path.exists():
        raise SystemExit(f"ERROR: missing {path}; build Pages first")
    page = path.read_text(encoding="utf-8")
    if "annual-overview-cluster" not in page:
        page = page.replace("</style>", CSS + "\n</style>", 1)
        page = page.replace("</script>", JS + "\n</script>", 1)
        path.write_text(page, encoding="utf-8")
    print("Pages polish: annual overview grouped, preference placeholders removed, top titles shortened")


if __name__ == "__main__":
    polish()
