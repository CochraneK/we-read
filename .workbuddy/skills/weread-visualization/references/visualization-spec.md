# WeRead Visualization Spec

## 1. 设计目标

让不同可视化 Skill 共享同一事实层、同一证据模型和同一输出约束，避免：

- 同一数据在不同页面计算结果不一致
- AI 自由生成页面导致结构漂移
- 把兴趣、书架、真实阅读混为一谈
- 把模型推断伪装成客观事实

## 2. 统一事实模型

### book
- bookId
- title
- author
- category
- secret
- readUpdateTime
- progress
- totalReadTime

### note
- bookId
- type: mark | review
- chapter
- text
- createTime

### reading_day
- date
- readSeconds

### evidence
- kind: book | mark | review | progress | reading_time | category
- sourceId
- bookId
- text
- timestamp
- weight

## 3. 推断模型

所有 AI 结论必须输出：

```json
{
  "label": "主题名或结论",
  "summary": "简要解释",
  "confidence": 0.0,
  "evidence": [],
  "counterEvidence": []
}
```

`confidence` 是相对置信度，不是统计概率。

## 4. Reading Map Schema

```json
{
  "version": "1",
  "nodes": [
    {
      "id": "theme-x",
      "label": "主题",
      "weight": 0,
      "tier": "core|secondary|peripheral",
      "evidence": []
    }
  ],
  "edges": [
    {
      "source": "theme-a",
      "target": "theme-b",
      "strength": 0,
      "reason": "关联原因"
    }
  ],
  "insights": []
}
```

## 5. Cognitive Shift Schema

```json
{
  "version": "1",
  "stages": [
    {
      "label": "阶段名称",
      "start": "YYYY-MM",
      "end": "YYYY-MM",
      "themes": [],
      "books": [],
      "evidence": [],
      "transition": "进入下一阶段的变化"
    }
  ]
}
```

## 6. Knowledge Graph Schema

```json
{
  "version": "1",
  "nodes": [
    {
      "id": "node-id",
      "type": "book|theme|concept|quote|review",
      "label": "显示名",
      "weight": 0
    }
  ],
  "edges": [
    {
      "source": "a",
      "target": "b",
      "type": "contains|supports|contrasts|related",
      "weight": 0
    }
  ]
}
```

## 7. Heatmap

Heatmap 不使用 AI 推断，是纯确定性视图。

建议分级：
- 0：无阅读
- 1：1–10 分钟
- 2：10–30 分钟
- 3：30–60 分钟
- 4：60 分钟以上

阈值允许后续按分位数自动调整，但必须在页面注明。

## 8. Profile

画像必须明确区分：

### facts
客观统计，例如：
- 阅读时长
- 有笔记书数
- 划线数量
- 分类分布
- 最近活跃主题

### interpretations
模型推断，例如：
- 关注结构性问题
- 偏好跨领域连接
- 更倾向通过批注而非高亮表达

禁止：
- 医学 / 心理诊断
- 确定人格类型断言
- 仅凭书架推断政治、宗教等敏感属性

## 9. 视觉输出

每个 renderer 应做到：

- 单 HTML 可离线打开优先
- 数据与样式分离
- 手机端可阅读
- SVG 优先用于网络图、时间轴
- 图表标题必须表达“看到了什么”
- tooltip 展示原始证据，而不仅是抽象标签
- 导出 PNG 时保证字体和布局不裁切

## 10. 证据覆盖率

每个高阶报告增加：

- 参与分析书籍数
- 有笔记书籍数
- 有进度书籍数
- 有阅读时长日期数
- 未知 / 缺失字段数量

避免用户把“不完整数据上的推断”误当作完整画像。

## 11. 与 analysis.py 的边界

`analysis.py` 继续负责：

- 类别参与度
- 作者集中度
- 参与人格分型
- 私密 / 公开对比
- 阅读时间线
- 其他已有统计项

`weread-visualization` 不复制这些计算。

它只消费这些统计结果或底层事实，进一步形成：

- Heatmap
- Reading Map
- Cognitive Shift
- Knowledge Graph
- Reading Profile
- Unified Report
