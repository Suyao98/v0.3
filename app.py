# -*- coding: utf-8 -*-
import datetime
from datetime import date, timedelta
import streamlit as st

# ========== 基础：干支、甲子表 ==========
tiangan = ["甲","乙","丙","丁","戊","己","庚","辛","壬","癸"]
dizhi = ["子","丑","寅","卯","辰","巳","午","未","申","酉","戌","亥"]
GZS_LIST = [tiangan[i%10] + dizhi[i%12] for i in range(60)]

def ganzhi_list():
    return GZS_LIST

# 五行（按天干）
WUXING_OF_GAN = {
    "甲":"木","乙":"木",
    "丙":"火","丁":"火",
    "戊":"土","己":"土",
    "庚":"金","辛":"金",
    "壬":"水","癸":"水"
}
# 五行颜色
WUXING_COLOR = {
    "木": "#2e7d32",   # 绿
    "火": "#d32f2f",   # 红
    "土": "#8d6e63",   # 棕
    "金": "#6e6e6e",   # 灰
    "水": "#1565c0"    # 蓝
}

# ========== 合/冲 规则（保持你之前的规则） ==========
gan_he = {"甲":"己","己":"甲","乙":"庚","庚":"乙","丙":"辛","辛":"丙","丁":"壬","壳":"壬","壬":"丁","戊":"癸","癸":"戊"}
# 去掉戊己的冲对（按你要求）
gan_chong = {"甲":"庚","庚":"甲","乙":"辛","辛":"乙","丙":"壬","壬":"丙","丁":"癸","癸":"丁"}
zhi_he = {"子":"丑","丑":"子","寅":"亥","亥":"寅","卯":"戌","戌":"卯","辰":"酉","酉":"辰","巳":"申","申":"巳","午":"未","未":"午"}
zhi_chong = {dz: dizhi[(i+6)%12] for i, dz in enumerate(dizhi)}

def zhi_next(z): return dizhi[(dizhi.index(z)+1)%12]
def zhi_prev(z): return dizhi[(dizhi.index(z)-1)%12]

def unique_list(seq):
    seen=set(); out=[]
    for s in seq:
        if s not in seen:
            seen.add(s); out.append(s)
    return out

def calc_jixiong(gz):
    """按既定规则计算某柱的 吉/凶 干支（双合进一/双冲退一）"""
    if not gz or len(gz) < 2:
        return {"吉":[], "凶":[]}
    tg, dz = gz[0], gz[1]
    res = {"吉":[], "凶":[]}
    tg_he = gan_he.get(tg, "")
    dz_he = zhi_he.get(dz, "")
    tg_ch = gan_chong.get(tg, "")
    dz_ch = zhi_chong.get(dz, "")
    if tg_he and dz_he:
        shuang_he = tg_he + dz_he
        jin_yi = tg_he + zhi_next(dz_he)
        res["吉"].extend([shuang_he, jin_yi])
    if tg_ch and dz_ch:
        shuang_ch = tg_ch + dz_ch
        tui_yi = tg_ch + zhi_prev(dz_ch)
        res["凶"].extend([shuang_ch, tui_yi])
    return res

def analyze_bazi(year_zhu, month_zhu, day_zhu, time_zhu):
    pillars = [p for p in (year_zhu, month_zhu, day_zhu) if p]
    if time_zhu and str(time_zhu).strip() and str(time_zhu).strip().lower() not in ["不要","不要时","不知道"]:
        pillars.append(time_zhu)
    all_ji=[]; all_xiong=[]
    for p in pillars:
        r = calc_jixiong(p)
        all_ji.extend(r["吉"]); all_xiong.extend(r["凶"])
    return unique_list(all_ji), unique_list(all_xiong)

# ========== 八字推算：锚点日法（1984-01-01 甲午） & 月柱/时柱规则 ==========

ANCHOR_DATE = date(1984,1,1)
ANCHOR_GZ = "甲午"
ANCHOR_INDEX = GZS_LIST.index(ANCHOR_GZ)

def day_ganzhi_by_anchor(y,m,d,h=None):
    # 23:00 及以后归入次日
    if h is not None and h >= 23:
        target = date(y,m,d) + timedelta(days=1)
    else:
        target = date(y,m,d)
    delta = (target - ANCHOR_DATE).days
    idx = (ANCHOR_INDEX + delta) % 60
    return GZS_LIST[idx]

# 立春简化边界（2月4日 00:00）
def get_li_chun_datetime(year):
    return datetime.datetime(year,2,4,0,0)

def year_ganzhi(year, month, day, hour=0, minute=0):
    dt = datetime.datetime(year, month, day, hour, minute)
    lichun = get_li_chun_datetime(year)
    adj_year = year if dt >= lichun else year-1
    return GZS_LIST[(adj_year - 1984) % 60], adj_year

