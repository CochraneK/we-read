# WeRead Skill / Tool 生态能力地图

> 扫描快照：2026-09-14。目标不是声称“互联网中一个不漏”，而是系统覆盖：官方 Skill、Awesome 清单、GitHub `weread skill` / 新近仓库搜索、MCP / CLI、报告与可视化、复习 / 深读、同步 / 导出、书架整理等主要分支，并把可复用能力映射回本项目。

## 1. 扫描方法

本轮按四层扫描：

1. **官方能力基线**：`Tencent/WeChatReading`，以当前 `readdata / shelf / notebook / bookmark / review / book` 文档为事实基线。
2. **精选生态**：`awesome-weread` / `Awesome-Weread` 等基于官方 Agent Gateway 的 curated list。
3. **GitHub 广搜**：`weread skill`、`weread report`、`weread MCP`、`weread dashboard`、`created:>2026-06-01` 等查询，补 6 月后新项目。
4. **重点项目源码 / README 复核**：只把确认过的模式写入“已吸收”；仅凭仓库名发现的项目放在“候选观察”。

因此本文是**高覆盖率工程调研**，不是不可证明的“全 GitHub 绝对全集”。

---

## 2. 官方 Skill 能力：Page 的数据上限

`Tencent/WeChatReading` 当前可提供的报告相关事实包括：

- 书架、书籍元数据、阅读进度；
- 月 / 年 / 总计阅读时长与阅读天数；
- `readTimes` / 日级阅读记录；
- `preferTime`（24 小时，从 06:00 开始排列）与 `preferTimeWord`；
- `preferCategory / preferAuthor / preferPublisher`；
- `readRate / wrReadTime / wrListenTime`；
- `readStat`、`registTime`、`medals`；
- `preferBooks`、`readLongest`、年度偏好书卡；
- notebooks、划线、想法、书签数量；
- 搜书、推荐、书籍信息等。

### 已吸收进当前 Page

| 官方字段 / 能力 | 当前页面表现 |
|---|---|
| `readTimes` | 每日 Heatmap、最长连续阅读、星期节律 |
| 月度 `totalReadTime` | 月度趋势、累计阅读生涯、年度透镜、季节性 |
| `preferTime` | 24 小时阅读时钟 |
| `preferTimeWord` | 官方阅读时段描述 |
| `readStat` | 阅读生涯官方统计卡 |
| `preferCategory` | 官方类别偏好 |
| `preferAuthor` | 官方作者偏好 |
| `preferPublisher` | 官方出版社偏好 |
| `preferBooks` | 年度偏好书卡 + 年度透镜 |
| `medals` | 阅读勋章 / 里程碑 |
| `registTime` | 阅读轨迹起点 / 使用年限 |
| `readLongest` | 阅读时长 Top |
| progress | 进度漏斗、进度 × 笔记散点、当前深读 |
| notebooks / marks / reviews | 笔记密度、想法占比、年度记录方式变化、知识网络 |
| shelf | 498 本完整书架 Explorer、分类 / 作者关系、盲点 |

`readRate / wrReadTime / wrListenTime` 当前缓存若没有真实值，模块自动隐藏，不用 0 冒充数据。

---

## 3. 已核验的生态模式

### A. 报告 / 可视化 / 画像

代表项目：

- `kkluote-kingkai/weread-report`
- `Simone-techAIGC/weread-report-generator`
- `viewer12/weread-mirror`
- `monsignorlaw1015/weread-report`
- `kejixiaoliang/read-persona`
- `monilulu/weread-reading-profile`
- `Jelly-LZL/weread-skills-extension`
- `lucis-yg/weread-dashboard`
- `PandoraReads/apex-dashboard`
- `TonyxSun/weread-visualization`

值得吸收的共同模式：

- 按时间讲故事，而不只堆 KPI；
- Heatmap / 星期节律 / 累计曲线；
- 阅读进度 × 笔记深度散点；
- 分类 / 作者 / 出版社多视角；
- Reading Map / Cognitive Shift / Knowledge Graph；
- 单页静态 HTML，稳定 JSON 数据契约；
- 报告应区分事实与解释。

