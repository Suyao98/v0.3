import streamlit as st
import datetime

st.set_page_config(page_title="吉凶推算", layout="centered")

# --- 基础数据 ---
tiangan = ["甲", "乙", "丙", "丁", "戊", "己", "庚", "辛", "壬", "癸"]
dizhi = ["子", "丑", "寅", "卯", "辰", "巳", "午", "未", "申", "酉", "戌", "亥"]

wuxing_map = {
    "甲": "木", "乙": "木",
    "丙": "火", "丁": "火",
    "戊": "土", "己": "土",
    "庚": "金", "辛": "金",
    "壬": "水", "癸": "水",
    "子": "水", "丑": "土", "寅": "木", "卯": "木", "辰": "土", "巳": "火",
    "午": "火", "未": "土", "申": "金", "酉": "金", "戌": "土", "亥": "水",
}

# 六十甲子列表（60个干支）
def ganzhi_list():
    result = []
    for i in range(60):
        tg = tiangan[i % 10]
        dz = dizhi[i % 12]
        result.append(tg + dz)
    return result

ganzhi60 = ganzhi_list()

# 根据阳历年月日计算日柱(简化锚点法，1984-01-01甲午日为基点)
def calc_rizhu(year, month, day):
    # 计算距1984-01-01天数差
    base_date = datetime.date(1984, 1, 1)
    target_date = datetime.date(year, month, day)
    delta_days = (target_date - base_date).days
    # 甲午日为锚点，甲午在天干地支中的索引：
    base_tg_index = tiangan.index("甲")
    base_dz_index = dizhi.index("午")
    tg_index = (base_tg_index + delta_days) % 10
    dz_index = (base_dz_index + delta_days) % 12
    return tiangan[tg_index] + dizhi[dz_index]

# 计算年柱（立春前属上一年）
# 这里简化用2月4日作为立春日
def calc_nianzhu(year, month, day):
    lichun_date = datetime.date(year, 2, 4)
    if datetime.date(year, month, day) < lichun_date:
        year -= 1
    # 1984为甲子年，计算偏移
    offset = (year - 1984) % 60
    return ganzhi60[offset]

# 月柱地支根据节气确定（月支）
jieqi_dates = [
    (2, 4),   # 立春 寅月开始
    (3, 6),   # 惊蛰 卯月
    (4, 5),   # 清明 辰月
    (5, 6),   # 立夏 巳月
    (6, 6),   # 芒种 午月
    (7, 7),   # 小暑 未月
    (8, 8),   # 立秋 申月
    (9, 8),   # 白露 酉月
    (10,8),   # 寒露 戌月
    (11,7),   # 立冬 亥月
    (12,7),   # 大雪 子月
    (1, 6)    # 小寒 丑月 (跨年)
]

month_dizhi_seq = ["寅", "卯", "辰", "巳", "午", "未", "申", "酉", "戌", "亥", "子", "丑"]

# 计算月支
def calc_yuezhi(year, month, day):
    # 根据简化节气判断
    for i, (m, d) in enumerate(jieqi_dates):
        # 用今年日期作比较
        check_date = datetime.date(year if m >= 2 else year+1, m, d)
        today = datetime.date(year, month, day)
        if today < check_date:
            return month_dizhi_seq[i - 1 if i > 0 else 11]
    return month_dizhi_seq[-1]

# 月干计算（五虎遁）
# 甲己年 -> 正月丙月起，乙庚年->戊，丙辛年->庚，丁壬年->壬，戊癸年->甲
def calc_yuegan(nian_tg, yuezhi):
    idx = month_dizhi_seq.index(yuezhi)
    if nian_tg in ["甲", "己"]:
        start = "丙"
    elif nian_tg in ["乙", "庚"]:
        start = "戊"
    elif nian_tg in ["丙", "辛"]:
        start = "庚"
    elif nian_tg in ["丁", "壬"]:
        start = "壬"
    else:
        start = "甲"
    start_index = tiangan.index(start)
    tg_index = (start_index + idx) % 10
    return tiangan[tg_index]