# 近似节气划分月支（寅月起）
JIEQI = [
    (2,4,"寅"), (3,6,"卯"), (4,5,"辰"), (5,6,"巳"), (6,6,"午"),
    (7,7,"未"), (8,7,"申"), (9,7,"酉"), (10,8,"戌"), (11,7,"亥"),
    (12,7,"子"), (1,6,"丑"),
]
def get_month_branch(year, month, day):
    bd = date(year, month, day)
    for i,(m,d,branch) in enumerate(JIEQI):
        dt = date(year if m != 1 else year+1, m, d)
        dt_next = date(year if JIEQI[(i+1)%12][0] != 1 else year+1, JIEQI[(i+1)%12][0], JIEQI[(i+1)%12][1])
        if dt <= bd < dt_next:
            return branch
    return "寅"

def month_stem_by_fihu_dun(year_tg, month_branch):
    if year_tg in ("甲","己"): first = "丙"
    elif year_tg in ("乙","庚"): first = "戊"
    elif year_tg in ("丙","辛"): first = "庚"
    elif year_tg in ("丁","壬"): first = "壬"
    elif year_tg in ("戊","癸"): first = "甲"
    else: first = "丙"
    start_idx = tiangan.index(first)
    offset = (dizhi.index(month_branch) - dizhi.index("寅")) % 12
    tg_idx = (start_idx + offset) % 10
    return tiangan[tg_idx] + month_branch

# 时辰（分钟精确）与五鼠遁
def get_hour_branch_by_minute(hour, minute):
    if hour is None:
        return None
    tot = hour*60 + (minute or 0)
    if tot >= 23*60 or tot < 1*60:
        return "子", 0
    intervals = [
        (1*60, 3*60, "丑"),
        (3*60, 5*60, "寅"),
        (5*60, 7*60, "卯"),
        (7*60, 9*60, "辰"),
        (9*60, 11*60, "巳"),
        (11*60, 13*60, "午"),
        (13*60, 15*60, "未"),
        (15*60, 17*60, "申"),
        (17*60, 19*60, "酉"),
        (19*60, 21*60, "戌"),
        (21*60, 23*60, "亥"),
    ]
    for i,(s,e,name) in enumerate(intervals):
        if s <= tot < e:
            return name, i+1
    return "子", 0

def time_ganzhi_by_rule(day_gz, hour, minute):
    if hour is None or hour < 0:
        return "不知道"
    branch, idx = get_hour_branch_by_minute(hour, minute)
    day_gan = day_gz[0]
    if day_gan in ("甲","己"): start = tiangan.index("甲")
    elif day_gan in ("乙","庚"): start = tiangan.index("丙")
    elif day_gan in ("丙","辛"): start = tiangan.index("戊")
    elif day_gan in ("丁","壬"): start = tiangan.index("庚")
    elif day_gan in ("戊","癸"): start = tiangan.index("壬")
    else: start = 0
    tg_idx = (start + idx) % 10
    return tiangan[tg_idx] + branch

# ========== 年份映射 ==========
def year_ganzhi_map(start=1900, end=2100):
    base = 1984
    return {y: GZS_LIST[(y-base) % 60] for y in range(start, end+1)}

# ========== UI 帮助函数 ==========
def element_of_gan(gan_ch):
    return WUXING_OF_GAN.get(gan_ch, "土")

def color_of_gan(gan_ch):
    el = element_of_gan(gan_ch)
    return WUXING_COLOR.get(el, "#000000")

# 美化四柱显示（按天干五行着色，无底色）
def render_four_pillars(year_p, month_p, day_p, hour_p):
    # 每个柱按天干颜色
    pillars = [("年", year_p), ("月", month_p), ("日", day_p), ("时", hour_p)]
    cols = st.columns(4)
    for i, (label, gz) in enumerate(pillars):
        if not gz:
            txt = f"{label}\n—"
            cols[i].markdown(txt)
            continue
        tg = gz[0]
        color = color_of_gan(tg)
        cols[i].markdown(f"<div style='text-align:center'><div style='font-size:14px;color:{color};font-weight:700'>{label}</div><div style='font-size:20px;color:{color}'>{gz}</div></div>", unsafe_allow_html=True)

