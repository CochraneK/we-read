# we-read · WeRead Intelligence

> 把微信读书从「读过什么」，变成「我在关注什么、认知如何变化，以及读过的知识现在能为我做什么」。

**Project Page:** https://cochranek.github.io/we-read/

本仓库围绕微信读书 Agent Gateway 构建一套**本地优先、证据可追溯**的导出、分析、检索、可视化、回顾、知识流转与复用工具链。

## 已完成能力

- 全量笔记 / 划线导出与阅读统计、进度、书籍信息补全
- GitHub-style 多年阅读热力图
- Reading Map / Knowledge Graph 稳定网络图 renderer
- Cognitive Shift 认知变迁时间轴
- Evidence-based Reading Profile
- Unified Reading Report 单页总览
- SQLite 本地全文检索：书名 / 作者 / 章节 / 划线 / 想法
- Reading Recall / Feynman 主动回顾队列与卡片
- Blindspot / Counter Reading 证据分析与反向阅读方向
- Obsidian 安全增量同步，永久保留 `USER_EDIT_ZONE`
- Book → Skill：把个人划线 / 想法生成可调用的本地 Skill
- Shelf Organizer / Booklist：可审核的书架整理计划，默认 **plan-only**
- 金句筛选、去重与版权复核候选提示
- 16 项 Plotly 单页看板（legacy，逐步迁移到共享 metrics）
- GitHub Pages 脱敏产品页与合成交互 Demo

## 核心架构

```text
WeRead Agent Gateway
        │
        ├─ export_notes.py / fetch_enrich.py
        ▼
     raw local data
        │
        ▼
build_visualization_context.py
        │
        ├─ metrics.py ───────────────→ deterministic metrics
        ├─ build_search_index.py ────→ local search
        ├─ build_recall_queue.py ────→ recall / Feynman
        ├─ build_blindspot_context.py → blindspot evidence
        ├─ plan_shelf_organization.py → shelf / booklist plan
        │
        ├─ AI / Skill interpretation
        │    ├─ reading_map.json
        │    ├─ knowledge_graph.json
        │    ├─ cognitive_shift.json
        │    ├─ reading_profile.json
        │    ├─ blindspot.json
        │    └─ reading_report.json
        │
        ├─ renderers/
        │    ├─ heatmap.py
        │    ├─ network.py
        │    ├─ timeline.py
        │    ├─ profile.py
        │    ├─ blindspot.py
        │    ├─ recall.py
        │    └─ report.py
        │
        ├─ sync_obsidian.py ────────→ Obsidian Vault
        └─ book_to_skill.py ────────→ private reusable Skill
```

关键原则是：

```text
事实由程序计算
      ↓
AI 只做解释型推断
      ↓
固定 Schema
      ↓
稳定 Renderer
```

Renderer 不负责修正或发明 AI 结论。

## 快速开始

### 1. 拉取数据

```bash
export WEREAD_API_KEY="wrk-..."
```

推荐把真实阅读数据完全放在仓库外：

```bash
export WEREAD_DATA_DIR="$HOME/.local/share/we-read"

python scripts/export_notes.py
python scripts/fetch_enrich.py
```

`fetch_enrich.py` 会自动发现年度范围；月度详情默认抓最近 48 个自然月，可调整：

```bash
export WEREAD_MONTHLY_HISTORY_MONTHS=72
```

### 2. 建立统一事实层

```bash
python scripts/build_visualization_context.py
```

输出：

```text
data/analysis/visualization_context.json
```

默认排除书架中 `secret=1` 的私密书。只有明确需要**本地私密分析**时才使用：

```bash
python scripts/build_visualization_context.py --include-private
```

不要把含私密书的上下文提交到 Git 或发布成公开报告。

### 3. 确定性可视化

阅读热力图：

```bash
python scripts/renderers/heatmap.py
```

输出：

```text
data/analysis/reading_heatmap.html
```

Legacy 16 项统计看板：

```bash
python -m pip install -r requirements-analysis.txt
python scripts/analysis.py
```

### 4. 高阶解释型可视化

`weread-visualization` Skill 基于 `visualization_context.json` 生成固定 Schema JSON，再交给 renderer：

```bash
python scripts/renderers/network.py --kind reading-map
python scripts/renderers/network.py --kind knowledge-graph
python scripts/renderers/timeline.py
python scripts/renderers/profile.py
```

对应输入与 Schema：

| 能力 | 输入 | Schema |
|---|---|---|
| Reading Map | `reading_map.json` | `schemas/reading_map.schema.json` |
| Knowledge Graph | `knowledge_graph.json` | `schemas/knowledge_graph.schema.json` |
| Cognitive Shift | `cognitive_shift.json` | `schemas/cognitive_shift.schema.json` |
| Reading Profile | `reading_profile.json` | `schemas/reading_profile.schema.json` |

