# Narrative Review Context：先做周期事实，再选平台写作

Review workflow 的事实阶段已有确定性实现：

```bash
python scripts/build_narrative_review_context.py \
  --start 2026-01-01 \
  --end 2026-09-14
```

输出：

```text
data/analysis/narrative_review_context.json
```

对应 schema：

```text
schemas/narrative_review_context.schema.json
```

## 它会计算什么

- 周期内日级阅读时长与活跃天数；
- 阅读最集中的月份；
- 完成 / 在读 / 浅尝 / 重读 / 进度未知但有活动；
- 有较强笔记证据 vs 轻读/无笔记；
- 周期内笔记最多的书；
- 累计投入时长靠前的书（明确标注它是累计值，不伪装成周期值）；
- 进度 30–70%、距周期末 90 天以上无活动的卡住候选；
- 笔记主题在周期前后半段的变化候选。

## 时间口径

周期总阅读时长优先从：

```text
weread_readdata.json → monthly[*].readTimes
```

按**日**去重后再过滤起止日期。这样季度、半年、过去若干月不会直接套用整月/整年的粗总量。

## 不推断“为什么”

如果前后半段 Top 类别变化，只标：

```text
focusShiftCandidate
```

这不是“用户因为某件事改变兴趣”的证据。原因只能由用户补充或其他明确证据支持。

## 平台 gate

没有指定出口时：

```json
"readyForNarrative": false,
"requiresPlatformConfirmation": true
```

支持：

- `moments`：朋友圈；
- `wechat`：公众号；
- `xiaohongshu`：小红书；
- `video`：视频脚本；
- `journal`：个人留存。

用户确认平台后，才进入真正的叙事写作层。

## 写作层必须保留的约束

- 至少写一个数字/阶段反差；
- 至少保留一个“不完美”：放下、卡住、轻读、没有沉淀等；
- 下一周期目标必须具体；
- 不编造兴趣转向或弃书原因；
- 完成但没有笔记的书仍算完成，只是不优先拿来写深度段落。
