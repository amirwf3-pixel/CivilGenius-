"""
CivilGenius Ultimate Portfolio Platform (v16.0 Final)
پلتفرم حرفه‌ای مهندسی عمران با ناوبری هوشمند و رابط سلطنتی
"""
import os
import time
import streamlit as st
import jdatetime
import plotly.graph_objects as go
from groq import Groq
from dotenv import load_dotenv

from civil_engine import calculate_foundation, calculate_beam, calculate_column
from document_generator import (
    build_excel, build_word, build_dxf,
    num_fa, money_fa, shamsi_now, create_output_folder
)

# ============================================================
# تنظیمات صفحه
# ============================================================
st.set_page_config(
    page_title="CivilGenius | Portfolio",
    page_icon="🏛️",
    layout="wide",
    initial_sidebar_state="expanded"
)

C_NAVY = "#0A192F"
C_NAVY2 = "#172A45"
C_GOLD = "#D4AF37"
C_LIGHT = "#F8F9FA"
C_GREEN = "#43A047"

# ============================================================
# استایل CSS نهایی (حرفه‌ای، مدرن، ریسپانسیو)
# ============================================================
st.markdown(f"""
<style>
    @import url('https://v1.fontapi.ir/css/Vazirmatn');
    
    * {{ font-family: 'Vazirmatn', sans-serif !important; direction: rtl !important; text-align: right !important; }}
    
    .stApp {{ background: linear-gradient(135deg, {C_LIGHT} 0%, #E8ECF1 100%); }}
    
    h1, h2, h3, h4 {{ color: {C_NAVY} !important; font-weight: 800 !important; }}
    
    /* سایدبار */
    [data-testid="stSidebar"] {{ 
        background: linear-gradient(180deg, {C_NAVY} 0%, {C_NAVY2} 100%) !important;
        border-left: 3px solid {C_GOLD};
    }}
    [data-testid="stSidebar"] * {{ color: white !important; }}
    [data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2, [data-testid="stSidebar"] h3 {{ color: {C_GOLD} !important; }}
    
    /* رادیو منوی سایدبار */
    [data-testid="stSidebar"] .stRadio > div {{
        background: rgba(255,255,255,0.05);
        padding: 10px;
        border-radius: 10px;
    }}
    [data-testid="stSidebar"] .stRadio label {{
        padding: 12px 15px !important;
        margin: 5px 0 !important;
        border-radius: 8px !important;
        transition: all 0.3s ease !important;
        font-size: 15px !important;
    }}
    [data-testid="stSidebar"] .stRadio label:hover {{
        background: rgba(212, 175, 55, 0.2) !important;
    }}
    
    /* هدر اصلی */
    .main-header {{
        background: linear-gradient(135deg, {C_NAVY} 0%, {C_NAVY2} 100%);
        padding: 30px;
        border-radius: 15px;
        color: white;
        margin-bottom: 25px;
        box-shadow: 0 15px 40px rgba(10,25,47,0.2);
        border-right: 8px solid {C_GOLD};
    }}
    .main-header h1 {{ color: white !important; margin: 0; font-size: 32px; }}
    .main-header p {{ color: #B8C5D6; margin-top: 10px; font-size: 15px; }}
    
    /* کارت‌های VIP نتایج */
    .vip-card {{ 
        background: linear-gradient(145deg, {C_NAVY}, {C_NAVY2}); 
        border-right: 6px solid {C_GOLD}; 
        border-radius: 15px; 
        padding: 22px; 
        color: white; 
        box-shadow: 0 12px 25px rgba(0,0,0,0.15); 
        margin-bottom: 15px; 
        min-height: 145px;
        transition: all 0.3s ease;
    }}
    .vip-card:hover {{ 
        transform: translateY(-5px);
        box-shadow: 0 20px 40px rgba(212,175,55,0.25);
    }}
    .vip-icon {{ font-size: 36px; margin-bottom: 8px; }}
    .vip-title {{ font-size: 14px; color: #8892B0; margin-bottom: 8px; font-weight: 500; }}
    .vip-value {{ font-size: 26px; font-weight: 800; color: {C_GOLD}; }}
    .vip-unit {{ font-size: 14px; color: white; margin-right: 5px; opacity: 0.7; }}
    
    /* کارت‌های آمار landing page */
    .stat-card {{
        background: white;
        border-radius: 15px;
        padding: 25px;
        text-align: center;
        box-shadow: 0 8px 20px rgba(0,0,0,0.08);
        border-top: 4px solid {C_GOLD};
        transition: all 0.3s ease;
    }}
    .stat-card:hover {{ transform: scale(1.03); }}
    .stat-card .num {{ font-size: 42px; font-weight: 800; color: {C_NAVY}; }}
    .stat-card .lbl {{ font-size: 15px; color: #666; margin-top: 5px; }}
    
    /* دکمه اصلی */
    .stButton>button {{ 
        background: linear-gradient(135deg, {C_NAVY} 0%, {C_NAVY2} 100%) !important; 
        color: {C_GOLD} !important; 
        border: 2px solid {C_GOLD} !important; 
        border-radius: 12px !important; 
        font-size: 17px !important; 
        font-weight: bold !important; 
        width: 100%; 
        height: 55px;
        transition: all 0.4s ease !important;
    }}
    .stButton>button:hover {{ 
        background: linear-gradient(135deg, {C_GOLD} 0%, #B8892C 100%) !important; 
        color: {C_NAVY} !important;
        transform: translateY(-2px);
        box-shadow: 0 10px 25px rgba(212,175,55,0.4) !important;
    }}
    
    /* دکمه دانلود */
    .stDownloadButton>button {{ 
        background: linear-gradient(135deg, {C_GREEN} 0%, #2E7D32 100%) !important; 
        color: white !important; 
        border: none !important;
        border-radius: 10px !important; 
        width: 100%; 
        height: 55px;
        font-weight: bold;
        font-size: 15px;
        transition: all 0.3s ease !important;
    }}
    .stDownloadButton>button:hover {{
        transform: translateY(-2px);
        box-shadow: 0 10px 20px rgba(67,160,71,0.3) !important;
    }}
    
    /* پیام موفقیت */
    .success-banner {{
        background: linear-gradient(135deg, {C_NAVY} 0%, {C_NAVY2} 100%);
        border: 2px solid {C_GOLD};
        border-radius: 15px;
        padding: 20px 30px;
        color: white;
        margin: 20px 0;
        text-align: center;
    }}
    .success-banner h3 {{ color: {C_GOLD} !important; margin: 0; }}
    
    /* چت */
    .chat-bubble-user {{ 
        background: linear-gradient(135deg, {C_NAVY} 0%, {C_NAVY2} 100%); 
        color: white; 
        padding: 15px 20px; 
        border-radius: 15px 15px 5px 15px; 
        margin-bottom: 10px;
        max-width: 80%;
        margin-right: auto;
    }}
    .chat-bubble-ai {{ 
        background: white; 
        color: {C_NAVY}; 
        padding: 15px 20px; 
        border-radius: 15px 15px 15px 5px; 
        border-right: 4px solid {C_GOLD};
        margin-bottom: 10px;
        max-width: 80%;
        box-shadow: 0 4px 10px rgba(0,0,0,0.05);
    }}
    
    /* رزومه */
    .skill-badge {{ 
        display: inline-block; 
        background: linear-gradient(135deg, {C_GOLD} 0%, #B8892C 100%);
        color: {C_NAVY}; 
        padding: 8px 16px; 
        border-radius: 25px; 
        margin: 6px; 
        font-weight: bold; 
        font-size: 13px;
        box-shadow: 0 4px 10px rgba(212,175,55,0.3);
    }}
    
    /* فرم ورودی */
    .input-section {{
        background: white;
        padding: 25px;
        border-radius: 15px;
        box-shadow: 0 8px 20px rgba(0,0,0,0.06);
        border-right: 5px solid {C_GOLD};
        margin-bottom: 20px;
    }}
    
    /* حذف Menu بالای Streamlit */
    #MainMenu {{visibility: hidden;}}
    footer {{visibility: hidden;}}
    header {{visibility: hidden;}}
</style>
""", unsafe_allow_html=True)

