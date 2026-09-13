# AGENTS.md — 微信读书项目

## 定位
把微信读书（WeRead）的阅读数据导出、分析、可视化，并从中筛选「名言警句」做成可出版的小卡片（翻转卡：正面金句、背面书封）。

## 怎么跑
环境变量：`WEREAD_API_KEY`（在 `i.weread.qq.com/api/agent/gateway` 网关侧配置）。
1. `scripts/export_notes.py` — 拉全量笔记/划线 → `data/weread_notes_export.json` + `.md`（标准库 urllib，无需第三方包）
2. `scripts/fetch_enrich.py` — 补 readdata/detail + progress + bookinfo → `data/weread_*.json`（同上）
3. `scripts/build_quote_lib.py` - 从导出 JSON 筛金句、打分去重、版权分级 → `quote_lib/金句库.json`（纯标准库）
4. `scripts/analysis.py` - 16 项分析 + 单页看板 → `data/analysis/reading_dashboard.html`（**需 `plotly` + `wordcloud`**，当前 managed venv 未装，重跑前先 `pip install`）

## 技术栈
Python 3；导出/抓取用标准库 `urllib`；分析用 `plotly` + `wordcloud`；卡片为纯静态 HTML/CSS（CSS 3D 翻转，无框架）。

## 目录与约定
- `data/` — 原始/中间数据（7 个 `weread_*.json` + `weread_notes_export.md`）；`data/analysis/` 分析产物
- `quote_lib/` — 交付物：`cards.html`（351 张翻转卡）、`cards_package.zip`、`金句库.json`、`金句库_top60.md`、`design-tokens.md`、`使用说明.txt`；`.backups/` 收历史 cards.html 副本
- `reports/generated/real-report/` — 真实数据报告（282 本笔记本、26 图）；`ai-founder-sample` 已删
- `scripts/` — 构建脚本（纯代码，数据读写统一走 `../data/`）
- `.workbuddy/skills/` — `yao-weread-skill`（v1.0.4，真实报告用它生成）、`huashu-weread`（顾问型）

## 当前状态 / 下一步
- 已闭环：文件整理（根目录收进 4 文件夹）、翻转卡交付、真实报告生成、yao skill 版本门修复（1.0.3→1.0.4）
- 待办：analysis.py 依赖安装；卡片封面离线化（现引用在线 `cdn.weread.qq.com`）；报告导出 PDF/PPTX
- 详细日志见 `.workbuddy/memory/`
