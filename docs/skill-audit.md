# WeRead Skill 审计

> 审计日期：2026-09-14。目标不是统计“有多少 Skill”，而是区分：**规范是否读过、能力是否实现、是否已经产品化、是否应该进入公开 Page**。

## 结论

仓库当前有 **10 个本地 Skill**。GitHub Pages 运行时不会动态执行这些 `SKILL.md`；Page 真正执行的是确定性 Python 模块。Skill 是工作流规范、数据语义、安全边界和输出契约的来源，脚本/renderer 再把能力落地。

这次新增：

- `weread-private-lab`：统一编排最初的划线卡片/深分析与后来 Search / Recall / Blindspot / Advisor / Alchemy / Review。

因此以后必须区分：

```text
spec audited
capability implemented
runtime executed
public surfaced
private surfaced
```

“仓库里有 Skill”不等于“Page 在调用 Skill”；“没有进公开 Page”也不等于没做，全文证据、Alchemy、Search、卡片等能力本来就应保持私有。

## 当前 10 个本地 Skill

| Skill | 实现度 | 主要角色 | 公开 Page | 主要剩余缺口 |
|---|---:|---|---|---|
| `weread-private-lab` | 中高 | **总编排 / 私有工作台** | 否 | 继续把更多私有 renderer 接入统一首页 |
| `weread-visualization` | 高 | Heatmap / Map / Shift / Graph / Profile / Report | 是 | 继续统一 schema / renderer |
| `weread-search` | 高（核心） | 本地全文检索 / evidence recall | 否 | Search → Recall / Alchemy / Map 统一 handoff |
| `weread-recall` | 中高 | Feynman / 主动回忆 | 仅元数据 | 答题历史、间隔复习、答后差异 |
| `weread-blindspot` | 中高 | 集中度 / 盲点 / Counter Reading | 是 | 学派 / stakeholder / 反向因果 / 新旧证据 |
| `weread-obsidian` | 高 | 私有知识库安全增量同步 | 否 | 核心安全边界已完成 |
| `weread-book-to-skill` | 中高 | 单书证据 → Skill | 否 | 第二阶段 3–7 步方法 refinement |
| `weread-organizer` | 中高（安全模式） | 书架整理 / Booklist plan | 部分（Pin） | 官方写接口确认后再做远端 mutation |
| `yao-weread-skill` | 中高 | 底层数据 / 报告 / 图表设计参考 | 大量吸收 | 不追求 27/27，文本模块保持私有 |
| `huashu-weread` | 中高 | Advisor / Path / Alchemy / Review | 少量非敏感事实 | 推荐/选书/语义聚类/最终写作执行层 |

## 最初工作有没有丢

没有。最初工作主要有两条：

### 1. 划线 → 金句 → 卡片

历史产物仍在：

```text
quote_lib/cards.html
quote_lib/cards_package.zip
quote_lib/design-tokens.md
quote_lib/金句库.json
quote_lib/金句库_top60.md
```

早期成品包含：

- 351 张划线卡片；
- A / B / C 三套风格；
- 点击/键盘翻转；
- 打印/PDF；
- 作者、书名强调；
- 历史版本背面在线加载书封。

过去的问题是：`cards.html` 更像“已经生成的一次性成品”，没有完整进入后来统一 Context 流水线。

现在已现代化成可重建链：

```text
weread_notes_export.json
        ↓
visualization_context privacy allowlist
        ↓
filtered_notes_private.json
        ↓
build_quote_lib.py
        ↓
quotes/金句库.json
        ↓
renderers/quote_cards.py
        ↓
private_lab/quote_cards.html
```

新的卡片 renderer 保留：

- 三主题；
- 搜索；
- 翻转；
- 键盘可访问；
- 打印/PDF；
- 书名/作者/章节/主题/评分；
- `weread://reading` 深链。

同时去掉“必须在线拉封面”的依赖，减少外部请求。它明确是私人原文证据，不进入公开 Pages。

### 2. 深入分析 A–E 16 项

旧 `scripts/analysis.py` 是一套 16 项 Plotly Dashboard，里面确实有很多后来非常有价值的分析：

- A1 类别参与度：藏书 vs 笔记、囤书 vs 真读；
- A2 作者集中度；
- A3 划线/想法参与模式；
- A4 私密 vs 公开；
- B5 月度阅读时长 + 笔记；
- B6 日内时段；
- B7 年×月热力与星期分布；
- C8 划线关键词/词云；
- C9 本人想法词频/启发式情感；
- C10 重复划线原文；
- D12 划线章节相对位置；
- D13 划线 ↔ 想法章节错位；
- E14 类别 × 划线/想法参与度；
- E15 进度 × 笔记密度；
- E16 累计有笔记书 × 累计笔记增长。

旧脚本仍保留，但不再作为新系统的数据真相层，因为已知存在：

- A1 重复计数问题；
- 私密书标题直接展示；
- `C:/Windows/Fonts/msyh.ttc` 非跨平台；
- “人格分型”命名过度；
- 情感词典只能算启发式；
- 年份/日期硬编码等维护问题。

## 深分析现在迁移到哪里

