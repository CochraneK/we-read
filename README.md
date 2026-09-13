# we-read · WeRead Intelligence

> 把微信读书从「读过什么」，变成「我在关注什么、阅读如何迁移，以及读过的知识现在能为我做什么」。

**个人阅读档案 Page：** https://cochranek.github.io/we-read/

`we-read` 是围绕微信读书 Agent Gateway 构建的一套**本地优先、证据可追溯**的导出、分析、检索、可视化、回顾与知识复用工具链。

## 当前成品

GitHub Pages 不是项目介绍页，而是直接用仓库中的真实微信读书数据重新生成的**完整个人阅读档案**。当前页面已融合官方 Skill 与社区报告 / Dashboard / Recall / Knowledge Graph 等高价值模式，包含：

- **生涯层**：微信读书记录起点、累计阅读曲线、每年一章、2023–2026 年度透镜；
- **阅读节律**：月度趋势、每日 Heatmap、24 小时阅读时钟、星期节律、跨年份月份季节性；
- **官方档案**：`readStat`、类别 / 作者 / 出版社偏好、年度偏好书卡、勋章与里程碑；
- **投入层**：进度漏斗及覆盖率、进度 × 笔记深度散点、月度时长 × 笔记量散点、当前深读；
- **知识层**：阅读关注迁移、类别 → 书 → 作者 Knowledge Graph、跨类别桥接作者；
- **记录演化**：年度划线 / 本人想法结构变化、事实型 Reading Profile；
- **反思层**：Blindspot / Counter Reading、值得重新激活、想法写得最多的书；
- **书目层**：高投入书、阅读时长 Top、最近阅读；
- **498 本完整书架 Explorer**：按书名 / 作者 / 类别搜索，按分类 / 进度过滤，按最近阅读 / 笔记 / 进度 / 书名排序；
- 可下载的聚合 `report-data.json`。

页面遵循“**有真实字段才展示**”：例如官方 `readRate / wrReadTime / wrListenTime` 当前缓存没有有效数据时，“文字阅读 vs 听书”整块自动隐藏，不用 0 伪装成事实。

当前 Pages workflow **显式设置**：

```text
WEREAD_PAGES_INCLUDE_PRIVATE=1
```

因此线上个人档案会纳入 `secret=1` 书目的书名、作者、类别、计数和网络关系。原始划线、想法正文、本地全文搜索索引、Socratic / Feynman 私有学习内容仍不会写入 Page。

如果未来需要恢复过滤模式，只需移除或关闭该环境变量；`build_pages_report.py` 默认仍是过滤私密书的安全模式。

## Skill 生态调研

项目已系统扫描：

- `Tencent/WeChatReading` 官方 Skill；
- `awesome-weread` curated ecosystem；
- GitHub `weread skill / report / dashboard / MCP / created:>2026-06-01` 等搜索结果；
- 报告 / 可视化、Search / MCP、Recall / Socratic / Anki、Obsidian / Notion、书架整理、Book → Skill、故事化发布等主要分支。

完整能力地图、已吸收模式、观察池和“刻意只保留本地”的功能见：

**[`docs/skill-landscape.md`](docs/skill-landscape.md)**

原则不是机械复制所有仓库，而是只有新项目提供新的事实维度、长期视角、可探索性或知识再激活能力时才进入 Page。

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
        ┌───────┼──────────────────────────┐
        ▼       ▼                          ▼
 metrics.py   visualization_context   Pages deterministic layer
        │       │                          │
        │       ├─ Search                  ├─ rhythm / heatmap / career
        │       ├─ Recall / Feynman        ├─ official preference / medals
        │       ├─ Blindspot               ├─ focus shift / year lens
        │       ├─ Obsidian                ├─ knowledge network
        │       └─ Book → Skill            ├─ blindspot / recall
        │                                  └─ 498-book explorer
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

Pages 的主要组装层：

- `scripts/pages_runtime.py`：部署入口、日级数据兼容层、最终组装；
- `scripts/pages_insights.py`：默认过滤模式的深度事实；
- `scripts/pages_insights_full.py`：全量书目模式；
- `scripts/pages_enrichment.py`：官方偏好、24h 时钟、星期 / 季节节律、进度、回顾、全书架数据；
- `scripts/pages_enrich_site.py`：档案 / 时钟 / 进度 / Explorer UI；
- `scripts/pages_story_ui.py`：累计生涯、双散点、记录方式演化；
- `scripts/pages_year_lens_ui.py`：2023–2026 交互式年度透镜。

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
4. **未知不等于零**：例如当前进度只有部分书有数据，页面必须展示 coverage，而不能把缺失进度当“未读”。
5. **可追溯**：高阶结论尽量能回到书籍、时间段和确定性计数。
6. **同步不覆盖用户内容**：自动同步只管理明确标记的机器区。
7. **远端写入先预览**：任何远端修改必须先有计划和明确确认。

## 测试与 CI

```bash
python -m unittest discover -s tests -v
```

GitHub Actions 在 Python 3.11 与 3.13 上运行测试。覆盖范围包括：

- Heatmap 和真实 `monthly[*].readTimes` 日级解析；
- Pages 默认过滤 / 显式包含私密书；
- 全量深度洞察不得泄露原始划线或想法正文；
- 官方 `preferTime` 从 06:00 开始的映射；
- 官方偏好 / 勋章 / 年度偏好书字段归一化；
- 进度漏斗中“未知”与“未读”的严格分离；
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
- ✅ 真实数据 GitHub Pages 完整个人阅读档案
- ✅ 24h 时钟 / 星期节律 / 季节性 / 生涯累计曲线
- ✅ 官方偏好 / 勋章 / 年度偏好书
- ✅ 年度透镜 / 双散点 / 划线→想法年度演化
- ✅ 498 本全书架 Explorer
- ✅ Pages 全量 `secret=1` 模式
- ✅ Python 3.11 / 3.13 CI

更多设计约定见 [`AGENTS.md`](AGENTS.md)、[`docs/ecosystem.md`](docs/ecosystem.md)、[`docs/skill-landscape.md`](docs/skill-landscape.md) 和 [visualization-spec.md](.workbuddy/skills/weread-visualization/references/visualization-spec.md)。
