# we-read

把微信读书从「读过什么」变成「我在关注什么、认知如何变化，以及读过的知识现在能为我做什么」。

本仓库围绕微信读书 Agent Gateway 构建一套本地优先的导出、分析、可视化与知识复用工具链。

## 当前能力

- 全量笔记 / 划线导出
- 阅读统计、进度、书籍信息补全
- 金句筛选、去重与版权分级
- 16 项阅读分析 + Plotly 单页看板
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
      data/
        │
        ├─ scripts/analysis.py
        ├─ scripts/build_quote_lib.py
        │
        ├─ .workbuddy/skills/huashu-weread
        │
        └─ .workbuddy/skills/weread-visualization
```

## 快速开始

```bash
export WEREAD_API_KEY="wrk-..."
python scripts/export_notes.py
python scripts/fetch_enrich.py
python scripts/build_quote_lib.py

pip install plotly wordcloud
python scripts/analysis.py
```

## Skills

### yao-weread-skill
底层微信读书能力与报告生成基础。

### huashu-weread
顾问型工作流，强调「书架 × 笔记」交叉分析：

- advisor：下一本读什么
- path：某领域如何从入门读到前沿
- alchemy：把划线和想法炼成主题笔记
- review：季度 / 年度阅读复盘

### weread-visualization
高阶解释型视觉分析：

| 模式 | 回答的问题 |
|---|---|
| dashboard | 我的阅读总体状态是什么？ |
| heatmap | 我什么时候真正持续在读？ |
| reading-map | 我长期关注哪些主题，它们如何相连？ |
| cognitive-shift | 我的兴趣和思考方式这些年怎么变化？ |
| knowledge-graph | 不同书中的划线、想法和主题如何形成网络？ |
| profile | 书架、阅读行为和划线共同呈现怎样的阅读画像？ |
| report | 如何生成一个可分享的周/月/年阅读报告？ |

## 可视化原则

1. 事实与 AI 推断分离。
2. 先结构化 JSON，再渲染 HTML/SVG/PNG。
3. 书架不等于阅读：书架代表兴趣意图，笔记、进度和阅读时长代表真实投入。
4. 原始数据、本地 Key、私密划线默认不进入公开产物。
5. 高阶结论尽可能保留书籍、划线与时间证据。
6. 新可视化优先复用已有数据，不重复请求微信读书 API。

## 推荐路线

1. Reading Heatmap
2. Reading Map
3. Cognitive Shift
4. Knowledge Graph
5. Reading Profile
6. Unified Reading Report
7. Reading Recall / Feynman
8. Blindspot / Counter Reading
9. Book → Skill
10. Shelf Organizer

更详细约定见 `AGENTS.md` 与 `.workbuddy/skills/weread-visualization/references/visualization-spec.md`。