# ============================================================
# مدیریت حافظه session (جداگانه برای هر ماژول)
# ============================================================
if "current_module" not in st.session_state:
    st.session_state.current_module = "home"
if "results" not in st.session_state:
    st.session_state.results = {}
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# ============================================================
# سایدبار حرفه‌ای با منوی رادیویی
# ============================================================
with st.sidebar:
    st.markdown(f"<h1 style='text-align:center; color:{C_GOLD}; font-size:70px; margin:0;'>🏛️</h1>", unsafe_allow_html=True)
    st.markdown(f"<h2 style='text-align:center; margin-top:0;'>CivilGenius</h2>", unsafe_allow_html=True)
    st.markdown("<p style='text-align:center; color:#8892B0; font-size:13px;'>پلتفرم هوشمند مهندسی عمران</p>", unsafe_allow_html=True)
    
    st.divider()
    
    st.markdown("### 📂 منوی اصلی")
    
    module = st.radio(
        "انتخاب ماژول:",
        options=["🏠 خانه", "🏗️ فونداسیون", "📏 تیر بتنی", "🏛️ ستون بتنی", "🤖 چت آیین‌نامه", "👤 درباره من"],
        key="menu_radio",
        label_visibility="collapsed"
    )
    
    st.divider()
    
    st.markdown("### 📅 اطلاعات جلسه")
    st.info(f"📆 {shamsi_now()}")
    
    st.markdown(f"""
    <div style='background:rgba(212,175,55,0.1); padding:15px; border-radius:10px; border-right:3px solid {C_GOLD};'>
        <p style='color:{C_GOLD} !important; font-size:13px; margin:0;'>
            <b>💡 راهنمای سریع:</b><br>
            از منوی بالا ماژول موردنظر را انتخاب کنید.
        </p>
    </div>
    """, unsafe_allow_html=True)

