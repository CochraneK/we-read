# AGENTS.md — WeRead Intelligence

## 定位

把微信读书阅读数据转化为可验证的事实、可解释的视觉结果、可检索的个人证据、可持续回顾的学习材料，以及可重新调用的个人知识 Skill。

项目同时保留旧有 Plotly 分析看板和金句卡片工作流，但新的能力应优先走共享事实层，不继续扩张 legacy `analysis.py`。

## 核心原则

1. **事实与解释分层**：时长、进度、书目、笔记数由代码确定性计算；主题、认知转向、画像、Blindspot 属于 AI 解释层。
2. **书架不等于阅读**：书架是兴趣 / acquisition intent；笔记、进度和阅读时长才是投入证据。
3. **先 JSON，后 renderer**：解释型可视化必须先生成固定 Schema JSON，再交给稳定 renderer。
4. **本地优先 + 显式发布边界**：API Key、完整原始 evidence、搜索索引、Private Lab 与生成 Skill 默认保持私有；公开 Page 只能发布 `docs/publication-policy.md` 明确允许且通过 validator 的内容。
5. **证据可追溯**：高阶结论尽量保留书籍、划线、时间段、置信度和反证。
6. **不重复拉 API**：优先复用本地数据和 `visualization_context.json`。
7. **同步不覆盖用户内容**：自动同步只能改明确标记的 machine-managed 区域。
8. **远端写操作预览优先**：任何可能修改微信读书远端状态的动作都必须先有 dry-run / plan、用户明确确认、执行后核验，并且只使用当前官方明确支持的写接口。
9. **公开发布以 canonical policy 为准**：Public Archive 可以使用真实阅读事实、获授权的书目元数据与受限划线摘录，但不得因此推断完整 raw export、用户 review 或其他私有 evidence 也可公开。
10. **Page 组合层冻结扩张**：现有 `pages_*.py` UI/增强层以维护为主。不要为了新增一个小功能继续创建新的字符串替换装饰层；重大 UI 改造应优先合并/简化现有层，再增加能力。

## 环境变量

- `WEREAD_API_KEY`：微信读书 Agent Gateway Key。
- `WEREAD_DATA_DIR`：可选，真实数据目录；推荐设置到仓库外。
- `WEREAD_MONTHLY_HISTORY_MONTHS`：可选，月度统计回溯月数，默认 48。
- `WEREAD_START_YEAR`：可选，强制年度统计起始年；默认自动发现。
- `OBSIDIAN_VAULT`：可选，Obsidian Vault 路径。

推荐：

```bash
export WEREAD_DATA_DIR="$HOME/.local/share/we-read"
```

## 标准数据流水线

```bash
python scripts/export_notes.py
python scripts/fetch_enrich.py
python scripts/build_visualization_context.py
```

`visualization_context.json` 是绝大多数后续能力的共享入口。默认排除明确 `secret=1` 的书；除非用户明确要求本地私密分析，否则不要加 `--include-private`。

## 确定性层

新增确定性指标优先进入：

```text
scripts/metrics.py
```

而不是复制进各 renderer。

legacy `analysis.py` 的 A1 历史重复计数问题已经修复；当前与新功能统一使用 `metrics.category_participation()` 的 union-by-bookId 口径。

确定性能力：

```bash
python scripts/renderers/heatmap.py
python scripts/build_search_index.py --rebuild
python scripts/build_recall_queue.py
python scripts/build_blindspot_context.py
python scripts/plan_shelf_organization.py --strategy hybrid
```

## 解释型可视化

统一 Skill：`.workbuddy/skills/weread-visualization/`

```text
visualization_context.json
        ↓
AI 按对应 schema 生成 analysis JSON
        ↓
稳定 renderer
        ↓
HTML
```

对应关系：

- Reading Map → `schemas/reading_map.schema.json` → `scripts/renderers/network.py --kind reading-map`
- Knowledge Graph → `schemas/knowledge_graph.schema.json` → `scripts/renderers/network.py --kind knowledge-graph`
- Cognitive Shift → `schemas/cognitive_shift.schema.json` → `scripts/renderers/timeline.py`
- Reading Profile → `schemas/reading_profile.schema.json` → `scripts/renderers/profile.py`
- Blindspot → `schemas/blindspot.schema.json` → `scripts/renderers/blindspot.py`
- Unified Report → `schemas/reading_report.schema.json` → `scripts/renderers/report.py`

Renderer 只负责呈现，不修正、不补写、不发明分析结论。

## Search / Recall

### Search

```bash
python scripts/build_search_index.py --rebuild
python scripts/build_search_index.py --query "关键词"
```

Search 只负责证据召回。命中划线不能自动视为用户本人观点。

### Recall / Feynman

```bash
python scripts/build_recall_queue.py
python scripts/renderers/recall.py
```

回顾卡必须先让用户回答，再展开证据；不要把任务设计成逐字背诵。

## Private Text Mining Lab

Lite 核心：

```bash
python scripts/build_text_mining_context.py
python scripts/renderers/text_mining_private.py
```

必须始终分离：

```text
source_text = 保存的作者/原书文本 = exposure evidence
user_thought = 用户自己写的 review = expression evidence
```

禁止把 source highlight 说成用户观点。

Lite 的中文 token 是 character bi/tri-gram，因此输出只能叫 lexical unit / lexical community / topic candidate，不能叫“真实语义主题”。

可选 semantic：

```bash
python scripts/build_private_reading_lab.py --semantic-text --embedding-model "MODEL_OR_LOCAL_PATH"
```

