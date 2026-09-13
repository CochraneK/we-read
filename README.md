# we-read

把微信读书从「读过什么」变成「我在关注什么、认知如何变化，以及读过的知识现在能为我做什么」。

本仓库围绕微信读书 Agent Gateway 构建一套**本地优先**的导出、分析、检索、可视化、回顾与知识复用工具链。

## 当前能力

- 全量笔记 / 划线导出
- 阅读统计、进度、书籍信息补全
- 金句筛选、去重与版权复核候选提示
- 16 项阅读分析 + Plotly 单页看板（legacy）
- GitHub-style 多年阅读热力图（纯标准库、单文件 HTML）
- Reading Map / Knowledge Graph 稳定网络图 renderer
- Cognitive Shift 交互时间轴 renderer
- Evidence-based Reading Profile renderer
- Unified Reading Report 单页总览 renderer
- 隐私感知的统一可视化上下文
- SQLite 本地全文检索（书名 / 作者 / 章节 / 划线 / 想法）
- Reading Recall / Feynman 主动回顾队列与卡片
- 翻转金句卡片
- 顾问型阅读工作流
- 高阶解释型可视化 Skill

## 数据链路

```text
WeRead Agent Gateway
        │
        ├─ scripts/export_notes.py
        ├─ scripts/fetch_enrich.py
        │
        ▼
      raw data
        │
        ├─ scripts/build_visualization_context.py
        │      └─ shelf + notes + progress + stats → normalized facts
        │
        ├─ scripts/metrics.py
        │      └─ 可测试确定性指标
        │
        ├─ scripts/build_search_index.py
        │      └─ normalized facts → local SQLite search index
        │
        ├─ scripts/build_recall_queue.py
        │      └─ old evidence → deterministic recall queue
        │
        ├─ AI / Skill 解释层
        │      ├─ reading_map.json
        │      ├─ knowledge_graph.json
        │      ├─ cognitive_shift.json
        │      ├─ reading_profile.json
        │      └─ reading_report.json（可选编辑层）
        │
        └─ scripts/renderers/
               ├─ heatmap.py
               ├─ network.py
               ├─ timeline.py
               ├─ profile.py
               ├─ report.py
               └─ recall.py
```

## 快速开始

### 1. 拉取数据

```bash
export WEREAD_API_KEY="wrk-..."
python scripts/export_notes.py
python scripts/fetch_enrich.py
```

默认写入仓库根目录的 `data/`。更推荐把真实阅读数据完全放在仓库外：

```bash
export WEREAD_DATA_DIR="$HOME/.local/share/we-read"
python scripts/export_notes.py
python scripts/fetch_enrich.py
```

`fetch_enrich.py` 会自动发现年度范围；月度详情默认抓最近 48 个自然月，可调整：

```bash
export WEREAD_MONTHLY_HISTORY_MONTHS=72
```

### 2. 确定性可视化

阅读热力图：

```bash
python scripts/renderers/heatmap.py
```

输出：`data/analysis/reading_heatmap.html`

现有 16 项统计看板：

```bash
python -m pip install -r requirements-analysis.txt
python scripts/analysis.py
```

### 3. 生成统一事实层

```bash
python scripts/build_visualization_context.py
```

输出：`data/analysis/visualization_context.json`

默认排除书架中 `secret=1` 的私密书；只有明确需要本地私密分析时才使用：

```bash
python scripts/build_visualization_context.py --include-private
```

### 4. 高阶解释型可视化

高阶分析先由 `weread-visualization` Skill 从 `visualization_context.json` 生成固定 Schema JSON，再交给 renderer。

```bash
python scripts/renderers/network.py --kind reading-map
python scripts/renderers/network.py --kind knowledge-graph
python scripts/renderers/timeline.py
python scripts/renderers/profile.py
```

分别消费：

- `data/analysis/reading_map.json`
- `data/analysis/knowledge_graph.json`
- `data/analysis/cognitive_shift.json`
- `data/analysis/reading_profile.json`

对应 Schema：

