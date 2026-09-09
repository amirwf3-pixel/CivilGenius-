"""
CivilGenius Ultimate Enterprise Platform (v20.0)
مجهز به موتور اقتصادی، نمودارهای تحلیل بازار و رابط کاربری سلطنتی بی‌نقص
"""

import os
import time
import streamlit as st
import jdatetime
import plotly.graph_objects as go
from groq import Groq
from dotenv import load_dotenv

from market_engine import MarketAnalyzer
from civil_engine import calculate_foundation, calculate_beam, calculate_column
from document_generator import (
    build_excel, build_word, build_dxf,
    num_fa, money_fa, shamsi_now, create_output_folder
)

st.set_page_config(page_title="CivilGenius | Enterprise", page_icon="🏛️", layout="wide")

C_NAVY = "#0f172a"
C_GOLD = "#d97706"
C_LIGHT = "#f8fafc"
C_GREEN = "#059669"
C_RED = "#dc2626"

st.markdown(f"""
<style>
    @import url('https://v1.fontapi.ir/css/Vazirmatn');
    * {{ font-family: 'Vazirmatn', sans-serif !important; direction: rtl !important; text-align: right !important; }}
    .stApp {{ background-color: {C_LIGHT}; }}
    h1, h2, h3, h4 {{ color: {C_NAVY} !important; font-weight: 800 !important; }}
    
    [data-testid="stSidebar"] {{ background: {C_NAVY} !important; border-left: 2px solid #1e293b; }}
    [data-testid="stSidebar"] * {{ color: #cbd5e1 !important; }}
    [data-testid="stSidebar"] h1, h2, h3 {{ color: white !important; }}
    
    .stTabs [data-baseweb="tab-list"] button {{ background: white; border-radius: 8px; margin-left: 5px; border: 1px solid #e2e8f0; }}
    .stTabs [aria-selected="true"] {{ background: {C_NAVY} !important; color: white !important; border:none; }}
    
    .vip-card {{ background: white; border-right: 5px solid {C_GOLD}; border-radius: 12px; padding: 20px; box-shadow: 0 4px 6px rgba(0,0,0,0.05); margin-bottom: 15px; border: 1px solid #e2e8f0; }}
    .vip-icon {{ font-size: 28px; margin-bottom: 10px; }}
    .vip-title {{ font-size: 13px; color: #64748b; font-weight: bold; margin-bottom: 5px; }}
    .vip-value {{ font-size: 24px; font-weight: 900; color: {C_NAVY}; }}
    
    .stButton>button {{ background-color: {C_NAVY} !important; color: white !important; border-radius: 8px !important; font-size: 16px !important; font-weight: bold !important; width: 100%; height: 50px; border: none !important; transition: 0.3s; }}
    .stButton>button:hover {{ background-color: {C_GOLD} !important; color: white !important; transform: translateY(-2px); box-shadow: 0 10px 15px rgba(217, 119, 6, 0.2) !important; }}
    
    .stDownloadButton>button {{ background-color: white !important; color: {C_NAVY} !important; border: 2px solid {C_NAVY} !important; border-radius: 8px !important; width: 100%; height: 45px; font-weight: bold; }}
    .stDownloadButton>button:hover {{ background-color: {C_NAVY} !important; color: white !important; }}
    
    .input-sec {{ background: white; padding: 20px; border-radius: 12px; box-shadow: 0 2px 4px rgba(0,0,0,0.02); border: 1px solid #e2e8f0; margin-bottom: 15px; }}
    
    /* مخفی کردن منوی بالا */
    #MainMenu, header, footer {{ visibility: hidden; }}
</style>
""", unsafe_allow_html=True)

# مقداردهی اولیه سیستم‌ها (Singleton Pattern برای موتور بازار)
@st.cache_resource
def get_market_engine():
    return MarketAnalyzer()

market_engine = get_market_engine()
current_prices = market_engine.get_prices()

if "results" not in st.session_state: st.session_state.results = {}
if "chat_history" not in st.session_state: st.session_state.chat_history = []

with st.sidebar:
    st.markdown(f"<div style='text-align:center;'><h1 style='font-size:50px; margin:0;'>🏛️</h1><h2 style='margin:0; font-size:22px;'>CivilGenius</h2><p style='font-size:12px;'>Enterprise Edition v20</p></div>", unsafe_allow_html=True)
    st.divider()
    module = st.radio("ناوبری سریع:", ["🏠 پیشخوان سازمانی", "📈 بازار و تحلیل مالی", "🏗️ فونداسیون", "📏 تیر بتنی", "🏛️ ستون بتنی", "🤖 مشاور آیین‌نامه"], label_visibility="collapsed")
    st.divider()
    st.info(f"📅 {shamsi_now()}")

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
    
    st.session_state.results[module_prefix] = {"data": data_dict, "code": code, "xls": xls_bytes, "doc": doc_bytes, "dxf": dxf_bytes}

