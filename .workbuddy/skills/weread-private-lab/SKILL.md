---
name: weread-private-lab
description: 微信读书私人深度工作台。把早期的划线金句卡片和 16 项深分析，与当前 Search / Recall / Blindspot / Advisor / Alchemy / Narrative Review 统一到一个本地私有入口。当用户说“整理我的微信读书”“做深入分析”“把划线做成卡片”“看我的想法和划线关系”“做阅读实验室”“把之前的微信读书工作合并起来”时触发。默认不公开原始划线/想法。
---

# WeRead Private Reading Lab

## 定位

这是本仓库所有**私人阅读证据能力的总编排层**，用于解决历史上功能分散的问题。

它不替代各个专业 Skill，而是负责把它们组合到一条统一的数据链：

```text
WeRead export / enrich
        ↓
visualization_context
        ├─ Advisor Context
        ├─ Blindspot Context
        ├─ Recall Queue
        ├─ Search Index
        ├─ Deep Notes Context
        ├─ Narrative Review Context
        └─ raw-text private branch
              ├─ Quote Library
              ├─ Quote Cards
              └─ Alchemy Context
```

## 一键入口

默认只构建事实/元数据分析，不额外生成原始文本资产：

```bash
python scripts/build_private_reading_lab.py
```

需要恢复和重建最初的“划线卡片 + 原始证据炼金”工作：

```bash
python scripts/build_private_reading_lab.py --with-text
```

指定一个主题做跨书 Alchemy：

```bash
python scripts/build_private_reading_lab.py --with-text --topic "认知科学"
```

指定一本书：

```bash
python scripts/build_private_reading_lab.py --with-text --book-id "BOOK_ID"
```

完整本地档案（包含 `secret=1`）必须显式打开：

```bash
python scripts/build_private_reading_lab.py --include-private --with-text
```

输出入口：

```text
data/analysis/private_lab/index.html
```

## 早期工作如何被吸收

### 划线卡片

历史 `quote_lib/cards.html` 是一份已经生成的成品，不应再作为唯一来源。

新的可重建链路：

```text
weread_notes_export.json
    ↓ privacy filter by visualization_context
filtered_notes_private.json
    ↓
build_quote_lib.py
    ↓
quotes/金句库.json
    ↓
renderers/quote_cards.py
    ↓
quote_cards.html
```

卡片保留：

- 三套主题；
- 搜索；
- 点击/键盘翻转；
- 打印/PDF 友好；
- 书名、作者、章节、主题、分数；
- `weread://reading` 深链。

不再默认依赖在线封面，以减少外部请求和隐私暴露。

### 深入分析

旧 `scripts/analysis.py` 的 A–E 16 项 Dashboard 保留为历史参考，但不作为新工作台的数据真相层。

已经迁移/现代化的能力包括：

- 类别/投入 → metrics + Advisor + Blindspot；
- 月度/日内/年度节律 → Pages enrichment/story；
- 阅读进度 × 笔记 → Pages 深度散点；
- 累积生涯 → Pages career；
- 划线/想法结构变化 → Reading Profile / Page note evolution；
- 重复划线 → Deep Notes Context；
- 划线长度 → Deep Notes Context；
- 划线章节位置 → Deep Notes Context（明确近似口径）；
- 划线 ↔ 想法章节错位 → Deep Notes Context；
- 想法密度 / 高划线书 → Deep Notes Context。

旧 C8 词云可作为本地辅助视图，但不能当成“认知主题”的强证据；旧 C9 词典情感只能作为启发式，不能写成心理结论。

## 与其他 Skill 的关系

- `weread-search`：找原始证据；
- `weread-recall`：重新激活旧证据；
- `weread-blindspot`：找阅读结构盲点；
- `huashu-weread`：Advisor / Path / Alchemy / Review 工作流；
- `weread-book-to-skill`：单本书转可复用方法；
- `weread-obsidian`：把结果安全同步到个人知识库；
- `weread-visualization`：公开/私有可视化结果；
- `yao-weread-skill`：底层报告/数据/图表设计参考。

本 Skill 是它们的**总入口和隐私路由器**，不是重复实现。

## 隐私规则

1. `site/` 永远不是 Raw Evidence 的目标目录。
2. `data/analysis/private_lab/` 可能包含原始划线、本人想法、全文搜索索引，默认被 `.gitignore` 排除。
3. `--with-text` 是显式开关；没有它，不生成金句卡片/Alchemy 原始证据包。
4. `secret=1` 默认仍排除；只有 `--include-private` 才进入统一 context。
5. marks = 保存的原文，不代表用户观点；reviews = 用户自己的想法证据。
6. 金句评分只是启发式；公开传播/出版前必须人工复核版权。

## 深分析规则

“深入”不等于“心理化”。允许分析：

- 阅读投入结构；
- 时间节律；
- 主题/类别迁移；
- 笔记与进度关系；
- 划线长度与位置；
- 划线与本人想法的结构关系；
- 重复证据和可重新激活证据；
- 知识缺口、反证方向。

不要把这些信号直接升级为人格诊断、敏感属性判断或无证据的认知因果故事。

## 输出层级

```text
公开 Page
  聚合事实 / 非敏感元数据 / 知识结构

Private Reading Lab
  搜索 / 原始划线 / 本人想法 / 卡片 / Alchemy / 深分析

需要确认后执行
  推荐书 / Path 最终书单 / 对外 Narrative Review / 远端写操作
```

这三个层级不可混淆。
