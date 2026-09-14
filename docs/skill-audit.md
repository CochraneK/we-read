# WeRead Skill 审计

> 审计日期：2026-09-14。目标不是统计“有多少 Skill”，而是区分：**规范是否读过、能力是否实现、是否应该进入公开 Page**。

## 先说结论

仓库当前有 9 个本地 Skill。GitHub Pages 运行时并不会动态执行这些 `SKILL.md`；Pages 实际执行的是确定性 Python 模块。Skill 的主要作用是定义工作流、数据语义、安全边界和输出规范，随后由脚本/渲染器把其中一部分能力产品化。

因此：

- “仓库里存在 Skill” ≠ “线上 Page 调用了 Skill”；
- “Skill 已分析” ≠ “全部功能已经实现”；
- “功能没有进 Page”也不一定是缺陷，一些能力应保持本地/私有。

## 总表

| Skill | 规范审计 | 当前实现度 | 公开 Page | 主要缺口 / 备注 |
|---|---|---:|---|---|
| `weread-visualization` | 高 | 高 | 是 | Heatmap / Map / Shift / Graph / Profile / Report 已基本产品化；继续以固定 schema + renderer 为准 |
| `weread-search` | 高 | 高（核心） | 否，刻意本地 | SQLite/FTS5/中文 fallback 已有；Search→Map / Alchemy / Recall 的跨 Skill 编排仍可加强 |
| `weread-recall` | 高 | 中高 | 仅元数据层 | 队列、Feynman 规则、renderer 已有；缺长期答题历史、间隔复习、答后差异分析的完整闭环 |
| `weread-blindspot` | 高 | 中高 | 是 | 集中度、投入落差、Counter Reading 已有；缺基于学派/利益相关者/证据类型/时代的更深反向证据搜索 |
| `weread-obsidian` | 高 | 高 | 否，刻意本地 | dry-run、managed region、`USER_EDIT_ZONE`、非托管文件保护等安全边界已实现 |
| `weread-book-to-skill` | 高 | 中高 | 否，刻意本地 | evidence-backed Skill 已有；“二次提炼成 3–7 步可执行方法 Skill”仍未完整产品化 |
| `weread-organizer` | 高 | 中高（安全模式） | 部分（本地 Pin） | plan-only 已实现；未实现未经官方文档确认的远端写入，这是有意安全边界 |
| `yao-weread-skill` | 高（已读 top-level + 3 个 references） | 中高 | 大量吸收 | 27 个图表模块并未 1:1 全复刻；词云/划线长度/部分书架树图与归档图等仍有差距；画像金句/划线清单不应直接公开 |
| `huashu-weread` | 高（已读 top-level、4 workflows、2 shared） | 中 | 少量结构能力 | Advisor / Path / Alchemy / Review 四条工作流尚未完整产品化，是目前最大的能力缺口 |

## 哪些能力已经真正进入代码

### 1. Visualization：最完整

已经有确定性事实层、固定 schema、稳定 renderer，并落实：

- GitHub-style Heatmap
- Reading Map
- Knowledge Graph
- Cognitive Shift
- Evidence-based Reading Profile
- Unified Reading Report

这一条不是只“借鉴了想法”，而是已经形成项目主干。

### 2. Search：核心已完成，但保持私有

已实现：

- SQLite 本地索引
- 标题 / 作者 / 类别 / 章节 / 划线 / 想法检索
- FTS5
- 中文 substring fallback
- 从 privacy-aware context 建索引

未充分产品化的是“检索结果作为其他工作流证据”的编排，例如：Search → Alchemy、Search → Recall、Search → Reading Map。

### 3. Recall：从“展示旧笔记”走到了主动回忆，但闭环还不完整

已有：

- deterministic recall queue
- 控制单书占比
- 优先旧证据及本人 review
- answer-first / reveal-evidence-later renderer
- Page 上的“今日重新激活”（只展示元数据）

缺口：

- 每次回答结果的本地历史
- 记忆强度 / 下次复习日期
- “遗漏了什么、误解了什么、出现了什么新理解”的结构化记录
- Search 驱动的补证据环节

这些内容应默认本地，不应直接进入公开 Page。

### 4. Blindspot：结构盲点已做，认识论盲点还可更深

已有：

- 类别集中度
- 收藏多但投入少
- 低进度 / 无笔记 backlog
- Counter Reading 方向

Skill 还要求更深的反向检查：

- 不同学派 / 范式
- 不同时间尺度
- 不同利益相关者
- 理论 vs 实证
- 经典观点 vs 新证据
- 反向因果 / 替代解释

这部分目前只部分实现。

### 5. Obsidian：安全边界基本吃透

当前实现与 Skill 的关键要求高度一致：

- dry-run
- 只更新 `WEREAD_SYNC_START ... WEREAD_SYNC_END`
- 永久保护 `USER_EDIT_ZONE`
- 非托管同名文件默认跳过
- 不自动删除孤儿文件
- manifest 不保存 API key

这条不需要为了“功能更多”而塞进公开 Page。

### 6. Book → Skill：第一阶段完成，第二阶段还欠一层

当前生成器能把单本书的个人证据转成 evidence-backed Skill，并清楚区分：

- 我的划线（原文，不等于本人观点）
- 我的想法（review）
- AI 提炼

但 Skill 规范中的第二阶段仍值得做：把证据总结进一步压缩成 **3–7 步、含适用/不适用条件的可执行方法 Skill**。

### 7. Organizer：安全地停在 plan-only 是正确的

当前做了：