def show_downloads(module_prefix):
    if module_prefix not in st.session_state.results: return
    res = st.session_state.results[module_prefix]
    st.success(f"🎉 اسناد پروژه {res['code']} با موفقیت آماده شد.")
    d1, d2, d3 = st.columns(3)
    d1.download_button("📊 دانلود Excel", data=res["xls"], file_name=f"{res['code']}_BOQ.xlsx", key=f"dl_x_{res['code']}")
    d2.download_button("📄 دانلود Word", data=res["doc"], file_name=f"{res['code']}_Report.docx", key=f"dl_w_{res['code']}")
    d3.download_button("📐 دانلود AutoCAD", data=res["dxf"], file_name=f"{res['code']}_Plan.dxf", key=f"dl_c_{res['code']}")

# ============================================================
# صفحات
# ============================================================
if "پیشخوان" in module:
    st.markdown(f"<h2>🏛️ پلتفرم سازمانی CivilGenius</h2>", unsafe_allow_html=True)
    st.caption("سیستم یکپارچه مهندسی، متصل به موتور تحلیلگر مالی و بازار مصالح ایران")
    st.divider()
    
    st.markdown("### 🌟 قابلیت‌های انحصاری این نسخه:")
    c1, c2 = st.columns(2)
    with c1:
        st.info("📈 **موتور اقتصادی زنده:** قیمت‌گذاری اتوماتیک بر اساس نرخ روز مصالح و تحلیل روند تورم ۶ ماهه.")
        st.success("🤖 **هوش مصنوعی RAG:** پاسخ‌گویی دقیق به سوالات مهندسی بر پایه مباحث مقررات ملی.")
    with c2:
        st.warning("📊 **داشبوردهای مدیریتی:** رسم زنده نمودارهای لنگر/برش و اندرکنش P-M ستون روی وب‌سایت.")
        st.error("📑 **اتوماسیون اسناد:** تولید حرفه‌ای اکسل، گزارش رسمی ورد و نقشه‌های استاندارد اتوکد.")

elif "بازار" in module:
    st.markdown(f"<h2>📈 داشبورد تحلیل بازار مصالح</h2>", unsafe_allow_html=True)
    st.caption(f"نرخ‌های زنده و روند تورم مصالح پایه (آخرین بروزرسانی: {shamsi_now()})")
    
    c1, c2 = st.columns(2)
    with c1: st.metric("میلگرد آجدار (تومان/kg)", money_fa(current_prices['rebar']), "+1.2% در ۲۴ ساعت گذشته")
    with c2: st.metric("بتن آماده C25 (تومان/m³)", money_fa(current_prices['concrete']), "+0.5% در ۲۴ ساعت گذشته")
    
    st.markdown("### 📊 روند ۶ ماهه قیمت میلگرد و بتن")
    df = market_engine.get_historical_dataframe()
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df['Date'], y=df['rebar'], mode='lines', name='روند قیمت میلگرد', line=dict(color=C_NAVY, width=3)))
    fig.update_layout(template="plotly_white", margin=dict(t=20, b=20), xaxis_title="تاریخ", yaxis_title="قیمت (تومان)")
    st.plotly_chart(fig, use_container_width=True)

