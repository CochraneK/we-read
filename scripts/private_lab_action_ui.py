#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Add Private Lab action/report hub for Alchemy, Advisor, Path and Review."""
from __future__ import annotations
import html

CSS = r'''
.action-grid{display:grid;grid-template-columns:repeat(3,1fr);gap:10px}.action-card{border:1px solid var(--line);background:var(--paper2);border-radius:14px;padding:13px;text-decoration:none}.action-card strong,.action-card span{display:block}.action-card span{font-size:11px;color:var(--muted);margin-top:5px}.action-card.ready{border-color:color-mix(in srgb,var(--accent2) 55%,var(--line))}.action-card.missing{opacity:.65}.action-code{margin-top:10px;border:1px dashed var(--line);border-radius:12px;padding:10px;font-family:ui-monospace,SFMono-Regular,Menlo,monospace;font-size:10px;white-space:pre-wrap;overflow:auto;color:var(--muted)}@media(max-width:800px){.action-grid{grid-template-columns:1fr}}
'''


def augment(page: str, assets: dict[str, bool]) -> str:
    if 'id="actions"' in page:
        return page
    def card(label, path, desc, key):
        if assets.get(key):
            return f'<a class="action-card ready" href="{html.escape(path, quote=True)}"><strong>{html.escape(label)}</strong><span>{html.escape(desc)}</span></a>'
        return f'<div class="action-card missing"><strong>{html.escape(label)}</strong><span>本次未生成。{html.escape(desc)}</span></div>'
    cards = ''.join([
        card('Narrative Review','narrative_review.html','周期事实 → 平台化可编辑草稿；未知原因不会自动编造。','review'),
        card('Alchemy · 单书','alchemy_book.html','章节证据 → 启发式议题聚类 → 来源/我的想法对照。','alchemyBook'),
        card('Alchemy · 跨主题','alchemy_topic.html','跨书证据景观；证据过大时会先触发 scope gate。','alchemyTopic'),
        card('Advisor shortlist','advisor.html','实时微信读书目录核验后的候选；语义缺口仍保留 gate。','advisor'),
        card('Reading Path 候选池','reading_path_discovery.html','入门/框架/前沿三阶段发现池，阶段只是候选。','pathDiscovery'),
        card('Reading Path 最终计划','reading_path.html','仅在阶段确认 + 实时核验 + 每阶段候选足够时生成。','pathPlan'),
    ])
    command = '''# 周期复盘成稿\npython scripts/build_private_reading_lab.py --include-private --review-platform 公众号\n\n# 实时 Advisor 候选（需要 WEREAD_API_KEY）\npython scripts/build_private_reading_lab.py --include-private --advisor-query "主题"\n\n# Path 候选池\npython scripts/build_private_reading_lab.py --include-private --path-topic "主题"'''
    section = f'''<section class="panel" id="actions" style="margin-top:14px"><div class="section-head"><div><h2>Knowledge Actions</h2><p>从“看数据”进入“复盘 / 重新理解 / 找下一本 / 构建路径”。实时目录动作需要本地 <code>WEREAD_API_KEY</code>。</p></div></div><div class="action-grid">{cards}</div><div class="action-code">{html.escape(command)}</div></section>'''
    page = page.replace('</style>', CSS + '\n</style>', 1)
    page = page.replace('<a href="#books">Books</a>', '<a href="#actions">Actions</a><a href="#books">Books</a>', 1)
    page = page.replace('<section class="panel" id="books"', section + '\n<section class="panel" id="books"', 1)
    return page
