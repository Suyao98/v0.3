# ... 前面代码不变 ...

# 五行颜色（同上）
def color_of_gan(gan_ch):
    el = WUXING_OF_GAN.get(gan_ch, "土")
    return WUXING_COLOR.get(el, "#000000")

def render_four_pillars_two_rows(year_p, month_p, day_p, hour_p):
    """
    四柱拆成两行：上行天干（五行颜色），下行地支（默认黑色）
    """
    pillars = [year_p, month_p, day_p, hour_p]
    # 如果空则用两个空格代替
    pillars = [p if p and len(p) == 2 else "  " for p in pillars]
    # 天干和地支分开
    tiangan_row = [p[0] for p in pillars]
    dizhi_row = [p[1] for p in pillars]

    # 生成html，天干带颜色，地支黑色
    html = "<div style='display:flex;justify-content:center;margin-bottom:10px;'>"
    for tg in tiangan_row:
        c = color_of_gan(tg)
        html += f"<div style='width:60px;text-align:center;font-size:24px;font-weight:700;color:{c};margin:0 5px'>{tg}</div>"
    html += "</div>"

    html += "<div style='display:flex;justify-content:center;'>"
    for dz in dizhi_row:
        html += f"<div style='width:60px;text-align:center;font-size:24px;font-weight:700;color:#222;margin:0 5px'>{dz}</div>"
    html += "</div>"
    st.markdown(html, unsafe_allow_html=True)

# ========== Streamlit 页面 ==========
st.set_page_config(page_title="八字排盘", layout="centered")
st.title("吉凶推算")

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

            st.markdown("## 推算结果（四柱）")
            render_four_pillars_two_rows(year_p, month_p, day_p, hour_p)

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
            st.markdown("## 你输入的四柱（天干地支分两行）")
            render_four_pillars_two_rows(nianzhu.strip() or "  ", yuezhu.strip() or "  ", rizhu.strip() or "  ", shizhu.strip() or "  ")
            st.markdown("---")
            show_jixiong(ji, xiong, int(start_year))
        except Exception as e:
            st.error(f"计算出错：{e}")
