---
name: weread-obsidian
description: 将微信读书书籍、划线和想法安全增量同步到 Obsidian。默认先 dry-run，只更新由本项目管理的同步区，永久保留 USER_EDIT_ZONE，不自动删除孤儿文件。当用户说“同步到 Obsidian”“导出到 Obsidian”“更新我的 Obsidian 微信读书笔记”时触发。
---

# weread-obsidian

## 核心原则

这个 Skill 的第一目标不是“覆盖得彻底”，而是**绝不误删用户自己的笔记**。

同步文件分成两块：

```text
WEREAD_SYNC_START ... WEREAD_SYNC_END
USER_EDIT_ZONE_START ... USER_EDIT_ZONE_END
```

程序只能重建 `WEREAD_SYNC_*` 区域；`USER_EDIT_ZONE` 必须原样保留。

## 标准工作流

1. 先确保存在隐私过滤后的统一事实层：

```bash
python scripts/build_visualization_context.py
```

2. 首次或每次批量更新前都先 dry-run：

```bash
python scripts/sync_obsidian.py \
  --vault "/path/to/your/vault" \
  --dry-run
```

3. 检查输出的 `created / updated / unchanged / skippedUnmanaged / wouldWrite`。
4. 确认无异常后再执行真实同步：

```bash
python scripts/sync_obsidian.py --vault "/path/to/your/vault"
```

默认写入 Vault 下的 `WeRead/`，可用 `--folder` 修改。

## 安全行为

- 默认继承 `visualization_context.json` 的隐私策略；该上下文默认排除 `secret=1` 的私密书。
- 已由本项目管理的文件：更新微信读书同步区，保留 USER_EDIT_ZONE。
- 同名但没有管理标记的文件：**跳过，不覆盖**。
- 只有用户明确同意接管现有文件时才使用 `--adopt-unmanaged`；接管时原文件全文会被放进 USER_EDIT_ZONE。
- 默认不删除任何 Obsidian 文件，即使它不再出现在当前微信读书上下文中。
- `.weread-sync.json` 只记录 bookId、目标文件名和内容 hash，不记录 API Key。

## 输出结构

每本书一个 Markdown：

```text
WeRead/
├── 书名 [bookId].md
├── 另一本文 [bookId].md
└── .weread-sync.json
```

每个文件包含：

- YAML 元信息
- 作者 / 分类 / 阅读进度
- 按时间排序的划线与想法
- USER_EDIT_ZONE

## 禁止事项

- 不得因为“同步更干净”而自动删除用户文件。
- 不得绕过 dry-run 直接批量接管已有文件。
- 不得从原始、未过滤的私密数据直接生成公开 Vault。
- 不得修改 USER_EDIT_ZONE 中的文字。
