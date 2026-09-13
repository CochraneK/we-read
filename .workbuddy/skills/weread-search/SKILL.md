---
name: weread-search
description: 微信读书本地全文检索与证据召回 Skill。基于隐私过滤后的 visualization_context.json 建立 SQLite 索引，搜索书名、作者、分类、章节、划线和想法。适用于“我在哪本书里划过X”“找关于某主题的原文”“搜索我的微信读书笔记”“把相关划线找出来”等请求。默认不联网、不重新请求微信读书 API。
---

# weread-search

## 目标

把微信读书从“导出后只能翻 JSON”变成可检索的个人阅读证据库。

本 Skill 只负责**召回**，不负责凭空总结。需要高阶解释时，把搜索结果交给 `huashu-weread` 或 `weread-visualization`。

## 数据入口

先确保存在隐私感知的统一上下文：

```bash
python scripts/build_visualization_context.py
```

默认排除 `secret=1` 的书。只有用户明确要求本地私密分析时，才允许用 `--include-private` 重建上下文。

## 建立索引

```bash
python scripts/build_search_index.py --rebuild
```

默认输出：

```text
data/analysis/weread_search.sqlite
```

索引内容：

- 书名
- 作者
- 分类
- 章节
- 划线正文
- 想法 / 点评

SQLite FTS5 可用时使用全文索引；中文短词或 FTS 不可用时会自动回退到 substring search。

## 搜索

```bash
python scripts/build_search_index.py --query "自由"
```

只搜划线：

```bash
python scripts/build_search_index.py --query "自由" --kind mark
```

只搜想法：

```bash
python scripts/build_search_index.py --query "自由" --kind review
```

限定某本书：

```bash
python scripts/build_search_index.py --query "自由" --book-id "BOOK_ID"
```

## 回答规则

1. 先搜索，再总结；不要先凭模型印象回答。
2. 引用用户划线时必须保持对应书名和章节信息。
3. 搜索不到就明确说“当前索引未找到”，不要生成相似句子冒充原文。
4. 对主题类问题，优先召回多个不同书籍的证据，避免单书过拟合。
5. 对“我以前怎么想的”这类问题，优先使用 `review`，划线只能代表关注，不能自动代表用户认同。
6. `book` 命中只表示元数据相关；真正的思想证据应来自 `mark` 或 `review`。
7. 私密书是否进入结果完全继承 `visualization_context.json` 的隐私策略，不得在搜索层自行绕过。

## 推荐联动

### Search → Reading Map

先搜索某领域的跨书证据，再让 `weread-visualization` 组织主题关系。

### Search → Alchemy

先召回相关划线与想法，再让 `huashu-weread` 的 alchemy 模式炼成主题笔记。

### Search → Recall

搜索一段时间未回顾、但曾有高投入的内容，生成复习问题或费曼式自测。

## 不做什么

- 不把全文索引提交到公开 Git 仓库。
- 不用搜索命中次数直接推断人格。
- 不把书架收藏当成已读证据。
- 不为了搜索重新抓取 API；本地上下文过期时才刷新数据。