# 新的吉凶输出：出生年..current_year（不标★） + (current_year+1..2100) 标★
def show_jixiong(ji_list, xiong_list, birth_year):
    current_year = datetime.datetime.now().year
    start = birth_year
    end = 2100
    ymap = year_ganzhi_map(start, end)

    # 排序依据甲子序
    order_key = lambda x: GZS_LIST.index(x) if x in GZS_LIST else 999

    st.subheader("🎉 吉年")
    if not ji_list:
        st.info("无吉年（按当前规则）")
    else:
        for gz in sorted(ji_list, key=order_key):
            years = [y for y,g in ymap.items() if g == gz]
            if not years: continue
            years.sort()
            # split into past (<= current_year) and future (> current_year)
            past = [y for y in years if y <= current_year]
            future = [y for y in years if y > current_year]
            parts = []
            for y in past:
                parts.append(f"{y}年")
            for y in future:
                parts.append(f"<b>{y}年★</b>")
            # color green
            st.markdown(f"<div style='padding:8px;border-left:4px solid #2e7d32;background:#f1fbf1;border-radius:6px;margin-bottom:6px;color:#145214'><b>{gz}</b>: {'，'.join(parts)}</div>", unsafe_allow_html=True)

    st.subheader("☠️ 凶年")
    if not xiong_list:
        st.info("无凶年（按当前规则）")
    else:
        for gz in sorted(xiong_list, key=order_key):
            years = [y for y,g in ymap.items() if g == gz]
            if not years: continue
            years.sort()
            past = [y for y in years if y <= current_year]
            future = [y for y in years if y > current_year]
            parts = []
            for y in past:
                parts.append(f"{y}年")
            for y in future:
                parts.append(f"<b>{y}年★</b>")
            # color dark red / burgundy
            st.markdown(f"<div style='padding:8px;border-left:4px solid #8b0000;background:#fff6f6;border-radius:6px;margin-bottom:6px;color:#5b0000'><b>{gz}</b>: {'，'.join(parts)}</div>", unsafe_allow_html=True)

# ========== Streamlit 页面 ==========
st.set_page_config(page_title="八字排盘", layout="centered")
st.title("八字排盘")

mode = st.radio("", ["阳历生日", "直接输入四柱八字"])

if mode == "阳历生日":
    col1, col2 = st.columns([2,1])
    with col1:
        byear = st.number_input("出生年", min_value=1900, max_value=2100, value=1990, step=1)
        bmonth = st.number_input("出生月（数字）", min_value=1, max_value=12, value=5, step=1)
        bday = st.number_input("出生日", min_value=1, max_value=31, value=18, step=1)
    with col2:
        unknown_time = st.checkbox("时辰未知（跳过时柱）", value=False)
        if unknown_time:
            bhour = -1
            bmin = 0
        else:
            bhour = st.number_input("小时（0-23）", min_value=0, max_value=23, value=8, step=1)
            bmin = st.number_input("分钟（0-59）", min_value=0, max_value=59, value=0, step=1)

    if st.button("推算八字并查询吉凶"):
        hour_val = None if bhour == -1 else int(bhour)
        min_val = None if bhour == -1 else int(bmin)
        try:
            year_p, adj_year = year_ganzhi(byear, bmonth, bday, hour_val or 0, min_val or 0)
            day_p = day_ganzhi_by_anchor(byear, bmonth, bday, hour_val)
            mb = get_month_branch(byear, bmonth, bday)
            month_p = month_stem_by_fihu_dun(year_p[0], mb)
            hour_p = "不知道" if hour_val is None else time_ganzhi_by_rule(day_p, hour_val, min_val or 0)

            # 四柱显示（按五行着色，无底色）
            st.markdown("## 推算结果（四柱）")
            render_four_pillars(year_p, month_p, day_p, hour_p)

            # 吉凶计算并显示
            ji, xiong = analyze_bazi(year_p, month_p, day_p, hour_p)
            st.markdown("---")
            show_jixiong(ji, xiong, byear)
        except Exception as e:
            st.error(f"计算出错：{e}")

else:
    st.markdown("请直接输入四柱八字（例如：庚午、辛巳），时柱可填“不知道”以跳过。")
    nianzhu = st.text_input("年柱", max_chars=2)
    yuezhu = st.text_input("月柱", max_chars=2)
    rizhu = st.text_input("日柱", max_chars=2)
    shizhu = st.text_input("时柱", max_chars=2)
    start_year = st.number_input("用于列出吉凶年份的起始年（例如出生年）", min_value=1600, max_value=2100, value=1990, step=1)

    if st.button("分析吉凶"):
        try:
            ji, xiong = analyze_bazi(nianzhu.strip(), yuezhu.strip(), rizhu.strip(), shizhu.strip())
            st.markdown("## 你输入的四柱（上色显示天干五行）")
            # 渲染四柱（使用输入的值）
            render_four_pillars(nianzhu.strip() or "  ", yuezhu.strip() or "  ", rizhu.strip() or "  ", shizhu.strip() or "  ")
            st.markdown("---")
            show_jixiong(ji, xiong, int(start_year))
        except Exception as e:
            st.error(f"计算出错：{e}")
