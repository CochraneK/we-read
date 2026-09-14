---
name: weread-private-lab
description: 微信读书私人深度工作台。把早期的划线金句卡片和 16 项深分析，与当前 Search / Recall / Blindspot / Advisor / Reading Path / Alchemy / Narrative Review 统一到一个本地私有入口。当用户说“整理我的微信读书”“做深入分析”“把划线做成卡片”“看我的想法和划线关系”“做阅读实验室”“把之前的微信读书工作合并起来”时触发。默认不公开原始划线/想法。
---

# WeRead Private Reading Lab

## 定位

这是本仓库所有**私人阅读证据能力的总编排层**。它不替代各个专业 Skill，而是把它们组合成一条可重复运行、可审计、可行动的数据链：

```text
WeRead export / enrich
        ↓
visualization_context
        ├─ Evidence Search
        ├─ Deep Notes
        ├─ Recall + answer history + spaced review
        ├─ Blindspot
        ├─ Advisor Context → live catalog → semantic gate
        ├─ Reading Path Context → live catalog → semantic stage gate
        ├─ Narrative Review Context → Draft → Markdown / HTML
        └─ raw-text private branch
              ├─ Quote Library / Quote Cards
              └─ Alchemy Context → Synthesis → private report
```

## 一键入口

基础私人工作台：

```bash
python scripts/build_private_reading_lab.py
```

完整本地档案（包含 `secret=1`）+ 划线卡片：

```bash
python scripts/build_private_reading_lab.py --include-private --with-text
```

输出入口：

```text
data/analysis/private_lab/index.html
```

> 核心 Lab 即使不加 `--with-text` 也已经包含 Search / Recall 所需的原始 evidence。`--with-text` 的真实含义是：额外生成可浏览的 Quote Cards / Alchemy 成品，不是“打开隐私模式”。整个 `private_lab/` 都应视为私有目录。

## 已闭环能力

### 1. 划线卡片

```text
weread_notes_export.json
    ↓ visualization_context privacy allowlist
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

卡片支持三主题、搜索、翻转、键盘、打印/PDF、章节/主题/评分和 `weread://reading` 深链，并可回到对应 Book Workbench。

### 2. Deep Notes

`scripts/build_deep_notes_context.py` 现代化迁移旧 Dashboard 的高价值深分析：

- 重复划线；
- 划线长度；
- 章节相对位置（明确近似口径）；
- 划线 ↔ 本人想法章节关系；
- 想法密集书；
- 划线很多但本人想法较少的书。

### 3. Recall 长期记忆

Private Lab 里的 Recall 现在包含：

- stable `evidenceId`，队列重排后不会串历史；
- 先写“我现在怎么理解”，再展开旧证据；
- 忘了 / 困难 / 记住 / 很熟；
- browser-local `nextReviewAt` 间隔复习；
- 每次回答保存到 `answerHistory`；
- 当前回答 vs 当时 evidence 的**表面文字重合提示**；
- JSON 导出 / 导入。

文字重合不是语义正确率，也不是记忆强度模型；它只是帮助回看“我的解释是否发生变化”的一个弱信号。

### 4. Alchemy

```bash
python scripts/build_private_reading_lab.py --include-private --with-text --topic "认知科学"
```

或单书：

```bash
python scripts/build_private_reading_lab.py --include-private --with-text --book-id "BOOK_ID"
```

生成 Context → heuristic synthesis → 私人 HTML。marks=`source_text`，reviews=`user_thought`；证据量过大时先触发 scope gate。

### 5. Narrative Review

```bash
python scripts/build_private_reading_lab.py \
  --include-private \
  --review-start 2026-01-01 \
  --review-end 2026-09-14 \
  --review-platform 公众号
```

会生成：

```text
narrative_review_context.json
narrative_review_draft.json
narrative_review.md
narrative_review.html
```

成稿器会自动写入可验证数字、书目、峰值月份、卡住的书和主题转向候选；**不会编造“为什么转向 / 为什么弃读 / 某本书改变了我”**。未知原因保留为编辑提示。