- `schemas/reading_map.schema.json`
- `schemas/knowledge_graph.schema.json`
- `schemas/cognitive_shift.schema.json`
- `schemas/reading_profile.schema.json`

### 5. Unified Reading Report

当统一事实层存在后，报告即使缺少部分 AI 组件也可以生成：

```bash
python scripts/renderers/report.py
```

输出：`data/analysis/reading_report.html`

如果希望加入编辑型摘要、关键结论和下一步行动，可生成符合 `schemas/reading_report.schema.json` 的：

```text
data/analysis/reading_report.json
```

Report 会自动吸收已经存在的 Reading Map、Cognitive Shift、Knowledge Graph、Reading Profile，并链接到对应详细 HTML；缺失的组件会显示“尚未生成”，不会伪造结论。

### 6. 本地全文检索

建立隐私感知的 SQLite 索引：

```bash
python scripts/build_search_index.py --rebuild
```

搜索所有书名、作者、章节、划线和想法：

```bash
python scripts/build_search_index.py --query "自由"
```

只搜划线 / 想法：

```bash
python scripts/build_search_index.py --query "自由" --kind mark
python scripts/build_search_index.py --query "自由" --kind review
```

索引直接消费 `visualization_context.json`，因此默认继承私密书排除策略。

### 7. Reading Recall / Feynman

建立确定性回顾队列：

```bash
python scripts/build_recall_queue.py
```

默认只选至少 30 天前的材料、更久未回顾的优先，并限制每本书最多 2 条；个人想法 `review` 在同龄证据中优先于普通划线。

可调整：

```bash
python scripts/build_recall_queue.py --min-age-days 90 --limit 10 --max-per-book 1
```

生成“先回答、再展开原始证据”的回顾卡：

```bash
python scripts/renderers/recall.py
```

输出：`data/analysis/reading_recall.html`

### 8. 金句库

```bash
python scripts/build_quote_lib.py
```

`public_domain` 字段为了兼容旧卡片链路仍保留 `pd/protected` 值，但 `pd` 只表示**优先人工版权复核候选**，不是法律结论。

## Skills

### `yao-weread-skill`

底层微信读书能力与报告生成基础。

### `huashu-weread`

顾问型工作流，强调「书架 × 笔记」交叉分析：

- `advisor`：下一本读什么
- `path`：某领域如何从入门读到前沿
- `alchemy`：把划线和想法炼成主题笔记
- `review`：季度 / 年度阅读复盘

### `weread-visualization`

| 模式 | 回答的问题 | 状态 |
|---|---|---|
| `dashboard` | 我的阅读总体状态是什么？ | ⚠️ legacy `analysis.py`，待模块化 |
| `heatmap` | 我什么时候真正持续在读？ | ✅ 完整实现 |
| `reading-map` | 我长期关注哪些主题，它们如何相连？ | ✅ Schema + renderer |
| `cognitive-shift` | 我的兴趣和思考方式这些年怎么变化？ | ✅ Schema + renderer |
| `knowledge-graph` | 不同书中的划线、想法和主题如何形成网络？ | ✅ Schema + renderer |
| `profile` | 书架、阅读行为和划线共同呈现怎样的阅读画像？ | ✅ Schema + renderer |
| `report` | 如何生成一个可分享的周/月/年阅读报告？ | ✅ Schema + renderer |

这里的“✅ Schema + renderer”表示输出契约和稳定呈现层已经完成；主题/阶段/画像的解释仍由 Skill 基于用户本地数据生成，不把模型结论硬编码进程序。

### `weread-search`

本地全文搜索和证据召回：

- 搜书名 / 作者 / 分类
- 搜章节
- 搜划线原文
- 搜个人想法
- 按 `mark / review / book` 过滤
- 限定 `bookId`
- FTS5 + CJK substring fallback

Search 只负责找证据，不把命中结果自动包装成人格或认知结论。

### `weread-recall`

主动回忆与 Feynman 工作流：

- `recall`：用自己的话解释旧划线
- `feynman`：像给没读过这本书的人重新讲一遍
- `contrast`：用 Search 找跨书观点，比较冲突或变化
- `review` 证据可以追问“现在还认同吗”；`mark` 只表示曾关注，不能自动视为用户观点

