# we-read · WeRead Intelligence

> 把微信读书从「读过什么」，变成「我在关注什么、阅读如何迁移，以及读过的知识现在能为我做什么」。

**个人阅读档案 Page：** https://cochranek.github.io/we-read/

`we-read` 是围绕微信读书 Agent Gateway 构建的一套**本地优先、证据可追溯**的导出、分析、检索、可视化、回顾与知识复用工具链。

## 当前成品

GitHub Pages 不是项目介绍页，而是直接用仓库中的真实微信读书数据重新生成的个人阅读档案。当前页面包含：

- 多年月度阅读时长与笔记趋势；
- 每日阅读热力图、年度汇总、最长连续阅读；
- 类别与作者投入分布；
- 阅读关注迁移：比较年度笔记占比变化，不把统计变化包装成人格或心理结论；
- 阅读版图与跨书知识网络：类别 → 高投入书 → 作者；
- 跨类别桥接作者；
- 事实型 Reading Profile；
- 书架盲点与 Counter Reading：寻找“收藏很多但实际投入较低”的类别；
- 高投入书目、阅读时长 Top、最近阅读；
- 可下载的聚合 `report-data.json`。

当前 Pages workflow **显式设置**：

```text
WEREAD_PAGES_INCLUDE_PRIVATE=1
```

因此线上个人档案会纳入 `secret=1` 书目的书名、作者、类别、计数和网络关系。原始划线、想法正文和本地全文搜索索引仍不会写入 Page。

如果未来需要恢复过滤模式，只需移除或关闭该环境变量；`build_pages_report.py` 默认仍是过滤私密书的安全模式。

## 已完成能力

- 全量笔记 / 划线导出；
- 阅读统计、进度、书籍信息补全；
- GitHub-style 阅读热力图；
- Reading Map / Knowledge Graph；
- Cognitive Shift 时间轴；
- Evidence-based Reading Profile；
- Unified Reading Report；
- SQLite 本地全文检索，含中文 substring fallback；
- Reading Recall / Feynman 主动回顾；
- Blindspot / Counter Reading；
- Obsidian 安全增量同步，永久保护 `USER_EDIT_ZONE`；
- Book → Skill；
- Shelf Organizer / Booklist Plan，默认 plan-only；
- 金句筛选、去重和版权人工复核提示；
- Legacy 16 项 Plotly Dashboard；
- GitHub Pages 真实个人阅读档案；
- Python 3.11 / 3.13 CI。

## 核心架构

```text
WeRead Agent Gateway
        │
        ├─ export_notes.py
        └─ fetch_enrich.py
                │
                ▼
          raw local facts
                │
        ┌───────┼──────────────────────┐
        ▼       ▼                      ▼
 metrics.py   visualization_context   Pages deterministic layer
        │       │                      │
        │       ├─ Search              ├─ reading rhythm / heatmap
        │       ├─ Recall / Feynman    ├─ focus shift
        │       ├─ Blindspot           ├─ knowledge network
        │       ├─ Obsidian            ├─ blindspot / counter reading
        │       └─ Book → Skill        └─ investment profile
        │
        ▼
 stable schemas + renderers
```

项目原则：

```text
事实由程序计算
      ↓
解释型推断保留证据与不确定性
      ↓
固定 Schema
      ↓
稳定 Renderer / Page
```

## 快速开始

### 1. 拉取数据

```bash
export WEREAD_API_KEY="wrk-..."
export WEREAD_DATA_DIR="$HOME/.local/share/we-read"

python scripts/export_notes.py
python scripts/fetch_enrich.py
```

`fetch_enrich.py` 自动发现年度范围，月度详情默认拉取最近 48 个自然月：

```bash
export WEREAD_MONTHLY_HISTORY_MONTHS=72
```

### 2. 建立统一事实层

```bash
python scripts/build_visualization_context.py
```

默认排除 `secret=1`。只有明确需要完整本地分析时：

```bash
python scripts/build_visualization_context.py --include-private
```

### 3. 阅读热力图

```bash
python scripts/renderers/heatmap.py
```

输出：

```text
data/analysis/reading_heatmap.html
```

### 4. Legacy Dashboard

```bash
python -m pip install -r requirements-analysis.txt
python scripts/analysis.py
```

### 5. 高阶可视化

```bash
python scripts/renderers/network.py --kind reading-map
python scripts/renderers/network.py --kind knowledge-graph
python scripts/renderers/timeline.py
python scripts/renderers/profile.py
python scripts/renderers/report.py
```

解释型结果遵循 `schemas/` 下的固定 JSON Schema；缺失组件不会由 renderer 伪造。

### 6. 本地全文检索

```bash
python scripts/build_search_index.py --rebuild
python scripts/build_search_index.py --query "自由"
python scripts/build_search_index.py --query "自由" --kind review
```

### 7. Recall / Feynman

```bash
python scripts/build_recall_queue.py --min-age-days 90 --limit 10 --max-per-book 1
python scripts/renderers/recall.py
```

回顾队列优先旧证据、控制单书占比，同龄证据中优先用户自己的 review；卡片先要求回忆，再展开证据。

