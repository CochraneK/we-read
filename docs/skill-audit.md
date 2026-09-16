# WeRead Skill 审计

> 审计日期：2026-09-14。目标不是统计“有多少 Skill”，而是区分：**规范是否读过、能力是否实现、是否已形成运行闭环、是否应该进入公开 Page**。

## 总结

仓库当前有 **10 个本地 WeRead Skill**。`SKILL.md` 是工作流规范、字段语义、隐私边界和输出契约；真正执行的是 Python builder / verifier / renderer。外部实时数据来自腾讯官方 WeChatReading Agent Gateway，当前脚本基线为 `skill_version=1.0.4`。

当前系统已经从“零散 Skill + Dashboard”收束为两类成品：

```text
WeRead Intelligence
├─ Public Reading Archive
│  └─ 聚合事实、阅读版图、长期轨迹、书架探索
└─ Private Reading Lab
   └─ 原始证据、Search、Recall、Deep Notes、Cards、Alchemy、Advisor、Path、Review
```

## 当前 10 个本地 Skill

| Skill | 当前实现度 | 主要角色 | 公开 Page | 仍值得做 |
|---|---:|---|---|---|
| `weread-private-lab` | **高** | 私有总编排 / Action Hub / 隐私路由 | 否 | 真实私有数据最终验收 |
| `weread-visualization` | **高** | Heatmap / Map / Shift / Graph / Profile / Report | 是 | 维护 schema / renderer |
| `weread-search` | **高** | 本地全文检索 / evidence recall | 否 | 更统一的跨模块 handoff UX |
| `weread-recall` | **高** | Feynman / 主动回忆 / spaced review | 公开仅元数据 | 可选语义级回答差异分析 |
| `weread-blindspot` | 中高 | 集中度 / 投入落差 / Counter Reading | 是 | 更丰富的反证维度 |
| `weread-obsidian` | **高** | 私有知识库安全增量同步 | 否 | 核心安全边界已完成 |
| `weread-book-to-skill` | **高** | 单书证据 → Skill → evidence-linked 方法 refinement | 否 | 真实使用反馈 / 方法质量迭代 |
| `weread-organizer` | 中高（安全模式） | 书架整理 / Booklist plan | 部分（Pin） | 仅在官方写接口明确后考虑远端 mutation |
| `yao-weread-skill` | 中高 | 官方数据/报告/图表设计参考 | 大量吸收 | 不追求机械 27/27 |
| `huashu-weread` | **高（核心闭环）** | Advisor / Path / Alchemy / Review | 少量非敏感事实 | 主要剩真实语义审核与实际使用 |

“高”不代表所有可能功能都实现，而是：主 contract、workflow、实现映射、测试与隐私边界已经闭环。

---

## 最初工作有没有被合并

**已经合并。**

### 划线 → 金句 → 卡片

历史产物仍保留在 `quote_lib/`，但现在已变成可重建正式流水线：

```text
weread_notes_export.json
→ visualization_context privacy allowlist
→ filtered_notes_private.json
→ build_quote_lib.py
→ quotes/金句库.json
→ renderers/quote_cards.py
→ private_lab/quote_cards.html
→ Book Workbench / Search / Recall / Alchemy
```

新版卡片保留三主题、搜索、翻转、键盘、PDF、章节/主题/评分与微信读书 deep link；不依赖在线封面。

### 旧 A–E 16 项深分析

`scripts/analysis.py` 只保留历史可复现性，不再作为数据真相层。

| 旧能力 | 新主干 |
|---|---|
| A1 / E14 类别参与 | `metrics.py` / Advisor / Blindspot |
| A2 作者集中 | Page 作者偏好 / Knowledge Graph |
| B5 月度时间线 | Page rhythm / career |
| B6 日内时段 | 24h 阅读时钟 |
| B7 年月 / 星期 | Heatmap / weekday / seasonality |
| C10 重复划线 | Deep Notes |
| D12 章节位置 | Deep Notes（近似口径） |
| D13 划线↔想法关系 | Deep Notes |
| E15 进度×笔记 | Page depth scatter |
| E16 累计增长 | Page career / note evolution |
| 原始划线卡片 | Private Quote Cards |

C8 词云不再被当作“认知主题证明”，C9 词典情感也不升级成心理结论。

---

## Private Reading Lab 当前闭环

统一入口：

```bash
python scripts/build_private_reading_lab.py
```

完整私有档案：

```bash
python scripts/build_private_reading_lab.py --include-private --with-text
```

入口：

```text
data/analysis/private_lab/index.html
```

核心 Lab 即使不加 `--with-text` 也包含 Search / Recall 所需的原始 evidence；`--with-text` 只是额外生成 Quote Cards / Alchemy 成品。

### Search

- SQLite 本地全文索引；
- title / author / category / chapter / mark / review；
- 中文 substring fallback；
- 不进入公开 Page。

### Deep Notes

