# Alchemy Context：私有证据包

Alchemy 的第一阶段已经有确定性实现：

```bash
# 单书
python scripts/build_alchemy_context.py --book-id "BOOK_ID"

# 跨主题
python scripts/build_alchemy_context.py --topic "神经科学" --keywords "脑,意识,认知"
```

输出：

```text
data/analysis/alchemy_context.json
```

对应 schema：

```text
schemas/alchemy_context.schema.json
```

## 关键边界

这个 artifact **包含原始划线和用户 review**，因此：

```json
"containsRawEvidence": true,
"publicPageSafe": false
```

绝不能接入公开 GitHub Pages 或 `report-data.json`。

## 单书模式

脚本会：

- 精确定位书；模糊命中多本时要求 `bookId`；
- 把 mark 标成 `source_text`；
- 把 review 标成 `user_thought`；
- 按章节分别聚合 marks / reviews；
- 给出 evidence count，但不自动写“用户相信什么”。

后续 synthesis 才负责：

1. 从证据提炼 3–5 个核心论点；
2. 对照作者原文与用户自己的 review；
3. 找未解决问题；
4. 生成读书笔记，而不是把所有划线重新导出一遍。

## 跨主题模式

脚本只负责确定性选书和证据 landscape。若证据量超过 gate threshold，输出：

```json
"requiresScopeConfirmation": true,
"readyForSynthesis": false
```

此时应先让用户选择重点子议题，再做 AI 主题聚类。

聚类标准必须是“议题”，而不是简单按书名或章节拼接。

## 证据角色

必须始终保持：

```text
mark   → 作者/原文证据，不等于用户观点
review → 用户自己的想法证据
```

如果后续生成“我和作者的对话”，只能从 review 与对应原文证据关系中推出，不能替用户编造赞同、反驳或行动改变。
