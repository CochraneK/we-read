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
| `weread-book-to-skill` | 中高 | 单书证据 → 可复用 Skill | 否 | 第二阶段 3–7 步方法 refinement |
| `weread-organizer` | 中高（安全模式） | 书架整理 / Booklist plan | 部分（Pin） | 仅在官方写接口明确后考虑远端 mutation |
| `yao-weread-skill` | 中高 | 官方数据/报告/图表设计参考 | 大量吸收 | 不追求机械 27/27 |
| `huashu-weread` | **高（核心闭环）** | Advisor / Path / Alchemy / Review | 少量非敏感事实 | 主要剩真实语义审核与实际使用 |

“高”不代表所有可能功能都实现，而是：主 contract、workflow、实现映射、测试与隐私边界已经闭环。

---

## 最初工作有没有被合并

**已经合并。**

### 1. 划线 → 金句 → 卡片

历史成品仍保留：

```text
quote_lib/cards.html
quote_lib/cards_package.zip
quote_lib/design-tokens.md
quote_lib/金句库.json
quote_lib/金句库_top60.md
```

历史版本约 351 张卡片，包含 A/B/C 三主题、翻转、键盘和 PDF 打印。

现在已经变成可重建正式流水线：

```text
weread_notes_export.json
        ↓
visualization_context privacy allowlist
        ↓
filtered_notes_private.json
        ↓
build_quote_lib.py
        ↓
quotes/金句库.json
        ↓
renderers/quote_cards.py
        ↓
private_lab/quote_cards.html
        ↓
Book Workbench / Search / Recall / Alchemy
```

新版卡片不依赖在线封面，减少外部请求；原始划线明确属于私有证据。

### 2. 旧 A–E 16 项深分析

`scripts/analysis.py` 仍保留作历史参考，但不再作为数据真相层。它曾包含：类别参与、作者集中、日/月节律、词云、想法词频/启发式情感、重复划线、章节位置、划线↔想法错位、进度×笔记和长期增长等。

有价值能力已经迁移：

| 旧能力 | 新主干 |
|---|---|
| A1 / E14 类别参与 | `metrics.py` / Advisor / Blindspot |
| A2 作者集中 | Page 作者偏好 / Knowledge Graph |
| B5 月度时间线 | Page rhythm / career |
| B6 日内时段 | 24h 阅读时钟 |
| B7 年月 / 星期 | Heatmap / weekday / seasonality |
| C10 重复划线 | Deep Notes |
| D12 章节位置 | Deep Notes（明确为近似口径） |
| D13 划线↔想法关系 | Deep Notes |
| E15 进度×笔记 | Page depth scatter |
| E16 累计增长 | Page career / note evolution |
| 原始划线卡片 | Private Quote Cards |

不再把 C8 词云当“认知主题证明”，也不把 C9 词典情感升级成心理结论。

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

`scripts/build_deep_notes_context.py`：

- 重复划线；
- 划线长度；
- 章节位置；
- mark/review 章节关系；
- thought-rich books；
- highlight-heavy books。

### Recall

已经完成：

- stable `evidenceId`；
- 先写“我现在怎么理解”，再展开旧证据；
- again / hard / good / easy；
- browser-local `nextReviewAt`；
- `answerHistory`；
- JSON 导入导出；
- 当前回答 vs 当时证据的**表面文字重合百分比**。

最后一项不是语义正确率，只是弱提示。

### Alchemy

已完成：

```text
Context
→ source_text / user_thought 分离
→ heuristic issue clusters
→ evidence-backed synthesis
→ unresolved questions
→ private HTML
```

大证据量先触发 scope gate。heuristic cluster 不宣称等于完整语义理解。

### Narrative Review

已从 Context 升级为可用成品：

```text
period facts
→ platform gate
→ deterministic draft JSON
→ Markdown
→ private HTML
```

支持朋友圈 / 公众号 / 小红书 / 视频脚本 / 个人日记。

成稿器自动使用可验证数字、书目、峰值月份、卡住的书和主题变化候选；不会编造：

- 为什么兴趣改变；
- 为什么弃读；
- “这本书改变了我”。

这些意义缺失时会留下明确编辑提示。

### Advisor

当前链路：

```text
Advisor Context
→ /store/search scope=10
→ live catalog verification
→ already-read exclusion
→ shortlist
→ semantic brief
→ offline semantic editor
→ strict semantic validator
→ final semantic result
```

语义 gate 要求每本书显式填写并给证据：

- `school_or_viewpoint`；
- `era_or_paradigm`；
- `abstraction_level`；
- `adjacent_discipline`；
- `conceptualFit`；
- 每项 `evidence + confidence`。

目录可用、评分高、标题相似都不能替代概念适配证据。

### Reading Path

当前链路：

```text
Path Context
→ live discovery
→ semantic brief/editor
→ stage + stageEvidence
→ semantic gate
→ live re-verification
→ /book/info enrichment
→ 2 × intro + 2 × framework + 2 × frontier
→ time estimate / minimum version / Feynman checkpoints
→ final private HTML
```

不会仅凭笔记数自动判断 advanced；最终 level 仍要求显式确认。

---

## `huashu-weread` 四条主线现在的真实状态

### Advisor — 核心闭环完成

已实现事实层、实时目录核验、已读排除、shortlist、语义编辑器、strict gate 和最终语义结果。

**刻意保留的人工/语义 gate**：真正判断一本书属于什么学派/范式、为什么补缺，需要 evidence；代码不硬猜。

### Path — 核心闭环完成

已实现起点建议、level 确认、live discovery、语义阶段审阅、目录重验、book info、6 本路径、最小版本、时间估算和 Feynman checkpoint。

### Alchemy — 私有闭环完成

已实现单书/跨主题 Context、证据分型、scope gate、heuristic synthesis 和私人 HTML。

### Review — 成稿闭环完成

已实现周期事实、platform gate、事实约束草稿、Markdown 与私人 HTML。

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

Private Lab 最终 artifact 还会运行 `validate_private_lab_output.py`：

- 必须 `noindex,nofollow,noarchive`；
- 必须有 Private / Raw Evidence 标记；
- 必须有 Search / Recall / Actions；
- 浏览器端禁止 `fetch()` / XHR / WebSocket；
- 内联 JS 必须通过 `node --check`。

---

## 目前真正还没完成的是什么

不再是“缺很多功能”，而是以下收尾：

1. **真实私有数据端到端运行**：公开 CI 故意不上传 raw marks/reviews 和 API key，因此最终 Private Lab 应在用户自己的环境跑一次完整验收。
2. **Book→Skill 第二阶段 refinement**：从证据进一步提炼 3–7 步可执行方法。
3. **Blindspot 更强反证**：学派、stakeholder、反向因果等。
4. **可选的语义回答差异**：Recall 当前只有安全、可解释的 lexical-overlap 弱信号；以后可加本地/私有语义模型，但不能伪装成“理解程度分数”。
5. **Legacy 清理**：`analysis.py` 继续保留历史可复现性，但不应再扩展。
6. **Git 历史隐私清理**：属于破坏性操作，只有用户明确授权才做。

## “充分分析”的标准

一个 Skill 只有以下四项都明确后才算规范级审计完成：

1. **Contract**：数据源、字段语义、fallback、隐私边界；
2. **Workflow**：真实步骤、分叉、确认点；
3. **Implementation mapping**：仓库哪段代码实现了什么；
4. **Gap decision**：缺失是继续做、暂缓，还是刻意不自动化。

当前 10 个本地 Skill 都完成了规范级 mapping；核心 WeRead 私人工作流已经由“分析阶段”进入“使用/维护阶段”。
