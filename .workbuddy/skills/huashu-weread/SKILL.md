---
name: huashu-weread-advisor
description: 微信读书高阶顾问。在底层 weread skill 的原子 API 之上，提供四类工作流：基于已读做个性化进阶推荐（advisor）、给方向规划入门到前沿的阶梯书单（path）、把零散划线想法提炼成读书笔记总结（alchemy）、做季度/年度阅读复盘并生成可发朋友圈/公众号的文章（review）。核心方法是「书架 + 笔记交叉分析」——书架揭示用户主动分类的兴趣，笔记数据揭示「真读过的」vs「只放着的」。当用户说「推荐书」「下一本读啥」「该读什么」「想搞懂 X 这个领域」「整理我的笔记」「这本书我记住了啥」「我今年读了什么」「读书复盘」「年度盘点」时触发。即使用户只是说「不知道读啥」「有没有相关的书」「帮我看看这本读完了吗」「这个领域我入门了吗」也应触发。
---

# huashu-weread-advisor

把原子的微信读书 API 变成一个真正读懂阅读证据的读书顾问。

## 定位

底层 weread skill 提供搜索、书架、笔记、点评、推荐、阅读统计等原子接口；本 skill 负责工作流编排，把数据转成有证据的推荐、学习路径、笔记提炼和阅读复盘。

## 前置依赖与版本规则

- 需要 `WEREAD_API_KEY` 环境变量。
- API 走 `POST https://i.weread.qq.com/api/agent/gateway`。
- 请求 body 必须带 `skill_version`。
- **版本值不要从本文件、旧 prompt 或示例代码硬抄。**如果本机安装了官方 weread skill，以其 `SKILL.md` frontmatter 的 `version` 为权威；本仓库当前 API 脚本基线为 `1.0.4`，未来仍可能升级。
- 收到 `upgrade_info` 时必须停止当前步骤、按服务端提示升级后重试，不能静默忽略。

## 核心方法论

### 1. 书架、笔记、进度、最近活动必须交叉

| 数据源 | 主要接口 | 揭示什么 |
|---|---|---|
| 书架 | `/shelf/sync` | 主动收藏/分类的兴趣方向 |
| 笔记 | `/user/notebooks` | 真正形成阅读证据的书与深度 |
| 进度 | `/book/getprogress` | 当前进度、累计时长 |
| 统计 | `/readdata/detail` | 周/月/年节律与官方偏好 |

关键点：书架不等于读过；没有放进书架的借阅/试读书也可能形成深读证据。公开文档和示例不要使用可识别个人的真实阅读记录，统一使用匿名或合成示例。

### 2. 最近兴趣和历史书架主题分开

未指定主题时，可以把 `readUpdateTime` 最近 7/30 天作为优先信号；用户明确指定主题时，**用户主题优先于最近活动**，最近活动只作为次要观察。

### 3. 推荐前验证微信读书当前是否上架

用 `/store/search` 验证。上架后再给 `weread://reading?bId={bookId}`；未上架时明确说明并提供合法替代路径。绝不推荐盗版来源。

### 4. 推荐必须解释证据

每本候选至少说明：

- 基于哪些已读/深读证据；
- 要补哪个知识缺口；
- 是否已经在书架或已经读过；
- 是否在微信读书当前上架。

## 确定性事实层

不要每次从原始 JSON 临时拼判断。本仓库已经把部分共用判断做成稳定 context：

```bash
python scripts/build_visualization_context.py
python scripts/build_advisor_context.py
```

见：

- [`shared/advisor-context.md`](shared/advisor-context.md)
- `schemas/advisor_context.schema.json`

Path 的起点判断另有：

```bash
python scripts/build_reading_path_context.py --topic "主题" --keywords "别名1,别名2"
```

见 [`shared/reading-path-context.md`](shared/reading-path-context.md)。

这些 context **只提供事实与流程契约，不直接推荐书**。

## 检查点设计原则

只在“会改变输出本质”的分叉要求用户确认：

- Advisor 推荐数量；
- Path 起点段位；
- Alchemy 大量证据时的主题范围；
- Review 的发布平台/语气；
- 是否允许推荐未上架书。

如果用户原始请求已经给出答案，跳过对应 gate。不要为日常小决策反复打断用户。

## 子命令路由

| 用户意图 | Workflow |
|---|---|
| 推荐书 / 下一本读啥 / 想读 X 方向 | [`workflows/advisor.md`](workflows/advisor.md) |
| 系统学习 X / 从零入门 X | [`workflows/path.md`](workflows/path.md) |
| 整理笔记 / 这本书记住了什么 / 提炼主题 | [`workflows/alchemy.md`](workflows/alchemy.md) |
| 年度/季度阅读复盘 / 写复盘文章 | [`workflows/review.md`](workflows/review.md) |
| 最近在读哪本 | 轻量直答 |

### 轻量直答：最近在读什么

1. `/shelf/sync` 拉书架；
2. 按 `readUpdateTime` 倒序；
3. 最新书调 `/book/getprogress`；
4. 用自然语言展示章节/进度/累计时长；
5. 附 weread 深链，并可补充最近一周的其他活跃书。

## 共享模块

- [`shared/knowledge-map.md`](shared/knowledge-map.md)：知识地图与交叉信号；
- [`shared/shelf-cross-notes.md`](shared/shelf-cross-notes.md)：书架 + 笔记交叉分析模板；
- [`shared/advisor-context.md`](shared/advisor-context.md)：确定性 Advisor Context；
- [`shared/reading-path-context.md`](shared/reading-path-context.md)：Path 起点与阶段契约。

## API 异常与边界

| 场景 | 处理 |
|---|---|
| `WEREAD_API_KEY` 缺失 | 明确报错并停止 |
| API `errcode != 0` | 告知错误，最多重试一次；仍失败则停止当前 workflow |
| 返回 `upgrade_info` | 升级 skill 后重试，不得忽略 |
| `/user/notebooks` `hasMore=true` | 按 `lastSort` 分页，参数平铺 |
| notebooks 为空 | 只能基于书架猜兴趣，并明确降低置信度 |
| 书架为空 | 不走 advisor/review/alchemy；可从 path 零基础规划 |
| `readUpdateTime=0` | 视为未打开，不进入最近活动 |
| 指名书搜不到 | 去标点/副标题模糊搜，仍失败则给候选让用户确认 |
| 主题过宽 | 先细化主题 |
| 主题过窄 | 明确平台覆盖有限，可组合纸质/其他合法来源 |

### `/store/search` 响应解析

不要假设顶层是 `books[]`。实际按 section 返回 `results[]`；电子书候选在对应 section 的 `books[*].bookInfo`。多候选时优先作者完全匹配，再考虑阅读人数；无法可靠消歧时应让用户确认。

## 数据展示规范

- Unix 时间戳 → `YYYY-MM-DD`；
- 秒 → “X 小时 Y 分钟”；
- 进度 → `X%`；
- 不向用户裸露无意义的 bookId；优先 weread 深链；
- marks 是保存的原文，不自动当成用户观点；reviews 才是用户自己的想法证据；
- 公开 Page 不发布原始划线/想法正文。

## 输出风格

保持自然、克制、有依据。避免堆砌结构词和无证据断言。风格要求不能覆盖事实边界：当证据不足时直接说不足。

## 调用约定

无论走哪个 workflow，都先读：

1. 本 `SKILL.md`；
2. 对应 workflow；
3. `shared/knowledge-map.md`；
4. 若已有对应 deterministic context，优先消费 context 而不是重新临时计算。

推荐、路径、总结和复盘都必须可追溯到数据证据；不要凭印象补书、补观点或补用户偏好。
