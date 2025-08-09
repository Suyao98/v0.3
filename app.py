import streamlit as st
from datetime import datetime, date

# 天干、地支
tiangan = ["甲", "乙", "丙", "丁", "戊", "己", "庚", "辛", "壬", "癸"]
dizhi = ["子", "丑", "寅", "卯", "辰", "巳", "午", "未", "申", "酉", "戌", "亥"]

# 五行映射
wuxing_map = {
    "甲": "木", "乙": "木",
    "丙": "火", "丁": "火",
    "戊": "土", "己": "土",
    "庚": "金", "辛": "金",
    "壬": "水", "癸": "水",
    "子": "水", "丑": "土", "寅": "木", "卯": "木", "辰": "土",
    "巳": "火", "午": "火", "未": "土", "申": "金", "酉": "金",
    "戌": "土", "亥": "水"
}

# 立春时间（简化固定为2月4日 04:00，真实精度可用万年历替换）
# 用于判定年柱边界，出生日期在立春前还是立春后决定年份干支
lichun_month = 2
lichun_day = 4
lichun_hour = 4

def is_after_lichun(y, m, d, h, minute):
    if m > lichun_month:
        return True
    if m < lichun_month:
        return False
    if d > lichun_day:
        return True
    if d < lichun_day:
        return False
    if h > lichun_hour:
        return True
    if h < lichun_hour:
        return False
    if minute is None:
        return True
    return minute >= 0

def leap_year(y):
    return (y % 4 == 0 and y % 100 != 0) or (y % 400 == 0)

def days_in_month(y, m):
    if m in [1,3,5,7,8,10,12]:
        return 31
    elif m in [4,6,9,11]:
        return 30
    elif m == 2:
        return 29 if leap_year(y) else 28
    else:
        return 30  # 防护

# 六十甲子序列
def ganzhi_list():
    lst = []
    for i in range(60):
        lst.append(tiangan[i % 10] + dizhi[i % 12])
    return lst

# 1984年1月1日甲午日（日干支锚点）
base_year = 1984
base_month = 1
base_day = 1
base_gz_day = "甲午"

# 获取天干索引
def tg_index(tg):
    return tiangan.index(tg)

def dz_index(dz):
    return dizhi.index(dz)

# 计算两个日期相差天数
def days_between(y1,m1,d1,y2,m2,d2):
    # 先用datetime计算天数差，更准确
    date1 = date(y1,m1,d1)
    date2 = date(y2,m2,d2)
    return (date2 - date1).days

# 计算年柱
def get_year_ganzhi(year, month, day, hour=None, minute=None):
    # 判断是否过立春
    if hour is None:
        hour = 0
    if minute is None:
        minute = 0
    if not is_after_lichun(year, month, day, hour, minute):
        year -= 1
    offset = (year - 1984) % 60
    gz = ganzhi_list()[offset]
    return gz

# 月支对应二十四节气时间简化版（以节气日为界，时间均以当日零点判断）
# 寅月：立春—惊蛰(3月6日)
# 卯月：惊蛰—清明(4月5日)
# 辰月：清明—立夏(5月6日)
# 巳月：立夏—芒种(6月6日)
# 午月：芒种—小暑(7月7日)
# 未月：小暑—立秋(8月8日)
# 申月：立秋—白露(9月8日)
# 酉月：白露—寒露(10月8日)
# 戌月：寒露—立冬(11月7日)
# 亥月：立冬—大雪(12月7日)
# 子月：大雪—小寒(1月6日)
# 丑月：小寒—立春(2月4日)

jieqi_map = [
    (2,4,"丑"),
    (1,6,"子"),
    (12,7,"亥"),
    (11,7,"戌"),
    (10,8,"酉"),
    (9,8,"申"),
    (8,8,"未"),
    (7,7,"午"),
    (6,6,"巳"),
    (5,6,"辰"),
    (4,5,"卯"),
    (3,6,"寅"),
]

def get_month_dizhi(year, month, day):
    # 判断属于哪个节气区间
    # 注意这里用简单判断，以节气日期为界，时间不精确
    m = month
    d = day
    for i in range(len(jieqi_map)):
        mon, day_jq, zhi = jieqi_map[i]
        if m == mon and d >= day_jq:
            return zhi
        if m == (mon % 12) + 1 and d < jieqi_map[(i+1)%len(jieqi_map)][1]:
            return zhi
    # 默认
    return "丑"

