"""
CivilGenius - Native Mobile App Edition (v18.0)
رابط کاربری ۱۰۰٪ بهینه‌شده برای موبایل، تبلت و دسکتاپ (بدون نیاز به سایدبار)
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
# ۱. تنظیمات صفحه
# ============================================================
st.set_page_config(
    page_title="CivilGenius | مهندس عمران هوشمند",
    page_icon="🏗️",
    layout="wide",
    initial_sidebar_state="collapsed" # بسته بودن سایدبار برای تمرکز روی موبایل
)

C_NAVY = "#0A192F"
C_NAVY2 = "#172A45"
C_GOLD = "#D4AF37"
C_LIGHT = "#F4F6F9"
C_GREEN = "#2E7D32"

# ============================================================
# ۲. استایل فوق‌العاده قوی CSS برای اپلیکیشن موبایل
# ============================================================
st.markdown(f"""
<style>
    @import url('https://v1.fontapi.ir/css/Vazirmatn');
    
    * {{ 
        font-family: 'Vazirmatn', sans-serif !important; 
        direction: rtl !important; 
        text-align: right !important;
        box-sizing: border-border-box;
    }}
    
    .stApp {{ background-color: {C_LIGHT}; }}
    
    /* مخفی کردن عناصر اضافی استریم‌لیت */
    #MainMenu, header, footer {{ visibility: hidden; height: 0; }}
    [data-testid="stSidebar"] {{ display: none; }}
    
    /* تنظیم پدینگ اصلی صفحه برای موبایل */
    .main .block-container {{
        padding-top: 1rem !important;
        padding-bottom: 2rem !important;
        padding-left: 0.8rem !important;
        padding-right: 0.8rem !important;
        max-width: 100% !important;
    }}
    
    /* هدر بالای اپلیکیشن */
    .app-header {{
        background: linear-gradient(135deg, {C_NAVY} 0%, {C_NAVY2} 100%);
        padding: 16px 20px;
        border-radius: 14px;
        color: white;
        margin-bottom: 15px;
        box-shadow: 0 8px 20px rgba(10,25,47,0.15);
        border-right: 5px solid {C_GOLD};
        display: flex;
        justify-content: space-between;
        align-items: center;
    }}
    .app-header h1 {{ color: {C_GOLD} !important; margin: 0; font-size: 20px !important; font-weight: 800; }}
    .app-header p {{ color: #B8C5D6; margin: 3px 0 0 0; font-size: 11px; }}
    
    /* ناوبری لمسی بالای صفحه (Top Nav Tabs) */
    .stTabs [data-baseweb="tab-list"] {{
        gap: 6px !important;
        background-color: #E2E8F0;
        padding: 6px;
        border-radius: 12px;
    }}
    .stTabs [data-baseweb="tab"] {{
        height: 44px !important;
        border-radius: 8px !important;
        background-color: transparent !important;
        color: {C_NAVY} !important;
        font-weight: bold !important;
        font-size: 13px !important;
        padding: 0 10px !important;
    }}
    .stTabs [aria-selected="true"] {{
        background-color: {C_NAVY} !important;
        color: {C_GOLD} !important;
        box-shadow: 0 4px 10px rgba(10,25,47,0.2) !important;
    }}
    
    /* کادرهای ورودی داده */
    .input-box {{
        background: white;
        padding: 15px;
        border-radius: 12px;
        box-shadow: 0 3px 12px rgba(0,0,0,0.04);
        border-right: 4px solid {C_GOLD};
        margin-bottom: 12px;
    }}
    .input-box h4 {{ margin: 0 0 10px 0; font-size: 15px !important; color: {C_NAVY} !important; }}
    
    /* کارت‌های نتایج گرافیکی */
    .card-grid {{
        display: grid;
        grid-template-columns: repeat(2, 1fr);
        gap: 10px;
        margin-bottom: 15px;
    }}
    .mobile-card {{
        background: linear-gradient(145deg, {C_NAVY}, {C_NAVY2});
        border-right: 4px solid {C_GOLD};
        border-radius: 10px;
        padding: 12px;
        color: white;
        box-shadow: 0 4px 12px rgba(0,0,0,0.08);
    }}
    .mobile-card .icon {{ font-size: 20px; float: left; }}
    .mobile-card .title {{ font-size: 11px; color: #8892B0; margin-bottom: 4px; }}
    .mobile-card .val {{ font-size: 17px; font-weight: bold; color: {C_GOLD}; }}
    .mobile-card .unit {{ font-size: 11px; color: #E2E8F0; margin-right: 2px; }}
    
    /* دکمه‌ها */
    .stButton>button {{
        background: linear-gradient(135deg, {C_NAVY} 0%, {C_NAVY2} 100%) !important;
        color: {C_GOLD} !important;
        border: 1.5px solid {C_GOLD} !important;
        border-radius: 10px !important;
        font-size: 15px !important;
        font-weight: bold !important;
        width: 100%;
        height: 48px !important;
        margin-top: 5px;
    }}
    .stDownloadButton>button {{
        background: linear-gradient(135deg, {C_GREEN} 0%, #1B5E20 100%) !important;
        color: white !important;
        border: none !important;
        border-radius: 10px !important;
        width: 100%;
        height: 46px !important;
        font-size: 13px !important;
        font-weight: bold;
    }}
    
    /* بنر موفقیت */
    .banner-success {{
        background: linear-gradient(135deg, {C_NAVY}, {C_NAVY2});
        border: 1.5px solid {C_GOLD};
        border-radius: 10px;
        padding: 12px;
        text-align: center;
        color: white;
        margin: 12px 0;
    }}
    .banner-success h4 {{ color: {C_GOLD} !important; margin: 0; font-size: 15px !important; }}

    /* چت‌بات */
    .chat-user {{
        background: {C_NAVY};
        color: white;
        padding: 10px 14px;
        border-radius: 12px 12px 2px 12px;
        margin-bottom: 8px;
        font-size: 13px;
    }}
    .chat-ai {{
        background: white;
        color: {C_NAVY};
        padding: 10px 14px;
        border-radius: 12px 12px 12px 2px;
        border-right: 3.5px solid {C_GOLD};
        margin-bottom: 8px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.04);
        font-size: 13px;
        line-height: 1.7;
    }}
    
    /* اجبار تک‌ستونه شدن تمام المان‌ها در موبایل */
    @media (max-width: 768px) {{
        [data-testid="column"] {{
            width: 100% !important;
            flex: 1 1 100% !important;
            min-width: 100% !important;
            margin-bottom: 5px;
        }}
    }}
</style>
""", unsafe_allow_html=True)

# ============================================================
# ۳. مدیریت حافظه
# ============================================================
if "results" not in st.session_state:
    st.session_state.results = {}
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# ============================================================
# ۴. هدر ثابت بالای اپلیکیشن
# ============================================================
st.markdown(f"""
<div class="app-header">
    <div>
        <h1>🏛️ CivilGenius</h1>
        <p>پلتفرم هوشمند محاسبات مهندسی عمران</p>
    </div>
    <div style="text-align:left;">
        <span style="background:rgba(212,175,55,0.2); color:{C_GOLD}; padding:4px 8px; border-radius:6px; font-size:11px; font-weight:bold;">
            {shamsi_now().split(' - ')[0]}
        </span>
    </div>
</div>
""", unsafe_allow_html=True)

# ============================================================
# ۵. ناوبری لمسی درشت (Top Mobile Navigation)
# ============================================================
tab_home, tab_fnd, tab_bm, tab_col, tab_chat, tab_about = st.tabs([
    "🏠 خانه", "🏗️ پی", "📏 تیر", "🏛️ ستون", "🤖 چت", "👤 من"
])

# ============================================================
# توابع پردازش و دانلود
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
        "xls": xls_bytes,
        "doc": doc_bytes,
        "dxf": dxf_bytes
    }

def render_downloads(module_prefix):
    if module_prefix not in st.session_state.results:
        return
    res = st.session_state.results[module_prefix]
    
    st.markdown(f"""
    <div class="banner-success">
        <h4>🎉 محاسبات انجام شد | کد: {res['code']}</h4>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("<h4 style='font-size:14px; margin-bottom:8px;'>📥 دانلود اسناد مهندسی:</h4>", unsafe_allow_html=True)
    d1, d2, d3 = st.columns(3)
    d1.download_button("📊 اکسل Excel", data=res["xls"], file_name=f"{res['code']}_BOQ.xlsx", key=f"x_{res['code']}")
    d2.download_button("📄 گزارش Word", data=res["doc"], file_name=f"{res['code']}_Report.docx", key=f"d_{res['code']}")
    d3.download_button("📐 نقشه CAD", data=res["dxf"], file_name=f"{res['code']}_Plan.dxf", key=f"c_{res['code']}")

# ============================================================
# تب ۱: خانه
# ============================================================
with tab_home:
    st.markdown("""
    <div class="input-box">
        <h4>👋 به CivilGenius خوش آمدید</h4>
        <p style="font-size:13px; color:#555; line-height:1.7; margin:0;">
        سامانه هوشمند محاسبات سازه‌ای، ژئوتکنیک و تولید خودکار مدارک مهندسی (اکسل، ورد و اتوکد).
        از تب‌های بالای صفحه، المان مورد نظر خود را برای طراحی انتخاب کنید.
        </p>
    </div>
    """, unsafe_allow_html=True)

# ============================================================
# تب ۲: فونداسیون
# ============================================================
with tab_fnd:
    st.markdown('<div class="input-box"><h4>📐 هندسه فونداسیون</h4></div>', unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    with c1:
        L = st.number_input("طول پی (متر)", value=15.0, step=1.0, key="fnd_L")
        B = st.number_input("عرض پی (متر)", value=8.0, step=1.0, key="fnd_B")
    with c2:
        H = st.number_input("ضخامت پی (متر)", value=1.2, step=0.1, key="fnd_H")
    
    st.markdown('<div class="input-box"><h4>🌍 مشخصات خاک بستر</h4></div>', unsafe_allow_html=True)
    c3, c4 = st.columns(2)
    with c3:
        c_soil = st.number_input("چسبندگی خاک (kPa)", value=20.0, step=1.0, key="fnd_c")
    with c4:
        gamma = st.number_input("وزن مخصوص (kN/m³)", value=18.0, step=0.5, key="fnd_g")
        
    if st.button("🚀 محاسبه و تولید مدارک پی", key="btn_fnd"):
        with st.spinner("در حال محاسبه..."):
            process_module(calculate_foundation(L, B, H, c_soil, gamma), "FND")
            
    if "FND" in st.session_state.results:
        render_downloads("FND")
        data = st.session_state.results["FND"]["data"]
        
        st.markdown(f"""
        <div class="card-grid">
            <div class="mobile-card">
                <span class="icon">🏗️</span>
                <div class="title">حجم بتن</div>
                <div class="val">{num_fa(data['geom']['vol'])}<span class="unit">m³</span></div>
            </div>
            <div class="mobile-card">
                <span class="icon">⚙️</span>
                <div class="title">وزن میلگرد</div>
                <div class="val">{num_fa(data['boq']['rebar'])}<span class="unit">kg</span></div>
            </div>
            <div class="mobile-card">
                <span class="icon">🌍</span>
                <div class="title">ظرفیت خاک</div>
                <div class="val">{num_fa(data['geo']['q_all'])}<span class="unit">kPa</span></div>
            </div>
            <div class="mobile-card">
                <span class="icon">💰</span>
                <div class="title">برآورد کل</div>
                <div class="val" style="font-size:14px;">{money_fa(data['boq']['total'])}<span class="unit">تومان</span></div>
            </div>
        </div>
        """, unsafe_allow_html=True)

# ============================================================
# تب ۳: تیر بتنی
# ============================================================
with tab_bm:
    st.markdown('<div class="input-box"><h4>📐 دهانه و بارگذاری تیر</h4></div>', unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    with c1:
        span = st.number_input("طول دهانه (متر)", value=6.0, step=0.5, key="bm_s")
        wd = st.number_input("بار مرده (kN/m)", value=25.0, step=1.0, key="bm_wd")
    with c2:
        wl = st.number_input("بار زنده (kN/m)", value=12.0, step=1.0, key="bm_wl")
        
    st.markdown('<div class="input-box"><h4>🧱 ابعاد مقطع (میلی‌متر)</h4></div>', unsafe_allow_html=True)
    c3, c4 = st.columns(2)
    with c3:
        bt = st.number_input("عرض تیر b (mm)", value=400, step=50, key="bm_b")
    with c4:
        ht = st.number_input("ارتفاع تیر h (mm)", value=600, step=50, key="bm_h")
        
    if st.button("🚀 محاسبه و طراحی تیر", key="btn_bm"):
        with st.spinner("در حال محاسبه..."):
            process_module(calculate_beam(span, wd, wl, bt, ht), "BEM")
            
    if "BEM" in st.session_state.results:
        render_downloads("BEM")
        data = st.session_state.results["BEM"]["data"]
        
        st.markdown(f"""
        <div class="card-grid">
            <div class="mobile-card">
                <span class="icon">📏</span>
                <div class="title">لنگر نهایی Mu</div>
                <div class="val">{num_fa(data['struc']['Mu'])}<span class="unit">kN.m</span></div>
            </div>
            <div class="mobile-card">
                <span class="icon">⚙️</span>
                <div class="title">آرماتور خمشی</div>
                <div class="val">{num_fa(data['struc']['As'])}<span class="unit">mm²</span></div>
            </div>
            <div class="mobile-card">
                <span class="icon">⛓️</span>
                <div class="title">فاصله خاموت</div>
                <div class="val">{num_fa(data['struc']['stirrup_spacing'])}<span class="unit">cm</span></div>
            </div>
            <div class="mobile-card">
                <span class="icon">💰</span>
                <div class="title">برآورد هزینه</div>
                <div class="val" style="font-size:14px;">{money_fa(data['boq']['total'])}<span class="unit">تومان</span></div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # نمودار مخصوص موبایل
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=data['diagrams']['x'], y=data['diagrams']['M'], mode='lines', name='لنگر (kN.m)', line=dict(color=C_GOLD, width=3)))
        fig.add_trace(go.Scatter(x=data['diagrams']['x'], y=data['diagrams']['V'], mode='lines', name='برش (kN)', line=dict(color=C_NAVY, width=2, dash='dash')))
        fig.update_layout(
            margin=dict(l=5, r=5, t=25, b=5),
            xaxis_title="طول (متر)",
            template="plotly_white",
            height=280,
            hovermode='x unified',
            legend=dict(orientation="h", y=1.2, font=dict(size=10))
        )
        st.plotly_chart(fig, use_container_width=True, config={'responsive': True})

# ============================================================
# تب ۴: ستون بتنی
# ============================================================
with tab_col:
    st.markdown('<div class="input-box"><h4>📐 بارگذاری ستون</h4></div>', unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    with c1:
        L_col = st.number_input("ارتفاع ستون (متر)", value=3.2, step=0.1, key="col_L")
        Pu = st.number_input("بار محوری Pu (kN)", value=1500.0, step=50.0, key="col_P")
    with c2:
        Mu_col = st.number_input("لنگر Mu (kN.m)", value=120.0, step=10.0, key="col_M")
        
    st.markdown('<div class="input-box"><h4>🧱 ابعاد ستون (میلی‌متر)</h4></div>', unsafe_allow_html=True)
    c3, c4 = st.columns(2)
    with c3:
        bc = st.number_input("عرض b (mm)", value=400, step=50, key="col_b")
    with c4:
        hc = st.number_input("عمق h (mm)", value=400, step=50, key="col_h")
        
    if st.button("🚀 محاسبه و طراحی ستون", key="btn_col"):
        with st.spinner("در حال محاسبه..."):
            process_module(calculate_column(L_col, Pu, Mu_col, bc, hc), "COL")
            
    if "COL" in st.session_state.results:
        render_downloads("COL")
        data = st.session_state.results["COL"]["data"]
        
        st.markdown(f"""
        <div class="card-grid">
            <div class="mobile-card">
                <span class="icon">🏛️</span>
                <div class="title">ظرفیت فشاری Pn</div>
                <div class="val">{num_fa(data['struc']['Pn_max'])}<span class="unit">kN</span></div>
            </div>
            <div class="mobile-card">
                <span class="icon">⚙️</span>
                <div class="title">تعداد میلگرد</div>
                <div class="val">{num_fa(data['struc']['num_bars'], 0)}<span class="unit">عدد</span></div>
            </div>
            <div class="mobile-card">
                <span class="icon">⛓️</span>
                <div class="title">فاصله خاموت</div>
                <div class="val">{num_fa(data['struc']['tie_spacing'])}<span class="unit">cm</span></div>
            </div>
            <div class="mobile-card">
                <span class="icon">💰</span>
                <div class="title">برآورد هزینه</div>
                <div class="val" style="font-size:14px;">{money_fa(data['boq']['total'])}<span class="unit">تومان</span></div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # منحنی P-M مخصوص موبایل
        pm = data['pm_curve']
        is_safe = pm['user_P'] <= max(pm['P']) and pm['user_M'] <= max(pm['M'])
        
        fig_pm = go.Figure()
        fig_pm.add_trace(go.Scatter(x=pm['M'], y=pm['P'], mode='lines', name='مرز ظرفیت', line=dict(color=C_NAVY, width=3)))
        fig_pm.add_trace(go.Scatter(x=[pm['user_M']], y=[pm['user_P']], mode='markers', name='نقطه بار', marker=dict(size=12, color=C_GOLD, symbol='diamond')))
        fig_pm.update_layout(
            margin=dict(l=5, r=5, t=25, b=5),
            xaxis=dict(title="لنگر Mu"),
            yaxis=dict(title="بار Pu"),
            template="plotly_white",
            height=300,
            legend=dict(orientation="h", y=1.2, font=dict(size=10))
        )
        st.plotly_chart(fig_pm, use_container_width=True, config={'responsive': True})

# ============================================================
# تب ۵: چت آیین‌نامه
# ============================================================
with tab_chat:
    st.markdown('<div class="input-box"><h4>🤖 دستیار آیین‌نامه مقررات ملی</h4></div>', unsafe_allow_html=True)
    
    for msg in st.session_state.chat_history:
        if msg['role'] == 'user':
            st.markdown(f"<div class='chat-user'><b>👤 شما:</b> {msg['content']}</div>", unsafe_allow_html=True)
        else:
            st.markdown(f"<div class='chat-ai'><b>🤖 AI:</b><br>{msg['content']}</div>", unsafe_allow_html=True)
    
    with st.form("chat_form", clear_on_submit=True):
        q = st.text_input("❓ سوال آیین‌نامه‌ای خود را بنویسید:", max_chars=300, placeholder="مثال: حداقل کاور بتن پی چقدر است؟")
        c1, c2 = st.columns([1, 1])
        with c1: ask = st.form_submit_button("📤 ارسال سوال")
        with c2: clear = st.form_submit_button("🗑️ پاک کردن چت")
    
    if clear:
        st.session_state.chat_history = []
        st.rerun()
    
    if ask and q.strip():
        st.session_state.chat_history.append({"role": "user", "content": q})
        try:
            load_dotenv()
            api_key = os.getenv("GROQ_API_KEY")
            if not api_key:
                st.error("❌ کلید API یافت نشد.")
            else:
                client = Groq(api_key=api_key)
                with st.spinner("در حال پاسخگویی..."):
                    res = client.chat.completions.create(
                        messages=[
                            {"role": "system", "content": "شما مهندس عمران ارشد مسلط به مقررات ملی ساختمان ایران هستید. پاسخ‌ها را بسیار کوتاه، کاربردی و فارسی بنویسید."},
                            {"role": "user", "content": q}
                        ],
                        model="llama-3.3-70b-versatile",
                        max_tokens=500
                    ).choices[0].message.content
                    st.session_state.chat_history.append({"role": "assistant", "content": res})
                    st.rerun()
        except Exception as e:
            st.error(f"❌ خطا: {str(e)[:100]}")

# ============================================================
# تب ۶: درباره من (رزومه موبایل)
# ============================================================
with tab_about:
    st.markdown(f"""
    <div style='background:linear-gradient(135deg, {C_NAVY}, {C_NAVY2}); border-radius:12px; padding:20px; text-align:center; color:white; margin-bottom:15px;'>
        <div style='font-size:50px;'>👨‍💻</div>
        <h3 style='color:{C_GOLD} !important; margin:5px 0;'>مهندس عمران</h3>
        <p style='color:#8892B0; font-size:12px; margin:0;'>توسعه‌دهنده نرم‌افزار مهندسی & AI</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <div class='input-box'>
        <h4>💼 درباره این پروژه</h4>
        <p style='color:#444; font-size:12px; line-height:1.7; margin:0;'>
        CivilGenius یک سامانه هوشمند برای اتوماسیون محاسبات دفتر فنی مهندسی عمران است. این پروژه توانایی تلفیق دانش سازه و ژئوتکنیک با برنامه‌نویسی پایتون، هوش مصنوعی و تولید خودکار فایل‌های اکسل، ورد و نقشه‌های اتوکد را به نمایش می‌گذارد.
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <div class='input-box'>
        <h4>🛠️ مهارت‌های به کار رفته</h4>
        <div>
            <span class='skill-badge'>Python</span>
            <span class='skill-badge'>Streamlit Mobile</span>
            <span class='skill-badge'>AI / Groq</span>
            <span class='skill-badge'>AutoCAD Automation</span>
            <span class='skill-badge'>Excel / Word API</span>
            <span class='skill-badge'>Structural Design</span>
        </div>
    </div>
    """, unsafe_allow_html=True)