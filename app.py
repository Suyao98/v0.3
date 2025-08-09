# -*- coding: utf-8 -*-
"""
Streamlit 八字排盘（锚点日法 + 五鼠遁时柱）
- 出生年月手动输入（数字）
- 出生时分精确到分钟，支持“时辰未知”跳过时柱
- 吉凶年份仅显示出生年份及以后
- UI美化，布局优化
"""
import datetime
from datetime import date, timedelta
import streamlit as st

# ---------- 干支基础数据 ----------
tiangan = ["甲","乙","丙","丁","戊","己","庚","辛","壬","癸"]
dizhi = ["子","丑","寅","卯","辰","巳","午","未","申","酉","戌","亥"]
GZS_LIST = [tiangan[i%10] + dizhi[i%12] for i in range(60)]

gan_he = {"甲":"己","己":"甲","乙":"庚","庚":"乙","丙":"辛","辛":"丙","丁":"壬","壬":"丁","戊":"癸","癸":"戊"}
gan_chong = {"甲":"庚","庚":"甲","乙":"辛","辛":"乙","丙":"壬","壬":"丙","丁":"癸","癸":"丁"}
zhi_he = {"子":"丑","丑":"子","寅":"亥","亥":"寅","卯":"戌","戌":"卯","辰":"酉","酉":"辰","巳":"申","申":"巳","午":"未","未":"午"}
zhi_chong = {dz: dizhi[(i+6)%12] for i, dz in enumerate(dizhi)}

def zhi_next(z): return dizhi[(dizhi.index(z)+1)%12]
def zhi_prev(z): return dizhi[(dizhi.index(z)-1)%12]

def year_ganzhi_map(start=1900, end=2100):
    base_year = 1984
    return {y: GZS_LIST[(y-base_year)%60] for y in range(start, end+1)}

# ---------- 吉凶计算 ----------
def calc_jixiong(gz):
    if not gz or len(gz) < 2:
        return {"吉": [], "凶": []}
    tg, dz = gz[0], gz[1]
    res = {"吉": [], "凶": []}
    tg_he = gan_he.get(tg, "")
    dz_he = zhi_he.get(dz, "")
    tg_ch = gan_chong.get(tg, "")
    dz_ch = zhi_chong.get(dz, "")
    if tg_he and dz_he:
        res["吉"].append(tg_he + dz_he)
        res["吉"].append(tg_he + zhi_next(dz_he))
    if tg_ch and dz_ch:
        res["凶"].append(tg_ch + dz_ch)
        res["凶"].append(tg_ch + zhi_prev(dz_ch))
    return res

def analyze_bazi(nianzhu, yuezhu, rizhu, shizhu):
    pillars = [p for p in (nianzhu, yuezhu, rizhu) if p]
    if shizhu and str(shizhu).strip() and str(shizhu).strip().lower() not in ["不要", "不要时", "不知道"]:
        pillars.append(shizhu)
    all_ji = []
    all_xiong = []
    for p in pillars:
        r = calc_jixiong(p)
        all_ji.extend(r["吉"])
        all_xiong.extend(r["凶"])
    # 去重但保序
    def unique_list(seq):
        seen = set()
        res = []
        for x in seq:
            if x not in seen:
                seen.add(x)
                res.append(x)
        return res
    return unique_list(all_ji), unique_list(all_xiong)

# ---------- 日柱（锚点法） ----------
ANCHOR_DATE = date(1984,1,1)
ANCHOR_GZ = "甲午"
ANCHOR_INDEX = GZS_LIST.index(ANCHOR_GZ)

def day_ganzhi_by_anchor(y, m, d, hour=None):
    # 23点以后归次日
    if hour is not None and hour >= 23:
        target = date(y,m,d) + timedelta(days=1)
    else:
        target = date(y,m,d)
    delta = (target - ANCHOR_DATE).days
    idx = (ANCHOR_INDEX + delta) % 60
    return GZS_LIST[idx]

# ---------- 月柱 ----------
def month_stem_by_fihu_dun(year_tg, month_branch):
    if year_tg in ("甲","己"): start = "丙"
    elif year_tg in ("乙","庚"): start = "戊"
    elif year_tg in ("丙","辛"): start = "庚"
    elif year_tg in ("丁","壬"): start = "壬"
    elif year_tg in ("戊","癸"): start = "甲"
    else: start = "丙"
    start_idx = tiangan.index(start)
    offset = (dizhi.index(month_branch) - dizhi.index("寅")) % 12
    stem_idx = (start_idx + offset) % 10
    return tiangan[stem_idx] + month_branch

