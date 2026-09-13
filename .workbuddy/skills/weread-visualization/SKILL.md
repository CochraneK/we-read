---
name: weread-visualization
description: 微信读书高阶可视化与认知分析 Skill。基于现有导出数据和底层 weread 能力生成阅读热力图、阅读版图、认知变迁、知识图谱、阅读画像与周期报告。强调“事实统计由程序计算、AI 只做解释型推断”，并要求所有高阶可视化先生成固定 JSON，再交给模板或渲染器。当用户说“做阅读可视化”“阅读热力图”“阅读地图”“知识图谱”“认知变化”“阅读画像”“年度报告”“可视化我的微信读书”时触发。
---

# weread-visualization

## 定位

本 Skill 不重复 `scripts/analysis.py` 已经完成的基础统计图，而是负责更适合 AI 的解释型视觉结果。

- `analysis.py` = 确定性统计层
- `build_visualization_context.py` = 统一事实层
- 本 Skill = AI 解释层
- `scripts/renderers/` = 稳定渲染层

## 优先复用本地数据

优先读取：

- `data/weread_shelf.json`
- `data/weread_notes_export.json`
- `data/weread_readdata.json`
- `data/weread_progress.json`
- `data/weread_bookinfo.json`
- `quote_lib/金句库.json`

只有本地数据缺失或过期时，才调用底层微信读书 Skill / Agent Gateway。不得为了一个可视化重复拉取已经存在的数据。

## 标准入口

除纯确定性 Heatmap 外，解释型可视化第一步统一运行：

```bash
python scripts/build_visualization_context.py
```

得到 `data/analysis/visualization_context.json`。默认排除 `secret=1` 的书。只有用户明确要求在**本地私密分析**中包含私密书时，才允许：

```bash
python scripts/build_visualization_context.py --include-private
```

不得把含私密书的上下文提交到 Git 或用于公开报告。

## 模式

### dashboard

在已有 `analysis.py` 看板基础上给出高层概览，不重新实现 16 项统计。

### heatmap

用每日阅读时长生成 GitHub contribution 风格热力图。数据来自年度 `dailyReadTimes`，不使用 AI 推断。

```bash
python scripts/renderers/heatmap.py
```

输出 `data/analysis/reading_heatmap.html`。

### reading-map

回答“我长期到底在关注什么”。

1. 读取 `data/analysis/visualization_context.json`
2. 按 `references/visualization-spec.md` 的证据规则提炼跨书主题
3. 生成严格符合 `schemas/reading_map.schema.json` 的 JSON
4. 写入 `data/analysis/reading_map.json`
5. 运行：

```bash
python scripts/renderers/network.py --kind reading-map
```

输出 `data/analysis/reading_map.html`。

主题节点必须包含 `id`、`label`、`weight`、`tier`、`confidence`、`evidence`，可选 `counterEvidence`。`tier` 只能是 `core | secondary | peripheral`。边必须有真实关联依据，禁止为了图好看而连接。

### cognitive-shift

回答“我的阅读兴趣和思考方式是怎么变过来的”。

1. 读取 `visualization_context.json` 中的年度统计、书籍、笔记时间戳和阅读证据
2. 优先按**主题结构变化**识别阶段，不按自然年机械切割
3. 连续年份主题结构近似时合并为同一阶段
4. 每个阶段保留时间范围、主导主题、代表书籍、代表证据、转向依据和置信度
5. 生成符合 `schemas/cognitive_shift.schema.json` 的 JSON
6. 写入 `data/analysis/cognitive_shift.json`
7. 运行：

```bash
python scripts/renderers/timeline.py
```

输出 `data/analysis/cognitive_shift.html`。

阶段不是人格诊断。证据无法支撑明确“转向”时，应写成“延续/轻微变化”并降低 `confidence`，不得为了故事性强行制造转折。

### knowledge-graph

构建：

```text
Book → Theme → Concept → Quote / Review
```

1. 读取 `visualization_context.json`
2. 先找跨书重复概念，再聚合主题
3. 生成符合 `schemas/knowledge_graph.schema.json` 的 JSON
4. 写入 `data/analysis/knowledge_graph.json`
5. 运行：

```bash
python scripts/renderers/network.py --kind knowledge-graph
```

输出 `data/analysis/knowledge_graph.html`。

节点类型限制为 `book | theme | concept | quote | review`；边类型限制为 `contains | supports | contrasts | related`。主题优先来自跨书重复概念，而不是简单把微信读书 `category` 当成主题。

### profile

生成阅读画像，但禁止把弱证据包装成确定人格诊断。画像表述应优先使用“数据显示……”“可能反映……”“从这些阅读行为看……”，而不是“你就是……”。

### report

组合现有统计图和解释型结果形成周/月/年报告。优先复用 `reading_dashboard.html`、`reading_heatmap.html`、Reading Map、Cognitive Shift、Knowledge Graph 的关键洞察，不重新计算一套口径不同的指标。

## 强制分析规则

1. 书架表示兴趣意图，不能直接当作“读过”。
2. 真实投入至少结合：阅读时长 / 进度 / 笔记 / 想法。
3. `readUpdateTime == 0` 视为未打开或缺失行为证据。
4. 主题结论至少引用 2 个不同证据源；跨书主题优先要求来自 3 本以上书。
5. 所有数值必须来自代码计算或原始数据，禁止模型心算估值。
6. AI 不得生成不存在的书名、划线或阅读日期。
7. 私密书籍和私密笔记默认不进入公开报告。
8. 对每个高阶结论尽量保留 `counterEvidence`，避免只挑支持结论的材料。
9. 证据不足时降低 `confidence`，不要强行补全主题。
10. 网络图边必须有语义或证据理由；禁止仅因为节点距离近而建立关系。

## 输出流程

```text
raw/local data
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

严禁直接从原始大 JSON 一步生成最终 HTML。

## 默认路由

| 用户请求 | 模式 |
|---|---|
| 阅读热力图 / 阅读日历 | heatmap |
| 我都在读什么 / 我的兴趣版图 | reading-map |
| 这几年阅读发生了什么变化 | cognitive-shift |
| 把我的书和笔记做成关系图 | knowledge-graph |
| 我的阅读能看出什么 | profile |
| 年度总结 / 阅读报告 | report |
| 做个总览 | dashboard |

## 共享规范

开始任何解释型可视化前，先读取：

- `references/visualization-spec.md`
- 对应 `schemas/*.schema.json`

Renderer 只负责呈现，不负责修正或发明 AI 分析结论。
