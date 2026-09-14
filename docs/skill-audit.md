# WeRead Skill 审计

> 审计日期：2026-09-14。目标不是统计“有多少 Skill”，而是区分：**规范是否读过、能力是否实现、是否应该进入公开 Page**。

## 结论

仓库当前有 9 个本地 Skill。GitHub Pages 运行时**不会动态执行这些 `SKILL.md`**；Pages 真正执行的是确定性 Python 模块。Skill 是工作流规范、数据语义、安全边界和输出契约的来源，脚本/renderer 再把其中适合产品化的能力落地。

因此：

- “仓库里存在 Skill” ≠ “线上 Page 调用了 Skill”；
- “Skill 已读” ≠ “Skill 的全部能力已实现”；
- “没有进入公开 Page”不一定是缺陷，全文证据、Alchemy、Obsidian 等能力本来就应保持私有；
- 判断一个 Skill 是否“吃透”，必须同时看 Contract、Workflow、Implementation mapping、Gap decision。

## 当前 9 个本地 Skill

| Skill | 规范审计 | 当前实现度 | 公开 Page | 主要剩余缺口 |
|---|---|---:|---|---|
| `weread-visualization` | 高 | 高 | 是 | 继续统一 schema / renderer，不再堆重复图 |
| `weread-search` | 高 | 高（核心） | 否，刻意本地 | Search → Recall / Alchemy / Map 的统一 evidence handoff |
| `weread-recall` | 高 | 中高 | 仅元数据层 | 答题历史、间隔复习、答后差异分析 |
| `weread-blindspot` | 高 | 中高 | 是 | 学派 / stakeholder / 因果反转 / 经典 vs 新证据等反证搜索 |
| `weread-obsidian` | 高 | 高 | 否，刻意本地 | 主要安全边界已完成 |
| `weread-book-to-skill` | 高 | 中高 | 否，刻意本地 | 第二阶段 3–7 步方法 Skill refinement |
| `weread-organizer` | 高 | 中高（安全模式） | 部分（本地 Pin） | 官方写接口被验证后才考虑 preview→confirm→execute |
| `yao-weread-skill` | 高（top-level + 3 references） | 中高 | 大量吸收 | 27 图未 1:1 全复刻；文本型模块应保留私有 |
| `huashu-weread` | 高（top-level + 4 workflows + shared） | **中高：四条事实/契约层已实现** | 仅少量非敏感事实 | 推荐/选书/语义聚类/最终多平台写作等执行层仍待完成 |

## 什么叫“实际调用”

### 真正调用外部能力

数据拉取脚本会调用微信读书 Agent Gateway：

```text
https://i.weread.qq.com/api/agent/gateway
```

本仓库 `export_notes.py` / `fetch_enrich.py` 当前基线使用 WeRead Skill `1.0.4`。`huashu-weread` 已改为：**运行时读取官方 Skill 的权威 version，不允许静默 fallback 到旧常量**。

### 本地 Skill 的实际角色

`.workbuddy/skills/*/SKILL.md` 当前是工作流规范，不是 Pages 运行时插件。比如：

```text
weread-recall/SKILL.md
        ↓ 约束队列选择与 Feynman 规则
 scripts/build_recall_queue.py + renderer
        ↓
 本地 Recall / Page 元数据 resurfacing
```

所以以后报告“Skill 使用情况”时必须区分：

```text
spec audited / capability implemented / runtime executed / public surfaced
```

## 已经真正进入代码的能力

### Visualization：最完整

已实现：

- GitHub-style Heatmap
- Reading Map
- Knowledge Graph
- Cognitive Shift
- Evidence-based Reading Profile
- Unified Reading Report
- 固定 schema + stable renderer

这条已经是项目主干，不只是参考了 Skill 文案。

### Search：核心完整，刻意私有

已有：

- SQLite 本地索引
- 标题 / 作者 / 类别 / 章节 / 划线 / review 检索
- FTS5
- 中文 substring fallback
- privacy-aware context

未充分产品化的是跨 Skill evidence handoff。

