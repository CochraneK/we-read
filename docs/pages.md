# GitHub Pages 一次性启用

公开 Page 源码已经位于：

```text
site/index.html
```

部署 workflow 已经位于：

```text
.github/workflows/pages.yml
```

它只会上传 `site/`，不会把 `data/`、个人划线、搜索索引或生成 Skill 放进公开站点。

## 为什么第一次还需要一个仓库设置

GitHub Pages 在第一次发布前要求仓库管理员先选择 publishing source。

本仓库的 workflow 已尝试使用 `actions/configure-pages` 自动启用，但 GitHub 返回：

```text
Create Pages site failed: Resource not accessible by integration
```

这表示 workflow 的 `GITHUB_TOKEN` 有部署 Pages 的权限，但当前 GitHub App / workflow token 没有替仓库执行“首次创建 Pages site”的管理权限。

## 只需做一次

打开：

```text
CochraneK/we-read → Settings → Pages
```

在 **Build and deployment → Source** 选择：

```text
GitHub Actions
```

不需要创建新 workflow；仓库里已经有 `.github/workflows/pages.yml`。

启用后，重新运行 `pages` workflow（或对 `site/` / `pages.yml` 做一次提交）即可部署。

目标地址：

```text
https://cochranek.github.io/we-read/
```

## 当前 Page 内容

- WeRead Intelligence 产品介绍
- Collect → Normalize → Analyze → Interpret → Reuse 架构
- 合成 Reading Heatmap Demo
- 合成 Reading Map Demo
- Cognitive Shift 时间轴 Demo
- Visualize / Search / Recall / Blindspot / Obsidian / Book→Skill 功能卡
- 快速开始命令
- 本地优先与隐私边界

所有演示数据均为合成数据，不读取仓库中历史遗留的真实阅读数据。
