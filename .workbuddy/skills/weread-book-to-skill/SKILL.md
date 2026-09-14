---
name: weread-book-to-skill
description: 把用户在某本微信读书书籍中的个人划线和想法生成一个本地 evidence-backed Skill，并可进一步精炼为 3–7 步 evidence-linked 方法型 Skill。强调“划线不等于用户观点”，只使用用户自己保存的证据，不冒充整本书。当用户说“把这本书做成 skill”“以后让我能调用这本书”“把我的这本书笔记做成方法库”时触发。
---

# weread-book-to-skill

## 目标

把“读完后躺在笔记里”的内容变成以后可以再次调用的个人知识 Skill。

但这个 Skill **不是电子书副本**：

- 只使用用户自己的划线和想法；
- 划线视为“用户保存的作者原文片段”，不是用户本人观点；
- 用户自己的 review / 想法优先作为个人理解证据；
- evidence 不够时明确说不够；
- 不从模型对这本书的一般知识偷偷补全方法。

## 第一阶段：证据型 Skill

先生成统一事实层：

```bash
python scripts/build_visualization_context.py
```

按 bookId（推荐）生成：

```bash
python scripts/book_to_skill.py --book-id "BOOK_ID"
```

也可以使用唯一书名：

```bash
python scripts/book_to_skill.py --title "书名"
```

输出默认位于：

```text
data/generated-skills/weread-book-*/
├── SKILL.md
├── manifest.json
└── references/
    └── evidence.md
```

第一阶段适合回答：

- 我的笔记里这本书与当前问题有什么相关证据？
- 我当时写过什么想法？
- 哪些是划线，哪些是自己的 review？

## 第二阶段：3–7 步方法 refinement

不要直接让模型“总结出一个方法”。先生成 evidence-linked brief：

```bash
python scripts/build_book_method_brief.py \
  --context data/analysis/visualization_context.json \
  --book-id "BOOK_ID" \
  --output data/analysis/private_lab/book_method_brief.json
```

生成本地离线编辑器：

```bash
python scripts/renderers/book_method_editor.py \
  --input data/analysis/private_lab/book_method_brief.json \
  --output data/analysis/private_lab/book_method_editor.html
```

编辑器要求填写：

```text
方法名称
适用目的
3–7 个步骤
每步 action
每步 why
每步 evidenceIds
```

Evidence Pool 中：

- `user_review` = 用户自己的想法；
- `highlight` = 用户保存的来源原文；
- 每条证据都有稳定 `be-...` evidenceId。

编辑后导出 JSON，再运行 gate：

```bash
python scripts/apply_book_method_refinement.py \
  --input /path/to/weread-book-method-refinement.json \
  --output data/analysis/private_lab/book_method.json \
  --markdown data/analysis/private_lab/book_method.md
```

只有满足以下条件才算 ready：

1. 3–7 步；
2. 每一步都有 action；
3. 每一步都有 why；
4. 每一步至少绑定一个真实 evidenceId；
5. evidenceId 必须来自当前书证据池；
6. 如果有用户 review 可用，最终方法至少要使用一条 review；
7. 不允许 validator 自己填补缺失语义。

最终 `book_method.md` 可以作为生成 Skill 的 `references/method.md` 候选，但在写回前应人工看一遍是否真的可执行。

## 推荐回答结构

```text
这本书在你的个人笔记里，与当前问题最相关的是：

1. 证据
2. 你当时的理解
3. 可以怎么用
4. 如果已通过 method refinement：对应的方法步骤
5. 哪些地方证据还不够
```

## 隐私与版权

- 生成目录默认属于个人本地数据，不应提交到公开仓库。
- 不导出整本书正文。
- 不为了“上下文完整”批量复制大量连续原文。
- 对外分享 Skill 时，优先保留用户自己的方法总结，减少原始划线暴露。
- 方法步骤可以公开，但原始 evidence 是否公开需要另行决定。