APPROX_JIEQI = {
    "立春": (2,4), "惊蛰": (3,6), "清明": (4,5), "立夏": (5,6),
    "芒种": (6,6), "小暑": (7,7), "立秋": (8,7), "白露": (9,7),
    "寒露": (10,8), "立冬": (11,7), "大雪": (12,7), "小寒": (1,6)
}
def get_month_branch_approx(year, month, day):
    bd = date(year, month, day)
    keys = list(APPROX_JIEQI.keys())
    seq=[]
    for k in keys:
        m,d = APPROX_JIEQI[k]
        yr = year if not (k=="小寒" and m==1) else year+1
        seq.append((k, date(yr,m,d)))
    for i in range(len(seq)):
        s = seq[i][1]
        e = seq[i+1][1] if i+1 < len(seq) else seq[0][1].replace(year=seq[0][1].year+1)
        if s <= bd < e:
            return ["寅","卯","辰","巳","午","未","申","酉","戌","亥","子","丑"][i]
    return dizhi[(month+10)%12]

# ---------- 时柱 五鼠遁 ----------
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
    for i, (s,e,name) in enumerate(intervals):
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

# ---------- 综合计算 ----------
def calc_bazi(year, month, day, hour=None, minute=None):
    day_p = day_ganzhi_by_anchor(year, month, day, hour)
    mb = get_month_branch_approx(year, month, day)
    month_p = month_stem_by_fihu_dun(day_p[0], mb)
    if hour is None or hour < 0:
        hour_p = "不知道"
    else:
        hour_p = time_ganzhi_by_rule(day_p, hour, minute or 0)
    # 年柱用立春边界简单估算
    birth_dt = datetime.datetime(year, month, day, hour or 0, minute or 0)
    lichun = datetime.datetime(year, 2, 4, 0, 0)
    adj_year = year if birth_dt >= lichun else year - 1
    year_p = GZS_LIST[(adj_year - 1984) % 60]
    return {"year": year_p, "month": month_p, "day": day_p, "hour": hour_p}

# ---------- 吉凶年份展示（只显示出生年及以后） ----------
def show_result_beauty(ji_list, xiong_list, birth_year):
    year_map = year_ganzhi_map(birth_year, 2100)
    cur = birth_year
    color_good = "#b22222"  # 深红
    color_bad = "#555555"   # 深灰
    st.markdown("### 🎉 吉年")
    if not ji_list:
        st.info("无吉年（按当前规则）")
    else:
        for gz in ji_list:
            years = [y for y,g in year_map.items() if g == gz]
            if not years: continue
            years.sort()
            parts=[]
            for y in years:
                s = f"{gz}{y}年"
                if y == cur:
                    s = f"**{s} （出生年）**"
                parts.append(s)
            st.markdown(f"<div style='color:{color_good};padding:8px;border-left:5px solid {color_good};background:#ffe6e6;border-radius:6px;margin-bottom:6px'>{gz}: {'，'.join(parts)}</div>", unsafe_allow_html=True)
    st.markdown("### ☠️ 凶年")
    if not xiong_list:
        st.info("无凶年（按当前规则）")
    else:
        for gz in xiong_list:
            years = [y for y,g in year_map.items() if g == gz]
            if not years: continue
            years.sort()
            parts=[]
            for y in years:
                s = f"{gz}{y}年"
                if y == cur:
                    s = f"**{s} （出生年）**"
                parts.append(s)
            st.markdown(f"<div style='color:{color_bad};padding:8px;border-left:5px solid {color_bad};background:#f7f7f7;border-radius:6px;margin-bottom:6px'>{gz}: {'，'.join(parts)}</div>", unsafe_allow_html=True)

# ---------- UI ----------
st.set_page_config(page_title="八字排盘（锚点日法+五鼠遁）", layout="centered")
st.title("🧧 八字排盘与吉凶年份查询")

st.markdown(
    """
    请填写阳历出生年月日及时分，时辰未知可勾选跳过时柱。
    日柱采用锚点法计算（月柱用五虎遁推算），时柱用五鼠遁规则（支持分钟精确）。
    """
)

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
        result = calc_bazi(byear, bmonth, bday, hour=hour_val, minute=min_val)
        st.markdown("## 📜 推算结果（四柱）")
        st.markdown(f"<div style='font-size:20px;line-height:1.6;padding:10px 20px;border-radius:10px;border:2px solid #b22222;background:#fff0f0;text-align:center;'>"
                    f"年柱：<b>{result['year']}</b>  &nbsp;&nbsp; 月柱：<b>{result['month']}</b>  &nbsp;&nbsp; 日柱：<b>{result['day']}</b>  &nbsp;&nbsp; 时柱：<b>{result['hour']}</b>"
                    f"</div>", unsafe_allow_html=True)
        ji, xiong = analyze_bazi(result["year"], result["month"], result["day"], result["hour"])
        st.markdown("---")
        show_result_beauty(ji, xiong, byear)
    except Exception as e:
        st.error(f"计算出错：{e}")