### 已进入公开档案/统一事实层

- A1 / E14 类别参与 → metrics / Advisor / Blindspot；
- A2 作者集中 → Page 作者偏好 / Knowledge Graph；
- B5 月度时间线 → Page 节律；
- B6 日内时段 → 24h 阅读时钟；
- B7 年×月 / 星期 → Heatmap / 星期节律 / seasonality；
- E15 进度 × 笔记 → Page 深度散点；
- E16 累积增长 → career / note evolution；
- marks/reviews 年度结构 → Reading Profile / Page note evolution。

### 新迁移到 Private Deep Notes Context

新实现：

```text
scripts/build_deep_notes_context.py
```

重新实现并明确口径：

- C10 重复划线；
- 划线长度分布；
- D12 划线章节位置（明确只是基于首次出现顺序的近似）；
- D13 划线 ↔ 想法章节错位；
- 想法密度高的书；
- 划线密集但本人想法少的书。

这里允许保留少量原始重复划线证据，因此默认：

```json
"publicPageSafe": false
```

### 不应该被“强整合”为结论的旧能力

- C8 词云：可保留为探索视图，但不能证明“认知主题”；
- C9 情感：词典法只能当启发式，不能推成心理状态；
- A3 原“人格分型”：应改称阅读记录/参与模式，不做人格诊断；
- A4 私密/公开：可做本地 coverage，不应把私密书样本公开。

## 新的统一入口

现在所有私人能力统一由：

```bash
python scripts/build_private_reading_lab.py
```

默认构建：

```text
visualization_context
advisor_context
blindspot_context
recall_queue
search.sqlite
deep_notes_context
narrative_review_context
private_lab/index.html
```

需要最初的划线卡片/全文证据：

```bash
python scripts/build_private_reading_lab.py --with-text
```

会追加：

```text
filtered_notes_private.json
quotes/金句库.json
quotes/金句库_top60.md
quote_cards.html
```

主题 Alchemy：

```bash
python scripts/build_private_reading_lab.py --with-text --topic "认知科学"
```

单书 Alchemy：

```bash
python scripts/build_private_reading_lab.py --with-text --book-id "BOOK_ID"
```

默认仍排除 `secret=1`；要做完整本地个人档案必须显式：

```bash
python scripts/build_private_reading_lab.py --include-private --with-text
```

## `huashu-weread` 四条主线状态

### Advisor

事实层已实现：深读/中读/轻读/浅尝/隐藏深读/收藏未投入/最近活动/类别投入率。

仍缺最终执行：知识缺口 enrichment、候选书发现、当前上架验证、最终推荐排序。

### Path

已实现：zero / beginner / intermediate 建议、用户确认 gate、intro → framework → frontier、Feynman checkpoints、6–8 本契约、最小路径规则。

不会仅靠笔记数量自动判断 advanced。

仍缺最终候选书 selection、`/store/search` 与 word-count enrichment。

### Alchemy

已进入 Private Reading Lab。已实现：

- 单书 / 跨主题；
- marks=`source_text`；
- reviews=`user_thought`；
- 章节归位；
- evidence landscape；
- 大体量 scope gate；
- 明确不公开 raw evidence。

仍缺最终语义聚类与私有长文 synthesis renderer。

### Review

周期事实 Context 已实现：完成/在读/浅尝/重读/未知进度、日级时长、stalled books、类别迁移候选与平台 gate。

仍缺最终多平台 narrative writer/renderer。

## Privacy routing

当前统一分三层：

```text
公开 Page
  聚合事实 + 非敏感交互 + 书目元数据

Private Reading Lab
  全文 Search + 划线卡片 + Deep Notes + Alchemy + Recall + 本人想法

需要明确确认后执行
  Advisor 推荐 + Path 最终书单 + 对外 Review + 远端写操作
```

这是现在所有 WeRead Skill 的总架构。

## “充分分析”的标准

一个 Skill 只有以下四项都明确后才算规范级审计完成：

1. **Contract**：数据源、字段语义、fallback、隐私边界；
2. **Workflow**：真实步骤、分叉、用户确认点；
3. **Implementation mapping**：仓库哪段代码实现了什么；
4. **Gap decision**：缺失能力是继续做、暂缓，还是刻意不公开。

目前 10 个本地 Skill 都已经完成规范级 mapping；实现深度不同。

## 下一步优先级

### P0

1. Advisor gap enrichment + candidate verifier；
2. Path candidate selection + availability / word-count verifier；
3. Alchemy semantic cluster + private synthesis renderer；
4. Narrative Review multi-platform writer/renderer。

### P1

1. Recall history + spaced review；
2. Search → Recall / Alchemy / Map evidence handoff；
3. Book→Skill 第二阶段方法 refinement；
4. Blindspot 反证维度。

### P2

选择性迁移旧/社区图表，不追求为了数量堆图。词云、原始划线时间线、高价值原文清单等默认留在 Private Reading Lab。

目标已经从“有很多零散微信读书能力”转成：

```text
一套统一事实层
+ 一个公开个人阅读档案
+ 一个私有深度阅读实验室
+ 一组可组合的 WeRead Skills
```
