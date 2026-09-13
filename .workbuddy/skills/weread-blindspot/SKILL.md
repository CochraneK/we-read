---
name: weread-blindspot
description: 基于微信读书的确定性覆盖数据寻找可能的阅读集中、投入落差和需要反例验证的区域，并生成 Counter Reading 方向。当用户说“我的阅读盲点”“找反例”“我是不是读得太偏”“给我反向阅读建议”“挑战我的阅读结构”时触发。
---

# weread-blindspot

## 定位

这个 Skill 不是人格诊断器，也不负责证明用户“偏见很重”。它只做两件事：

1. 从确定性数据里找值得核对的集中度 / 参与度信号；
2. 把这些信号转换成**可证伪的问题和反向阅读方向**。

## 标准工作流

先生成统一事实层：

```bash
python scripts/build_visualization_context.py
python scripts/build_blindspot_context.py
```

读取：

```text
data/analysis/blindspot_context.json
```

然后生成严格符合：

```text
schemas/blindspot.schema.json
```

的：

```text
data/analysis/blindspot.json
```

最后渲染：

```bash
python scripts/renderers/blindspot.py
```

输出：

```text
data/analysis/blindspot.html
```

## 允许使用的信号

- 某分类在真正有笔记书中的占比明显集中；
- 某分类书架数量很多，但有笔记书比例很低；
- 大量书长期停留在极低进度且没有任何笔记；
- Reading Map 中核心主题长期高度集中；
- 用户自己的想法里某个论点反复出现，但存在明显反证或例外。

## 每个 blindspot 必须包含

- `label`
- `summary`
- `confidence`
- `evidence`
- `counterEvidence`（若存在）
- `counterReadingDirections`
- `questions`（建议提供）

## Counter Reading 规则

反向阅读不是“推荐完全相反立场的书”这么简单。优先给以下方向：

1. 同一问题的不同学科解释；
2. 能推翻或限制当前核心论点的证据类型；
3. 当前书单里被忽略的利益相关者 / 时间尺度 / 因果方向；
4. 理论与经验研究之间的冲突；
5. 经典观点与最新证据之间的张力。

如果要进一步推荐具体书籍，应单独进行公开图书检索，并说明为什么它能提供反例；不得编造书名。

## 表述要求

使用：

- “当前数据可能显示……”
- “值得核对的是……”
- “一个反例方向是……”

避免：

- “你就是信息茧房”
- “你缺乏某种人格特质”
- 根据阅读记录推断政治、宗教、健康等敏感属性

## 证据规则

- 单一本书不能支撑“长期盲点”。
- 结论至少引用两个不同证据点。
- 集中并不等于问题，必须保留“可能是有意专业化”的反证。
- 元数据不完整时降低 `confidence`。
