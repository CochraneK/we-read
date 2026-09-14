# Advisor Context：先算事实，再做推荐

本项目已把 `knowledge-map.md` 里的第一阶段交叉分析做成确定性脚本：

```bash
python scripts/build_visualization_context.py
python scripts/build_advisor_context.py
```

输出：

```text
data/analysis/advisor_context.json
```

对应 schema：

```text
schemas/advisor_context.schema.json
```

## 这一步解决什么

`build_advisor_context.py` 只计算事实，不推荐书：

- `deep20Plus`：笔记 ≥ 20；
- `medium10To19`：笔记 10–19；
- `light3To9`：笔记 3–9；
- `glance1To2`：笔记 1–2；
- `noNotes`：没有笔记；
- `hiddenDeepBooks`：不在书架但笔记 ≥ 10；
- `shelvedUnengagedBooks`：在书架但没有笔记；
- `recent7d / recent30d`：近期活动；
- 类别维度的书架数、笔记书数、深读书数、近期活动与 engagement rate。

Normalized context 现在明确保留：

- `inShelf`
- `inNotebook`
- `shelfReadUpdateTime`

因此不要再用“是否有标题”“是否有 privacy metadata”等旁路字段猜书来自哪里。

## 为什么 `readyForRecommendation=false`

书架类别和笔记数量只能告诉我们“读了什么、投入多深”，不能可靠告诉我们：

- 缺哪个学派 / 观点；
- 缺哪个时代 / 范式；
- 缺理论还是案例；
- 缺哪个相邻学科。

所以 `advisor_context.json` 会明确列出：

```json
"gapAxesRequiringEnrichment": [
  "school_or_viewpoint",
  "era_or_paradigm",
  "abstraction_level",
  "adjacent_discipline"
]
```

在这些轴没有补证据前，**不要直接进入推荐**。

## Advisor 正确的后续顺序

```text
advisor_context
  ↓
确定用户主题（显式主题优先；否则参考 recent/deep evidence）
  ↓
补充知识地图维度（学派 / 时代 / 抽象层次 / 相邻学科）
  ↓
识别拼图缺口
  ↓
生成候选书
  ↓
/store/search 验证微信读书当前是否上架
  ↓
排除已充分读过的书 / 标注“已加未读”旧书
  ↓
输出：为什么推荐 + 补什么缺口 + weread:// 深链
```

## 隐私

默认 `visualization_context.json` 会排除明确 `secret=1` 的书；只有用户明确使用 `--include-private` 时 Advisor Context 才能继承完整私有书目。

Advisor 的知识地图、搜索候选与推荐理由属于个性化私有分析，默认不进入公开 GitHub Pages。