### 8. Blindspot / Counter Reading

```bash
python scripts/build_blindspot_context.py
python scripts/renderers/blindspot.py
```

“盲点”只表示阅读集中、投入落差或值得核对的缺失视角，不是人格诊断。

### 9. Obsidian 安全增量同步

```bash
python scripts/sync_obsidian.py --vault "/path/to/vault" --dry-run
python scripts/sync_obsidian.py --vault "/path/to/vault"
```

安全边界：机器只覆盖 `WEREAD_SYNC_START ... WEREAD_SYNC_END`，`USER_EDIT_ZONE` 永久保留；非托管同名文件默认跳过，不自动删除孤儿笔记。

### 10. Book → Skill

```bash
python scripts/book_to_skill.py --book-id "BOOK_ID"
```

生成结果明确区分：

- **我的划线**：保存的原文，不代表用户本人观点；
- **我的想法**：用户自己的 review；
- **AI 提炼**：后续建立在证据上的总结。

### 11. Shelf Organizer / Booklist

```bash
python scripts/plan_shelf_organization.py --strategy hybrid
```

当前只生成可审核计划，明确记录：

```json
"remoteMutationPerformed": false
```

不会调用未文档化接口修改远端微信读书书架。

## Pages 构建

本地默认安全模式：

```bash
python scripts/pages_runtime.py
```

完整个人档案模式：

```bash
WEREAD_PAGES_INCLUDE_PRIVATE=1 python scripts/pages_runtime.py
```

输出：

```text
site/index.html
site/report-data.json
```

线上 `.github/workflows/pages.yml` 当前显式使用完整个人档案模式。

Pages 的深度结果由确定性程序生成：

- `scripts/pages_insights.py`：过滤私密书模式；
- `scripts/pages_insights_full.py`：显式全量模式；
- `scripts/pages_runtime.py`：部署入口、日级数据兼容层和最终页面组装。

## Skills

| Skill | 作用 |
|---|---|
| `yao-weread-skill` | 微信读书底层能力 / 报告基础 |
| `huashu-weread` | advisor / path / alchemy / review |
| `weread-visualization` | Heatmap / Map / Shift / Graph / Profile / Report |
| `weread-search` | 本地全文检索与证据召回 |
| `weread-recall` | Recall / Feynman / Contrast |
| `weread-blindspot` | Blindspot / Counter Reading |
| `weread-obsidian` | 安全增量同步到 Obsidian |
| `weread-book-to-skill` | 单本书个人笔记 → evidence-backed Skill |
| `weread-organizer` | 本地书架整理与书单计划 |

## 设计边界

1. **书架不等于阅读**：书架表示兴趣或收藏，笔记、进度、阅读时长才是投入证据。
2. **事实与解释分离**：数值由代码计算；解释层不得伪造书、日期、引用或确定性心理标签。
3. **不公开原始正文**：Pages 即使开启全量书目模式，也只发布聚合统计与书目元数据。
4. **可追溯**：高阶结论尽量能回到书籍、时间段和确定性计数。
5. **同步不覆盖用户内容**：自动同步只管理明确标记的机器区。
6. **远端写入先预览**：任何远端修改必须先有计划和明确确认。

## 测试与 CI

```bash
python -m unittest discover -s tests -v
```

GitHub Actions 在 Python 3.11 与 3.13 上运行测试。覆盖范围包括：

- Heatmap 和真实 `monthly[*].readTimes` 日级解析；
- Pages 默认过滤 / 显式包含私密书；
- 全量深度洞察不得泄露原始划线或想法正文；
- Reading Map / Knowledge Graph；
- Cognitive Shift；
- Reading Profile；
- Unified Report；
- Search / Recall / Blindspot；
- Obsidian `USER_EDIT_ZONE`；
- Book → Skill；
- Shelf Planner；
- 金句库；
- category union-by-bookId 防重复计数。

## Legacy 维护

`scripts/metrics.py` 已实现正确的 union-by-bookId 类别统计，并有回归测试。Legacy `analysis.py` 的 A1 模块仍应逐步迁移到共享 metrics；跟踪见 Issue #1。

仓库历史中已经存在真实个人阅读数据。`.gitignore` 只能阻止后续新增；若未来要从 Git 历史彻底移除，需要单独备份并重写历史。该操作是破坏性的，不自动执行。

## 状态

- ✅ 数据导出与补全
- ✅ Heatmap / Reading Map / Knowledge Graph
- ✅ Cognitive Shift / Reading Profile / Unified Report
- ✅ Search / Recall / Feynman
- ✅ Blindspot / Counter Reading
- ✅ Safe Obsidian Sync
- ✅ Book → Skill
- ✅ Shelf Organizer / Booklist Plan
- ✅ 真实数据 GitHub Pages 个人阅读档案
- ✅ Pages 全量 `secret=1` 模式
- ✅ Python 3.11 / 3.13 CI

更多设计约定见 [`AGENTS.md`](AGENTS.md)、[`docs/ecosystem.md`](docs/ecosystem.md) 和 [visualization-spec.md](.workbuddy/skills/weread-visualization/references/visualization-spec.md)。
