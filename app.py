# -*- coding: utf-8 -*-
import datetime
from datetime import date, timedelta
import streamlit as st

# 天干地支列表
tiangan = ["甲","乙","丙","丁","戊","己","庚","辛","壬","癸"]
dizhi = ["子","丑","寅","卯","辰","巳","午","未","申","酉","戌","亥"]
GZS_LIST = [tiangan[i%10] + dizhi[i%12] for i in range(60)]

gan_he = {"甲":"己","己":"甲","乙":"庚","庚":"乙","丙":"辛","辛":"丙","丁":"壬","壬":"丁","戊":"癸","癸":"戊"}
zhi_he = {"子":"丑","丑":"子","寅":"亥","亥":"寅","卯":"戌","戌":"卯","辰":"酉","酉":"辰","巳":"申","申":"巳","午":"未","未":"午"}
gan_chong = {"甲":"庚","庚":"甲","乙":"辛","辛":"乙","丙":"壬","壬":"丙","丁":"癸","癸":"丁"}
zhi_chong = {dz: dizhi[(i+6)%12] for i, dz in enumerate(dizhi)}

def unique_list(seq):
    seen = set()
    res = []
    for x in seq:
        if x not in seen:
            seen.add(x)
            res.append(x)
    return res

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
        res["吉"].append(tg_he + dizhi[(dizhi.index(dz_he)+1)%12])
    if tg_ch and dz_ch:
        res["凶"].append(tg_ch + dz_ch)
        res["凶"].append(tg_ch + dizhi[(dizhi.index(dz_ch)-1)%12])
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
    return unique_list(all_ji), unique_list(all_xiong)

# 日柱锚点法，1984-01-01甲午日
ANCHOR_DATE = date(1984,1,1)
ANCHOR_GZ = "甲午"
ANCHOR_INDEX = GZS_LIST.index(ANCHOR_GZ)

def day_ganzhi_by_anchor(y,m,d,h=None):
    if h is not None and h >= 23:
        target = date(y,m,d) + timedelta(days=1)
    else:
        target = date(y,m,d)
    delta = (target - ANCHOR_DATE).days
    idx = (ANCHOR_INDEX + delta) % 60
    return GZS_LIST[idx]

def get_li_chun_datetime(year):
    # 简化立春时间为2月4日0时0分
    return datetime.datetime(year, 2, 4, 0, 0)

def year_ganzhi(year, month, day, hour=0, minute=0):
    dt = datetime.datetime(year, month, day, hour, minute)
    lichun = get_li_chun_datetime(year)
    adj_year = year if dt >= lichun else year-1
    return GZS_LIST[(adj_year - 1984) % 60], adj_year

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

def month_stem_by_fihu_dun(year_gan, month_branch):
    if year_gan in ("甲","己"): start = "丙"
    elif year_gan in ("乙","庚"): start = "戊"
    elif year_gan in ("丙","辛"): start = "庚"
    elif year_gan in ("丁","壬"): start = "壬"
    elif year_gan in ("戊","癸"): start = "甲"
    else: start = "丙"
    start_idx = tiangan.index(start)
    offset = (dizhi.index(month_branch) - dizhi.index("寅")) % 12
    stem_idx = (start_idx + offset) % 10
    return tiangan[stem_idx] + month_branch

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