# ============================================================
# صفحه اصلی (Home)
# ============================================================
if "خانه" in module:
    st.markdown(f"""
    <div class="main-header">
        <h1>🏛️ به پلتفرم CivilGenius خوش آمدید</h1>
        <p>یک سیستم یکپارچه هوشمند برای طراحی، محاسبه و تولید مدارک مهندسی عمران — تلفیق مهندسی + پایتون + هوش مصنوعی</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("### 🎯 قابلیت‌های سامانه")
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown(f"""<div class="stat-card"><div class="num">۳</div><div class="lbl">ماژول طراحی سازه</div></div>""", unsafe_allow_html=True)
    with c2:
        st.markdown(f"""<div class="stat-card"><div class="num">۳</div><div class="lbl">نوع خروجی حرفه‌ای</div></div>""", unsafe_allow_html=True)
    with c3:
        st.markdown(f"""<div class="stat-card"><div class="num">AI</div><div class="lbl">دستیار آیین‌نامه</div></div>""", unsafe_allow_html=True)
    with c4:
        st.markdown(f"""<div class="stat-card"><div class="num">∞</div><div class="lbl">پروژه در دقیقه</div></div>""", unsafe_allow_html=True)
    
    st.markdown("### ✨ ویژگی‌های کلیدی")
    c1, c2 = st.columns(2)
    with c1:
        st.markdown(f"""
        <div class='input-section'>
            <h4>🚀 محاسبات لحظه‌ای</h4>
            <p style='color:#555; line-height:1.8;'>محاسبات ژئوتکنیک، سازه و متره در کسری از ثانیه با دقت آیین‌نامه‌ای.</p>
        </div>
        """, unsafe_allow_html=True)
        st.markdown(f"""
        <div class='input-section'>
            <h4>📈 نمودارهای تعاملی</h4>
            <p style='color:#555; line-height:1.8;'>رسم زنده دیاگرام لنگر، برش و منحنی اندرکنش P-M ستون‌ها.</p>
        </div>
        """, unsafe_allow_html=True)
    with c2:
        st.markdown(f"""
        <div class='input-section'>
            <h4>📄 خروجی چند فرمته</h4>
            <p style='color:#555; line-height:1.8;'>تولید همزمان اکسل، ورد و نقشه اتوکد در پوشه‌های سازماندهی شده.</p>
        </div>
        """, unsafe_allow_html=True)
        st.markdown(f"""
        <div class='input-section'>
            <h4>🤖 هوش مصنوعی مهندسی</h4>
            <p style='color:#555; line-height:1.8;'>پرسش و پاسخ تخصصی درباره مقررات ملی ساختمان با دستیار AI.</p>
        </div>
        """, unsafe_allow_html=True)

# ============================================================
# تابع مرکزی پردازش و دانلود
# ============================================================
def process_module(data_dict, module_prefix):
    code = f"PRJ-{module_prefix}-{jdatetime.datetime.now().strftime('%y%m%d%H%M%S')}"
    project_dir = create_output_folder(module_prefix, code)
    
    excel_path = os.path.join(project_dir, f"{code}_BOQ.xlsx")
    word_path = os.path.join(project_dir, f"{code}_Report.docx")
    dxf_path = os.path.join(project_dir, f"{code}_Plan.dxf")
    
    build_excel(data_dict, excel_path, code)
    build_word(data_dict, word_path, code)
    build_dxf(data_dict, dxf_path, code)
    
    with open(excel_path, "rb") as f: xls_bytes = f.read()
    with open(word_path, "rb") as f: doc_bytes = f.read()
    with open(dxf_path, "rb") as f: dxf_bytes = f.read()
    
    st.session_state.results[module_prefix] = {
        "data": data_dict,
        "code": code,
        "folder": project_dir,
        "xls": xls_bytes,
        "doc": doc_bytes,
        "dxf": dxf_bytes
    }

def show_download_section(module_prefix):
    if module_prefix not in st.session_state.results:
        return
    res = st.session_state.results[module_prefix]
    
    st.markdown(f"""
    <div class="success-banner">
        <h3>🎉 پروژه با موفقیت آماده شد!</h3>
        <p style='margin:8px 0 0 0; color:#B8C5D6;'>کد پروژه: <b style='color:{C_GOLD};'>{res['code']}</b></p>
        <p style='margin:5px 0 0 0; color:#B8C5D6; font-size:12px;'>📁 پوشه ذخیره: outputs/{res['code']}</p>
    </div>
    """, unsafe_allow_html=True)
    
    return res

def show_download_buttons(res):
    st.markdown("### 📥 دریافت اسناد مهندسی")
    d1, d2, d3 = st.columns(3)
    d1.download_button("📊 دفترچه محاسبات Excel", data=res["xls"], file_name=f"{res['code']}_BOQ.xlsx", key=f"dl_x_{res['code']}")
    d2.download_button("📄 گزارش فنی Word", data=res["doc"], file_name=f"{res['code']}_Report.docx", key=f"dl_d_{res['code']}")
    d3.download_button("📐 نقشه AutoCAD", data=res["dxf"], file_name=f"{res['code']}_Plan.dxf", key=f"dl_c_{res['code']}")

# ============================================================
# ماژول فونداسیون
# ============================================================
if "فونداسیون" in module:
    st.markdown(f"""
    <div class="main-header">
        <h1>🏗️ طراحی و متره فونداسیون گسترده</h1>
        <p>محاسبات ژئوتکنیک، برش پانچ و برآورد کامل احجام و هزینه فونداسیون</p>
    </div>
    """, unsafe_allow_html=True)
    
    c1, c2 = st.columns(2)
    with c1:
        st.markdown('<div class="input-section"><h4>📐 پارامترهای هندسی</h4></div>', unsafe_allow_html=True)
        L = st.number_input("طول فونداسیون (متر)", value=15.0, min_value=1.0, step=0.5, key="fnd_L")
        B = st.number_input("عرض فونداسیون (متر)", value=8.0, min_value=1.0, step=0.5, key="fnd_B")
        H = st.number_input("ضخامت فونداسیون (متر)", value=1.2, min_value=0.3, step=0.1, key="fnd_H")
    with c2:
        st.markdown('<div class="input-section"><h4>🌍 پارامترهای ژئوتکنیک</h4></div>', unsafe_allow_html=True)
        c_soil = st.number_input("چسبندگی خاک c (kPa)", value=20.0, min_value=0.0, step=1.0, key="fnd_c")
        gamma = st.number_input("وزن مخصوص خاک γ (kN/m³)", value=18.0, min_value=10.0, step=0.5, key="fnd_g")
    
    if st.button("🚀 پردازش، محاسبه و تولید مدارک", key="btn_fnd"):
        with st.spinner("در حال تحلیل و ساخت اسناد..."):
            process_module(calculate_foundation(L, B, H, c_soil, gamma), "FND")
        st.balloons()
    
    if "FND" in st.session_state.results:
        res = show_download_section("FND")
        data = res["data"]
        
        st.markdown("### 📊 داشبورد نتایج فنی")
        m1, m2, m3, m4 = st.columns(4)
        with m1: st.markdown(f"""<div class="vip-card"><div class="vip-icon">🏗️</div><div class="vip-title">حجم بتن‌ریزی</div><div class="vip-value">{num_fa(data['geom']['vol'])}<span class="vip-unit">m³</span></div></div>""", unsafe_allow_html=True)
        with m2: st.markdown(f"""<div class="vip-card"><div class="vip-icon">⚙️</div><div class="vip-title">وزن آرماتور</div><div class="vip-value">{num_fa(data['boq']['rebar'])}<span class="vip-unit">kg</span></div></div>""", unsafe_allow_html=True)
        with m3: st.markdown(f"""<div class="vip-card"><div class="vip-icon">🌍</div><div class="vip-title">ظرفیت باربری خاک</div><div class="vip-value">{num_fa(data['geo']['q_all'])}<span class="vip-unit">kPa</span></div></div>""", unsafe_allow_html=True)
        with m4: st.markdown(f"""<div class="vip-card"><div class="vip-icon">💰</div><div class="vip-title">برآورد کل هزینه</div><div class="vip-value">{money_fa(data['boq']['total'])}<span class="vip-unit">تومان</span></div></div>""", unsafe_allow_html=True)
        
        st.divider()
        show_download_buttons(res)

# ============================================================
# ماژول تیر
# ============================================================
if "تیر" in module:
    st.markdown(f"""
    <div class="main-header">
        <h1>📏 طراحی و محاسبه تیر بتن آرمه</h1>
        <p>تحلیل خمشی، برشی و طراحی آرماتور تیر مطابق مبحث نهم مقررات ملی</p>
    </div>
    """, unsafe_allow_html=True)
    
    c1, c2 = st.columns(2)
    with c1:
        st.markdown('<div class="input-section"><h4>📐 هندسه و بارگذاری</h4></div>', unsafe_allow_html=True)
        span = st.number_input("طول دهانه (متر)", value=6.0, min_value=1.0, step=0.5, key="bm_s")
        wd = st.number_input("بار مرده (kN/m)", value=25.0, min_value=0.0, step=1.0, key="bm_wd")
        wl = st.number_input("بار زنده (kN/m)", value=12.0, min_value=0.0, step=1.0, key="bm_wl")
    with c2:
        st.markdown('<div class="input-section"><h4>🧱 مقطع تیر</h4></div>', unsafe_allow_html=True)
        bt = st.number_input("عرض تیر b (میلی‌متر)", value=400, min_value=100, step=50, key="bm_b")
        ht = st.number_input("ارتفاع تیر h (میلی‌متر)", value=600, min_value=100, step=50, key="bm_h")
    
    if st.button("🚀 محاسبه و طراحی تیر", key="btn_bm"):
        with st.spinner("در حال تحلیل تیر..."):
            process_module(calculate_beam(span, wd, wl, bt, ht), "BEM")
        st.balloons()
    
    if "BEM" in st.session_state.results:
        res = show_download_section("BEM")
        data = res["data"]
        
        st.markdown("### 📊 نتایج طراحی سازه‌ای")
        m1, m2, m3, m4 = st.columns(4)
        with m1: st.markdown(f"""<div class="vip-card"><div class="vip-icon">📐</div><div class="vip-title">لنگر نهایی Mu</div><div class="vip-value">{num_fa(data['struc']['Mu'])}<span class="vip-unit">kN.m</span></div></div>""", unsafe_allow_html=True)
        with m2: st.markdown(f"""<div class="vip-card"><div class="vip-icon">⚙️</div><div class="vip-title">آرماتور خمشی</div><div class="vip-value">{num_fa(data['struc']['As'])}<span class="vip-unit">mm²</span></div></div>""", unsafe_allow_html=True)
        with m3: st.markdown(f"""<div class="vip-card"><div class="vip-icon">⛓️</div><div class="vip-title">فاصله خاموت</div><div class="vip-value">{num_fa(data['struc']['stirrup_spacing'])}<span class="vip-unit">cm</span></div></div>""", unsafe_allow_html=True)
        with m4: st.markdown(f"""<div class="vip-card"><div class="vip-icon">💰</div><div class="vip-title">برآورد هزینه</div><div class="vip-value">{money_fa(data['boq']['total'])}<span class="vip-unit">تومان</span></div></div>""", unsafe_allow_html=True)
        
        st.markdown("### 📈 دیاگرام لنگر خمشی و نیروی برشی")
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=data['diagrams']['x'], y=data['diagrams']['M'], mode='lines', name='لنگر خمشی (kN.m)', line=dict(color=C_GOLD, width=4), fill='tozeroy', fillcolor='rgba(212,175,55,0.15)'))
        fig.add_trace(go.Scatter(x=data['diagrams']['x'], y=data['diagrams']['V'], mode='lines', name='نیروی برشی (kN)', line=dict(color=C_NAVY, width=3, dash='dash')))
        fig.update_layout(
            title=dict(text="<b>دیاگرام تلاش‌های داخلی در طول دهانه تیر</b>", font=dict(size=18, color=C_NAVY)),
            xaxis_title="طول تیر (متر)",
            yaxis_title="مقدار تلاش داخلی",
            template="plotly_white",
            height=450,
            hovermode='x unified',
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )
        st.plotly_chart(fig, use_container_width=True)
        
        st.divider()
        show_download_buttons(res)

# ============================================================
# ماژول ستون
# ============================================================
if "ستون" in module:
    st.markdown(f"""
    <div class="main-header">
        <h1>🏛️ طراحی و محاسبه ستون بتن آرمه</h1>
        <p>کنترل ظرفیت، طراحی آرماتور و رسم منحنی اندرکنش P-M</p>
    </div>
    """, unsafe_allow_html=True)
    
    c1, c2 = st.columns(2)
    with c1:
        st.markdown('<div class="input-section"><h4>📐 ارتفاع و بارگذاری</h4></div>', unsafe_allow_html=True)
        L_col = st.number_input("ارتفاع ستون (متر)", value=3.2, min_value=1.0, step=0.1, key="col_L")
        Pu = st.number_input("بار محوری نهایی Pu (kN)", value=1500.0, min_value=0.0, step=50.0, key="col_P")
        Mu_col = st.number_input("لنگر خمشی نهایی Mu (kN.m)", value=120.0, min_value=0.0, step=10.0, key="col_M")
    with c2:
        st.markdown('<div class="input-section"><h4>🧱 مقطع ستون</h4></div>', unsafe_allow_html=True)
        bc = st.number_input("عرض ستون b (میلی‌متر)", value=400, min_value=200, step=50, key="col_b")
        hc = st.number_input("عمق ستون h (میلی‌متر)", value=400, min_value=200, step=50, key="col_h")
    
    if st.button("🚀 محاسبه و طراحی ستون", key="btn_col"):
        with st.spinner("در حال طراحی ستون..."):
            process_module(calculate_column(L_col, Pu, Mu_col, bc, hc), "COL")
        st.balloons()
    
    if "COL" in st.session_state.results:
        res = show_download_section("COL")
        data = res["data"]
        
        st.markdown("### 📊 نتایج طراحی سازه‌ای")
        m1, m2, m3, m4 = st.columns(4)
        with m1: st.markdown(f"""<div class="vip-card"><div class="vip-icon">🏛️</div><div class="vip-title">ظرفیت فشاری Pn</div><div class="vip-value">{num_fa(data['struc']['Pn_max'])}<span class="vip-unit">kN</span></div></div>""", unsafe_allow_html=True)
        with m2: st.markdown(f"""<div class="vip-card"><div class="vip-icon">⚙️</div><div class="vip-title">تعداد میلگرد طولی</div><div class="vip-value">{num_fa(data['struc']['num_bars'], 0)}<span class="vip-unit">عدد</span></div></div>""", unsafe_allow_html=True)
        with m3: st.markdown(f"""<div class="vip-card"><div class="vip-icon">⛓️</div><div class="vip-title">فاصله خاموت</div><div class="vip-value">{num_fa(data['struc']['tie_spacing'])}<span class="vip-unit">cm</span></div></div>""", unsafe_allow_html=True)
        with m4: st.markdown(f"""<div class="vip-card"><div class="vip-icon">💰</div><div class="vip-title">برآورد هزینه</div><div class="vip-value">{money_fa(data['boq']['total'])}<span class="vip-unit">تومان</span></div></div>""", unsafe_allow_html=True)
        
        st.markdown("### 📊 منحنی اندرکنش نیروی محوری - لنگر خمشی (P-M)")
        
        # ساخت نمودار زیبای P-M
        pm = data['pm_curve']
        is_safe = pm['user_P'] <= max(pm['P']) and pm['user_M'] <= max(pm['M'])
        
        fig_pm = go.Figure()
        
        # ناحیه ایمن (زیر منحنی)
        fig_pm.add_trace(go.Scatter(
            x=pm['M'] + [0, 0],
            y=pm['P'] + [0, pm['P'][0]],
            fill='toself',
            fillcolor='rgba(67,160,71,0.15)',
            line=dict(color='rgba(0,0,0,0)'),
            name='ناحیه ایمن (Safe Zone)',
            hoverinfo='skip'
        ))
        
        # منحنی مرزی
        fig_pm.add_trace(go.Scatter(
            x=pm['M'], y=pm['P'],
            mode='lines+markers',
            name='مرز ظرفیت مقطع',
            line=dict(color=C_NAVY, width=4),
            marker=dict(size=8, color=C_GOLD, line=dict(color=C_NAVY, width=2))
        ))
        
        # نقطه بارگذاری کاربر
        point_color = C_GREEN if is_safe else "#D32F2F"
        fig_pm.add_trace(go.Scatter(
            x=[pm['user_M']], y=[pm['user_P']],
            mode='markers+text',
            name='نقطه بارگذاری (Pu, Mu)',
            marker=dict(size=22, color=point_color, symbol='star', line=dict(color=C_NAVY, width=3)),
            text=[f"  ({num_fa(pm['user_M'])}, {num_fa(pm['user_P'])})"],
            textposition="top right",
            textfont=dict(size=13, color=C_NAVY, family="Vazirmatn")
        ))
        
        fig_pm.update_layout(
            title=dict(
                text=f"<b>منحنی اندرکنش P-M | وضعیت طراحی: {'✅ ایمن' if is_safe else '❌ ناایمن - نیاز به تقویت'}</b>",
                font=dict(size=18, color=C_NAVY)
            ),
            xaxis=dict(title="لنگر خمشی Mu (kN.m)", gridcolor='#E0E0E0', zerolinecolor='#999'),
            yaxis=dict(title="نیروی محوری Pu (kN)", gridcolor='#E0E0E0', zerolinecolor='#999'),
            template="plotly_white",
            height=550,
            hovermode='closest',
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
            plot_bgcolor='#FAFAFA'
        )
        st.plotly_chart(fig_pm, use_container_width=True)
        
        st.divider()
        show_download_buttons(res)

# ============================================================
# چت آیین‌نامه
# ============================================================
if "چت" in module:
    st.markdown(f"""
    <div class="main-header">
        <h1>🤖 دستیار هوشمند آیین‌نامه</h1>
        <p>پرسش تخصصی درباره مقررات ملی ساختمان، ژئوتکنیک و طراحی سازه‌ای</p>
    </div>
    """, unsafe_allow_html=True)
    
    # نمایش تاریخچه چت
    chat_container = st.container()
    with chat_container:
        for msg in st.session_state.chat_history:
            if msg['role'] == 'user':
                st.markdown(f"<div class='chat-bubble-user'><b>👤 شما:</b><br>{msg['content']}</div>", unsafe_allow_html=True)
            else:
                st.markdown(f"<div class='chat-bubble-ai'><b>🤖 دستیار AI:</b><br>{msg['content']}</div>", unsafe_allow_html=True)
    
    # فرم ورودی سوال
    st.divider()
    with st.form("chat_form", clear_on_submit=True):
        q = st.text_area("❓ سوال مهندسی خود را اینجا بنویسید:", height=100, max_chars=500, placeholder="مثال: حداقل کاور بتن فونداسیون طبق مبحث نهم چقدر است؟")
        c1, c2 = st.columns([1, 5])
        with c1:
            ask = st.form_submit_button("📤 ارسال")
        with c2:
            clear = st.form_submit_button("🗑️ پاک کردن تاریخچه")
    
    if clear:
        st.session_state.chat_history = []
        st.rerun()
    
    if ask and q.strip():
        if len(q) > 500:
            st.error("⚠️ لطفاً سوال را کوتاه‌تر بنویسید (حداکثر ۵۰۰ کاراکتر).")
        else:
            st.session_state.chat_history.append({"role": "user", "content": q})
            
            try:
                load_dotenv()
                api_key = os.getenv("GROQ_API_KEY")
                
                if not api_key:
                    st.error("❌ کلید GROQ_API_KEY در فایل .env یافت نشد.")
                else:
                    client = Groq(api_key=api_key)
                    
                    with st.spinner("🤖 دستیار در حال تحلیل و پاسخگویی..."):
                        response = client.chat.completions.create(
                            messages=[
                                {"role": "system", "content": "شما یک مهندس عمران ارشد و مسلط بر مقررات ملی ساختمان ایران، مبحث نهم بتن و مبحث هفتم پی و ژئوتکنیک هستید. پاسخ‌ها را کوتاه، دقیق، علمی و به فارسی روان بنویسید."},
                                {"role": "user", "content": q}
                            ],
                            model="llama-3.3-70b-versatile",
                            max_tokens=1024,
                            temperature=0.3
                        )
                        answer = response.choices[0].message.content
                        st.session_state.chat_history.append({"role": "assistant", "content": answer})
                        st.rerun()
                        
            except Exception as e:
                error_msg = str(e)
                if "413" in error_msg or "too_large" in error_msg.lower():
                    st.error("⚠️ حجم درخواست بیش از حد است. لطفاً سوال کوتاه‌تری بپرسید.")
                elif "401" in error_msg or "auth" in error_msg.lower():
                    st.error("🔐 کلید API نامعتبر است. فایل .env را بررسی کنید.")
                elif "model" in error_msg.lower():
                    st.error("🤖 مدل هوش مصنوعی در دسترس نیست. لطفاً دوباره امتحان کنید.")
                else:
                    st.error(f"❌ خطا در ارتباط با هوش مصنوعی:\n\n{error_msg[:200]}")
                # حذف پیام کاربر در صورت خطا
                if st.session_state.chat_history and st.session_state.chat_history[-1]['role'] == 'user':
                    st.session_state.chat_history.pop()

# ============================================================
# درباره من
# ============================================================
if "درباره" in module:
    st.markdown(f"""
    <div class="main-header">
        <h1>👤 درباره توسعه‌دهنده و پروژه</h1>
        <p>نمایه تخصصی و معرفی سامانه CivilGenius</p>
    </div>
    """, unsafe_allow_html=True)
    
    col_a, col_b = st.columns([1, 2])
    with col_a:
        st.markdown(f"""
        <div style='background:linear-gradient(145deg, {C_NAVY}, {C_NAVY2}); border-radius:20px; padding:35px; text-align:center; color:white; box-shadow: 0 15px 35px rgba(10,25,47,0.2);'>
            <div style='font-size:100px; margin-bottom:15px;'>👨‍💻</div>
            <h2 style='color:{C_GOLD} !important; margin:5px 0;'>مهندس عمران</h2>
            <p style='color:#8892B0; font-size:14px;'>توسعه‌دهنده نرم‌افزار مهندسی</p>
            <div style='margin-top:20px; padding-top:20px; border-top:1px solid rgba(255,255,255,0.1);'>
                <p style='color:{C_GOLD}; font-size:13px; margin:5px 0;'>🎓 مهندسی عمران</p>
                <p style='color:{C_GOLD}; font-size:13px; margin:5px 0;'>💻 توسعه‌دهنده پایتون</p>
                <p style='color:{C_GOLD}; font-size:13px; margin:5px 0;'>🤖 متخصص هوش مصنوعی</p>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col_b:
        st.markdown(f"""
        <div class='input-section'>
            <h3>💼 معرفی</h3>
            <p style='color:#444; line-height:2; font-size:15px;'>
            مهندس عمران با تخصص ترکیبی در طراحی سازه، ژئوتکنیک و توسعه نرم‌افزار. علاقه‌مند به خودکارسازی فرآیندهای مهندسی با استفاده از پایتون و هوش مصنوعی. این سامانه نمونه‌ای عملی از توانمندی من در تبدیل چالش‌های واقعی دفتر فنی به راه‌حل‌های دیجیتال و کاربردی است.
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown(f"""
        <div class='input-section'>
            <h3>🛠️ مهارت‌های فنی</h3>
            <div>
                <span class='skill-badge'>Python</span>
                <span class='skill-badge'>Streamlit</span>
                <span class='skill-badge'>AI / LLM</span>
                <span class='skill-badge'>Groq API</span>
                <span class='skill-badge'>Plotly</span>
                <span class='skill-badge'>AutoCAD Automation</span>
                <span class='skill-badge'>Excel Reporting</span>
                <span class='skill-badge'>Word Automation</span>
                <span class='skill-badge'>Structural Design</span>
                <span class='skill-badge'>Geotechnics</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown(f"""
    <div class='input-section'>
        <h3>🚀 درباره پروژه CivilGenius</h3>
        <p style='color:#444; line-height:2; font-size:14px;'>
        CivilGenius یک پلتفرم جامع تحت وب برای اتوماسیون محاسبات و تولید مدارک مهندسی عمران است. این سامانه با تلفیق دانش تخصصی سازه و ژئوتکنیک با فناوری‌های نوین برنامه‌نویسی، توانسته است چرخه کامل طراحی از ورود داده تا تحویل نقشه اتوکد را در چند ثانیه محقق سازد. این پروژه نشان‌دهنده توانمندی من در طراحی معماری نرم‌افزار، UI/UX، و پیاده‌سازی الگوریتم‌های مهندسی است.
        </p>
    </div>
    """, unsafe_allow_html=True)