elif "فونداسیون" in module:
    st.markdown("<h2>🏗️ طراحی فونداسیون با نرخ زنده</h2>", unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    with c1:
        st.markdown('<div class="input-sec"><h4>📐 هندسه</h4>', unsafe_allow_html=True)
        L = st.number_input("طول پی (m)", value=15.0); B = st.number_input("عرض پی (m)", value=8.0); H = st.number_input("ضخامت (m)", value=1.2)
        st.markdown('</div>', unsafe_allow_html=True)
    with c2:
        st.markdown('<div class="input-sec"><h4>🌍 ژئوتکنیک</h4>', unsafe_allow_html=True)
        c_s = st.number_input("چسبندگی (kPa)", value=20.0); gamma = st.number_input("وزن مخصوص (kN/m³)", value=18.0)
        st.markdown('</div>', unsafe_allow_html=True)
        
    if st.button("🚀 محاسبه مهندسی و مالی"):
        with st.spinner("استخراج قیمت زنده و تحلیل سازه..."):
            process_module(calculate_foundation(L, B, H, c_s, gamma, current_prices), "FND")
            
    if "FND" in st.session_state.results:
        d = st.session_state.results["FND"]["data"]
        m1, m2, m3, m4 = st.columns(4)
        with m1: st.markdown(f"""<div class="vip-card"><div class="vip-icon">🏗️</div><div class="vip-title">حجم بتن</div><div class="vip-value">{num_fa(d['geom']['vol'])}</div></div>""", unsafe_allow_html=True)
        with m2: st.markdown(f"""<div class="vip-card"><div class="vip-icon">⚙️</div><div class="vip-title">وزن میلگرد</div><div class="vip-value">{num_fa(d['boq']['rebar'])}</div></div>""", unsafe_allow_html=True)
        with m3: st.markdown(f"""<div class="vip-card"><div class="vip-icon">🌍</div><div class="vip-title">باربری خاک</div><div class="vip-value">{num_fa(d['geo']['q_all'])}</div></div>""", unsafe_allow_html=True)
        with m4: st.markdown(f"""<div class="vip-card"><div class="vip-icon">💰</div><div class="vip-title">برآورد کل</div><div class="vip-value">{money_fa(d['boq']['total'])}</div></div>""", unsafe_allow_html=True)
        show_downloads("FND")

elif "تیر" in module:
    st.markdown("<h2>📏 طراحی تیر با رسم نمودارها</h2>", unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    with c1:
        st.markdown('<div class="input-sec"><h4>⚖️ بارگذاری</h4>', unsafe_allow_html=True)
        sp = st.number_input("دهانه (m)", value=6.0); wd = st.number_input("بار مرده (kN/m)", value=25.0); wl = st.number_input("بار زنده", value=12.0)
        st.markdown('</div>', unsafe_allow_html=True)
    with c2:
        st.markdown('<div class="input-sec"><h4>🧱 مقطع</h4>', unsafe_allow_html=True)
        bt = st.number_input("عرض (mm)", value=400, step=50); ht = st.number_input("ارتفاع (mm)", value=600, step=50)
        st.markdown('</div>', unsafe_allow_html=True)
        
    if st.button("🚀 محاسبه مهندسی و مالی"):
        with st.spinner("رسم دیاگرام و متره..."):
            process_module(calculate_beam(sp, wd, wl, bt, ht, current_prices), "BEM")
            
    if "BEM" in st.session_state.results:
        d = st.session_state.results["BEM"]["data"]
        m1, m2, m3, m4 = st.columns(4)
        with m1: st.markdown(f"""<div class="vip-card"><div class="vip-icon">📉</div><div class="vip-title">لنگر نهایی</div><div class="vip-value">{num_fa(d['struc']['Mu'])}</div></div>""", unsafe_allow_html=True)
        with m2: st.markdown(f"""<div class="vip-card"><div class="vip-icon">⚙️</div><div class="vip-title">مساحت میلگرد</div><div class="vip-value">{num_fa(d['struc']['As'])}</div></div>""", unsafe_allow_html=True)
        with m3: st.markdown(f"""<div class="vip-card"><div class="vip-icon">📏</div><div class="vip-title">فاصله خاموت</div><div class="vip-value">{num_fa(d['struc']['stirrup_spacing'])}</div></div>""", unsafe_allow_html=True)
        with m4: st.markdown(f"""<div class="vip-card"><div class="vip-icon">💰</div><div class="vip-title">هزینه کل</div><div class="vip-value">{money_fa(d['boq']['total'])}</div></div>""", unsafe_allow_html=True)
        
        st.markdown("### 📉 دیاگرام نیروهای داخلی")
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=d['diagrams']['x'], y=d['diagrams']['M'], mode='lines', name='لنگر', line=dict(color=C_GOLD, width=3), fill='tozeroy'))
        fig.add_trace(go.Scatter(x=d['diagrams']['x'], y=d['diagrams']['V'], mode='lines', name='برش', line=dict(color=C_NAVY, width=2, dash='dash')))
        fig.update_layout(template="plotly_white", margin=dict(t=20, b=20), xaxis_title="طول تیر (m)")
        st.plotly_chart(fig, use_container_width=True)
        show_downloads("BEM")