### 5. Unified Reading Report

```bash
python scripts/renderers/report.py
```

输出：

```text
data/analysis/reading_report.html
```

报告会自动吸收已经存在的 Reading Map、Cognitive Shift、Knowledge Graph、Reading Profile；缺失组件显示“尚未生成”，不会伪造结论。

可选编辑层遵循：

```text
schemas/reading_report.schema.json
```

### 6. 本地全文检索

```bash
python scripts/build_search_index.py --rebuild
python scripts/build_search_index.py --query "自由"
```

过滤类型：

```bash
python scripts/build_search_index.py --query "自由" --kind mark
python scripts/build_search_index.py --query "自由" --kind review
```

索引直接消费隐私过滤后的统一事实层，支持 FTS5，并为中文短词提供 substring fallback。

### 7. Reading Recall / Feynman

```bash
python scripts/build_recall_queue.py
python scripts/renderers/recall.py
```

默认：

- 优先较久未接触的证据；
- 控制同一本书的占比；
- 同龄证据中优先用户自己的 `review`；
- 卡片先让用户回忆，再展开原始证据。

例如：

```bash
python scripts/build_recall_queue.py \
  --min-age-days 90 \
  --limit 10 \
  --max-per-book 1
```

### 8. Blindspot / Counter Reading

先构建只含确定性信号的 context：

```bash
python scripts/build_blindspot_context.py
```

由 `weread-blindspot` Skill 生成符合：

```text
schemas/blindspot.schema.json
```

的：

```text
data/analysis/blindspot.json
```

再渲染：

```bash
python scripts/renderers/blindspot.py
```

“盲点”只表示值得核对的阅读集中、投入落差或缺失视角；不是人格诊断，也不从阅读记录推断敏感属性。

### 9. Obsidian 安全增量同步

首次和批量更新前先 dry-run：

```bash
python scripts/sync_obsidian.py \
  --vault "/path/to/vault" \
  --dry-run
```

确认后：

```bash
python scripts/sync_obsidian.py --vault "/path/to/vault"
```

也可：

```bash
export OBSIDIAN_VAULT="/path/to/vault"
python scripts/sync_obsidian.py
```

安全边界：

- 程序只更新 `WEREAD_SYNC_START ... WEREAD_SYNC_END`；
- `USER_EDIT_ZONE` 永久保留；
- 同名但非本项目管理的文件默认跳过；
- 不自动删除孤儿笔记；
- `--adopt-unmanaged` 必须显式使用，接管时旧全文保存在 USER_EDIT_ZONE。

### 10. Book → Skill

推荐按稳定 `bookId`：

```bash
python scripts/book_to_skill.py --book-id "BOOK_ID"
```

也可用唯一书名：

```bash
python scripts/book_to_skill.py --title "书名"
```

默认输出：

```text
data/generated-skills/weread-book-*/
├── SKILL.md
├── manifest.json
└── references/
    └── evidence.md
```

生成结果明确区分：

- `我的划线`：用户保存的原文片段，不等于用户本人观点；
- `我的想法`：用户自己写下的 review；
- `AI 提炼`：后续基于证据做的方法总结。

这个目录默认被 `.gitignore`，属于个人本地产物。

### 11. Shelf Organizer / Booklist

生成可审核的本地计划：

```bash
python scripts/plan_shelf_organization.py --strategy hybrid
```

支持：

```text
status    深读 / 已读 / 在读 / 待读
category  一级分类
hybrid    状态 × 分类
```

输出：

```text
data/analysis/shelf_plan.json
data/analysis/shelf_plan.md
```

当前实现**不会直接修改微信读书远端书架**，并明确记录：

```json
"remoteMutationPerformed": false
```

只有当前官方能力文档 / `/_list` 明确提供对应写操作、且用户再次确认计划后，才应增加远端执行层；不会使用未文档化接口冒险写入。

### 12. 金句库

```bash
python scripts/build_quote_lib.py
```

`public_domain` 为兼容旧卡片链路仍保留 `pd/protected`，但 `pd` 仅代表**优先人工版权复核候选**，不是法律结论。

## Skills

当前 Skill 层：

| Skill | 作用 |
|---|---|
| `yao-weread-skill` | 微信读书底层能力 / 报告基础 |
| `huashu-weread` | advisor / path / alchemy / review 顾问工作流 |
| `weread-visualization` | Heatmap / Map / Shift / Graph / Profile / Report |
| `weread-search` | 本地全文检索和证据召回 |
| `weread-recall` | Recall / Feynman / Contrast |
| `weread-blindspot` | Blindspot / Counter Reading |
| `weread-obsidian` | 安全增量同步到 Obsidian |
| `weread-book-to-skill` | 单本书个人笔记 → evidence-backed Skill |
| `weread-organizer` | 本地书架整理与书单计划 |