**本项目状态：已基本吸收。**

### B. 搜索 / CLI / SDK / MCP / Cache

代表项目：

- `shiquda/weread-cli`
- `nlimpid/weread`
- `ipfans/weread-cli`
- `Ceelog/OpenWeRead`
- `lucis-yg/weread-skill-api`
- `aixiasang/weread-mcp`
- `taxueseek/taxue-weread`
- `jerlinn/jerlin-weread`
- `marcus776957/weread-master`
- `Vanishia/weread-search`

共同模式：

- 本地缓存 / SQLite；
- CLI 按需调用，节省 Agent 上下文；
- 全文搜索；
- API / MCP 做统一数据入口；
- 增量同步而非每次全量请求。

**本项目状态：** 已有本地 SQLite Search、统一 normalized facts 和文件缓存；Page 只发布书目元数据搜索，不发布笔记全文索引。

### C. 回顾 / Feynman / Socratic / Anki

代表项目：

- `Llxsfd/weread-review-web`
- `bonniegeng-max/weread-socrates`
- `taxueseek/taxue-weread` 的 recall 工作流
- `zhjccoffee/ebook-weread-anki-skill`
- `Eleven1111/weread-insight-skill`
- `MondayLabOS/weread-insight-notes`

共同模式：

- 让旧笔记重新进入工作记忆；
- Feynman / Socratic 提问比“再看一遍划线”更有效；
- 复习队列需要时效、跨书多样性；
- Anki / 卡片适合作为输出层；
- 原始划线应保持本地学习用途。

**本项目状态：** 已有 Recall / Feynman 队列；Page 新增“值得重新激活”，但不公开原始证据正文。

### D. Obsidian / Notion / Markdown / 知识流转

代表项目：

- `zhongyi-byte/openclaw-weread-skill`
- `sancijun/weread-toolbox`
- `xrMDX/weread2notion`
- `zhaoyue-zhang/weread2notion-pro-skill_version`
- `MilesUsa/weread-notion`
- `weread-obsidian` 类项目

共同模式：

- 增量同步；
- Markdown / Obsidian / Notion 是长期知识库落点；
- 自动区与 USER_EDIT_ZONE 分离；
- 同步必须保护用户手写内容。

**本项目状态：** 已有 Obsidian 安全增量同步和 USER_EDIT_ZONE；不把外部同步硬塞进公开 Page。

### E. 书架整理 / 推荐 / 学习路径

代表项目：

- `alchaincyf/huashu-weread`
- `tanyaqiong31029/weread-shelf-organizer`
- `flybear16/weread-shelf`
- `tiankk66/weread-add-shelf`
- `taxueseek/taxue-weread`

共同模式：

- shelf ≠ reading；
- 书架收藏只能代表兴趣 / 意图；
- 推荐应结合进度、笔记和实际投入；
- 写操作应 plan-first、dry-run、显式确认。

**本项目状态：** Page 已加入“书架→笔记投入率、进度漏斗、Blindspot / Counter Reading、全书架 Explorer”；本地 Shelf Organizer 保持 plan-only。

### F. Book → Skill / Skill Factory

代表项目：

- `jyqi/weread-to-skill`
- `kuhung/weread-book-skills`
- `FlapPearLabs/hermes-weread-skill-factory`
- 本项目 `weread-book-to-skill`

共同模式：

- 单本书笔记可变成 evidence-backed reusable Skill；
- 必须区分作者原文、用户想法和 AI 提炼；
- Skill 的价值在“重新调用”，不是一次性总结。

**本项目状态：已实现。** Page 只展示高投入书和证据覆盖，不公开 Skill 私有 evidence 文件。

### G. 发布 / 故事化 / 多终端

近期发现：

- `goking81/weread-story-publisher`
- `mariposawxt-dotcom/weread-cinematic-book-video-dynamic`
- `bingze6-creator/kindle-weread-skills`
- `weread-report-skills`
- `weread-skill-desktop`

这些项目提示了三个方向：

1. 报告可以“故事化”，而非只有统计图；
2. Kindle / 本地电子书可作为微信读书以外的数据源；
3. 桌面常驻 / 视频发布属于消费层，不应污染事实层。