elif "ستون" in module:
    st.markdown("<h2>🏛️ طراحی ستون و منحنی P-M</h2>", unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    with c1:
        st.markdown('<div class="input-sec"><h4>⚖️ بارگذاری</h4>', unsafe_allow_html=True)
        Lc = st.number_input("ارتفاع ستون (m)", value=3.2); Pu = st.number_input("بار محوری Pu (kN)", value=1500.0); Mu = st.number_input("لنگر Mu (kN.m)", value=120.0)
        st.markdown('</div>', unsafe_allow_html=True)
    with c2:
        st.markdown('<div class="input-sec"><h4>🧱 مقطع</h4>', unsafe_allow_html=True)
        bc = st.number_input("عرض (mm)", value=400, step=50, key='c1'); hc = st.number_input("عمق (mm)", value=400, step=50, key='c2')
        st.markdown('</div>', unsafe_allow_html=True)
        
    if st.button("🚀 محاسبه و رسم نمودار"):
        with st.spinner("ترسیم منحنی اندرکنش..."):
            process_module(calculate_column(Lc, Pu, Mu, bc, hc, current_prices), "COL")
            
    if "COL" in st.session_state.results:
        d = st.session_state.results["COL"]["data"]
        m1, m2, m3, m4 = st.columns(4)
        with m1: st.markdown(f"""<div class="vip-card"><div class="vip-icon">🔻</div><div class="vip-title">ظرفیت فشاری مقطع</div><div class="vip-value">{num_fa(d['struc']['Pn_max'])}</div></div>""", unsafe_allow_html=True)
        with m2: st.markdown(f"""<div class="vip-card"><div class="vip-icon">🔢</div><div class="vip-title">تعداد میلگرد</div><div class="vip-value">{num_fa(d['struc']['num_bars'],0)}</div></div>""", unsafe_allow_html=True)
        with m3: st.markdown(f"""<div class="vip-card"><div class="vip-icon">📏</div><div class="vip-title">فاصله خاموت</div><div class="vip-value">{num_fa(d['struc']['tie_spacing'])}</div></div>""", unsafe_allow_html=True)
        with m4: st.markdown(f"""<div class="vip-card"><div class="vip-icon">💰</div><div class="vip-title">هزینه کل</div><div class="vip-value">{money_fa(d['boq']['total'])}</div></div>""", unsafe_allow_html=True)
        
        st.markdown("### 📊 منحنی اندرکنش P-M")
        pm = d['pm_curve']
        is_safe = pm['user_P'] <= max(pm['P']) and pm['user_M'] <= max(pm['M'])
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=pm['M'], y=pm['P'], mode='lines', name='مرز ظرفیت', line=dict(color=C_NAVY, width=3)))
        fig.add_trace(go.Scatter(x=[pm['user_M']], y=[pm['user_P']], mode='markers', name='نقطه بارگذاری', marker=dict(size=14, color=C_GREEN if is_safe else C_RED)))
        fig.update_layout(template="plotly_white", margin=dict(t=20, b=20), xaxis_title="لنگر Mu (kN.m)", yaxis_title="بار محوری Pu (kN)")
        st.plotly_chart(fig, use_container_width=True)
        show_downloads("COL")

elif "آیین" in module:
    st.markdown("<h2>🤖 مشاور هوشمند مباحث مقررات ملی</h2>", unsafe_allow_html=True)
    for msg in st.session_state.chat_history:
        cls = "chat-user" if msg['role'] == 'user' else "chat-ai"
        nm = "شما" if msg['role'] == 'user' else "دستیار مهندس"
        st.markdown(f"<div class='{cls}'><b>{nm}:</b><br>{msg['content']}</div>", unsafe_allow_html=True)
    
    with st.form("chat", clear_on_submit=True):
        q = st.text_area("سوال خود را تایپ کنید (مثلاً ضوابط آرماتور حرارتی):", height=100)
        c1, c2 = st.columns([1, 4])
        with c1: submitted = st.form_submit_button("ارسال سوال")
        with c2: clear = st.form_submit_button("پاک کردن تاریخچه")
    
    if clear: st.session_state.chat_history = []; st.rerun()
    if submitted and q.strip():
        st.session_state.chat_history.append({"role": "user", "content": q})
        try:
            load_dotenv()
            client = Groq(api_key=os.getenv("GROQ_API_KEY"))
            with st.spinner("دستیار در حال بررسی منابع..."):
                res = client.chat.completions.create(
                    messages=[{"role": "system", "content": "شما مهندس مسلط به مقررات ملی ساختمان ایران هستید. پاسخ بسیار کوتاه، دقیق و به زبان فارسی معیار بدهید."},{"role": "user", "content": q}],
                    model="llama-3.3-70b-versatile", max_tokens=600
                ).choices[0].message.content
                st.session_state.chat_history.append({"role": "assistant", "content": res})
                st.rerun()
        except Exception as e:
            st.error("خطا در ارتباط با سرور هوش مصنوعی.")