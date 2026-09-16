# GitHub Pages 发布

公开站点：

```text
https://cochranek.github.io/we-read/
```

部署 workflow：

```text
.github/workflows/pages.yml
```

公开范围的唯一规范见：

```text
docs/publication-policy.md
```

如果本文、README 或其他旧文档与 publication policy 冲突，以 publication policy 为准。

## 当前发布流程

当前 Page 已不是早期的纯合成 Demo，而是 **Public Reading Archive**。

workflow 会：

```text
checkout
→ build real-data public report
→ add explicitly authorized bounded public quotes
→ polish site
→ validate final public artifact
→ node --check inline JS
→ upload site/
→ deploy GitHub Pages
```

当前 workflow 显式设置：

```text
WEREAD_PAGES_INCLUDE_PRIVATE=1
WEREAD_PAGES_INCLUDE_PUBLIC_QUOTES=1
```

这意味着公开 Page 可以包含 publication policy 已授权的真实阅读事实、书目元数据和受限划线摘录。

## 不会随 Page 发布的内容

即使构建过程读取真实数据，最终 GitHub Pages artifact 仍必须排除：

- 完整 raw notes export；
- 完整 mark / review 正文；
- 用户 review / thoughts；
- 本地 Search index；
- Private Reading Lab；
- 私有 synthesis / semantic review；
- API Key 或其他凭据。

workflow 最终只上传 `site/`，并在上传前运行：

```bash
python scripts/validate_pages_output.py --js-out /tmp/we-read-pages-inline.js
node --check /tmp/we-read-pages-inline.js
```

## 划线公开边界

公开划线遵循 `docs/publication-policy.md`：

```text
source                marks/highlights only
reviews               never published by this module
max characters        90 per excerpt
max per book          1
max total             48
full raw body         remains private
```

书目隐私范围和划线公开范围是两个独立开关，不能互相推导授权。

## 仓库历史不是 Page 发布策略

Public Page 的发布许可不等于允许自动删除或重写 Git 历史。

仓库中历史遗留的个人 WeRead 数据由 Issue #2 单独跟踪。未经明确授权，不执行 destructive history rewrite。
