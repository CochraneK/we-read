---
name: weread-visualization
description: 微信读书高阶可视化与认知分析 Skill。基于现有导出数据和底层 weread 能力生成阅读热力图、阅读版图、认知变迁、知识图谱、阅读画像与周期报告。强调“事实统计由程序计算、AI 只做解释型推断”，并要求所有高阶可视化先生成固定 JSON，再交给模板或渲染器。当用户说“做阅读可视化”“阅读热力图”“阅读地图”“知识图谱”“认知变化”“阅读画像”“年度报告”“可视化我的微信读书”时触发。
---

# weread-visualization

## 定位

本 Skill 不重复 `scripts/analysis.py` 已经完成的基础统计图，而是负责更适合 AI 的解释型视觉结果。

现有 `analysis.py` = 确定性统计层。  
本 Skill = 解释型视觉层。

## 优先复用本地数据

优先读取：

- `data/weread_shelf.json`
- `data/weread_notes_export.json`
- `data/weread_readdata.json`
- `data/weread_progress.json`
- `data/weread_bookinfo.json`
- `quote_lib/金句库.json`

只有本地数据缺失或过期时，才调用底层微信读书 Skill / Agent Gateway。

不得为了一个可视化重复拉取已经存在的数据。

## 模式

### dashboard
在已有 `analysis.py` 看板基础上给出高层概览，不重新实现 16 项统计。

### heatmap
用每日阅读时长生成 GitHub contribution 风格热力图。数据优先来自年度 `dailyReadTimes`。

### reading-map
把主题组织为“阅读版图”。输出必须包含：

- 主题节点
- 主题权重
- 主题证据书籍
- 主题之间的关联
- 核心主题 / 外围主题
- 证据覆盖率

### cognitive-shift
按时间阶段呈现兴趣与认知转向。每个阶段必须有：

- 时间范围
- 主导主题
- 代表书籍
- 代表划线或想法
- 转向依据
- 置信度

### knowledge-graph
构建 Book → Theme → Concept → Quote/Review 图谱。

主题应优先来自跨书重复概念，而非仅按微信读书 category 分类。

### profile
生成阅读画像，但禁止把弱证据包装成确定人格诊断。画像表述应优先使用：

- “数据显示……”
- “可能反映……”
- “从这些阅读行为看……”

而不是“你就是……”。

### report
组合现有统计图和解释型结果形成周/月/年报告。

## 强制分析规则

1. 书架表示兴趣意图，不能直接当作“读过”。
2. 真实投入至少结合：阅读时长 / 进度 / 笔记 / 想法。
3. `readUpdateTime == 0` 视为未打开或缺失行为证据。
4. 主题结论至少引用 2 个不同证据源；跨书主题优先要求来自 3 本以上书。
5. 所有数值必须来自代码计算或原始数据，禁止模型心算估值。
6. AI 不得生成不存在的书名、划线或阅读日期。
7. 私密书籍和私密笔记默认不进入公开报告。

## 输出流程

```text
raw/local data
   ↓
normalized facts
   ↓
analysis JSON
   ↓
schema validation
   ↓
renderer
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

读取 `references/visualization-spec.md` 后再生成任何解释型可视化。