## 可视化原则

```text
raw WeRead data
      ↓
normalized deterministic facts
      ↓
AI analysis JSON
      ↓
schema
      ↓
stable renderer
      ↓
HTML / SVG / PNG
```

1. **事实与 AI 推断分离**：阅读时长、书目、笔记数由代码计算；主题、认知转向、画像属于解释层。
2. **先结构化再渲染**：高阶可视化先生成固定 JSON，再交给 renderer，避免每次自由生成完全不同的网页。
3. **书架不等于阅读**：书架表示兴趣意图；笔记、进度、阅读时长表示真实投入。
4. **本地优先**：API Key、原始划线、个人想法和生成上下文默认不应进入公开仓库。
5. **可追溯**：高阶结论尽可能保留对应书籍、划线、时间段和反证。
6. **避免重复请求**：新可视化优先消费本地 normalized facts，而不是每个 Skill 各自重新调用微信读书。

## 统计正确性

新增确定性统计应进入 `scripts/metrics.py` 并配回归测试，不再直接散落进 renderer。

已发现 legacy `analysis.py` 的 A1 类别参与度存在书架/笔记交集重复计数问题；正确的 union-by-bookId 口径已经在 `metrics.category_participation()` 中实现并测试。旧 Dashboard 的迁移跟踪见 Issue #1。

## 隐私与仓库卫生

`.gitignore` 已默认忽略真实微信读书 JSON、Markdown、日志、生成报告、SQLite 索引和金句产物。

> 注意：`.gitignore` 只阻止**以后新增**的文件。如果个人数据已经被 Git 跟踪或提交过，需要另外执行 `git rm --cached`；如果曾经公开推送到远端并希望彻底清理历史，还需要重写 Git 历史并轮换任何可能泄露的凭据。

建议把真实数据放在仓库外：

```bash
export WEREAD_DATA_DIR="$HOME/.local/share/we-read"
```

公开仓库中的测试数据应只使用合成/脱敏 fixture。

## 测试

核心新增代码优先只使用 Python 标准库：

```bash
python -m unittest discover -s tests -v
```

GitHub Actions 同时在 Python 3.11 与 3.13 上运行测试。当前覆盖：

- Heatmap 分级边界与 `dailyReadTimes` 解析
- 私密书默认排除 / 显式包含
- Reading Map / Knowledge Graph 清洗与 HTML 输出
- Cognitive Shift 阶段归一化与 HTML 输出
- Reading Profile 事实 / 解释分层与置信度约束
- Unified Report 合并、缺失组件降级与隐私提示
- 本地全文搜索与中文 substring fallback
- Recall 队列的时间阈值、跨书多样性与原始证据延迟展示
- 金句库去重、打分和版权警告
- 类别参与度 union-by-bookId，防止重复计数

## 开源生态调研

项目对 WeRead MCP、可视化 Dashboard、Obsidian Skill、增量导出等公开实现做了能力对照。不是简单复制前端，而是吸收成熟模式：全文检索、周期切换、增量同步、USER_EDIT_ZONE、书单等。

详见 [`docs/ecosystem.md`](docs/ecosystem.md)。

## 推荐路线

1. ✅ Reading Heatmap
2. ✅ Reading Map renderer
3. ✅ Knowledge Graph renderer
4. ✅ Cognitive Shift renderer
5. ✅ Reading Profile renderer
6. ✅ Unified Reading Report
7. ✅ Local Search / Evidence Recall
8. ✅ Reading Recall / Feynman
9. Legacy `analysis.py` 模块化迁移
10. Obsidian Incremental Sync
11. Blindspot / Counter Reading
12. Booklist / Shelf Organizer / Book → Skill

更详细约定见 [`AGENTS.md`](AGENTS.md)、[`docs/ecosystem.md`](docs/ecosystem.md) 与 [`.workbuddy/skills/weread-visualization/references/visualization-spec.md`](.workbuddy/skills/weread-visualization/references/visualization-spec.md)。
