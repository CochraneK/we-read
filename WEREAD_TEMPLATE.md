# WeRead Template

这是当前 `we-read` GitHub Pages 体验的**可复现模板入口**。

目标只有两个：

1. 任何人都可以用自己的微信读书导出数据生成同一套 Page；
2. 模板构建永远不覆盖仓库当前用于部署的 `site/`。

完整说明见 [`template/README.md`](template/README.md)。

## 用完全合成数据验证

不需要 API Key，也不需要任何真实个人数据：

```bash
python template/demo_data.py --output .tmp/weread-demo-data

python scripts/build_template_site.py \
  --data .tmp/weread-demo-data \
  --output .tmp/weread-demo-site \
  --include-private \
  --publish-marks

python scripts/validate_pages_output.py \
  --site .tmp/weread-demo-site \
  --data .tmp/weread-demo-data \
  --js-out .tmp/weread-demo-inline.js

node --check .tmp/weread-demo-inline.js
python -m http.server 8000 -d .tmp/weread-demo-site
```

打开 `http://localhost:8000` 即可看到由合成数据生成的完整页面。

## 用自己的数据

准备至少以下文件：

```text
weread_shelf.json
weread_notebooks.json
weread_notes_export.json
weread_readdata.json
```

然后：

```bash
python scripts/build_template_site.py \
  --data /path/to/your/weread-data \
  --output dist
```

默认不会发布 `secret=1` 书目，也不会把划线正文放入静态网站。

若你明确希望复现当前 owner Page 的完整公开 profile，可显式加：

```bash
--include-private --publish-marks
```

其中 `--publish-marks` 会把符合条件的完整划线文本写入静态 `public-marks-index.js`，因此只应在你明确愿意公开这些内容时使用。

## 不破坏当前 Page 的保证

模板 builder 会直接拒绝：

```bash
--output site
```

模板使用的是当前生产渲染模块，但输出到独立目录；最后还有一个仅作用于模板产物的去个人化适配层，会把 owner 页面里的人类可读计数字样替换成当前数据集自己的书架/划线数量。

`tests/test_template_site.py` 会在 CI 中验证：

- synthetic demo 可以完整构建；
- 生产 Page validator 通过；
- 最终内联 JavaScript 语法正确；
- owner-specific 计数不会泄漏到 demo；
- `site/index.html` 在模板构建前后 byte-for-byte 不变；
- builder 对 `site/` 输出路径硬拒绝。

`.github/workflows/template-smoke.yml` 只做上述 smoke test，**没有 Pages deploy 权限，也不会部署任何站点**。