Semantic similarity / cluster / drift 只能解释为 representational proximity / corpus shift / candidate relationship，禁止直接解释为赞同、因果、内化、人格、诊断或敏感属性。

完整规则见 `docs/text-mining.md`。

## Blindspot / Counter Reading

```bash
python scripts/build_blindspot_context.py
```

只允许从确定性覆盖 / 集中 / 投入落差信号提出“值得核对的问题”。

禁止：

- 将集中阅读直接定义为缺陷；
- 做医学 / 心理诊断；
- 从阅读记录推断政治、宗教、健康等敏感属性；
- 在没有检索证据的情况下编造“反方书籍”。

## Obsidian

```bash
python scripts/sync_obsidian.py --vault "/path/to/vault" --dry-run
```

每个文件分成：

```text
WEREAD_SYNC_START ... WEREAD_SYNC_END
USER_EDIT_ZONE_START ... USER_EDIT_ZONE_END
```

程序只能重建 `WEREAD_SYNC_*`；`USER_EDIT_ZONE` 必须原样保留。

- unmanaged 同名文件默认跳过；
- `--adopt-unmanaged` 只能在用户明确要求后使用；
- 不自动删除孤儿笔记。

## Book → Skill

```bash
python scripts/book_to_skill.py --book-id "BOOK_ID"
```

生成的 Skill 是**个人证据 Skill，不是整本书副本**。

必须区分：

- highlight：用户划下的作者原文片段；
- user_review：用户本人写下的想法；
- AI interpretation：后续基于证据的提炼。

不得把 highlight 误说成用户观点，也不得用模型对该书的一般知识偷偷补全 evidence。

## Shelf Organizer

```bash
python scripts/plan_shelf_organization.py --strategy hybrid
```

当前实现是 `plan-only`，不会修改微信读书远端。

只有当前官方 Skill / `/_list` 明确支持相应写操作，并且用户确认具体变更计划后，才能增加远端执行步骤。社区旧接口不能作为直接写入依据。

## 金句库

```bash
python scripts/build_quote_lib.py
```

`public_domain=pd` 只是版权人工复核候选，不是法律结论。出版、印刷、公开传播前必须人工确认作品、版本、译本和地区权利状态。

## Skills

- `yao-weread-skill`：微信读书底层能力 / 报告基础
- `huashu-weread`：advisor / path / alchemy / review
- `weread-visualization`：可视化 / 报告
- `weread-search`：本地证据检索
- `weread-recall`：Recall / Feynman / Contrast
- `weread-blindspot`：Blindspot / Counter Reading
- `weread-obsidian`：安全增量同步
- `weread-book-to-skill`：个人笔记 → Skill
- `weread-organizer`：书架 / 书单计划

## Public Page

`site/index.html` 是公开 GitHub Pages 成品页。公开范围的唯一规范见 [`docs/publication-policy.md`](docs/publication-policy.md)。

当前约束：

- workflow 可以从真实阅读数据生成公开档案，但最终只上传经过验证的 `site/`；
- 聚合阅读事实、书目元数据以及经显式授权的 bounded highlight excerpts 可以进入公开 Page；
- 完整 raw notes、完整 mark/review 正文、搜索索引、Private Reading Lab 与私有 synthesis 不得进入公开 Page；
- `WEREAD_PAGES_INCLUDE_PRIVATE` 与 `WEREAD_PAGES_INCLUDE_PUBLIC_QUOTES` 是独立的发布开关；
- 发布前必须经过 `scripts/validate_pages_output.py`，不能用 README 或人工判断替代 validator。

## 测试

```bash
python -m unittest discover -s tests -v
```

GitHub Actions 在 Python 3.11 与 3.13 上执行测试。新增数据规则、同步规则、隐私规则、renderer 或 Skill helper 时必须补回归测试。

## 隐私与公开仓库规则

- `.env`、API Key 不进 Git。
- `data/weread_*.json`、`data/weread_*.md`、`data/analysis/`、`data/generated-skills/` 默认不进 Git。
- 真实搜索索引、报告、金句库、卡片默认不进 Git。
- 测试只能使用合成或充分脱敏数据。
- `.gitignore` 不会自动取消已经被 Git 跟踪的历史文件；公开历史中的真实个人数据清理由 Issue #2 跟踪，未经明确确认不要重写历史。

## 目录职责

```text
scripts/
  export_notes.py
  fetch_enrich.py
  build_visualization_context.py
  metrics.py
  build_search_index.py
  build_recall_queue.py
  build_blindspot_context.py
  build_text_mining_context.py
  build_semantic_text_mining.py      optional
  sync_obsidian.py
  book_to_skill.py
  plan_shelf_organization.py
  build_quote_lib.py
  analysis.py                     legacy dashboard
  renderers/
    heatmap.py
    network.py
    timeline.py
    profile.py
    blindspot.py
    recall.py
    text_mining_private.py
    report.py
schemas/                           AI 输出契约
site/                              经 publication policy 约束的 Public Page artifact
tests/                             合成数据回归测试
.workbuddy/skills/                 Agent Skills
docs/                              生态与架构说明
```

## 明确保留的维护项

1. legacy `analysis.py` 保持冻结，只做必要 bugfix / 历史可复现性维护；A1 已完成正确口径迁移。
2. Public Page 现有组合层只做维护；不要继续新增 `pages_*_ui.py` 式补丁层。未来若进行大改，先制定合并现有 renderer/enhancer 的收敛方案。
3. 公开 Git 历史中的个人数据清理必须单独确认后处理。
4. 远端书架写入只在官方当前接口明确支持且用户再次确认后实现。