# 五虎遁月干对应表
five_hu_dun = {
    "甲": "丙",
    "己": "丙",
    "乙": "戊",
    "庚": "戊",
    "丙": "庚",
    "辛": "庚",
    "丁": "壬",
    "壬": "壬",
    "戊": "甲",
    "癸": "甲",
}

def get_month_gan(year_gan, month_dz):
    # 根据年干和月支推月干
    start_gan = five_hu_dun.get(year_gan)
    if start_gan is None:
        start_gan = "甲"  # 默认
    start_index = tiangan.index(start_gan)
    dz_idx = dizhi.index(month_dz)
    # 寅月对应dz_idx=2，正月，依次加数
    offset = (dz_idx - 2) % 12
    month_gan_idx = (start_index + offset) % 10
    return tiangan[month_gan_idx]

# 日柱推算（锚点法）
def get_day_ganzhi(year, month, day):
    base_tg = base_gz_day[0]
    base_dz = base_gz_day[1]
    days_diff = days_between(base_year, base_month, base_day, year, month, day)
    tg_idx = (tg_index(base_tg) + days_diff) % 10
    dz_idx = (dz_index(base_dz) + days_diff) % 12
    return tiangan[tg_idx] + dizhi[dz_idx]

# 时辰对应地支（2小时为一时辰）
def get_shizhi(hour, minute):
    # 23:00-0:59 属子时
    total_minutes = hour * 60 + minute
    # 定义时辰起始分钟，从23:00开始算
    # 以23:00为0分钟，01:00为120分钟，依次类推
    # 23:00-00:59为子时，01:00-02:59丑时...
    if total_minutes >= 1380:  # 23*60
        return "子"
    elif total_minutes < 60:
        return "子"
    else:
        # 1点之后就从60开始
        offset = total_minutes - 60
        idx = offset // 120 + 1  # 子时为0，丑时为1，依次类推
        return dizhi[idx % 12]