支持：朋友圈 / 公众号 / 小红书 / 视频脚本 / 个人日记。

### 6. Advisor：目录核验 → 语义 gate

第一步发现当前微信读书实时候选：

```bash
python scripts/build_private_reading_lab.py \
  --include-private \
  --advisor-query "认知科学"
```

自动完成：

- `/store/search` 实时目录核验；
- 已深读排除；
- 已收藏未投入识别；
- shortlist；
- `advisor_semantic_editor.html`。

Semantic Editor 要求逐候选填写：

- `school_or_viewpoint`；
- `era_or_paradigm`；
- `abstraction_level`；
- `adjacent_discipline`；
- `conceptualFit`；
- 每项 evidence + confidence。

编辑器导出 JSON 后：

```bash
python scripts/build_private_reading_lab.py \
  --include-private \
  --advisor-query "认知科学" \
  --advisor-semantic-annotations /path/to/weread-semantic-advisor.json
```

只有完整语义证据通过 gate 的候选才进入 `advisor_semantic.html`。目录可用、评分高、标题相似都不等于概念上真正补缺。

### 7. Reading Path：候选池 → 语义阶段 → 6 本路径

先发现候选并生成语义编辑器：

```bash
python scripts/build_private_reading_lab.py \
  --include-private \
  --path-topic "心理学"
```

Semantic Editor 除四个语义轴外，还必须明确：

- `stage = intro | framework | frontier`；
- `stageEvidence`：为什么它承担这个学习阶段角色。

导出后：

```bash
python scripts/build_private_reading_lab.py \
  --include-private \
  --path-topic "心理学" \
  --path-semantic-annotations /path/to/weread-semantic-path.json \
  --path-confirmed-level beginner
```

随后系统会再次实时核验目录、补 `/book/info`、计算字数/时间，并在每阶段至少有 2 本合格候选时生成正式 6 本路径与最小版本。

## 与其他 Skill 的关系

- `weread-search`：找原始证据；
- `weread-recall`：重新激活旧证据；
- `weread-blindspot`：找阅读结构盲点；
- `huashu-weread`：Advisor / Path / Alchemy / Review 工作流；
- `weread-book-to-skill`：单本书转可复用方法；
- `weread-obsidian`：安全同步到个人知识库；
- `weread-visualization`：公开/私有可视化；
- `yao-weread-skill`：底层报告/数据/图表设计参考。

本 Skill 是它们的**总入口、隐私路由器和 Action Hub**。

## 隐私规则

1. `site/` 永远不是 Raw Evidence 的目标目录。
2. `data/analysis/private_lab/` 可能包含原始划线、本人想法、全文搜索索引，默认被 `.gitignore` 排除。
3. `secret=1` 默认排除；只有 `--include-private` 才进入统一 context。
4. marks = 保存的原文，不代表用户观点；reviews = 用户自己的想法证据。
5. Recall 回答历史、Pin 等浏览器状态只在 `localStorage`，不上传网络。
6. 金句评分、文字重合、heuristic cluster 都是辅助信号，不是心理或语义定论。
7. Semantic gate 不自动填写概念标签；没有 evidence 就不晋升。
8. 金句公开传播/出版前必须人工复核版权。

## 成品验证

`build_private_reading_lab.py` 在生成最终首页后自动调用：

```bash
python scripts/validate_private_lab_output.py --html data/analysis/private_lab/index.html
```

验证包括：

- `noindex,nofollow,noarchive`；
- Private / Raw Evidence 标记；
- Search / Recall / Actions 模块；
- 禁止浏览器端 `fetch()` / XHR / WebSocket；
- 最终内联 JS `node --check`。

## 输出层级

```text
公开 Page
  聚合事实 / 非敏感元数据 / 知识结构

Private Reading Lab
  Search / 原始证据 / Quote Cards / Deep Notes / Recall / Alchemy
  Review Draft / Advisor / Reading Path / Semantic Review

需要明确人工语义或现实确认
  “为什么”类因果意义 / 概念适配 / Path 阶段角色 / 对外发布 / 远端写操作
```

这三个层级不可混淆。