## 公开 Project Page

`site/index.html` 是完全脱敏的静态产品页：

- 不读取 `data/`；
- 不展示真实书名、划线或想法；
- Heatmap、Reading Map、Cognitive Shift 均使用合成 Demo；
- 通过 GitHub Pages workflow 自动部署。

访问：

**https://cochranek.github.io/we-read/**

## 设计原则

1. **事实与 AI 推断分离**：阅读时长、书目、笔记数由代码计算；主题、认知转向、画像属于解释层。
2. **先结构化再渲染**：解释型结果先生成固定 JSON，再交给稳定 renderer。
3. **书架不等于阅读**：书架表示兴趣意图；笔记、进度和阅读时长才是投入证据。
4. **本地优先**：API Key、原始划线、个人想法、搜索索引和生成 Skill 默认不进入公开仓库。
5. **可追溯**：高阶结论尽量保留对应书籍、划线、时间段、置信度和反证。
6. **避免重复请求**：所有高级能力优先消费统一 normalized facts。
7. **同步不覆盖用户内容**：自动同步只能管理明确标记的机器区。
8. **远端写入预览优先**：任何可能修改远端状态的操作都必须先有可审核计划与明确确认。

## 统计正确性

新增确定性统计应进入 `scripts/metrics.py` 并配回归测试。

已发现 legacy `analysis.py` 的 A1 类别参与度存在书架/笔记交集重复计数问题；正确的 union-by-bookId 口径已经在 `metrics.category_participation()` 中实现并测试。旧 Dashboard 模块化迁移见 Issue #1。

## 隐私与仓库卫生

`.gitignore` 已默认忽略：

- `data/weread_*.json / .md`
- `data/analysis/*`
- `data/generated-skills/`
- 生成报告、SQLite 索引和金句产物
- `.env*`

建议：

```bash
export WEREAD_DATA_DIR="$HOME/.local/share/we-read"
```

> `.gitignore` 只阻止以后新增。仓库历史中如果已经存在真实个人阅读数据，仍需要单独执行 `git rm --cached`；如果希望从已公开历史彻底移除，需要经过备份后显式重写 Git 历史。该破坏性维护事项记录在 Issue #2，本项目不会自动执行。

## 测试与 CI

```bash
python -m unittest discover -s tests -v
```

GitHub Actions 在 Python 3.11 与 3.13 上运行测试，当前新增测试覆盖：

- Heatmap 分级与 `dailyReadTimes` 解析
- 私密书默认排除 / 显式包含
- Reading Map / Knowledge Graph 清洗与 HTML
- Cognitive Shift 阶段归一化
- Reading Profile 事实 / 解释分层
- Unified Report 缺失组件降级和隐私提示
- SQLite Search / 中文 substring fallback
- Recall 队列的时效、跨书多样性与延迟展示
- Blindspot 确定性信号和 HTML escaping
- Obsidian USER_EDIT_ZONE、dry-run、unmanaged-file 保护
- Book → Skill 证据边界和歧义书名保护
- Shelf Planner 的互斥状态、分类和 plan-only 不变量
- 金句库去重、打分和版权警告
- category union-by-bookId 防重复计数

CI workflow 使用 Node 24 兼容版本的 GitHub Actions。

## 开源生态调研

项目对官方 WeChatReading Skill、WeRead MCP、Dashboard、Obsidian Skill、增量导出、书架整理等公开实践做了能力对照。目标不是复制多个互不兼容的前端，而是吸收成熟模式并统一到共享事实层。

详见 [`docs/ecosystem.md`](docs/ecosystem.md)。

## 状态

### 已完成

- ✅ Reading Heatmap
- ✅ Reading Map
- ✅ Knowledge Graph
- ✅ Cognitive Shift
- ✅ Reading Profile
- ✅ Unified Reading Report
- ✅ Local Search / Evidence Recall
- ✅ Reading Recall / Feynman
- ✅ Blindspot / Counter Reading
- ✅ Safe Obsidian Incremental Sync
- ✅ Book → Skill
- ✅ Shelf Organizer / Local Booklist Plan
- ✅ Public GitHub Page
- ✅ Python 3.11 / 3.13 CI

### 明确保留的遗留维护

- ⚠️ Legacy `analysis.py` 仍需继续模块化，并迁移到 `metrics.py` 的正确口径
- ⚠️ 公开 Git 历史中的真实个人数据清理属于破坏性维护，需要单独确认后执行
- ⏸️ 远端微信读书书架写入只在官方当前接口明确支持且用户确认后实现

更详细约定见 [`AGENTS.md`](AGENTS.md)、[`docs/ecosystem.md`](docs/ecosystem.md) 与 [`.workbuddy/skills/weread-visualization/references/visualization-spec.md`](.workbuddy/skills/weread-visualization/references/visualization-spec.md)。
