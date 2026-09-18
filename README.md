<div align="center">

# we-read · WeRead Intelligence

**把“读过什么”升级为“我长期在关注什么，以及读过的知识现在能为我做什么”。**

<p>
  <img alt="Local first" src="https://img.shields.io/badge/design-local--first-6C63FF">
  <img alt="Evidence" src="https://img.shields.io/badge/analysis-evidence--traceable-2F80ED">
  <img alt="Public archive" src="https://img.shields.io/badge/product-Public%20Reading%20Archive-27AE60">
  <img alt="Private lab" src="https://img.shields.io/badge/workspace-Private%20Reading%20Lab-F2994A">
</p>

[**公开阅读档案**](https://cochranek.github.io/we-read/)

</div>

> 把微信读书从「读过什么」，变成「我在关注什么、阅读如何迁移，以及读过的知识现在能为我做什么」。

**公开个人阅读档案：** https://cochranek.github.io/we-read/

**复刻自己的版本：** [`CochraneK/we-read-template`](https://github.com/CochraneK/we-read-template) — 干净 starter、synthetic fixtures、`setup / doctor / sync`，不包含本仓个人阅读数据。

`we-read` 是一套围绕腾讯微信读书 Agent Gateway 构建的**本地优先、证据可追溯**的阅读数据、分析、检索、回顾与知识复用系统。

项目现在有两个明确成品：

```text
WeRead Intelligence
├─ Public Reading Archive
│  └─ 长期阅读档案 / 版图 / 节律 / 知识结构 / 书架探索
└─ Private Reading Lab
   └─ 原始证据 / Search / Recall / Deep Notes / Text Mining / Cards / Alchemy / Advisor / Path / Review
```

---

## 1. Public Reading Archive

GitHub Pages 直接由真实微信读书数据生成，不是产品介绍页。

当前包含：

- 七章档案：生涯 / 节律 / 投入 / 知识 / 回顾 / 书架 / 数据边界；
- 累计阅读生涯、年度章节、2023–2026 年度透镜；
- Daily Heatmap、最长连续阅读、24 小时阅读时钟、星期节律、季节性；
- 官方 `readStat`、类别 / 作者 / 出版社偏好、年度偏好书、勋章；
- 月度阅读时长、月度笔记、累计曲线；
- 进度漏斗与 coverage；
- 进度 × 笔记深度散点、时长 × 笔记散点；
- Reading Map / Knowledge Graph / Focus Shift / Reading Profile；
- Blindspot / Counter Reading；
- 高投入书、阅读时长 Top、最近阅读；
- 498 本完整书架 Explorer；
- 浏览器本地 Pin 队列与 JSON 导入/导出；
- 每日重新激活；
- sticky 章节导航、精简模式、状态恢复；
- `/` 搜书、⌘/Ctrl+K 命令面板；
- 系统 / 浅色 / 深色主题；
- 移动端、键盘、reduced-motion、长页面渲染优化。

当前 Pages workflow 显式使用：

```text
WEREAD_PAGES_INCLUDE_PRIVATE=1
```

因此公开档案包含 `secret=1` 书目的**书名、作者、类别、计数和关系**。原始划线、本人想法正文、本地全文索引不会进入 Page。

Pages 发布前还会自动验证：

- 数据契约；
- 书架数量一致性；
- raw mark/review 泄漏抽样；
- 关键 UX 模块；
- 最终内联 JS `node --check`。

---

## 2. Private Reading Lab

Private Reading Lab 是最初“划线卡片 + 深分析”与后续 WeRead Skills 的统一入口。

基础构建：

```bash
python scripts/build_private_reading_lab.py
```

完整私有档案，包含 `secret=1` 与可浏览划线卡片：

```bash
python scripts/build_private_reading_lab.py \
  --include-private \
  --with-text
```

入口：

```text
data/analysis/private_lab/index.html
```

> 整个 `private_lab/` 都是私有目录。核心 Lab 即使不加 `--with-text`，Search / Recall 也需要原始 evidence；`--with-text` 只是额外生成 Quote Cards / Alchemy 成品。

### Evidence Search

本地 SQLite 全文检索：

```bash
python scripts/build_search_index.py --rebuild
python scripts/build_search_index.py --query "自由"
python scripts/build_search_index.py --query "自由" --kind review
```

支持书名、作者、类别、章节、mark、review，并有中文 substring fallback。

### Quote Cards

早期历史 `quote_lib/cards.html` 已经现代化成可重建链路：

```text
notes export
→ privacy allowlist
→ quote scoring / dedupe
→ quote_cards.html
→ Book Workbench / Search / Recall / Alchemy
```

新版支持三主题、搜索、翻转、键盘、PDF 打印、章节/主题/评分、微信读书 deep link。

### Deep Notes

`scripts/build_deep_notes_context.py` 重新实现旧 Dashboard 中最有价值的笔记结构分析：

- 重复划线；
- 划线长度；
- 章节相对位置；
- 划线 ↔ 本人想法章节关系；
- 想法密集书；
- 划线很多但本人想法少的书。

### Text Mining Lab

Private Lab 现在默认生成零依赖的文本挖掘层：

- Source highlights 与 user-authored reviews 分离；
- TF-IDF / lexical diversity / Source-vs-Self contrastive terms；
- document co-occurrence + positive-PMI lexical communities；
- 年度词汇结构、burst、concept resurgence；
- lexical novelty / redundancy；
- exposure → expression lexical lag；
- review 中的 question / challenge / uncertainty / causal 等显式 rhetorical signals。

入口：

```text
data/analysis/private_lab/text_mining.html
```

可选本地语义层：

```bash
pip install -r requirements-text-mining.txt

python scripts/build_private_reading_lab.py \
  --include-private \
  --semantic-text \
  --embedding-model "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
```

增加 embedding clusters、NMF/LDA topic baselines、跨书 semantic nearest-neighbors、年度 corpus drift 与 Source → Self semantic candidates。Similarity 不等于赞同、因果或“认知改变”。

完整边界见 [`docs/text-mining.md`](docs/text-mining.md)。

### Recall / Feynman / Spaced Review

Recall 现在不仅是“翻答案”：

- stable `evidenceId`；
- 先写“我现在怎么理解”，再展开旧证据；
- 忘了 / 困难 / 记住 / 很熟；
- browser-local `nextReviewAt`；
- `answerHistory`；
- JSON 导入 / 导出；
- 当前回答 vs 当时 evidence 的**表面文字重合提示**。

文字重合不是语义正确率，只是帮助观察自己的解释是否变化。

### Alchemy

跨书主题：

```bash
python scripts/build_private_reading_lab.py \
  --include-private \
  --with-text \
  --topic "认知科学"
```

单书：

```bash
python scripts/build_private_reading_lab.py \
  --include-private \
  --with-text \
  --book-id "BOOK_ID"
```

链路：

```text
source_text / user_thought
→ evidence landscape
→ heuristic issue clusters
→ evidence-bounded synthesis
→ unresolved questions
→ private HTML
```

### Narrative Review

```bash
python scripts/build_private_reading_lab.py \
  --include-private \
  --review-start 2026-01-01 \
  --review-end 2026-09-14 \
  --review-platform 公众号
```

输出：

```text
narrative_review_context.json
narrative_review_draft.json
narrative_review.md
narrative_review.html
```

支持：朋友圈 / 公众号 / 小红书 / 视频脚本 / 个人日记。

Review 会自动使用可验证数字、书目、峰值月份、卡住的书和主题变化候选；**不会自动编造为什么转向、为什么弃读、某本书如何“改变了我”**。这些意义缺失时会留下编辑提示。

### Advisor

先实时发现并核验微信读书候选：

```bash
python scripts/build_private_reading_lab.py \
  --include-private \
  --advisor-query "认知科学"
```

系统会：

```text
/store/search scope=10
→ live catalog verification
→ 已深读排除
→ shortlist
→ advisor_semantic_editor.html
```

语义编辑器要求每本候选显式填写：

- 观点 / 学派；
- 时代 / 范式；
- 抽象层级；
- 相邻学科；
- conceptual fit；
- 每项 evidence + confidence。

导出编辑后的 JSON 后：

```bash
python scripts/build_private_reading_lab.py \
  --include-private \
  --advisor-query "认知科学" \
  --advisor-semantic-annotations /path/to/weread-semantic-advisor.json
```

只有完整证据通过 strict gate 的候选才进入最终语义结果。

### Reading Path

先发现候选并生成语义编辑器：

```bash
python scripts/build_private_reading_lab.py \
  --include-private \
  --path-topic "心理学"
```

除四个语义轴外，还要明确：

```text
stage = intro | framework | frontier
stageEvidence = 为什么承担这个学习阶段角色
```

导出后：

```bash
python scripts/build_private_reading_lab.py \
  --include-private \
  --path-topic "心理学" \
  --path-semantic-annotations /path/to/weread-semantic-path.json \
  --path-confirmed-level beginner
```

随后系统会：

```text
semantic gate
→ live catalog re-verification
→ /book/info enrichment
→ wordCount / time estimate
→ 2 intro + 2 framework + 2 frontier
→ minimum version
→ Feynman checkpoints
→ final private HTML
```

---

## 3. 数据与架构

```text
WeRead Agent Gateway
    ↓
export_notes.py / fetch_enrich.py
    ↓
raw local facts
    ↓
visualization_context
    ├─ Public Archive deterministic layer
    └─ Private Reading Lab evidence layer
```

项目原则：

```text
事实由代码计算
→ 解释必须带 evidence / uncertainty
→ schema / contract
→ stable renderer
```

关键边界：

1. 书架 ≠ 阅读；
2. mark = 保存的原文，不自动代表用户观点；
3. review = 用户自己的想法证据，但仍不能过度推成人格；
4. unknown ≠ 0；
5. live catalog availability ≠ conceptual fit；
6. Semantic gate 不自动填写学派/范式；
7. browser local state ≠ 微信读书远端状态；
8. 远端写操作必须 plan-first + explicit confirmation。

---

## 4. 数据拉取

```bash
export WEREAD_API_KEY="wrk-..."
export WEREAD_DATA_DIR="$HOME/.local/share/we-read"

python scripts/export_notes.py
python scripts/fetch_enrich.py
```

当前官方 Skill 基线：

```text
Tencent/WeChatReading 1.0.4
```

实时目录核验：

- `/store/search`，ebook lookup 使用 `scope=10`；
- `/book/info` 补 wordCount / publisher / category / deepLink 等。

没有 `WEREAD_API_KEY` 时，live Advisor / Reading Path 会明确失败，不会拿旧缓存伪装实时状态。

---

## 5. 其他能力

### Obsidian 安全同步

```bash
python scripts/sync_obsidian.py --vault "/path/to/vault" --dry-run
python scripts/sync_obsidian.py --vault "/path/to/vault"
```

机器只覆盖 `WEREAD_SYNC_START ... WEREAD_SYNC_END`；`USER_EDIT_ZONE` 永久保留。

### Book → Skill

第一阶段：生成 evidence-backed Skill：

```bash
python scripts/book_to_skill.py --book-id "BOOK_ID"
```

输出严格区分 source highlight / user review / AI refinement。

第二阶段：把个人证据精炼为 3–7 步可执行方法，但不允许无证据补全：

```bash
python scripts/build_book_method_brief.py \
  --context data/analysis/visualization_context.json \
  --book-id "BOOK_ID" \
  --output data/analysis/private_lab/book_method_brief.json

python scripts/renderers/book_method_editor.py \
  --input data/analysis/private_lab/book_method_brief.json \
  --output data/analysis/private_lab/book_method_editor.html
```

编辑器导出 refinement JSON 后：

```bash
python scripts/apply_book_method_refinement.py \
  --input /path/to/weread-book-method-refinement.json \
  --output data/analysis/private_lab/book_method.json \
  --markdown data/analysis/private_lab/book_method.md
```

每一步必须有 `action + why + evidenceIds`；有 user review 可用时，最终方法至少要引用一条自己的想法。

### Shelf Organizer

```bash
python scripts/plan_shelf_organization.py --strategy hybrid
```

当前默认 `plan-only`，不会调用未文档化接口修改远端书架。

---

## 6. 当前 10 个本地 Skills

| Skill | 角色 |
|---|---|
| `weread-private-lab` | 私有总编排 / Action Hub / 隐私路由 |
| `yao-weread-skill` | 底层数据 / 报告设计参考 |
| `huashu-weread` | Advisor / Path / Alchemy / Review |
| `weread-visualization` | Heatmap / Map / Shift / Graph / Profile / Report |
| `weread-search` | 本地全文检索 |
| `weread-recall` | Recall / Feynman / spaced review |
| `weread-blindspot` | Blindspot / Counter Reading |
| `weread-obsidian` | 安全增量同步 |
| `weread-book-to-skill` | 单书证据 → reusable Skill / 方法 refinement |
| `weread-organizer` | 本地书架整理 / Booklist plan |

完整生态扫描：[`docs/skill-landscape.md`](docs/skill-landscape.md)

实现审计：[`docs/skill-audit.md`](docs/skill-audit.md)

---

## 7. Legacy

`scripts/analysis.py` 保留用于历史可复现性，但**不再作为新系统的数据真相层，也不继续扩展**。

历史债与限制包括：

- A1 曾有 category double-counting，现已修复并统一复用 `metrics.category_participation()` 的 union-by-bookId 口径；
- 私密标题样本展示；
- Windows-only wordcloud font；
- 年份硬编码；
- 旧“人格分型”命名过强；
- 词典情感只能作为启发式。

有价值模块已经迁入 metrics / Pages / Deep Notes / Private Lab。

---

## 8. 测试与验证

```bash
python -m unittest discover -s tests -v
```

GitHub Actions 在 Python 3.11 与 3.13 上运行。

覆盖包括：

- Heatmap / daily parsing；
- private/public Page scope；
- raw body leakage；
- official readdata fields；
- Page UI / Explorer / Pin / command palette / theme；
- Search / Recall / stable evidenceId；
- Recall browser-local answerHistory / spaced review；
- Deep Notes；
- Text Mining Lite / Source-vs-Self / novelty / burst / resurgence；
- Text Mining optional semantic contracts；
- Quote Cards；
- Alchemy synthesis；
- Narrative Review platform alias / fact-bounded draft；
- Advisor / Path live candidate contracts；
- Semantic brief / evidence gate；
- Reading Path six-book contract；
- Book→Skill evidence-backed generation；
- Book→Skill 3–7 步 method refinement gate；
- Obsidian USER_EDIT_ZONE；
- Shelf Planner；
- Public Pages artifact validator；
- Private Lab artifact validator + final JS `node --check`。

---

## 9. 维护阶段

核心产品已进入维护阶段，默认策略是**停止横向扩功能**。当前只保留这些维护事项：

1. 可选：在用户自己的私有环境做一次完整真实数据端到端验收；
2. 保持 schema、validator、workflow 与 publication policy 一致；
3. legacy `analysis.py` 只做必要 bugfix / 可复现性维护，不再扩功能；
4. Page 现有 UI 组合层以维护为主，不继续新增 `pages_*_ui.py` 补丁层；若未来需要大改，优先合并现有层而不是继续叠加；
5. 如需从 Git 历史彻底移除个人阅读数据，必须单独备份并显式授权后做 history rewrite。

更重的 NLI contradiction、BERTopic/STM 对照、语义 Recall diff 等保留为**未来可选研究方向**，不是当前 backlog。

`.gitignore` 只能阻止未来新增，不能清除历史提交。

---

## 10. 状态

- ✅ Public Reading Archive
- ✅ 完整真实数据 Pages
- ✅ Heatmap / Map / Graph / Shift / Profile
- ✅ 498 本书架 Explorer
- ✅ Private Reading Lab
- ✅ Search / Deep Notes / Text Mining Lab / Quote Cards
- ✅ Recall + answer history + spaced review
- ✅ Alchemy private synthesis
- ✅ Narrative Review draft / Markdown / HTML
- ✅ Advisor live verification + semantic gate
- ✅ Reading Path live discovery + semantic stage gate + six-book plan
- ✅ Blindspot / Counter Reading
- ✅ Safe Obsidian Sync
- ✅ Book → Skill evidence-backed generation
- ✅ Book → Skill 3–7 step evidence-linked method refinement
- ✅ Shelf Organizer plan-only
- ✅ Public/Private artifact validators
- ✅ Python 3.11 / 3.13 CI

更多约定见 [`AGENTS.md`](AGENTS.md)、[`docs/ecosystem.md`](docs/ecosystem.md)、[`docs/skill-landscape.md`](docs/skill-landscape.md)、[`docs/skill-audit.md`](docs/skill-audit.md)。
