# -*- coding: utf-8 -*-
"""从微信读书导出划线中筛选「名言警句」候选，打分+去重+版权分级。
输出 quote_lib/金句库.json（含 quotes + insights）。纯标准库，无需联网。
"""
import json, re, os
from datetime import datetime

SRC = "D:/workbuddy/微信读书/data/weread_notes_export.json"
OUT = "D:/workbuddy/微信读书/quote_lib"
os.makedirs(OUT, exist_ok=True)

data = json.load(open(SRC, encoding="utf-8"))

# ---------- 公版知识库（作者去世>50年；仅作第一道粗筛，出版前仍需人工法务复核） ----------
PD_AUTHORS = {
    "老子","李耳","庄周","庄子","列子","列御寇","孔子","孔丘","仲尼","孟轲","孟子",
    "荀况","荀子","韩非","墨翟","墨子","司马迁","李白","杜甫","王维","白居易","苏轼",
    "苏东坡","辛弃疾","李清照","曹操","陶渊明","屈原","王阳明","王守仁","曹雪芹",
    "罗贯中","施耐庵","吴承恩","蒲松龄","关汉卿","汤显祖","鲁迅","周树人","王国维",
    "莎士比亚","托尔斯泰","列夫·托尔斯泰","陀思妥耶夫斯基","费奥多尔·陀思妥耶夫斯基",
    "歌德","卡夫卡","加缪","阿尔贝·加缪","叔本华","尼采","伏尔泰","卢梭","培根",
    "蒙田","梭罗","爱默生","纪伯伦","泰戈尔","芥川龙之介","夏目漱石","川端康成",
    "太宰治","三岛由纪夫","紫式部","清少纳言","荷马","但丁","塞万提斯","雨果",
    "巴尔扎克","狄更斯","福楼拜","莫泊桑","契诃夫","欧·亨利","海明威","马克·吐温",
    "屠格涅夫","果戈里","易卜生","安徒生","王尔德",
}
PD_TITLE_HINTS = [
    "论语","道德经","老子","庄子","孟子","荀子","韩非子","墨子","列子","史记",
    "诗经","楚辞","周易","易经","尚书","礼记","大学","中庸","资治通鉴","红楼梦",
    "三国演义","西游记","水浒传","聊斋志异","世说新语","唐诗","宋词","千家诗",
    "金刚经","心经","坛经","孙子兵法","鬼谷子","资治通鉴","古文观止",
]

# ---------- 金句度词典 ----------
WISDOM = [
    "人生","生命","活着","生活","命运","意义","自我","自己","本真","真实","伪装",
    "孤独","自由","灵魂","内心","爱","心","情感","思念","温柔","时间","时光","岁月",
    "当下","现在","过去","未来","青春","知识","真理","智慧","思考","理解","认知",
    "无知","学习","读书","朋友","他人","陪伴","宽容","痛苦","苦难","悲伤","绝望",
    "勇气","坚强","挫折","成长","遗憾","希望","现实","理想","人性","平静","选择",
    "死亡","记忆","幸福","平和","独立","尊严","信仰","世界","平凡","伟大",
    "坚持","善良","真诚","放下","释怀","故乡","远方","包容","控制","永恒",
    "正义","平等","诚实","原谅","谦逊","清醒","热爱","等待","失去","得到",
]
THEME_MAP = {
    "人生": ["人生","生命","活着","生活","命运","意义","遗憾","平凡","伟大"],
    "自我": ["自我","自己","本真","真实","伪装","孤独","自由","灵魂","内心","独立","尊严"],
    "情感": ["爱","心","情感","思念","温柔","喜欢","幸福","悲伤"],
    "时间": ["时间","时光","岁月","当下","现在","过去","未来","青春"],
    "认知": ["知识","真理","智慧","思考","理解","认知","无知","学习","读书"],
    "关系": ["朋友","他人","陪伴","宽容","理解","人际"],
    "苦难": ["痛苦","苦难","悲伤","绝望","勇气","坚强","挫折","成长"],
    "社会": ["社会","时代","历史","权力","公平","世界","人性","现实","理想"],
}
NOISE = re.compile(r"z-lib|1lib|\.pdf|http|https|证书|下载|微盘|百度网盘|pan\.baidu|kindle|epub", re.I)
YEAR = re.compile(r"(19|20)\d\d")
QUOTE_OPEN = ("「", '"', "“", "'", "‘", "『")
QUOTE_CLOSE = ("」", '"', "”", "'", "’", "』")
PLOT_START = re.compile(r"^(他|她|它|他们|她们|它们|那人|此人|这家|本书|小说|故事|这天|那天|这时|那时)")


def clean(t: str) -> str:
    t = t.strip()
    t = re.sub(r'^[\s"\'"「」『』“”‘’]+', "", t)
    t = re.sub(r'[\s"\'"「」『』“”‘’]+$', "", t)
    # 去掉首/尾的中文标点碎片（如句首的 。，、；： 等多是章节片段）
    t = re.sub(r'^[。，、；：！？…—~·\s]+', "", t)
    t = re.sub(r'[。，、；：！？…—~·\s]+$', "", t)
    return t


def theme_of(t: str) -> str:
    for th, words in THEME_MAP.items():
        if any(w in t for w in words):
            return th
    return "其他"


def clean_title(t: str) -> str:
    """清洗书名：去掉版本/影视/出版社等括号噪声，优先保留《》内的真书名。"""
    t = t.strip()
    m = re.search(r"《([^》]+)》", t)
    if m:
        return m.group(1).strip()
    t = re.split(r"[（(【\[]", t)[0].strip()
    return t


