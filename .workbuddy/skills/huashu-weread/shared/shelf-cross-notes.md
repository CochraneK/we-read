# 书架 + 笔记交叉分析

这份文档描述 `huashu-weread` 的底层交叉分析方法。项目已有确定性实现时，**优先使用脚本输出，不要每个 workflow 临时重写一份 join 逻辑**。

## 首选：统一事实层

```bash
python scripts/build_visualization_context.py
python scripts/build_advisor_context.py
```

`visualization_context.json` 明确保留：

- `inShelf`
- `inNotebook`
- `shelfReadUpdateTime`
- progress / reading time
- note / mark / review counts

`advisor_context.json` 再派生：

- 深读 / 中读 / 轻读 / 浅尝 / 无笔记；
- 不在书架但有深读证据的书；
- 在书架但尚未形成笔记证据的书；
- 最近 7 / 30 天活动；
- 类别 engagement rate。

这样 Advisor / Path / Review 可以消费同一套事实，而不是不同脚本各算一套口径。

## 如果必须直接调用 Gateway

版本号必须来自**官方 weread skill 的权威 frontmatter**。不要从旧 prompt、示例或本文件硬编码版本。

本仓库当前 API 脚本基线是 `1.0.4`，但它未来仍可能变化；若本机找不到官方 Skill 版本，应明确失败或让调用方提供版本，而不是静默回退到一个可能过期的常量。

```python
import json, os, pathlib, re, subprocess

API_KEY = os.environ["WEREAD_API_KEY"]
GATEWAY = "https://i.weread.qq.com/api/agent/gateway"


def read_version():
    candidates = [
        pathlib.Path(os.path.expanduser("~/.claude/skills/weread/SKILL.md")),
    ]
    for path in candidates:
        try:
            text = path.read_text(encoding="utf-8")
            match = re.search(r"^version:\s*([\d.]+)", text, re.M)
            if match:
                return match.group(1)
        except OSError:
            pass
    raise RuntimeError("未找到官方 weread skill version；不要使用硬编码旧版本")


def call(api_name, **params):
    body = {"api_name": api_name, "skill_version": read_version(), **params}
    result = subprocess.run(
        [
            "curl", "-s", "-X", "POST", GATEWAY,
            "-H", f"Authorization: Bearer {API_KEY}",
            "-H", "Content-Type: application/json",
            "-d", json.dumps(body, ensure_ascii=False),
        ],
        capture_output=True,
        text=True,
        check=True,
    )
    payload = json.loads(result.stdout)
    if payload.get("upgrade_info"):
        raise RuntimeError(f"weread skill 需要升级: {payload['upgrade_info']}")
    if payload.get("errcode", 0) != 0:
        raise RuntimeError(payload.get("errmsg") or f"errcode={payload.get('errcode')}")
    return payload
```

## 核心集合

直接 join `/shelf/sync` 与 `/user/notebooks` 时，至少保留这些集合：

```text
shelf ∩ notebook       → 书架内且形成笔记证据
shelf - notebook       → 收藏/兴趣，但不能称作“读过”
notebook - shelf       → 隐藏阅读证据，借阅/试读等来源可能被书架视角漏掉
recent activity        → 当前兴趣的次级信号
```

笔记深度只是一种行为证据，不是“掌握程度”的心理测量。当前 Advisor Context 使用互斥分档：

```text
20+   deep
10–19 medium
3–9   light
1–2   glance
0     none
```

## 主题筛选

标题/类别关键词匹配只能做确定性候选筛选，不能等价为语义分类。Path Context 支持显式别名：

```bash
python scripts/build_reading_path_context.py \
  --topic "神经科学" \
  --keywords "脑,意识,认知,记忆"
```

主题过宽时先让用户细化；主题过窄时明确说明平台覆盖不足，不要静默扩展到相邻但不等价的领域。

## 最近活动

只有真实 `readUpdateTime > 0` 的书进入最近活动。`readUpdateTime=0` 代表尚无打开证据，不能为了排序方便当成最近阅读。

用户明确指定主题时，主题优先；只有用户没有给方向时，最近 7/30 天活动才可以帮助选择 Advisor 的候选主题。

## 数据展示

- 时间戳 → `YYYY-MM-DD`；
- 秒 → “X 小时 Y 分钟”；
- 进度 → `X%`；
- marks 是保存的原文，不自动视为用户观点；
- reviews 是用户自己的想法证据；
- 对外公开页面不发布原始 mark/review 正文。