# 五鼠遁时干推算
def calc_shigan(ri_tg, shizhi):
    shizhi_order = ["子","丑","寅","卯","辰","巳","午","未","申","酉","戌","亥"]
    # 子时天干对应五组
    rule_map = {
        "甲": ["甲","乙","丙","丁","戊","己","庚","辛","壬","癸","甲","乙"],
        "己": ["甲","乙","丙","丁","戊","己","庚","辛","壬","癸","甲","乙"],
        "乙": ["丙","丁","戊","己","庚","辛","壬","癸","甲","乙","丙","丁"],
        "庚": ["丙","丁","戊","己","庚","辛","壬","癸","甲","乙","丙","丁"],
        "丙": ["戊","己","庚","辛","壬","癸","甲","乙","丙","丁","戊","己"],
        "辛": ["戊","己","庚","辛","壬","癸","甲","乙","丙","丁","戊","己"],
        "丁": ["庚","辛","壬","癸","甲","乙","丙","丁","戊","己","庚","辛"],
        "壬": ["庚","辛","壬","癸","甲","乙","丙","丁","戊","己","庚","辛"],
        "戊": ["壬","癸","甲","乙","丙","丁","戊","己","庚","辛","壬","癸"],
        "癸": ["壬","癸","甲","乙","丙","丁","戊","己","庚","辛","壬","癸"]
    }
    if ri_tg not in rule_map or shizhi not in shizhi_order:
        return None
    return rule_map[ri_tg][shizhi_order.index(shizhi)]

def analyze_bazi(year, month, day, hour, minute):
    nianzhu = calc_nianzhu(year, month, day)
    nian_tg = nianzhu[0]

    yuezhi = calc_yuezhi(year, month, day)
    yuegan = calc_yuegan(nian_tg, yuezhi)
    yuezhu = yuegan + yuezhi

    rizhu = calc_rizhu(year, month, day)

    # 计算时支
    if hour is None or minute is None:
        shizhi = None
        shigan = None
    else:
        # 根据时辰地支规律划分
        shizhi_list = ["子","丑","寅","卯","辰","巳","午","未","申","酉","戌","亥"]
        # 小时转24小时制，如果是23:xx属于子时
        hm = hour + (minute/60)
        if hm >= 23 or hm < 1:
            shizhi = "子"
        else:
            for i in range(1,12):
                start = i*2 -1
                end = start + 2
                if hm >= start and hm < end:
                    shizhi = shizhi_list[i]
                    break
            else:
                shizhi = None
        if shizhi and rizhu:
            shigan = calc_shigan(rizhu[0], shizhi)
        else:
            shigan = None

    if shigan and shizhi:
        shizhu = shigan + shizhi
    else:
        shizhu = "未知"

    return nianzhu, yuezhu, rizhu, shizhu

# 天干合、冲，地支合、冲，吉凶规则
gan_he = {
    "甲": "己", "己": "甲",
    "乙": "庚", "庚": "乙",
    "丙": "辛", "辛": "丙",
    "丁": "壬", "壬": "丁",
    "戊": "癸", "癸": "戊"
}

gan_chong = {
    "甲": "庚", "庚": "甲",
    "乙": "辛", "辛": "乙",
    "丙": "壬", "壬": "丙",
    "丁": "癸", "癸": "丁"
}

zhi_he = {
    "子": "丑", "丑": "子",
    "寅": "亥", "亥": "寅",
    "卯": "戌", "戌": "卯",
    "辰": "酉", "酉": "辰",
    "巳": "申", "申": "巳",
    "午": "未", "未": "午"
}

dizhi = ["子", "丑", "寅", "卯", "辰", "巳", "午", "未", "申", "酉", "戌", "亥"]
zhi_chong = {dz: dizhi[(i + 6) % 12] for i, dz in enumerate(dizhi)}

def zhi_next(zhi):
    return dizhi[(dizhi.index(zhi) + 1) % 12]

def zhi_prev(zhi):
    return dizhi[(dizhi.index(zhi) - 1) % 12]

def find_jixiong(gz):
    tg = gz[0]
    dz = gz[1]
    results = {"吉": [], "凶": []}

    tg_he = gan_he.get(tg, "")
    dz_he = zhi_he.get(dz, "")
    tg_ch = gan_chong.get(tg, "")
    dz_ch = zhi_chong.get(dz, "")

    if tg_he and dz_he:
        shuang_he = tg_he + dz_he
        jin_yi = tg_he + zhi_next(dz_he)
        results["吉"].extend([shuang_he, jin_yi])

    if tg_ch and dz_ch:
        shuang_ch = tg_ch + dz_ch
        tui_yi = tg_ch + zhi_prev(dz_ch)
        results["凶"].extend([shuang_ch, tui_yi])

    return results