# 简易阴历转阳历推算，基于农历数据2020-2040（注意这只是示例，实际推荐用专业库）
# 用于演示，未覆盖所有年份和闰月。这里只支持非闰月，且月份天数参考农历常规。
def lunar_to_solar_simple(l_year, l_month, l_day, is_leap_month=False):
    # 2020年农历正月初一对应公历2020-01-25
    # 以2020年为基准，往后推算简化
    base_lunar_new_year = date(2020,1,25)
    base_year = 2020
    if is_leap_month:
        return None  # 简化版本不支持闰月
    # 月份天数示例（不准确，仅做示例）
    lunar_month_days = [30,29,30,29,30,29,30,29,30,29,30,29]
    # 计算偏移天数
    year_diff = l_year - base_year
    days_offset = year_diff * 354 + (year_diff//4)  # 简化润年影响
    for i in range(l_month-1):
        days_offset += lunar_month_days[i%12]
    days_offset += (l_day - 1)
    solar_date = base_lunar_new_year + timedelta(days=days_offset)
    return solar_date.year, solar_date.month, solar_date.day

def year_ganzhi_map(start=1900, end=2100):
    base_year = 1984
    return {y: GZS_LIST[(y-base_year)%60] for y in range(start, end+1)}

def show_result_beauty(ji_list, xiong_list, birth_year):
    now_year = datetime.datetime.now().year
    year_map = year_ganzhi_map(max(birth_year, now_year), 2100)
    cur = birth_year if birth_year >= now_year else now_year
    color_good = "#b22222"
    color_bad = "#555555"
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
                    s = f"**{s} （当前或出生年）**"
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
                    s = f"**{s} （当前或出生年）**"
                parts.append(s)
            st.markdown(f"<div style='color:{color_bad};padding:8px;border-left:5px solid {color_bad};background:#f7f7f7;border-radius:6px;margin-bottom:6px'>{gz}: {'，'.join(parts)}</div>", unsafe_allow_html=True)

st.set_page_config(page_title="八字排盘", layout="centered")
st.title("八字排盘")

input_mode = st.radio("", ["阳历生日", "阴历生日", "直接输入四柱八字"])

if input_mode == "阳历生日":
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
            if hour_val is None:
                hour_p = "不知道"
            else:
                hour_p = time_ganzhi_by_rule(day_p, hour_val, min_val or 0)
            bazi = {"year": year_p, "month": month_p, "day": day_p, "hour": hour_p}

            st.markdown("## 推算结果（四柱）")
            st.markdown(f"<div style='font-size:20px;line-height:1.6;padding:10px 20px;border-radius:10px;border:2px solid #b22222;background:#fff0f0;text-align:center;'>"
                        f"年柱：<b>{bazi['year']}</b>  &nbsp;&nbsp; 月柱：<b>{bazi['month']}</b>  &nbsp;&nbsp; 日柱：<b>{bazi['day']}</b>  &nbsp;&nbsp; 时柱：<b>{bazi['hour']}</b>"
                        f"</div>", unsafe_allow_html=True)
            ji, xiong = analyze_bazi(bazi["year"], bazi["month"], bazi["day"], bazi["hour"])
            st.markdown("---")
            show_result_beauty(ji, xiong, adj_year)
        except Exception as e:
            st.error(f"计算出错：{e}")

elif input_mode == "阴历生日":
    col1, col2 = st.columns([2,1])
    with col1:
        ly = st.number_input("农历年", min_value=1900, max_value=2100, value=1990, step=1)
        lm = st.number_input("农历月", min_value=1, max_value=12, value=1, step=1)
        ld = st.number_input("农历日", min_value=1, max_value=30, value=1, step=1)
        isleap = st.checkbox("闰月", value=False)
    with col2:
        unknown_time = st.checkbox("时辰未知（跳过时柱）", value=False)
        if unknown_time:
            bhour = -1
            bmin = 0
        else:
            bhour = st.number_input("小时（0-23）", min_value=0, max_value=23, value=8, step=1)
            bmin = st.number_input("分钟（0-59）", min_value=0, max_value=59, value=0, step=1)

    if st.button("阴历转阳历并推算八字"):
        solar_date = lunar_to_solar_simple(ly, lm, ld, isleap)
        if solar_date is None:
            st.error("暂不支持闰月或超出范围的阴历转换，请重新输入。")
            st.stop()
        sy, sm, sd = solar_date
        hour_val = None if bhour == -1 else int(bhour)
        min_val = None if bhour == -1 else int(bmin)
        try:
            year_p, adj_year = year_ganzhi(sy, sm, sd, hour_val or 0, min_val or 0)
            day_p = day_ganzhi_by_anchor(sy, sm, sd, hour_val)
            mb = get_month_branch(sy, sm, sd)
            month_p = month_stem_by_fihu_dun(year_p[0], mb)
            if hour_val is None:
                hour_p = "不知道"
            else:
                hour_p = time_ganzhi_by_rule(day_p, hour_val, min_val or 0)
            bazi = {"year": year_p, "month": month_p, "day": day_p, "hour": hour_p}

            st.markdown(f"转换后的阳历日期：{sy}年{sm}月{sd}日")
            st.markdown("## 推算结果（四柱）")
            st.markdown(f"<div style='font-size:20px;line-height:1.6;padding:10px 20px;border-radius:10px;border:2px solid #b22222;background:#fff0f0;text-align:center;'>"
                        f"年柱：<b>{bazi['year']}</b>  &nbsp;&nbsp; 月柱：<b>{bazi['month']}</b>  &nbsp;&nbsp; 日柱：<b>{bazi['day']}</b>  &nbsp;&nbsp; 时柱：<b>{bazi['hour']}</b>"
                        f"</div>", unsafe_allow_html=True)
            ji, xiong = analyze_bazi(bazi["year"], bazi["month"], bazi["day"], bazi["hour"])
            st.markdown("---")
            show_result_beauty(ji, xiong, adj_year)
        except Exception as e:
            st.error(f"计算出错：{e}")

else:  # 直接输入四柱八字
    st.markdown("请直接输入四柱八字（每柱两个字符，天干+地支），不输入则自动不计入分析。")
    nianzhu = st.text_input("年柱", max_chars=2)
    yuezhu = st.text_input("月柱", max_chars=2)
    rizhu = st.text_input("日柱", max_chars=2)
    shizhu = st.text_input("时柱", max_chars=2)

    if st.button("分析吉凶"):
        try:
            ji, xiong = analyze_bazi(nianzhu.strip(), yuezhu.strip(), rizhu.strip(), shizhu.strip())
            st.markdown("## 输入八字四柱")
            st.markdown(f"年柱：{nianzhu}  月柱：{yuezhu}  日柱：{rizhu}  时柱：{shizhu}")
            byear = 1900
            show_result_beauty(ji, xiong, byear)
        except Exception as e:
            st.error(f"计算出错：{e}")

st.markdown("---")
st.markdown("程序默认以锚点日法（日柱）与五鼠遁时柱规则为主。阴历转阳历为简化演示，适用于部分年份。")