### Recall：主动回忆已完成第一阶段

已有：

- deterministic recall queue
- 控制单书占比
- 旧证据优先，同龄证据优先用户 review
- answer-first / reveal-evidence-later renderer
- Page “今日重新激活”只消费元数据

还缺：

- 本地答题历史
- 记忆强度 / next review date
- 遗漏 / 误解 / 新理解的结构化差异
- Search 补证据闭环

### Blindspot：结构盲点已做

已有：

- 类别集中度
- 收藏多但投入少
- 低进度 / 无笔记 backlog
- Counter Reading 方向

未完整实现：

- 不同学派 / 范式
- stakeholder
- 理论 vs 实证
- 经典观点 vs 新证据
- 反向因果 / 替代解释

### Obsidian：安全边界基本吃透

已实现：

- dry-run
- 只更新 `WEREAD_SYNC_START ... WEREAD_SYNC_END`
- 永久保护 `USER_EDIT_ZONE`
- 非托管同名文件跳过
- 不自动删除孤儿文件
- manifest 不保存 API key

它没有必要为了“展示能力”进入公开 Page。

### Book → Skill：第一阶段完成

已有 evidence-backed Skill，并明确区分：

```text
mark   = 保存的原文，不等于本人观点
review = 用户自己的想法
AI     = 后续证据提炼
```

下一阶段是把总结再压缩成 **3–7 步、含适用/不适用条件的可执行方法 Skill**。

### Organizer：plan-only 是正确安全边界

已有：

- status/category/hybrid 计划
- `remoteMutationPerformed=false`
- 浏览器本地 Pin 队列
- Pin JSON 导入/导出

没有用未文档化接口改远端书架，这是刻意设计。

## `yao-weread-skill`：已深入读，但不追求 27/27

已审读：

- `SKILL.md`
- `references/chart-catalog.md`
- `references/data-contract.md`
- `references/report-design.md`

图表目录定义了 27 个核心模块。当前 Page 已覆盖 KPI、月度趋势、Heatmap、累计生涯、年度透镜、Top 书、类别/作者/出版社、阅读/听书、进度、笔记 Top、散点关系等大量高价值模块，但不是逐项复刻。

仍未完整吸收或有意保持私有：

- 阅读日时长分布
- 某些月度堆叠统计
- 分类 radar / treemap 的 1:1 形态
- 书架公开/私密/归档专门图
- 近期书架活动 timeline
- 笔记类型堆叠图
- 划线/想法词云
- 笔记时间线
- 划线长度直方图
- 画像金句 / 高价值划线清单

涉及原始文本的模块默认应留在本地私有报告，而不是为了“完成度”公开。

## `huashu-weread`：四条事实/契约层已经补上

本轮已审读：

- `SKILL.md`
- `workflows/advisor.md`
- `workflows/path.md`
- `workflows/alchemy.md`
- `workflows/review.md`
- `shared/knowledge-map.md`
- `shared/shelf-cross-notes.md`

并修复了两个 Skill 自身问题：

- 固定 `1.0.3` 版本说明改成“读官方权威版本”，仓库当前脚本基线为 `1.0.4`；
- 移除公开文档中的可识别个人阅读案例，改为匿名/合成示例规范。

### Advisor：事实层完成，推荐执行层未完成

新实现：

```text
scripts/build_advisor_context.py
schemas/advisor_context.schema.json
shared/advisor-context.md
```

确定性输出：

- deep / medium / light / glance / none
- hidden deep：不在书架但形成深读证据
- shelved unengaged：在书架但没有笔记证据
- recent 7d / 30d
- 类别 engagement rate
- deep categories
- shelf-heavy low-engagement categories

normalized context 也新增：

```text
inShelf
inNotebook
shelfReadUpdateTime
```

Advisor Context 明确：

```json
"readyForRecommendation": false
```

还缺执行层：