# 五鼠遁时干推算表，日干对应各时辰天干
five_shu_dun = {
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

def get_shigan(day_gan, shizhi):
    dz_idx = dizhi.index(shizhi)
    return five_shu_dun[day_gan][dz_idx]

# 天干合（五合）和天干冲（四冲）
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

zhi_chong = {dz: dizhi[(i + 6) % 12] for i, dz in enumerate(dizhi)}

# 计算吉凶
def calc_jixiong(gz):
    tg = gz[0]
    dz = gz[1]
    results = {"吉": [], "凶": []}
    tg_he = gan_he.get(tg, "")
    dz_he = zhi_he.get(dz, "")
    tg_ch = gan_chong.get(tg, "")
    dz_ch = zhi_chong.get(dz, "")

    if tg_he and dz_he:
        shuang_he = tg_he + dz_he
        jin_yi = tg_he + dizhi[(dizhi.index(dz_he) + 1) % 12]
        results["吉"].extend([shuang_he, jin_yi])
    if tg_ch and dz_ch:
        shuang_ch = tg_ch + dz_ch
        tui_yi = tg_ch + dizhi[(dizhi.index(dz_ch) - 1) % 12]
        results["凶"].extend([shuang_ch, tui_yi])
    return results

# 60甲子列表
ganzhi60 = ganzhi_list()

# 年份干支映射
def year_ganzhi_map(start=1900, end=2100):
    base_year = 1984
    result = {}
    for y in range(start, end + 1):
        idx = (y - base_year) % 60
        result[y] = ganzhi60[idx]
    return result

def colorize(char):
    w = wuxing_map.get(char, "土")
    color_dict = {
        "木": "#228B22",
        "火": "#FF4500",
        "土": "#DAA520",
        "金": "#1E90FF",
        "水": "#00CED1",
    }
    return f"<span style='color:{color_dict[w]}; font-weight:bold'>{char}</span>"

def main():
    st.set_page_config(page_title="吉凶推算", layout="centered")

    st.title("吉凶推算")

    mode = st.radio("选择输入方式", ["阳历生日", "四柱八字"])

    if mode == "阳历生日":
        year = st.number_input("出生年份", min_value=1900, max_value=2100, value=1990)
        month = st.text_input("出生月份（数字，例如5）", "1")
        day = st.number_input("出生日", min_value=1, max_value=31, value=1)
        hour = st.text_input("出生小时（0-23，未知可留空）", "")
        minute = st.text_input("出生分钟（0-59，未知可留空）", "")

        try:
            month = int(month)
            if hour.strip() == "":
                hour_val = None
            else:
                hour_val = int(hour)
                if not (0 <= hour_val <= 23):
                    st.error("小时应在0-23之间")
                    return
            if minute.strip() == "":
                minute_val = None
            else:
                minute_val = int(minute)
                if not (0 <= minute_val <= 59):
                    st.error("分钟应在0-59之间")
                    return
        except:
            st.error("月份、小时、分钟应输入数字")
            return

    else:
        year_zhu = st.text_input("年柱（例如：甲子）").strip()
        month_zhu = st.text_input("月柱（例如：乙丑）").strip()
        day_zhu = st.text_input("日柱（例如：丙寅）").strip()
        time_zhu = st.text_input("时柱（例如：丁卯，未知可留空）").strip()
        # 校验长度
        if any(len(x) != 2 for x in [year_zhu, month_zhu, day_zhu]):
            st.error("年柱、月柱、日柱必须为两个字符")
            return
        if time_zhu and len(time_zhu) != 2:
            time_zhu = "未知"
        if not time_zhu:
            time_zhu = "未知"

    if st.button("推算"):
        if mode == "阳历生日":
            nianzhu = get_year_ganzhi(year, month, day, hour_val, minute_val)

            month_dz = get_month_dizhi(year, month, day)
            yuegan = get_month_gan(nianzhu[0], month_dz)
            yuezhu = yuegan + month_dz

            rizhu = get_day_ganzhi(year, month, day)

            if hour_val is not None and minute_val is not None:
                shizhi_dz = get_shizhi(hour_val, minute_val)
                shigan = get_shigan(rizhu[0], shizhi_dz)
                shizhu = shigan + shizhi_dz
            else:
                shizhu = "未知"

        else:
            nianzhu = year_zhu
            yuezhu = month_zhu
            rizhu = day_zhu
            shizhu = time_zhu

        # 显示八字，天干一行，地支一行，五行色
        st.subheader("四柱八字")
        tg_line = nianzhu[0] + yuezhu[0] + rizhu[0] + (shizhu[0] if shizhu != "未知" else "")
        dz_line = nianzhu[1] + yuezhu[1] + rizhu[1] + (shizhu[1] if shizhu != "未知" else "")

        def show_bazi_line(chars):
            res = ""
            spacing = " " * 4  # 加大间距，中文空格
            for c in chars:
                res += colorize(c) + spacing
            return res

        st.markdown(f"<div style='font-size:40px'>{show_bazi_line(tg_line)}</div>", unsafe_allow_html=True)
        st.markdown(f"<div style='font-size:40px'>{show_bazi_line(dz_line)}</div>", unsafe_allow_html=True)

        # 生成吉凶年份数据
        current_year = datetime.now().year
        start_year = year if mode == "阳历生日" else 1900
        year_map = year_ganzhi_map(start_year, 2100)

        # 简单吉凶分类：按天干地支组合分组，这里示范使用固定吉凶列表
        all_ji = ["甲子", "乙丑", "丙寅", "丁卯", "戊辰"]  # 示例吉年干支，真实可用你的业务逻辑替换
        all_xiong = ["己巳", "庚午", "辛未", "壬申", "癸酉"]  # 示例凶年干支

        # 吉年输出
        st.subheader("吉年")
        for gz in sorted(all_ji, key=lambda x: ganzhi60.index(x) if x in ganzhi60 else 999):
            years = [y for y, gz_y in year_map.items() if gz_y == gz and y >= start_year]
            if years:
                year_strs = []
                for y in years:
                    if y > current_year:
                        year_strs.append(f"{y}年★")
                    else:
                        year_strs.append(f"{y}年")
                st.markdown(
                    f"<span style='color:green; font-weight:bold'>{gz}: {', '.join(year_strs)}</span>",
                    unsafe_allow_html=True
                )

        # 凶年输出
        st.subheader("凶年")
        for gz in sorted(all_xiong, key=lambda x: ganzhi60.index(x) if x in ganzhi60 else 999):
            years = [y for y, gz_y in year_map.items() if gz_y == gz and y >= start_year]
            if years:
                year_strs = []
                for y in years:
                    if y > current_year:
                        year_strs.append(f"{y}年★")
                    else:
                        year_strs.append(f"{y}年")
                st.markdown(
                    f"<span style='color:red; font-weight:bold'>{gz}: {', '.join(year_strs)}</span>",
                    unsafe_allow_html=True
                )

if __name__ == "__main__":
    main()
