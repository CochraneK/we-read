# WeRead / 微信读书开源能力调研

本文件记录 `we-read` 在继续设计 Skill 和可视化时参考过的公开项目，以及“借鉴什么 / 不照搬什么”。目标不是做项目清单，而是避免重复造轮子。

## 1. Tencent / WeChatReading

https://github.com/Tencent/WeChatReading

官方/底层能力参考。重点价值：

- API 字段与统计口径
- `readdata/detail` 的周 / 月 / 年 / overall 模式
- 书架、书籍、笔记、想法等基础能力

本项目策略：底层字段口径以这里为准，但高阶主题、知识网络和阅读画像放在本地解释层完成。

## 2. freestylefly / mcp-server-weread

https://github.com/freestylefly/mcp-server-weread

将微信读书书架、划线、笔记暴露为 MCP 工具，适合 LLM 客户端即时查询。

可借鉴：

- 工具化访问，而不是要求模型直接吞大 JSON
- 搜索 / 单书笔记查询应成为稳定能力

本项目对应：`weread-search` 使用本地索引完成证据召回；底层在线查询仍由现有 WeRead Skill 负责。

## 3. frankliu20 / mcp-server-weread

https://github.com/frankliu20/mcp-server-weread

社区变体补充了 booklists / 书单读取。

可借鉴：

- 书单是比单纯 category 更有“用户主动策展”含义的数据层
- 后续 Reading Map 可以将“书单”作为一种兴趣意图证据，而不是已读证据

待办：当底层 API / Skill 能稳定提供书单时，再加入统一事实层。

## 4. haoliangjun-95 / weread-mark

https://github.com/haoliangjun-95/weread-mark

偏产品化的微信读书数据可视化 Web 界面。

值得吸收的能力：

- 阅读看板
- 全文搜索划线 / 想法
- 书架与笔记浏览
- 图片 / PDF 导出
- 多主题 / 字体等可视化体验

本项目不复制其 React 前端，而是吸收“检索是核心能力”的产品判断，并保持本地优先、脚本 + Skill + standalone HTML 路线。

## 5. Learnmore-smart / Wechat-read-dashboard

https://github.com/Learnmore-smart/Wechat-read-dashboard

重点是多周期阅读统计切换：Weekly / Monthly / Annual / Overall，以及趋势图。

可借鉴：

- Dashboard 不应只固定展示一个时间范围
- 统一 Report 应明确 period，而不是把不同时间口径混在一起

本项目对应：`visualization_context.json` 保留 annual / overall；后续 dashboard v2 可增加周期选择。

## 6. Yant2023 / weread-obsidian

https://github.com/Yant2023/weread-obsidian

WorkBuddy Skill，重点是把微信读书同步到 Obsidian。

最值得借鉴：

- YAML Frontmatter
- 双向链接
- 增量更新
- `USER_EDIT_ZONE`：同步时保护用户手写内容

本项目后续的 `weread-obsidian-sync` 不应只做“一次性导出”，而应把 USER_EDIT_ZONE / 增量同步当成核心设计约束。

## 7. chanity256 / weread-export

https://github.com/chanity256/weread-export

重点是自动化、增量导出和本地状态文件。

可借鉴：

- 定时同步
- 已处理 bookId 状态
- 数据抓取与 Markdown 转换分离

这与本项目现在“raw data → normalized facts → renderer”的分层方向一致。

## 8. crazyJiaLin / we-read-tool

https://github.com/crazyJiaLin/we-read-tool

覆盖阅读统计、笔记管理、AI 整理和 Web 可视化。

可借鉴的不是技术栈，而是产品边界：

- AI 整理应建立在可搜索、可管理的笔记层上
- 视觉分析和知识整理最终需要互相跳转，而不是孤立页面

## 对本项目的路线影响

优先级从“继续加更多图”调整为：

1. **Visualize**：Heatmap / Reading Map / Cognitive Shift / Knowledge Graph / Profile / Unified Report
2. **Search**：本地全文搜索与证据召回
3. **Recall**：基于旧划线和想法的回顾 / 自测 / Feynman
4. **Flow**：Obsidian 增量同步、Markdown 导出、图片/PDF 分享
5. **Organize**：书单、Shelf Organizer、主题集合
6. **Act**：从阅读主题生成项目、写作题材或可执行 Skill

## 明确不做

- 不为了“AI 感”让模型重新计算原始统计值。
- 不把微信读书 category 直接冒充为知识主题。
- 不把书架收藏直接当成真实阅读投入。
- 不把完整 raw 个人数据、用户 review、搜索索引或私有 evidence 直接变成公开内容；Public Archive 仅按 `docs/publication-policy.md` 发布获授权且经过 validator 的有限事实、元数据与 bounded excerpts。
- 不把多个已有项目的前端功能机械复制进一个巨型应用。

`we-read` 的差异化应保持在：**本地优先 + 证据可追溯 + AI 解释与确定性事实分层 + 可组合 Skill**。