def year_ganzhi_map(start=1900, end=2100):
    gzs = ganzhi60
    base_year = 1984  # 甲子年
    year_map = {}
    for year in range(start, end + 1):
        index = (year - base_year) % 60
        year_map[year] = gzs[index]
    return year_map

def main():
    st.title("吉凶推算")

    mode = st.radio("选择输入方式", ["阳历生日", "四柱八字"])

    if mode == "阳历生日":
        year = st.number_input("出生年份", min_value=1900, max_value=2100, value=1990)
        month = st.text_input("出生月份（数字，例如5）", "1")
        day = st.number_input("出生日", min_value=1, max_value=31, value=1)
        hour = st.number_input("出生小时（0-23，未知可留空）", min_value=0, max_value=23, value=0)
        minute = st.number_input("出生分钟（0-59，未知可留空）", min_value=0, max_value=59, value=0)

        try:
            month = int(month)
        except:
            st.error("月份输入错误")
            return

        if hour == 0 and minute == 0:
            hour = None
            minute = None

    else:
        year_zhu = st.text_input("年柱（例如：甲子）")
        month_zhu = st.text_input("月柱（例如：乙丑）")
        day_zhu = st.text_input("日柱（例如：丙寅）")
        time_zhu = st.text_input("时柱（例如：丁卯，未知可留空）")

    if st.button("推算"):
        if mode == "阳历生日":
            nianzhu, yuezhu, rizhu, shizhu = analyze_bazi(year, month, day, hour, minute)
        else:
            if len(year_zhu) != 2 or len(month_zhu) != 2 or len(day_zhu) != 2:
                st.error("请输入正确的四柱，每柱为两个字符")
                return
            shizhu = time_zhu if len(time_zhu) == 2 else "未知"
            nianzhu, yuezhu, rizhu = year_zhu, month_zhu, day_zhu

        st.subheader("推算八字")

        def colorize(char):
            w = wuxing_map.get(char, "土")
            color_dict = {
                "木": "#228B22",
                "火": "#FF4500",
                "土": "#DAA520",
                "金": "#1E90FF",
                "水": "#00CED1",
            }
            return f"<span style='color:{color_dict[w]};font-weight:bold'>{char}</span>"

        def show_bazi_line(chars):
            return "".join([colorize(c) for c in chars])

        tg_chars = nianzhu[0] + yuezhu[0] + rizhu[0] + (shizhu[0] if shizhu != "未知" else "")
        dz_chars = nianzhu[1] + yuezhu[1] + rizhu[1] + (shizhu[1] if shizhu != "未知" else "")

        st.markdown(f"<div style='font-size:40px; letter-spacing:20px'>{show_bazi_line(tg_chars)}</div>", unsafe_allow_html=True)
        st.markdown(f"<div style='font-size:40px; letter-spacing:20px'>{show_bazi_line(dz_chars)}</div>", unsafe_allow_html=True)
        
    # 吉凶推算
    zhus = [nianzhu, yuezhu, rizhu]
    if shizhu != "未知":
        zhus.append(shizhu)

    all_ji = set()
    all_xiong = set()
    for zhu in zhus:
        res = find_jixiong(zhu)
        all_ji.update(res["吉"])
        all_xiong.update(res["凶"])

    year_map = year_ganzhi_map(start=year, end=2100)
    current_year = datetime.datetime.now().year

    st.subheader("🎉 吉年")
    for gz in sorted(all_ji, key=lambda x: ganzhi60.index(x) if x in ganzhi60 else 999):
        years = [y for y, val in year_map.items() if val == gz]
        if years:
            year_strs = []
            for y in years:
                if y >= current_year:
                    year_strs.append(f"<b>{gz}: {y}★</b>")
                else:
                    year_strs.append(f"{gz}: {y}")
            st.markdown(
                f"<span style='color:#FF0000'>{', '.join(year_strs)}</span>",
                unsafe_allow_html=True
            )

    st.subheader("☠️ 凶年")
    for gz in sorted(all_xiong, key=lambda x: ganzhi60.index(x) if x in ganzhi60 else 999):
        years = [y for y, val in year_map.items() if val == gz]
        if years:
            year_strs = []
            for y in years:
                if y >= current_year:
                    year_strs.append(f"<b>{gz}: {y}★</b>")
                else:
                    year_strs.append(f"{gz}: {y}")
            st.markdown(
                f"<span style='color:#555555'>{', '.join(year_strs)}</span>",
                unsafe_allow_html=True
            )

if __name__ == "__main__":
    main()
