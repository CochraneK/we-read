# 书架 + 笔记交叉分析（实用脚本）

把 `/shelf/sync` 和 `/user/notebooks` 两份数据合并后做筛选的代码模板。

## 完整模板

```python
import json, subprocess, datetime, os

API_KEY = os.environ["WEREAD_API_KEY"]
GATEWAY = "https://i.weread.qq.com/api/agent/gateway"

# VERSION 的权威来源是 ~/.claude/skills/weread/SKILL.md 顶部 frontmatter 的 version 字段。
# 这里的字面值可能滞后于真实最新值——执行前应该 grep 一下 weread/SKILL.md 确认。
# 别从用户 prompt 里抄版本号（A/B 测试发现 prompt 里的 version 经常是过时的）。
import re, pathlib
def _read_version():
    try:
        text = pathlib.Path(os.path.expanduser("~/.claude/skills/weread/SKILL.md")).read_text()
        m = re.search(r"^version:\s*([\d.]+)", text, re.M)
        if m: return m.group(1)
    except Exception:
        pass
    return "1.0.3"  # fallback，不一定最新
VERSION = _read_version()

def call(api_name, **params):
    body = {"api_name": api_name, "skill_version": VERSION, **params}
    r = subprocess.run(
        ["curl", "-s", "-X", "POST", GATEWAY,
         "-H", f"Authorization: Bearer {API_KEY}",
         "-H", "Content-Type: application/json",
         "-d", json.dumps(body)],
        capture_output=True, text=True
    )
    return json.loads(r.stdout)

# 拿两份数据
shelf = call("/shelf/sync")
notebooks = call("/user/notebooks", count=200)

# 建索引
shelf_books = {str(b["bookId"]): b for b in shelf.get("books", [])}
notebook_map = {str(b["book"]["bookId"]): b for b in notebooks.get("books", [])}

# 四种集合
read_deep = []         # 笔记 >= 10：吃透了
read_medium = []       # 笔记 3-10：认真读了
read_light = []        # 笔记 1-3：翻了一下
shelved_unread = []    # 书架有但 notebook 无：放着没动

for bid, book in shelf_books.items():
    nb = notebook_map.get(bid)
    note_count = nb.get("noteCount", 0) if nb else 0
    if note_count >= 10:
        read_deep.append((book, nb))
    elif note_count >= 3:
        read_medium.append((book, nb))
    elif note_count > 0:
        read_light.append((book, nb))
    else:
        shelved_unread.append(book)

# 隐藏深读：notebook 有但 shelf 没有（借阅/试读但深读）
hidden_deep = [
    nb for bid, nb in notebook_map.items()
    if bid not in shelf_books and nb.get("noteCount", 0) >= 10
]

# 最近活跃书（按 readUpdateTime 倒序）
recent = sorted(
    [b for b in shelf.get("books", []) if b.get("readUpdateTime", 0) > 0],
    key=lambda b: b["readUpdateTime"], reverse=True
)[:10]
```

## 按主题筛选

调用 `filter_by_topic(books, keywords)`：

```python
def filter_by_topic(books, keywords):
    """books 是 (book, notebook) 元组列表或 book 列表"""
    result = []
    for item in books:
        b = item[0] if isinstance(item, tuple) else item
        title = b.get("title", "")
        if any(k in title for k in keywords):
            result.append(item)
    return result
```

## 常用主题关键词组

照搬即可。需要扩充时优先加中文同义词。

```python
TOPIC_KEYWORDS = {
    "神经科学": ["脑", "意识", "神经", "心智", "认知", "记忆", "思维", "情绪"],
    "投资": ["投资", "估值", "价值", "巴菲特", "芒格", "段永平", "证券", "股票", "财务"],
    "心理学": ["心理", "行为", "情绪", "动机", "性格", "认知"],
    "哲学": ["哲学", "存在", "形而上", "伦理", "尼采", "海德格尔", "维特根斯坦"],
    "经济学": ["经济", "市场", "货币", "通胀", "凯恩斯", "哈耶克", "弗里德曼"],
    "AI": ["AI", "人工智能", "机器学习", "深度学习", "大模型", "智能"],
    "创业": ["创业", "增长", "产品", "MVP", "PMF", "0到1"],
    "历史": ["历史", "通史", "断代", "近代", "古代", "战争"],
    "文学": ["小说", "诗", "散文", "短篇", "长篇"],
    "推理": ["推理", "悬疑", "凶杀", "侦探", "罪案", "黑色"],
    "佛学": ["佛", "禅", "冥想", "正念", "般若", "金刚经"],
    "科普": ["科学", "宇宙", "物理", "生物", "化学", "数学"],
}
```

## 输出已读书目（带笔记深度标签）

```python
def render_books_in_topic(topic, books_with_notes):
    print(f"### {topic}已读 ({len(books_with_notes)} 本)\n")
    for book, nb in sorted(books_with_notes, key=lambda x: -(x[1].get("noteCount",0) if x[1] else 0)):
        title = book.get("title", "?")
        author = book.get("author", "?")
        note_count = nb.get("noteCount", 0) if nb else 0
        depth = "深读" if note_count >= 10 else "精读片段" if note_count >= 3 else "略读"
        print(f"- 「{title}」{author} ({depth}, {note_count}笔记)")
```

## 数据展示规范

调任何接口处理时间戳字段（`readUpdateTime` / `updateTime` / `finishTime` / `createTime`）时一律转 `YYYY-MM-DD`：

```python
def fmt_ts(ts):
    if not ts:
        return ""
    return datetime.datetime.fromtimestamp(ts).strftime("%Y-%m-%d")
```

阅读时长字段单位是秒，展示时转成「X 小时 Y 分钟」：

```python
def fmt_duration(seconds):
    h = seconds // 3600
    m = (seconds % 3600) // 60
    return f"{h}小时{m}分钟" if h else f"{m}分钟"
```
