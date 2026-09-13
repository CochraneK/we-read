---
name: weread-book-to-skill
description: 把用户在某本微信读书书籍中的个人划线和想法生成一个本地 evidence-backed Skill，用于之后的检索、复盘和应用。强调“划线不等于用户观点”，只使用用户自己保存的证据，不冒充整本书。当用户说“把这本书做成 skill”“以后让我能调用这本书”“把我的这本书笔记做成方法库”时触发。
---

# weread-book-to-skill

## 目标

把“读完后躺在笔记里”的内容变成以后可以再次调用的个人知识 Skill。

但这个 Skill **不是电子书副本**：

- 只使用用户自己的划线和想法；
- 划线视为“用户保存的作者原文片段”，不是用户本人观点；
- 用户自己的 review / 想法应优先作为个人理解证据；
- evidence 不够时明确说不够。

## 标准流程

先生成统一事实层：

```bash
python scripts/build_visualization_context.py
```

然后按 bookId（推荐）生成：

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

## 生成后的二次精炼

脚本生成的是**安全、可追溯的证据型 Skill**。如果用户还希望把它进一步提炼成“方法型 Skill”，可以在不新增外部内容的前提下：

1. 读取 `references/evidence.md`；
2. 从重复出现的用户想法中总结 3–7 个方法步骤；
3. 每个方法步骤保留对应 evidence；
4. 加入适用条件和不适用条件；
5. 明确区分“原书划线”“用户想法”“AI 提炼”。

不得把 AI 自己知道的书籍内容悄悄塞进这个 Skill。

## 隐私与版权

- 生成目录默认属于个人本地数据，不应提交到公开仓库。
- 不导出整本书正文。
- 不为了“上下文完整”批量复制大量连续原文。
- 对外分享 Skill 时，优先保留用户自己的方法总结，减少原始划线暴露。