def score_quote(t: str, has_bookref: bool) -> int:
    s = 0
    n = len(t)
    # 长度：精炼优先
    if 12 <= n <= 26:
        s += 22
    elif 27 <= n <= 38:
        s += 18
    elif 39 <= n <= 50:
        s += 10
    elif 51 <= n <= 64:
        s += 2
    else:
        s -= 15
    hits = sum(1 for w in WISDOM if w in t)
    s += min(hits, 4) * 6
    if re.search(r"[像如仿佛如同好似犹如]", t):
        s += 7
    if "？" in t or "?" in t:
        s += 7
    if re.search(r"不是.*而是|与其.*不如|不在于.*而在于|越是.*越|与其说.*不如", t):
        s += 8
    if re.search(r"没有.*(就|才|不)|不.*(才|就|也)|并非|不要|不必", t):
        s += 6
    if t.count("，") >= 1 and ("；" in t or t.count("，") >= 2):
        s += 4
    s -= min(t.count("他") + t.count("她") + t.count("它"), 4) * 3
    if has_bookref:
        s -= 3
    if YEAR.search(t):
        s -= 6
    if "（" in t or "(" in t:
        s -= 3
    if PLOT_START.match(t):
        s -= 22
    return max(0, min(100, s))


def pd_flag(author: str, title: str) -> str:
    a = author.strip()
    if a in PD_AUTHORS:
        return "pd"
    if any(h in title for h in PD_TITLE_HINTS):
        return "pd"
    return "protected"


quotes = []
insights = []
for b in data:
    title = clean_title(b.get("title", ""))
    author = b.get("author", "")
    pd = pd_flag(author, title)
    for m in b.get("marks", []):
        raw = m.get("text", "")
        if not raw:
            continue
        if NOISE.search(raw):
            continue
        # 对话包裹（「」或成对引号）大概率是剧情对白，丢弃
        st = raw.strip()
        if st.startswith(QUOTE_OPEN) and any(c in raw for c in QUOTE_CLOSE):
            continue
        t = clean(raw)
        n = len(t)
        if not (8 <= n <= 64):
            continue
        # 句首必须是实词（汉字或我/你/他等），否则是章节片段，丢弃
        if not re.match(r"^[\u4e00-\u9fff我你他它这那一是不没如人在当若有若此]", t):
            continue
        if PLOT_START.match(t):
            continue
        has_bookref = "《" in raw
        sc = score_quote(t, has_bookref)
        quotes.append({
            "bookId": b.get("bookId"), "title": title, "author": author,
            "chapter": m.get("chapter", ""), "text": t, "score": sc,
            "theme": theme_of(t), "public_domain": pd, "selected": False,
        })
    for r in b.get("reviews", []):
        insights.append({
            "title": title, "author": author, "chapter": r.get("chapter", ""),
            "abstract": r.get("abstract", ""), "content": r.get("content", ""),
            "createTime": r.get("createTime", 0),
        })

# 去重（归一化后比对，保留最高分）
def norm(t):
    return re.sub(r"\s+", "", re.sub(r"[^\u4e00-\u9fffA-Za-z0-9]", "", t))

seen = {}
for q in quotes:
    k = norm(q["text"])
    if not k:
        continue
    if k in seen:
        if q["score"] > seen[k]["score"]:
            seen[k] = q
    else:
        seen[k] = q
dedup = list(seen.values())
dedup.sort(key=lambda x: x["score"], reverse=True)

# 选中：分数>=30 取 Top 500 作为策划池；A级(>=42)可直接做卡，B级(30-41)需二审
SELECT_THRESH = 30
SELECT_CAP = 500
sel = [q for q in dedup if q["score"] >= SELECT_THRESH]
sel = sel[:SELECT_CAP]
sel_ids = {id(q) for q in sel}
for q in dedup:
    if id(q) in sel_ids:
        q["selected"] = True
        q["tier"] = "A" if q["score"] >= 42 else "B"
    else:
        q["selected"] = False
        q["tier"] = None

out = {
    "meta": {
        "generated": datetime.now().isoformat(timespec="seconds"),
        "total_marks": sum(len(b.get("marks", [])) for b in data),
        "candidates_after_filter": len(quotes),
        "after_dedup": len(dedup),
        "selected": len(sel),
        "select_threshold": SELECT_THRESH,
        "select_cap": SELECT_CAP,
        "pd_selected": sum(1 for q in sel if q["public_domain"] == "pd"),
        "insights_count": len(insights),
        "note": "public_domain 仅按作者/书名粗筛，出版前须人工法务复核；score 为启发式金句度(0-100)。",
    },
    "quotes": dedup,
    "insights": insights,
}
with open(os.path.join(OUT, "金句库.json"), "w", encoding="utf-8") as f:
    json.dump(out, f, ensure_ascii=False, indent=2)

# 主题分布
from collections import Counter
theme_cnt = Counter(q["theme"] for q in sel)
print(f"候选(过滤后)={len(quotes)}  去重后={len(dedup)}  选中={len(sel)}  (其中公版={out['meta']['pd_selected']})")
print(f"主题分布(选中): {dict(theme_cnt)}")

# 导出 Top60 可读 Markdown 供人工抽检
top = dedup[:60]
lines = ["# 金句库 Top 60（按金句度排序，人工抽检用）\n"]
for i, q in enumerate(top, 1):
    lines.append(f"{i}. {q['text']}  \n   —— {q['author']}《{q['title']}》 〔{q['theme']}·{q['public_domain']}·{q['score']}〕\n")
with open(os.path.join(OUT, "金句库_top60.md"), "w", encoding="utf-8") as f:
    f.write("\n".join(lines))
print("已写出 quote_lib/金句库.json 与 金句库_top60.md")