**本项目当前吸收：** “每年一章、年度透镜、累计生涯”作为故事化层；跨设备数据暂不混入 WeRead 主档案。

---

## 4. 2026-06 之后 GitHub 广搜发现的新增 / 活跃候选

本轮搜索还发现以下仓库，作为持续观察池：

- `elroy1213/weread-collector-skill`
- `jyqi/weread-to-skill`
- `bingze6-creator/kindle-weread-skills`
- `comeonlzq/weread-report-skills`
- `ningyan1228/weread-skills-web`
- `FlapPearLabs/hermes-weread-skill-factory`
- `dongwei6688/weread-notes-export-skill`
- `245678000000/weread-mp-monitor-skill`
- `zhjccoffee/ebook-weread-anki-skill`
- `goking81/weread-story-publisher`
- `YunhaoDou/weread-portrait`
- `YunhaoDou/weread-heatmap`
- `Vanishia/weread-search`
- `Rao2424/weread-knowledge-Rassistant`
- `MondayLabOS/weread-insight-notes`
- `bonniegeng-max/weread-socrates`
- `xychan2/weread-exporter-skill`
- `us-oyster/weread-omni`
- `joo2017/weread-omni`
- `ip4case/weread-omni`

仓库名被发现不等于能力已全部复核；只有上文“已核验模式”才作为设计依据。

---

## 5. 当前 Page 已形成的能力层

```text
完整个人阅读档案
├─ 生涯
│  ├─ 2019 起点 / 使用年限
│  ├─ 累计阅读曲线
│  ├─ 每年一章
│  ├─ 年度透镜 2023 / 2024 / 2025 / 2026
│  └─ 勋章 / 官方年度偏好书
├─ 节律
│  ├─ 月度趋势
│  ├─ Daily Heatmap
│  ├─ 24h 阅读时钟
│  ├─ 星期节律
│  └─ 跨年月份季节性
├─ 投入
│  ├─ 进度漏斗（含覆盖率）
│  ├─ 进度 × 笔记散点
│  ├─ 月度时长 × 笔记散点
│  ├─ 高投入书
│  └─ 当前深读
├─ 偏好
│  ├─ 官方类别 / 作者 / 出版社
│  ├─ 类别 ↔ 作者阅读版图
│  └─ 年度关注迁移
├─ 知识
│  ├─ 类别 → 书 → 作者 Knowledge Graph
│  ├─ Bridge Authors
│  ├─ 划线 → 想法年度演化
│  └─ Reading Profile
├─ 反思
│  ├─ Blindspot
│  ├─ Counter Reading
│  ├─ 值得重新激活
│  └─ 想法写得最多的书
└─ 探索
   └─ 498 本全书架搜索 / 分类 / 进度 / 排序
```

---

## 6. 刻意不默认公开的功能

“最大化丰富页面”不等于“把所有数据公开”。以下能力技术上可做，但目前保留本地：

- **原始划线墙 / 金句墙**：会直接发布受版权保护原文和私人选择；
- **原始想法正文**：属于个人内容；
- **基于原始笔记的词云 / 高频短语**：即使不是逐字正文，也可能泄露语义；
- **全文 Search Index**：留在本地 SQLite；
- **Socratic 对话内容 / Feynman 答案**：属于个人学习过程；
- **Anki 卡片正文**：适合作为私有导出；
- **Obsidian / Notion 同步内容**：属于知识库层，而非公开展示层。

如果未来明确希望公开这些内容，应单独增加 publish policy，而不是从本地数据层自动泄漏。

---

## 7. 后续新增功能的判断规则

新 Skill / 新项目只有满足至少一个条件才值得进入 Page：

1. 提供当前没有的**事实维度**；
2. 能让 498 本书架更可探索；
3. 能让旧知识重新被调用；
4. 能形成新的长期时间视角；
5. 能改善信息结构 / 交互，而不是重复已有图；
6. 不要求公开原始笔记正文。

否则优先放到本地 Skill / export / sync 层，而不是继续把首页无限拉长。