- 重复划线；
- 划线长度；
- 章节位置；
- mark/review 章节关系；
- thought-rich books；
- highlight-heavy books。

### Recall

- stable `evidenceId`；
- 先写“我现在怎么理解”，再展开旧证据；
- again / hard / good / easy；
- browser-local `nextReviewAt`；
- `answerHistory`；
- JSON 导入导出；
- 当前回答 vs 当时证据的表面文字重合百分比。

最后一项不是语义正确率，只是弱提示。

### Alchemy

```text
Context
→ source_text / user_thought 分离
→ heuristic issue clusters
→ evidence-backed synthesis
→ unresolved questions
→ private HTML
```

大证据量先触发 scope gate；heuristic cluster 不宣称等于完整语义理解。

### Narrative Review

```text
period facts
→ platform gate
→ deterministic draft JSON
→ Markdown
→ private HTML
```

支持朋友圈 / 公众号 / 小红书 / 视频脚本 / 个人日记。不会编造兴趣转向、弃读原因或“某本书改变了我”。

### Advisor

```text
Advisor Context
→ /store/search scope=10
→ live catalog verification
→ already-read exclusion
→ shortlist
→ semantic brief/editor
→ strict semantic validator
→ final semantic result
```

语义 gate 要求：观点/学派、时代/范式、抽象层级、相邻学科、conceptual fit，并逐项给 evidence + confidence。

### Reading Path

```text
Path Context
→ live discovery
→ semantic brief/editor
→ stage + stageEvidence
→ semantic gate
→ live re-verification
→ /book/info enrichment
→ 2 intro + 2 framework + 2 frontier
→ time estimate / minimum version / Feynman checkpoints
→ final private HTML
```

不会仅凭笔记数自动判断 advanced；最终 level 仍要求显式确认。

### Book → Skill 方法 refinement

现在第二阶段也已闭环：

```text
single-book personal evidence
→ stable be-* evidence IDs
→ method brief
→ offline method editor
→ 3–7 step strict refinement gate
→ book_method.json / book_method.md
```

每一步必须包含：

- `action`；
- `why`；
- 至少一个当前书真实 `evidenceId`。

如果有 user review 可用，最终方法至少必须引用一条自己的想法。validator 不会用模型常识补缺失步骤。

---

## `huashu-weread` 四条主线状态

### Advisor — 核心闭环完成

事实层、实时目录核验、已读排除、shortlist、语义编辑器、strict gate 和最终语义结果已实现。真正的学派/范式/补缺判断仍要求 evidence。

### Path — 核心闭环完成

起点建议、level 确认、live discovery、语义阶段审阅、目录重验、book info、6 本路径、最小版本、时间估算和 Feynman checkpoint 已实现。

### Alchemy — 私有闭环完成

单书/跨主题 Context、证据分型、scope gate、heuristic synthesis 和私人 HTML 已实现。

### Review — 成稿闭环完成

周期事实、platform gate、事实约束草稿、Markdown 与私人 HTML 已实现。

---

## 隐私路由

```text
公开 Page
  聚合事实 + 非敏感书目元数据 + 结构化洞察

Private Reading Lab
  原始 marks/reviews + Search + Cards + Deep Notes + Recall
  Alchemy + Review + Advisor + Reading Path + Semantic Review

需要显式人工确认
  因果意义 / 概念适配 / Path 阶段角色 / 对外发布 / 远端写操作
```

Private Lab artifact validator 强制：

- `noindex,nofollow,noarchive`；
- Private / Raw Evidence 标记；
- Search / Recall / Actions；
- 浏览器端禁止 `fetch()` / XHR / WebSocket；
- 内联 JS 通过 `node --check`。

---

## 维护阶段

核心闭环已经完成，以下不是功能开发 backlog，而是使用与维护事项：

1. **可选真实私有数据端到端验收**：公开 CI 故意不上传 raw marks/reviews 和 API key；需要时可在用户自己的环境做一次完整验收。
2. **Legacy 维护**：`analysis.py` 保留历史可复现性，只做必要 bugfix，不再扩展。
3. **Page 组合层维护**：现有 `pages_*.py` enhancer 不再横向增加；未来大改时优先合并层级。
4. **Git 历史隐私清理**：属于破坏性操作，只有用户明确授权才做。
5. **可选研究方向**：Blindspot 更强反证、Recall 私有语义差异等可以未来研究，但不视为当前未完成项。

## “充分分析”的标准

一个 Skill 只有以下四项都明确后才算规范级审计完成：

1. **Contract**：数据源、字段语义、fallback、隐私边界；
2. **Workflow**：真实步骤、分叉、确认点；
3. **Implementation mapping**：仓库哪段代码实现了什么；
4. **Gap decision**：缺失是继续做、暂缓，还是刻意不自动化。

当前 10 个本地 Skill 都完成了规范级 mapping；核心 WeRead 私人工作流已经由“开发阶段”进入“使用/维护阶段”。
