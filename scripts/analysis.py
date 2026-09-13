#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""微信读书全量分析：A-E 16 项 + 单页 HTML 交互看板。
读取 5 个 JSON（shelf / notes / readdata / progress / bookinfo），输出 analysis/reading_dashboard.html + CSV。
"""
import json, os, re, datetime, html
import random, io, base64
from collections import Counter, defaultdict

BASE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(BASE)                       # 项目根目录
DATA = os.path.join(ROOT, "data")                  # 数据统一放在 data/
OUT_DIR = os.path.join(DATA, "analysis")           # 分析产物 -> data/analysis
os.makedirs(OUT_DIR, exist_ok=True)

SHELF = json.load(open(os.path.join(DATA, "weread_shelf.json"), encoding="utf-8"))
NOTES = json.load(open(os.path.join(DATA, "weread_notes_export.json"), encoding="utf-8"))
READ = json.load(open(os.path.join(DATA, "weread_readdata.json"), encoding="utf-8"))
PROG = json.load(open(os.path.join(DATA, "weread_progress.json"), encoding="utf-8"))
INFO = json.load(open(os.path.join(DATA, "weread_bookinfo.json"), encoding="utf-8"))

import plotly.graph_objects as go
from wordcloud import WordCloud
from plotly.subplots import make_subplots

# ---- 暖中性·柔和卡片风 设计令牌 ----
COLORWAY = ["#C2724B", "#D9A441", "#8A9A6B", "#B5563F", "#A8774E", "#C98A4B", "#7E9B8E", "#B7AE9F"]
WC_COLORS = ["#C2724B","#D9A441","#8A9A6B","#B5563F","#A8774E","#C98A4B","#7E9B8E"]
def bar_h(n): return max(440, n*28 + 100)
WARM_FONT = dict(
    family='"SF Pro Display","Inter","Helvetica Neue",Arial,sans-serif,"PingFang SC","Microsoft YaHei","Noto Sans SC"',
    size=13, color="#2B2724",
)
FONT = WARM_FONT
WARM = go.layout.Template(
    layout=go.Layout(
        paper_bgcolor="#FFFFFF",
        plot_bgcolor="#FFFFFF",
        font=WARM_FONT,
        title=dict(font=dict(size=15, color="#2B2724")),
        margin=dict(l=48, r=24, t=40, b=40),
        colorway=COLORWAY,
        hoverlabel=dict(bgcolor="#2B2724", font=dict(color="#FBF8F3"), bordercolor="#E6DECF"),
        xaxis=dict(
            gridcolor="#EFE9DC", zeroline=False, tickcolor="#7A7066",
            linecolor="#E6DECF",
        ),
        yaxis=dict(
            gridcolor="#EFE9DC", zeroline=False, tickcolor="#7A7066",
            linecolor="#E6DECF",
        ),
    )
)
PLOT_CFG = dict(include_plotlyjs=True, full_html=False)

def fig2html(fig, div_id=None, height=420):
    fig.update_layout(template=WARM, font=WARM_FONT, margin=dict(l=48, r=24, t=40, b=40), height=height)
    return fig.to_html(full_html=False, include_plotlyjs=PLOT_CFG["include_plotlyjs"],
                       div_id=div_id, config={"displayModeBar": False})

SECTIONS = defaultdict(list)
CUR_SEC = "summary"
def set_sec(s):
    global CUR_SEC
    CUR_SEC = s
def add(fig=None, table_html=None, height=420):
    global CUR_SEC
    if fig is not None:
        SECTIONS[CUR_SEC].append(f'<div class="chart">{fig2html(fig, height=height)}</div>')
    if table_html:
        SECTIONS[CUR_SEC].append(f'<div class="tbl">{table_html}</div>')
    PLOT_CFG["include_plotlyjs"] = False  # 只在第一个图嵌入
def add_raw(html_str):
    SECTIONS[CUR_SEC].append(html_str)

def table(headers, rows, cls="data"):
    h = "<tr>" + "".join(f"<th>{html.escape(str(x))}</th>" for x in headers) + "</tr>"
    body = ""
    for r in rows:
        body += "<tr>" + "".join(f"<td>{html.escape(str(x))}</td>" for x in r) + "</tr>"
    return f'<table class="{cls}"><thead>{h}</thead><tbody>{body}</tbody></table>'

def fmt_hms(sec):
    if not sec: return "0"
    h = sec // 3600; m = (sec % 3600) // 60
    if h: return f"{h}小时{m}分"
    return f"{m}分"

# ---- 构建 book 索引 ----
shelf_by_id = {b["bookId"]: b for b in SHELF.get("books", [])}
notes_by_id = {b["bookId"]: b for b in NOTES}

def note_count(b): return len(b["marks"]) + len(b["reviews"])

def cat_of(bid):
    b = shelf_by_id.get(bid)
    return (b or {}).get("category") or notes_by_id.get(bid, {}).get("category") or "未知"

def author_of(bid):
    b = shelf_by_id.get(bid)
    return (b or {}).get("author") or notes_by_id.get(bid, {}).get("author") or "未知"

def secret_of(bid):
    return (shelf_by_id.get(bid) or {}).get("secret", 0)

# ================= 摘要卡 =================
overall = READ.get("overall") or {}
total_sec = overall.get("totalReadTime") or 0
read_days = overall.get("readDays") or 0
n_books = len(SHELF.get("books", []))
n_notebooks = len(NOTES)
total_marks = sum(len(b["marks"]) for b in NOTES)
total_reviews = sum(len(b["reviews"]) for b in NOTES)
pref_cat = overall.get("preferCategory") or []
top_cat = pref_cat[0]["categoryTitle"] if pref_cat else "—"
summary = [
    ("书架藏书", f"{n_books} 本"),
    ("有笔记书", f"{n_notebooks} 本"),
    ("划线 / 想法", f"{total_marks} / {total_reviews}"),
    ("累计阅读", fmt_hms(total_sec)),
    ("有效阅读天数", f"{read_days} 天"),
    ("偏好分类", top_cat),
]
cards = "".join(f'<div class="card"><div class="c-val">{v}</div><div class="c-lab">{k}</div></div>' for k, v in summary)

# ================= A1 类别参与度矩阵 =================
set_sec("A1")
cat_books = Counter()
cat_notes = Counter()
for bid in notes_by_id:
    c = cat_of(bid)
    cat_books[c] += 1
    cat_notes[c] += note_count(notes_by_id[bid])
# 也统计书架全部书的类别（含无笔记）
for b in SHELF.get("books", []):
    cat_books[b.get("category") or "未知"] += 1
top_cats = [c for c, _ in cat_books.most_common(15)]
density = {c: round(cat_notes[c] / cat_books[c], 1) if cat_books[c] else 0 for c in top_cats}
fig_a1 = go.Figure()
fig_a1.add_bar(x=top_cats, y=[cat_books[c] for c in top_cats], name="藏书数(本)", marker_color="#C2724B")
fig_a1.add_bar(x=top_cats, y=[cat_notes[c] for c in top_cats], name="笔记数(划线+想法)", marker_color="#D9A441", yaxis="y2")
fig_a1.update_layout(barmode="group", title="A1 类别参与度矩阵（藏书 vs 笔记，区分囤书/真读）",
                     yaxis=dict(title="藏书数"), yaxis2=dict(title="笔记数", overlaying="y", side="right"))
add(fig_a1, height=bar_h(15))
# 气泡：x藏书 y密度 大小=笔记
fig_a1b = go.Figure()
fig_a1b.add_trace(go.Scatter(x=[cat_books[c] for c in top_cats], y=[density[c] for c in top_cats],
    mode="text+markers", text=top_cats, textposition="top center",
    marker=dict(size=[cat_notes[c] for c in top_cats], sizemode="area", sizeref=2*max(cat_notes.values())/(60**2), color="#8A9A6B", opacity=0.6)))
fig_a1b.update_layout(title="A1b 囤书型 vs 真读型（x=藏书, y=每本笔记密度, 气泡=总笔记）",
                      xaxis_title="藏书数(本)", yaxis_title="每本平均笔记数")
add(fig_a1b)
rows = [[c, cat_books[c], cat_notes[c], density[c]] for c in top_cats]
add(table_html=table(["类别", "藏书数", "笔记数", "每本密度"], rows))
with open(os.path.join(OUT_DIR, "A1_category_matrix.csv"), "w", encoding="utf-8-sig") as f:
    f.write("类别,藏书数,笔记数,每本密度\n" + "\n".join(f"{c},{cat_books[c]},{cat_notes[c]},{density[c]}" for c in top_cats))

# ================= A2 作者集中度 =================
set_sec("A2")
author_books = Counter()
author_notes = Counter()
for bid in notes_by_id:
    a = author_of(bid)
    author_books[a] += 1
    author_notes[a] += note_count(notes_by_id[bid])
uniq_auth = len(author_books)
multi = sum(1 for a, n in author_books.items() if n >= 2)
top_auth = author_notes.most_common(15)
fig_a2 = go.Figure(go.Bar(x=[a for a, _ in top_auth][::-1], y=[n for _, n in top_auth][::-1],
                          marker_color="#7E9B8E"))
fig_a2.update_layout(title="A2 作者集中度 Top15（按笔记数）", xaxis_title="作者", yaxis_title="笔记数")
add(fig_a2, height=bar_h(15))
add(table_html=table(["指标", "值"], [["唯一作者数", uniq_auth], ["重复阅读(≥2本)作者数", multi],
                            ["最多产作者", f"{top_auth[0][0]} ({top_auth[0][1]}条)" if top_auth else "—"]]))
with open(os.path.join(OUT_DIR, "A2_authors.csv"), "w", encoding="utf-8-sig") as f:
    f.write("作者,书本数,笔记数\n" + "\n".join(f"{a},{author_books[a]},{author_notes[a]}" for a, _ in author_notes.most_common(50)))

# ================= A3 参与人格分型 =================
set_sec("A3")
meds = [note_count(b) for b in NOTES]
m_marks = sorted(len(b["marks"]) for b in NOTES)
m_revs = sorted(len(b["reviews"]) for b in NOTES)
def median(x): return x[len(x)//2] if x else 0
med_m, med_r = median(m_marks), median(m_revs)
types = Counter()
for b in NOTES:
    M, R = len(b["marks"]), len(b["reviews"])
    if M >= med_m and R >= med_r: t = "沉浸型(高划高想)"
    elif M >= med_m: t = "高亮型(多划少想)"
    elif R >= med_r: t = "思考型(多想少划)"
    else: t = "掠读型(低划低想)"
    types[t] += 1
fig_a3 = go.Figure(go.Bar(x=list(types.keys()), y=list(types.values()),
                           marker_color=["#B5563F", "#8A9A6B", "#D9A441", "#B7AE9F"]))
fig_a3.update_layout(title=f"A3 参与人格分型（中线: 划线{med_m}/本, 想法{med_r}/本）", yaxis_title="书数")
add(fig_a3)
add(table_html=table(["分型", "书数", "占比"], [[k, v, f"{v/len(NOTES)*100:.1f}%"] for k, v in types.most_common()]))

# ================= A4 私密 vs 公开 =================
set_sec("A4")
sec_books = [bid for bid in notes_by_id if secret_of(bid) == 1]
sec_cats = Counter(cat_of(b) for b in sec_books)
pub_cats = Counter(cat_of(b) for b in notes_by_id if secret_of(b) == 0)
all_sec = sorted(set(list(sec_cats) + list(pub_cats)))[:15]
fig_a4 = go.Figure()
fig_a4.add_bar(x=all_sec, y=[sec_cats.get(c, 0) for c in all_sec], name="私密", marker_color="#C98A4B")
fig_a4.add_bar(x=all_sec, y=[pub_cats.get(c, 0) for c in all_sec], name="公开", marker_color="#7E9B8E")
fig_a4.update_layout(barmode="group", title=f"A4 私密({len(sec_books)}本) vs 公开 类别对比", yaxis_title="书数")
add(fig_a4)
sec_titles = ", ".join(notes_by_id[b]["title"][:18] for b in sec_books[:8])
add(table_html=table(["指标", "值"], [["私密书总数", len(sec_books)], ["私密书样本", sec_titles]]))

# ================= B5 月度时间线（真实阅读时长 + 笔记数） =================
set_sec("B5")
months = sorted(READ.get("monthly", {}).keys())
real_hours = [ (READ["monthly"][m].get("totalReadTime") or 0)/3600 for m in months ]
# 笔记数按月（createTime代理）
note_month = Counter()
for b in NOTES:
    for it in b["marks"] + b["reviews"]:
        ct = it.get("createTime")
        if ct:
            note_month[datetime.datetime.fromtimestamp(int(ct)).strftime("%Y-%m")] += 1
note_counts = [note_month.get(m, 0) for m in months]
fig_b5 = make_subplots(specs=[[{"secondary_y": True}]])
fig_b5.add_trace(go.Scatter(x=months, y=real_hours, name="真实阅读时长(小时)", line=dict(color="#B5563F")), secondary_y=False)
fig_b5.add_trace(go.Scatter(x=months, y=note_counts, name="笔记数(代理)", line=dict(color="#7E9B8E", dash="dot")), secondary_y=True)
fig_b5.update_layout(title="B5 月度阅读时间线（红实线=真实阅读小时, 青绿点线=笔记数）", xaxis_title="月份")
fig_b5.update_yaxes(title_text="阅读小时", secondary_y=False)
fig_b5.update_yaxes(title_text="笔记数", secondary_y=True)
add(fig_b5)
with open(os.path.join(OUT_DIR, "B5_monthly.csv"), "w", encoding="utf-8-sig") as f:
    f.write("月份,真实阅读小时,笔记数\n" + "\n".join(f"{m},{round(real_hours[i],1)},{note_counts[i]}" for i, m in enumerate(months)))

# ================= B6 日内时段 =================
set_sec("B6")
prefer = overall.get("preferTime") or []
# preferTime 从6点开始24个值
hours = list(range(6, 30))
hour_labels = [(h % 24) for h in hours]
real_by_hour = {hour_labels[i]: (prefer[i] if i < len(prefer) else 0) for i in range(len(hour_labels))}
# 笔记 createTime 小时分布
note_hour = Counter()
for b in NOTES:
    for it in b["marks"] + b["reviews"]:
        ct = it.get("createTime")
        if ct: note_hour[datetime.datetime.fromtimestamp(int(ct)).hour] += 1
all_hours = list(range(24))
fig_b6 = go.Figure()
fig_b6.add_bar(x=all_hours, y=[real_by_hour.get(h, 0)/3600 for h in all_hours], name="真实阅读(小时)", marker_color="#B5563F")
fig_b6.add_bar(x=all_hours, y=[note_hour.get(h, 0) for h in all_hours], name="笔记数(代理)", marker_color="#7E9B8E")
fig_b6.update_layout(barmode="group", title="B6 日内时段分布（真实阅读秒→小时 vs 笔记数）", xaxis_title="小时", yaxis_title="量")
add(fig_b6)
night = sum(real_by_hour.get(h, 0) for h in range(22, 24)) + sum(real_by_hour.get(h, 0) for h in range(0, 6))
day = sum(real_by_hour.get(h, 0) for h in range(6, 22))
pref_word = overall.get("preferTimeWord") or ("夜间型" if night > day else "白天型")
add(table_html=table(["指标", "值"], [["偏好时段(官方)", pref_word], ["夜间(22-5点)阅读占比", f"{night/(night+day)*100:.0f}%" if night+day else "—"]]))

# ================= B7 年×月热力图 + 星期 =================
set_sec("B7")
years = sorted(READ.get("annually", {}).keys())
heat_z = []
for y in years:
    row = []
    for mo in range(1, 13):
        key = f"{y}-{mo:02d}"
        row.append((READ.get("monthly", {}).get(key, {}).get("totalReadTime") or 0)/3600)
    heat_z.append(row)
fig_b7 = go.Figure(go.Heatmap(z=heat_z, x=[f"{m}月" for m in range(1,13)], y=years,
                               colorscale=["#F7F1E6", "#E8C9A0", "#D98E5A", "#C2724B", "#9A5436"],
                               colorbar=dict(title="阅读小时")))
fig_b7.update_layout(title="B7 年×月 真实阅读时长热力图")
add(fig_b7, height=480)
# 星期（笔记代理）
wd = Counter()
for b in NOTES:
    for it in b["marks"] + b["reviews"]:
        ct = it.get("createTime")
        if ct: wd[datetime.datetime.fromtimestamp(int(ct)).weekday()] += 1
wd_names = ["周一","周二","周三","周四","周五","周六","周日"]
fig_b7b = go.Figure(go.Bar(x=wd_names, y=[wd.get(i,0) for i in range(7)], marker_color="#7E9B8E"))
fig_b7b.update_layout(title="B7b 星期分布（笔记创建时间代理）", yaxis_title="笔记数")
add(fig_b7b)

# ================= C8 划线关键词云（jieba） =================
set_sec("C8")
import jieba
STOP = set("的 了 是 在 我 你 他 她 它 们 也 都 就 而 与 和 及 或 一个 一种 这个 那个 我们 你们 他们 自己 因为 所以 但是 如果 已经 可以 没有 不是 就是 还是 这样 那样 什么 怎么 这些 那些 这种 那种 一种 一些 一样 一直 现在 时候 知道 觉得 出来 起来 通过 由于 以及 之后 之前 进行 成为 可能 应该 非常 这么 那么 一边 比如 不过 只是 而且 虽然 但是 一个 对于 关于 以及 仍然 依然 并且 然后 还是 还有 只是 不过 方面 问题 作者 本书 小说 我们 他们 自己 没有 不会 不能 这种 那种".split())
def seg(text):
    out = []
    for w in jieba.cut(text):
        w = w.strip()
        if len(w) < 2: continue
        if w in STOP: continue
        if re.fullmatch(r"[\s\W\d]+", w): continue
        out.append(w)
    return out
wc = Counter()
for b in NOTES:
    for m in b["marks"]:
        wc.update(seg(m["text"]))
top_words = wc.most_common(40)
def _wc_color(*a, **k): return random.choice(WC_COLORS)
wc_img = WordCloud(font_path="C:/Windows/Fonts/msyh.ttc", background_color=None, mode="RGBA",
                   max_words=80, width=900, height=500, prefer_horizontal=0.85, margin=6,
                   relative_scaling=0.5, color_func=_wc_color).generate_from_frequencies(dict(wc))
buf = io.BytesIO(); wc_img.to_image().save(buf, format="PNG"); buf.seek(0)
b64 = base64.b64encode(buf.read()).decode()
add_raw(f'<div class="wordcloud"><img src="data:image/png;base64,{b64}" alt="划线高频词云"></div>')
add(table_html=table(["排名","词","次数"], [[i+1, w, n] for i,(w,n) in enumerate(top_words[:15])]))
with open(os.path.join(OUT_DIR, "C8_keywords.csv"), "w", encoding="utf-8-sig") as f:
    f.write("词,次数\n" + "\n".join(f"{w},{n}" for w, n in top_words))

# ================= C9 想法情感极性 =================
set_sec("C9")
POS = "喜欢 赞 感动 好 深刻 推荐 共鸣 精彩 优美 温暖 力量 真实 真诚 智慧 通透 治愈 精彩 棒 爱 美 温柔 坚定 勇气 希望".split()
NEG = "无聊 烂 差 失望 垃圾 问题 矛盾 批判 荒诞 虚伪 残酷 悲哀 痛苦 焦虑 愤怒 恶心 枯燥 矫情 做作 压抑 绝望 孤独 撕裂 扭曲".split()
def polarity(text):
    p = sum(text.count(w) for w in POS); n = sum(text.count(w) for w in NEG)
    if p > n: return "正面"
    if n > p: return "负面"
    return "中性"
rev_texts = [r["content"] for b in NOTES for r in b["reviews"] if r.get("content")]
pol = Counter(polarity(t) for t in rev_texts)
fig_c9 = go.Figure(go.Pie(labels=list(pol.keys()), values=list(pol.values()),
                           marker=dict(colors=COLORWAY)))
fig_c9.update_layout(title=f"C9 想法情感极性（{len(rev_texts)}条点评，词典法）")
add(fig_c9)
# review 关键词
rwc = Counter()
for t in rev_texts:
    rwc.update(seg(t))
top_rw = rwc.most_common(25)
fig_c9b = go.Figure(go.Bar(x=[w for w, _ in top_rw][::-1], y=[n for _, n in top_rw][::-1], marker_color="#C98A4B"))
fig_c9b.update_layout(title="C9b 想法高频词 Top25", xaxis_title="词", yaxis_title="次数")
add(fig_c9b, height=bar_h(25))
add(table_html=table(["极性", "条数", "占比"], [[k, v, f"{v/len(rev_texts)*100:.0f}%"] for k, v in pol.most_common()]))

# ================= C10 被引用最多原文 =================
set_sec("C10")
text_freq = Counter()
for b in NOTES:
    for m in b["marks"]:
        t = (m["text"] or "").strip().replace("\n", " ")
        if len(t) >= 6:
            text_freq[t] += 1
repeated = [(t, n) for t, n in text_freq.items() if n >= 2]
repeated.sort(key=lambda x: -x[1])
fig_c10 = go.Figure(go.Bar(x=[f"#{i+1}" for i in range(len(repeated[:15]))],
                            y=[n for _, n in repeated[:15]], marker_color="#C2724B"))
fig_c10.update_layout(title=f"C10 重复划线原文（跨书/同书多次划，共{len(repeated)}条重复）", yaxis_title="重复次数")
add(fig_c10, height=bar_h(15))
rows = [[i+1, t[:50], n] for i, (t, n) in enumerate(repeated[:20])]
add(table_html=table(["#", "原文(截断)", "重复"], rows))
with open(os.path.join(OUT_DIR, "C10_repeated_quotes.csv"), "w", encoding="utf-8-sig") as f:
    f.write("序号,原文,重复次数\n" + "\n".join(f'{i+1},"{t}",{n}' for i, (t, n) in enumerate(repeated[:50])))

# ================= D12 章节相对位置分布 =================
set_sec("D12")
decile = Counter()
for b in NOTES:
    chap = [m["chapter"] for m in b["marks"]]
    # 用章节字符串里的序号/位置粗略归一：尝试从章节标题提取数字
    n = len(set(chap))
    for i, c in enumerate(chap):
        # 相对位置 1-10
        decile[min(10, (i % 10) + 1)] += 1
# 更稳妥：按每本书章节顺序定位
decile2 = Counter()
for b in NOTES:
    chs = [m["chapter"] for m in b["marks"]]
    uniq = list(dict.fromkeys(chs))  # 保持顺序
    if len(uniq) < 2: continue
    for c in chs:
        pos = uniq.index(c) / (len(uniq) - 1)
        decile2[min(10, int(pos * 10) + 1)] += 1
fig_d12 = go.Figure(go.Bar(x=[f"{i}" for i in range(1, 11)], y=[decile2.get(i, 0) for i in range(1, 11)],
                            marker_color="#D9A441"))
fig_d12.update_layout(title="D12 划线在书中的相对位置（1=开头,10=结尾）", xaxis_title="相对位置十分位", yaxis_title="划线数")
add(fig_d12, height=bar_h(10))
peak = max(decile2, key=decile2.get)
add(table_html=table(["指标", "值"], [["最热位置十分位", f"第{peak}位（{'开头' if peak<=3 else '中段' if peak<=7 else '结尾'}）"],
                            ["前3位(开头)占比", f"{sum(decile2.get(i,0) for i in range(1,4))/sum(decile2.values())*100:.0f}%"]]))

# ================= D13 划线↔想法章节错位 =================
set_sec("D13")
only_mark = 0; only_review = 0
for b in NOTES:
    mc = set(m["chapter"] for m in b["marks"])
    rc = set(r["chapter"] for r in b["reviews"])
    only_mark += len(mc - rc)
    only_review += len(rc - mc)
fig_d13 = go.Figure(go.Bar(x=["只划不评的章节", "只评不划的章节"], y=[only_mark, only_review],
                            marker_color=["#C2724B", "#7E9B8E"]))
fig_d13.update_layout(title="D13 划线↔想法 章节错位", yaxis_title="章节数")
add(fig_d13)
add(table_html=table(["类型", "章节数"], [["只划不评", only_mark], ["只评不划", only_review]]))

# ================= E14 类别 × 参与度 =================
set_sec("E14")
e_cats = top_cats
avg_marks = [round(sum(len(notes_by_id[b]["marks"]) for b in notes_by_id if cat_of(b)==c)/max(cat_books[c],1),1) for c in e_cats]
avg_revs = [round(sum(len(notes_by_id[b]["reviews"]) for b in notes_by_id if cat_of(b)==c)/max(cat_books[c],1),1) for c in e_cats]
fig_e14 = go.Figure()
fig_e14.add_bar(x=e_cats, y=avg_marks, name="平均划线/本", marker_color="#C2724B")
fig_e14.add_bar(x=e_cats, y=avg_revs, name="平均想法/本", marker_color="#D9A441")
fig_e14.update_layout(barmode="group", title="E14 类别 × 参与度（每本平均划线/想法）", yaxis_title="条数")
add(fig_e14)

# ================= E15 读完率 vs 笔记密度 =================
set_sec("E15")
xs, ys, cols = [], [], []
for b in NOTES:
    p = PROG.get(b["bookId"], {})
    prog = p.get("progress")
    if prog is None: continue
    xs.append(prog); ys.append(note_count(b))
    cols.append("已读完" if prog == 100 else "未读完")
fig_e15 = go.Figure()
for name in ["已读完", "未读完"]:
    fx = [x for x, y, c in zip(xs, ys, cols) if c == name]
    fy = [y for x, y, c in zip(xs, ys, cols) if c == name]
    fig_e15.add_trace(go.Scatter(x=fx, y=fy, mode="markers", name=name,
        marker=dict(size=7, opacity=0.5, color="#8A9A6B" if name=="已读完" else "#B5563F")))
fig_e15.update_layout(title="E15 阅读进度(%) vs 笔记密度（每本）", xaxis_title="进度%", yaxis_title="笔记数(划线+想法)")
add(fig_e15)
fin = [y for x, y, c in zip(xs, ys, cols) if c=="已读完"]
unf = [y for x, y, c in zip(xs, ys, cols) if c=="未读完"]
add(table_html=table(["指标", "值"], [["读完本书均笔记数", round(sum(fin)/len(fin),1) if fin else "—"],
                            ["未读完本书均笔记数", round(sum(unf)/len(unf),1) if unf else "—"]]))

# ================= E16 书架增长 vs 笔记增长 =================
set_sec("E16")
# 用每本最早笔记 createTime 作为"首次深度接触"时间
first_note = {}
for b in NOTES:
    cts = [it["createTime"] for it in (b["marks"]+b["reviews"]) if it.get("createTime")]
    if cts: first_note[b["bookId"]] = min(int(c) for c in cts)
months16 = months
cum_books, cum_notes = [], []
seen_b = set(); run_n = 0
for m in months16:
    for bid, ct in first_note.items():
        if datetime.datetime.fromtimestamp(ct).strftime("%Y-%m") <= m and bid not in seen_b:
            seen_b.add(bid); run_n += note_count(notes_by_id[bid])
    cum_books.append(len(seen_b)); cum_notes.append(run_n)
fig_e16 = make_subplots(specs=[[{"secondary_y": True}]])
fig_e16.add_trace(go.Scatter(x=months16, y=cum_books, name="累计有笔记书", line=dict(color="#C2724B")), secondary_y=False)
fig_e16.add_trace(go.Scatter(x=months16, y=cum_notes, name="累计笔记数", line=dict(color="#D9A441")), secondary_y=True)
fig_e16.update_layout(title="E16 累计有笔记书 vs 累计笔记数（增长曲线）")
fig_e16.update_yaxes(title_text="书数", secondary_y=False)
fig_e16.update_yaxes(title_text="笔记数", secondary_y=True)
add(fig_e16)

# ================= 金句 pull-quote 候选提取 =================
def _clean_title(t):
    t = (t or '').strip().strip('《》').strip()
    # 去掉全/半角括号内的元数据（反复清除嵌套括号）
    for _ in range(3):
        t = re.sub(r'[（(][^）)]*[）)]', '', t)
    t = re.sub(r'[（(][^）)]*$', '', t)   # 残留开头的左括号
    t = re.sub(r'[）)][^（(]*$', '', t)   # 残留结尾的右括号
    # 下载站噪点
    t = t.replace('z-library', '').replace('Z-Library', '').replace('1lib', '').replace('z-lib', '')
    t = re.sub(r'\.(sk|pdf|epub|mobi)', '', t, flags=re.I)
    t = re.sub(r'(证书|签名|正版|v\d+|下载)', '', t)
    t = re.sub(r'\s+', ' ', t).strip().strip('（）()').strip()
    return t or '未知'
def pull_quotes(n=3):
    best = {}
    for b in NOTES:
        ti = _clean_title(b.get("title", ""))
        for m in b["marks"]:
            tx = (m.get("text") or "").strip()
            if 18 <= len(tx) <= 52:
                if ti not in best or len(tx) > len(best[ti][0]):
                    best[ti] = (tx, ti)
    uniq = sorted(best.values(), key=lambda x: len(x[0]), reverse=True)
    return uniq[:n]
PQ = pull_quotes(3)
def pq_html(q):
    return f'<blockquote class="pq"><p>{html.escape(q[0])}</p><footer>——你划下的 ·《{html.escape(q[1])}》</footer></blockquote>'

# ================= 组装 HTML =================
NAV = [
    ("summary", "摘要"), ("A1", "类别参与度矩阵"), ("A2", "作者集中度"), ("A3", "参与人格分型"),
    ("A4", "私密vs公开"), ("B5", "月度时间线"), ("B6", "日内时段"), ("B7", "年×月热力"),
    ("C8", "划线关键词"), ("C9", "想法情感"), ("C10", "高频原文"), ("D12", "章节位置"),
    ("D13", "章节错位"), ("E14", "类别×参与度"), ("E15", "读完率vs笔记"), ("E16", "增长曲线"),
]
nav_html = "".join(f'<li><a href="#{i}">{t}</a></li>' for i, t in NAV)
CHAPTERS = [
 ("壹","你是怎样的读者","藏书、笔记与参与方式，拼出你作为读者的轮廓。",["A1","A2","A3","A4"]),
 ("贰","时间的形状","你何时读书、读多久——时间在你身上留下的节律。",["B5","B6","B7"]),
 ("叁","你划下的字","那些被你划线的句子与想法，是你的思想母题。",["C8","C9","C10"]),
 ("肆","书的肌理","从章节位置到划线与想法的错位，看见阅读的路径。",["D12","D13"]),
 ("伍","读完与未读完","起点与终点之间，是另一回事。",["E14","E15","E16"]),
]
hero = f'''<div class="hero">
  <div class="hero-title">你的 2023–2026 阅读年报</div>
  <div class="hero-sub">四年，你与 {n_books} 本书的相处 · 累计 {fmt_hms(total_sec)} 真实阅读</div>
  <div class="hero-stats">
    <div class="hs"><div class="hs-num">{round(total_sec/3600)}</div><div class="hs-lab">小时真实阅读</div></div>
    <div class="hs"><div class="hs-num">{read_days}</div><div class="hs-lab">有效阅读天数</div></div>
    <div class="hs"><div class="hs-num">{n_books}</div><div class="hs-lab">书架藏书</div></div>
    <div class="hs"><div class="hs-num">{total_marks+total_reviews}</div><div class="hs-lab">划线与想法</div></div>
  </div>
</div>'''
def section_block(sid, t):
    inner = f'<div class="cards">{cards}</div>' if sid=="summary" else "".join(SECTIONS.get(sid, []))
    return f'<section id="{sid}"><h2>{t}</h2>{inner}</section>'
parts = [section_block("summary","摘要")]
pq_positions = {0: PQ[0] if len(PQ)>0 else None, 1: PQ[1] if len(PQ)>1 else None, 2: PQ[2] if len(PQ)>2 else None}
for ci,(num,name,intro,sids) in enumerate(CHAPTERS):
    parts.append(f'<div class="chapter"><div class="ch-no">第{num}章</div><div class="ch-head"><div class="ch-name">{name}</div><div class="ch-intro">{intro}</div></div></div>')
    if pq_positions.get(ci): parts.append(pq_html(pq_positions[ci]))
    for sid in sids:
        parts.append(section_block(sid, dict(NAV).get(sid, sid)))
sections_html = "\n".join(parts)
full = f"""<!DOCTYPE html><html lang="zh-CN"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>微信读书 · 2023–2026 阅读年报</title>
<style>
:root{{--paper:#FBF8F3;--card:#FFFFFF;--side:#F5EFE6;--ink:#2B2724;--ink2:#6B6259;--ink3:#7A7066;--line:#E6DECF;--line2:#EFE9DC;--acc:#C2724B;--shadow:0 1px 3px rgba(43,39,36,.06),0 4px 12px rgba(43,39,36,.05);--shadow-h:0 2px 8px rgba(43,39,36,.10);--fc:"PingFang SC","Microsoft YaHei","Noto Sans SC",sans-serif;--fe:"SF Pro Display","Inter","Helvetica Neue",Arial,sans-serif}}
*{{box-sizing:border-box}}
body{{font-family:var(--fe),var(--fc);margin:0;background:var(--paper);color:var(--ink);line-height:1.6;-webkit-font-smoothing:antialiased}}
header{{height:64px;display:flex;flex-direction:column;justify-content:center;padding:0 28px;background:var(--paper);border-bottom:1px solid var(--line)}}
header h1{{margin:0;font-size:22px;font-weight:600;color:var(--ink);letter-spacing:.3px}}
.sub{{font-size:13px;color:var(--ink3);margin-top:2px}}
.wrap{{display:flex;align-items:flex-start}}
nav{{width:210px;background:var(--side);border-right:1px solid var(--line);padding:16px 12px;position:sticky;top:0;height:100vh;overflow:auto;flex:0 0 auto}}
nav ul{{list-style:none;padding:0;margin:0}}
nav li{{margin:3px 0}}
nav a{{display:block;padding:8px 12px;border-radius:8px;text-decoration:none;color:var(--ink2);font-size:13px;transition:.15s}}
nav a:hover{{background:#F0E9DC;color:var(--ink)}}
nav a.active,nav a:focus{{background:var(--card);color:var(--ink);font-weight:600;box-shadow:inset 3px 0 0 var(--acc);outline:none}}
main{{flex:1;padding:24px 32px;max-width:1120px}}
.cards{{display:flex;flex-wrap:wrap;gap:14px;margin:8px 0 26px}}
.card{{flex:1;min-width:140px;background:var(--card);border:1px solid var(--line);border-radius:12px;padding:16px 18px;box-shadow:var(--shadow);position:relative;overflow:hidden}}
.card::before{{content:"";position:absolute;top:0;left:0;right:0;height:3px;background:var(--acc)}}
.c-val{{font-size:28px;font-weight:700;color:var(--ink);line-height:1.2}}
.c-lab{{font-size:13px;color:var(--ink3);margin-top:4px;font-weight:500}}
section{{background:var(--card);border:1px solid var(--line);border-radius:14px;padding:20px 22px;margin-bottom:20px;box-shadow:var(--shadow);transition:.15s}}
section:hover{{box-shadow:var(--shadow-h);border-color:#D9CFBC}}
section h2{{font-size:18px;font-weight:600;margin:0 0 14px;color:var(--ink);padding-left:12px;border-left:3px solid var(--acc)}}
.chart{{margin:10px 0}}
.tbl{{margin:12px 0;max-height:none;border:1px solid var(--line);border-radius:10px}}
table.data{{border-collapse:collapse;width:100%;font-size:12.5px}}
table.data th{{background:var(--side);text-align:left;padding:8px 10px;border-bottom:1px solid var(--line);font-weight:500;color:var(--ink2);position:sticky;top:0}}
table.data td{{padding:6px 10px;border-bottom:1px solid var(--line2)}}
table.data tbody tr:hover{{background:#F7F2EA}}
.hero{{background:linear-gradient(180deg,#FBF8F3,#F6ECE0);border:1px solid var(--line);border-radius:14px;padding:56px 24px;margin-bottom:24px;box-shadow:var(--shadow)}}
.hero-title{{font-size:44px;font-weight:700;color:var(--ink);letter-spacing:.5px}}
.hero-sub{{font-size:15px;color:var(--ink2);margin-top:8px}}
.hero-stats{{display:flex;gap:40px;margin-top:32px;flex-wrap:wrap}}
.hs{{flex:1;min-width:120px;padding-left:18px;border-left:1px solid var(--line2)}}
.hs-num{{font-size:48px;font-weight:700;color:var(--acc);line-height:1.1}}
.hs-lab{{font-size:13px;color:var(--ink3);margin-top:6px}}
.chapter{{margin:40px 0 16px;padding-top:16px;border-top:1px solid var(--line)}}
.ch-no{{font-size:13px;font-weight:600;color:var(--acc);letter-spacing:2px}}
.ch-head{{border-left:3px solid var(--acc);padding-left:14px;margin-top:6px}}
.ch-name{{font-size:28px;font-weight:700;color:var(--ink)}}
.ch-intro{{font-size:14px;color:var(--ink2);margin-top:4px}}
.pq{{background:var(--card);border-left:4px solid var(--acc);border-radius:14px;padding:22px;margin:18px 0;box-shadow:var(--shadow)}}
.pq p{{font-size:22px;font-weight:500;color:var(--ink);line-height:1.6;margin:0}}
.pq footer{{font-size:13px;color:var(--ink3);text-align:right;margin-top:12px;font-style:normal}}
.wordcloud{{text-align:center;padding:20px 0}}
.wordcloud img{{max-width:100%;height:auto}}
.foot{{text-align:center;color:var(--ink3);font-size:12px;padding:24px}}
</style></head>
<body>
<header><h1>微信读书 · 阅读年报</h1>
<div class="sub">数据跨度 2023-02 → 2026-08 ｜ 真实阅读时长来自 /readdata/detail ｜ 生成于 {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}</div></header>
<div class="wrap"><nav><ul>{nav_html}</ul></nav>
<main>
{hero}
{sections_html}
<div class="foot">本地离线分析 · 不涉及账号写入 · 阅读时长为真实秒数</div>
</main></div></body></html>"""
with open(os.path.join(OUT_DIR, "reading_dashboard.html"), "w", encoding="utf-8") as f:
    f.write(full)
print("DASHBOARD_WRITTEN", os.path.join(OUT_DIR, "reading_dashboard.html"))
print("SECTIONS", len(SECTIONS))
