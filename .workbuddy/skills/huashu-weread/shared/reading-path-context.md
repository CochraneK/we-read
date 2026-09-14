# Reading Path Context：路径规划前先确认起点

`path.md` 的 Step 1 / Step 1.5 已有确定性实现：

```bash
python scripts/build_visualization_context.py
python scripts/build_advisor_context.py
python scripts/build_reading_path_context.py --topic "神经科学" --keywords "脑,意识,认知"
```

输出：

```text
data/analysis/reading_path_context.json
```

对应 schema：

```text
schemas/reading_path_context.schema.json
```

## 当前自动判断能力

Path Context 会从 Advisor Context 的真实阅读证据里匹配主题，输出：

- topic-matched 书目；
- 有笔记书目；
- 笔记 ≥ 5 的实质阅读书目；
- 笔记 ≥ 3、最终路径里应标记“你已读”的书；
- 建议起点：`zero / beginner / intermediate`；
- 是否建议切换到 Advisor；
- 用户确认 gate。

### 为什么不会自动判 `advanced`

`path.md` 对高级的定义不仅是“读得多”，还要求前沿 / 一手文献信号。标题、类别、笔记条数无法可靠证明这一点。

因此：

- deterministic layer 最多自动建议到 `intermediate`；
- `advanced` 只能由用户明确覆盖，或后续内容 enrichment 证明；
- 笔记量不能冒充学术层级。

## Path Contract

在用户确认段位之前：

```json
"readyForBookSelection": false
```

固定保留三阶梯：

1. `intro`：建立兴趣和基础术语；
2. `framework`：建立主要学派 / 概念 / 争议框架；
3. `frontier`：看到研究边界、范式变化和未解决问题。

每阶梯强制带 Feynman checkpoint。

最终候选书层还必须满足：

- 总数 6–8 本；
- `/store/search` 验证当前微信读书上架；
- `/book/info` 或等价可靠字段获取字数后按 300 字/分钟估算；
- 已读书保留路径位置但标记并跳过；
- 入门阶段全部未上架视为失败信号；
- 提供最小版本退出路线。

## 边界

主题匹配当前是确定性 metadata matching，不等价于语义理解。若主题宽泛、冷门或书名/分类不足以匹配，应在用户确认 gate 前说明证据不足，而不是扩大关键词后静默“猜中”。