1. 对候选主题补 `school_or_viewpoint / era_or_paradigm / abstraction_level / adjacent_discipline` 证据；
2. 识别真正知识缺口；
3. 生成候选书；
4. `/store/search` 验证当前上架；
5. 排除已充分读过 / 标注已收藏未读；
6. 输出 weread 深链和 evidence-backed reason。

### Path：起点判断和三阶段契约完成

新实现：

```text
scripts/build_reading_path_context.py
schemas/reading_path_context.schema.json
shared/reading-path-context.md
```

已经落实：

- topic metadata matching + aliases
- `zero / beginner / intermediate` 起点建议
- 用户确认 gate
- 3 本以上实质阅读信号建议切 Advisor
- 三阶段 `intro → framework → frontier`
- 每阶段 Feynman checkpoint
- 总量 6–8 本契约
- 最小版本要求
- 300 字/分钟时长规则
- 上架验证要求

**不会自动判 advanced**：高级需要前沿/一手文献证据，不能用笔记数量冒充。

还缺：候选书 discovery、`/store/search`、字数 enrichment、最终 6–8 本路线与最小版本选择。

### Alchemy：私有证据 Context 完成

新实现：

```text
scripts/build_alchemy_context.py
schemas/alchemy_context.schema.json
shared/alchemy-context.md
```

已经落实：

- 单书 / 跨主题两种模式
- book title 消歧
- mark → `source_text`
- review → `user_thought`
- 按章节聚合
- 跨主题 evidence landscape
- 大体量 scope gate
- 明确 `containsRawEvidence=true`
- 明确 `publicPageSafe=false`

还缺执行层：语义议题聚类、3–5 核心论点、作者 vs 用户对话、未回答问题、最终私有笔记文章。

### Review：周期事实 Context 完成

新实现：

```text
scripts/build_narrative_review_context.py
schemas/narrative_review_context.schema.json
shared/review-context.md
```

已经落实：

- 任意起止日期
- `monthly[*].readTimes` 日级去重后聚合周期时长
- 完成 / 在读 / 浅尝 / 重读 / active_unknown
- evidence-rich vs light/no-note
- top period notes
- 累计投入参考（明确不是周期时长）
- 30–70% 且 90 天以上无活动的 stalled candidates
- note category 前后半段 shift candidate
- 平台确认 gate

不会把主题变化直接解释成“为什么转向”。平台未确认时：

```json
"readyForNarrative": false
```

还缺最终多平台写作层与可选图文导出。

## “充分分析”的标准

一个 Skill 只有以下四项都明确后才算完成审计：

1. **Contract**：数据源、字段语义、fallback、隐私边界；
2. **Workflow**：真实步骤、分叉、用户确认点；
3. **Implementation mapping**：仓库里哪段代码实现了什么；
4. **Gap decision**：缺失能力是继续做、暂缓，还是刻意不公开。

按这个标准，目前 9 个本地 Skill 都已完成**规范级审计**；实现深度不相同。

## 下一步

### P0：把 `huashu` 从 Context 推到执行层

1. Advisor gap enrichment + candidate verifier；
2. Reading Path candidate selection + availability/word-count verification；
3. Alchemy semantic cluster + private synthesis renderer；
4. Narrative Review multi-platform writer/renderer。

### P1：知识复用闭环

1. Recall history + spaced review；
2. Book→Skill method refinement；
3. Search → Recall / Alchemy / Map evidence handoff；
4. Blindspot 反证维度。

### P2：选择性补 `yao-weread` 图表

优先增加新信息维度：

- 阅读日时长分布
- 笔记类型结构
- 书架资产/归档结构
- 近期活动 timeline

不为 27/27 而堆图；原始文本模块默认私有。

## 最终分层

```text
公开 Page
  聚合事实 + 非敏感交互 + 书目元数据

本地私有
  全文 Search / Recall 历史 / Alchemy / Book→Skill / Obsidian

需要用户确认后执行
  Advisor 推荐 / Path 书单 / 远端书架写入 / 对外发布型 Review
```

目标不是“调用最多 Skill”，而是把每个 Skill 的高价值能力放进正确层，并保证证据、隐私和可维护性。