- status/category/hybrid 整理策略
- 本地可审核计划
- `remoteMutationPerformed=false`
- Page 本地 Pin 队列

没有使用未文档化接口自动改微信读书书架。这不是“没做完”，而是安全边界。只有官方写接口被验证后，才应该另做 preview → explicit confirm → execute。

## `yao-weread-skill`：不是“已完全复刻”

这次已审读：

- `SKILL.md`
- `references/chart-catalog.md`
- `references/data-contract.md`
- `references/report-design.md`

其中图表目录明确给出 27 个核心模块。当前新 Page 已覆盖大量高价值能力，例如 KPI、月度趋势、Heatmap、累计生涯、年度对比、Top 书、分类/作者/出版社偏好、阅读/听书、进度、笔记 Top、进度×笔记散点等，但不是逐项 1:1。

仍未完整吸收或有意没有公开的包括：

- 阅读日时长分布
- 某些月度堆叠统计
- 分类雷达 / treemap 的一对一复刻
- 书架构成 / 公开私密 / 归档等专门图表
- 近期书架活动时间线的专门形态
- 笔记类型堆叠图
- 划线/想法词云
- 笔记时间线
- 划线长度直方图
- 画像金句与最多 20 条高价值划线清单

最后三类涉及原始文本，不应因为原 Skill 有就直接放到公开 Page。更合理的是保留在本地私有报告。

## `huashu-weread`：当前最大的未充分吸收区

这次已审读：

- `SKILL.md`
- `workflows/advisor.md`
- `workflows/path.md`
- `workflows/alchemy.md`
- `workflows/review.md`
- `shared/knowledge-map.md`
- `shared/shelf-cross-notes.md`

### Advisor：尚未完整实现

Skill 要求的不只是“猜你喜欢”，而是：

1. 书架 + notebooks + progress + 最近活动交叉；
2. 判断真读 / 浅尝 / 放着 / 隐藏深读；
3. 找知识地图的拼图缺口；
4. 按学派、时代、抽象层次、相邻学科补缺；
5. 推荐前用 `/store/search` 验证微信读书上架；
6. 输出 weread 深链和推荐理由。

当前 Page 的 Blindspot、Explorer、投入分析只提供了第 1–3 步的一部分事实基础，还不是完整 Advisor。

### Path：尚未完整实现

Skill 要求：

- 判断 zero / beginner / intermediate / advanced
- 用户确认段位
- 3 阶段路径：入门 → 框架 → 前沿
- 总量通常 6–8 本
- 基于字数估算时间
- 每阶段设置 Feynman checkpoint
- 提供“最小版本”退出路线

当前 Shelf Organizer / Booklist Plan 不能等价替代这条能力。

### Alchemy：已有组件，但没有完整跨书炼金工作流

已有 Search、Book→Skill、Recall 等基础设施，但尚缺：

- 单书按章节聚合 marks + reviews
- “作者主张 vs 我的想法”对照
- 跨书主题聚类
- 数据量大时先展示议题簇再让用户缩小范围
- 生成“我从 X 主题学到了什么 + 仍未回答的问题”的私有报告

这应以本地/private artifact 为主，不直接公开原始证据。

### Review：统计有了，叙事型复盘还不完整

Page 已有年度透镜、迁移、节律、投入变化，但 Skill 还要求：

- 完读 / 在读 / 浅尝 / 重读分组
- 明确的同比或阶段对照
- “意外转折”与放弃书
- 下一周期具体目标
- 朋友圈 / 公众号 / 小红书 / 视频脚本等不同出口

这更适合做可选择导出的私有 Narrative Review，而不是写死在公开 Page。

## “充分分析”的新标准

今后不再用“看过 README / SKILL.md”就标记完成。一个 Skill 只有在以下四项都明确后才算完成审计：

1. **Contract**：数据源、字段语义、fallback、隐私边界；
2. **Workflow**：真正的步骤、分叉、用户确认点；
3. **Implementation mapping**：仓库里哪段代码已经实现；
4. **Gap decision**：缺失能力是要做、暂缓，还是刻意不公开。

## 下一步优先级

### P0：把 `huashu` 真正吃透

1. `Advisor Context`：先做纯确定性知识地图与拼图缺口 context，不自动推荐；
2. `Reading Path Planner`：段位 → 3 阶段路径 → checkpoint 的稳定 schema；
3. `Alchemy Context`：本地跨书主题聚类与证据包；
4. `Narrative Review Context`：把现有年度事实层转成可供多平台写作的私有事实包。

### P1：补完整知识复用闭环

1. Recall history + spaced review；
2. Book→Skill 第二阶段 method refinement；
3. Search → Recall / Alchemy / Map 的统一 evidence handoff；
4. Blindspot 的反证 / 学派 / 时代 / stakeholder 维度。

### P2：从 `yao-weread` 选择性补图

不追求为了“27/27”而堆图。优先补真正增加信息维度的：

- 阅读日时长分布
- 笔记类型结构
- 书架资产结构 / 归档结构
- 近期活动时间线

词云、划线时间线、画像金句等原始文本相关模块默认留在本地私有报告。

## 最后原则

目标不是“调用最多 Skill”，而是让每个 Skill 的高价值能力进入正确层：

```text
公开 Page：聚合事实 + 非敏感交互 + 元数据
本地工具：全文 Search / Recall / Alchemy / Book→Skill / Obsidian
需要确认后执行：推荐、远端书架写入、对外发布型复盘
```

这样才能同时获得能力密度、可维护性和隐私边界。
