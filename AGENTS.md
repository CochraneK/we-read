# AGENTS.md — 微信读书项目

## 定位

把微信读书（WeRead）的阅读数据导出、分析、可视化，并把长期阅读转化为可追溯的阅读版图、认知轨迹、知识网络与可复用知识；同时保留「金句卡片」这条出版素材工作流。

## 核心原则

1. **事实与解释分层**：时长、进度、书目、笔记数由代码确定性计算；主题、认知转向、画像属于 AI 解释层。
2. **书架不等于阅读**：书架是兴趣意图，笔记、进度、阅读时长才是投入证据。
3. **先 JSON，后 renderer**：解释型可视化必须先生成固定 Schema JSON，再交给稳定 renderer；禁止从原始大 JSON 一步自由生成最终 HTML。
4. **本地优先**：真实书架、划线、想法、API Key、生成报告默认不进入公开 Git。
5. **证据可追溯**：高阶结论尽量保留书籍、划线、时间段、置信度和反证。
6. **不重复拉 API**：优先复用本地数据和 `visualization_context.json`。

## 环境变量

- `WEREAD_API_KEY`：微信读书 Agent Gateway Key。
- `WEREAD_DATA_DIR`：可选，真实数据目录；推荐设置到仓库外。
- `WEREAD_MONTHLY_HISTORY_MONTHS`：可选，月度统计回溯月数，默认 48。
- `WEREAD_START_YEAR`：可选，强制年度统计起始年；默认自动发现。

推荐：

```bash
export WEREAD_DATA_DIR="$HOME/.local/share/we-read"
```

## 标准数据流水线

```bash
python scripts/export_notes.py
python scripts/fetch_enrich.py
python scripts/build_visualization_context.py
```

主要本地数据：

- `weread_shelf.json`
- `weread_notes_export.json`
- `weread_readdata.json`
- `weread_progress.json`
- `weread_bookinfo.json`
- `analysis/visualization_context.json`

## 确定性可视化

阅读热力图：

```bash
python scripts/renderers/heatmap.py
```

现有 16 项 Plotly 分析：

```bash
python -m pip install -r requirements-analysis.txt
python scripts/analysis.py
```

`analysis.py` 继续负责已有统计，不要把 Reading Map / Knowledge Graph / Cognitive Shift 再塞回这个大脚本。

## 解释型可视化

统一 Skill：`.workbuddy/skills/weread-visualization/`

工作顺序：

```text
visualization_context.json
        ↓
AI 按对应 schema 生成 analysis JSON
        ↓
稳定 renderer
        ↓
HTML
```

对应关系：

- Reading Map → `schemas/reading_map.schema.json` → `scripts/renderers/network.py --kind reading-map`
- Knowledge Graph → `schemas/knowledge_graph.schema.json` → `scripts/renderers/network.py --kind knowledge-graph`
- Cognitive Shift → `schemas/cognitive_shift.schema.json` → `scripts/renderers/timeline.py`

## 金句库

```bash
python scripts/build_quote_lib.py
```

默认读取 `WEREAD_DATA_DIR/weread_notes_export.json`，输出到 `quote_lib/`。

`public_domain` 是历史兼容字段：值为 `pd` 也只表示“规则筛出的版权人工复核候选”，绝不是法律结论。出版、印刷、公开传播之前必须人工确认作品、版本、译本与地区权利状态。

## Skills

- `.workbuddy/skills/yao-weread-skill`：底层微信读书能力 / 报告基础。
- `.workbuddy/skills/huashu-weread`：推荐、学习路径、笔记炼金、阅读复盘。
- `.workbuddy/skills/weread-visualization`：Heatmap / Reading Map / Cognitive Shift / Knowledge Graph / Profile / Report。

## 测试

核心新增代码优先保持 Python 标准库依赖：

```bash
python -m unittest discover -s tests -v
```

GitHub Actions 在 Python 3.11 与 3.13 上执行测试。新增 renderer、数据清洗规则、隐私规则时必须补回归测试。

## 隐私与公开仓库规则

- `.env`、API Key 不进 Git。
- `data/weread_*.json`、`data/weread_*.md`、日志、`data/analysis/` 默认不进 Git。
- `reports/generated/`、真实金句库、真实卡片默认不进 Git。
- 测试只能使用合成或充分脱敏数据。
- `.gitignore` 不会自动取消已经被 Git 跟踪的历史文件；如发现真实个人数据已在公开历史中，需单独处理 Git 跟踪和历史清理。

## 目录职责

```text
scripts/
  export_notes.py                 原始笔记/划线导出
  fetch_enrich.py                 阅读统计/进度/书籍信息
  build_visualization_context.py  统一事实层
  build_quote_lib.py              金句候选库
  analysis.py                     旧有 16 项统计看板
  renderers/
    heatmap.py                     确定性热力图
    network.py                     Reading Map / Knowledge Graph
    timeline.py                    Cognitive Shift
schemas/                           解释层输出契约
tests/                             合成数据回归测试
.workbuddy/skills/                 Agent Skills
quote_lib/                         金句卡片相关代码/产物
reports/                           报告相关资产；真实生成物不公开
```

## 下一阶段优先级

1. Reading Profile Schema + renderer
2. Unified Reading Report（聚合 dashboard / heatmap / map / shift / graph）
3. `analysis.py` 拆分成 loader / metrics / renderer，降低单文件耦合
4. Reading Recall / Feynman
5. Blindspot / Counter Reading
6. Book → Skill
7. Shelf Organizer（任何写操作必须 dry-run + 明确确认 + 执行后核验）
