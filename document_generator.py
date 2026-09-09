"""
Document Generator Module (v20.0 Enterprise)
"""
import os
import jdatetime
from openpyxl import Workbook
from openpyxl.styles import Font, Alignment, PatternFill, Border, Side
from docx import Document
from docx.shared import Pt, RGBColor, Cm
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_LINE_SPACING
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml.ns import qn
from docx.oxml import OxmlElement
import ezdxf
from ezdxf import units

try:
    import arabic_reshaper
    from bidi.algorithm import get_display
    FARSI_OK = True
except Exception:
    FARSI_OK = False

C_NAVY, C_GOLD, C_GRAY = "0A192F", "D4AF37", "F0F4F8"

def shamsi_now():
    now = jdatetime.datetime.now()
    return f"{now.day} {['فروردین','اردیبهشت','خرداد','تیر','مرداد','شهریور','مهر','آبان','آذر','دی','بهمن','اسفند'][now.month-1]} {now.year}"

def num_fa(n, d=2):
    s = f"{n:,.{d}f}".rstrip('0').rstrip('.') if isinstance(n, float) and '.' in f"{n:,.{d}f}" else f"{n:,}"
    return s.translate(str.maketrans("0123456789", "۰۱۲۳۴۵۶۷۸۹"))

def money_fa(n):
    return f"{int(round(n)):,}".translate(str.maketrans("0123456789", "۰۱۲۳۴۵۶۷۸۹"))

def fix_cad(text):
    if not FARSI_OK or not text: return text
    try: return get_display(arabic_reshaper.reshape(text))[::-1]
    except Exception: return text

def create_output_folder(module_code, project_code):
    base = os.path.join(os.getcwd(), "outputs")
    os.makedirs(base, exist_ok=True)
    project_dir = os.path.join(base, project_code)
    os.makedirs(project_dir, exist_ok=True)
    return project_dir

def build_excel(data, path, code):
    wb = Workbook()
    ws = wb.active
    ws.title = "داشبورد مهندسی"
    ws.sheet_view.rightToLeft = True
    ws.sheet_view.showGridLines = False

    def style_c(r, c, val, b=False, bg=None, clr="000000", al="center"):
        cell = ws.cell(row=r, column=c, value=val)
        cell.font = Font(name="Tahoma", size=11, bold=b, color=clr)
        cell.alignment = Alignment(horizontal=al, vertical="center", wrap_text=True)
        if bg: cell.fill = PatternFill("solid", fgColor=bg)
        s = Side(style="thin", color="E2E8F0")
        cell.border = Border(left=s, right=s, top=s, bottom=s)
        return cell

    title = {"foundation": "فونداسیون گسترده", "beam": "تیر بتن آرمه", "column": "ستون بتن آرمه"}[data["type"]]
    ws.merge_cells("B2:H3")
    style_c(2, 2, f"🏛️ دفترچه محاسبات و متره {title} | کد: {code}", b=True, bg=C_NAVY, clr="FFFFFF")

    ws.merge_cells("B4:H4")
    style_c(4, 2, f"⚠️ مبنای قیمت‌گذاری: نرخ زنده بازار در تاریخ {shamsi_now()}", b=True, bg=C_GOLD, clr="FFFFFF")

    r = 6
    for i, (icode, desc, unit, qty, price) in enumerate(data['boq']['items'], 1):
        if i == 1:
            for j, h in enumerate(["ردیف", "کد", "شرح عملیات اجرایی", "واحد", "مقدار", "بهای روز (تومان)", "بهای کل (تومان)"]):
                style_c(5, j+2, h, b=True, bg=C_NAVY, clr="FFFFFF")
        bg = C_GRAY if i % 2 == 0 else "FFFFFF"
        style_c(r, 2, num_fa(i, 0), bg=bg)
        style_c(r, 3, icode, bg=bg, b=True)
        style_c(r, 4, desc, bg=bg, al="right")
        style_c(r, 5, unit, bg=bg)
        style_c(r, 6, qty, bg=bg).number_format = "#,##0.0"
        style_c(r, 7, price, bg=bg).number_format = "#,##0"
        style_c(r, 8, f"=F{r}*G{r}", bg=bg, b=True).number_format = "#,##0"
        r += 1

    ws.merge_cells(f"B{r}:G{r}")
    style_c(r, 2, "جمع کل برآورد هزینه (تومان)", b=True, bg=C_NAVY, clr="FFFFFF")
    style_c(r, 8, f"=SUM(H6:H{r-1})", b=True, bg=C_NAVY, clr="FFFFFF").number_format = "#,##0"

    for col, w in zip("BCDEFGH", [6, 12, 45, 10, 15, 20, 22]): ws.column_dimensions[col].width = w
    wb.save(path)

def build_word(data, path, code):
    doc = Document()
    for s in doc.sections: s.left_margin = s.right_margin = Cm(2.5)

    def set_rtl(p):
        p._p.get_or_add_pPr().append(OxmlElement("w:bidi"))
        p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY

    def add_run(p, text, size=12, b=False, color="000000"):
        run = p.add_run(text)
        run.font.name = "B Nazanin"
        run._element.rPr.rFonts.set(qn("w:cs"), "B Nazanin")
        run._element.rPr.rFonts.set(qn("w:ascii"), "B Nazanin")
        rtl = OxmlElement("w:rtl")
        rtl.set(qn("w:val"), "1")
        run._element.rPr.append(rtl)
        run.font.size, run.font.bold, run.font.color.rgb = Pt(size), b, RGBColor.from_string(color)
        return run

    doc.add_paragraph().paragraph_format.space_before = Pt(100)
    tbl = doc.add_table(rows=1, cols=1)
    tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    shd = OxmlElement("w:shd")
    shd.set(qn("w:val"), "clear")
    shd.set(qn("w:fill"), C_NAVY)
    tbl.rows[0].cells[0]._tc.get_or_add_tcPr().append(shd)

    p = tbl.rows[0].cells[0].paragraphs[0]
    set_rtl(p)
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    t_name = {"foundation": "فونداسیون", "beam": "تیر بتنی", "column": "ستون بتنی"}[data["type"]]
    add_run(p, f"گزارش فنی و برآورد مالی {t_name}", size=24, b=True, color="FFFFFF")

    p2 = doc.add_paragraph()
    set_rtl(p2)
    p2.alignment = WD_ALIGN_PARAGRAPH.CENTER
    add_run(p2, f"\nکد پروژه: {code}  |  تاریخ استعلام بازار: {shamsi_now()}", size=14, color=C_GOLD)
    doc.add_page_break()

    def add_h(txt):
        p = doc.add_paragraph()
        set_rtl(p)
        p.alignment = WD_ALIGN_PARAGRAPH.RIGHT
        add_run(p, txt, 15, True, C_NAVY)

    def add_p(txt):
        p = doc.add_paragraph()
        set_rtl(p)
        add_run(p, txt, 12)
        p.paragraph_format.line_spacing_rule = WD_LINE_SPACING.ONE_POINT_FIVE

    add_h("۱. ارزیابی مهندسی پروژه")
    add_p(f"طراحی این {t_name} بر اساس آخرین استانداردهای مقررات ملی ساختمان و شرایط ژئوتکنیکی / سازه‌ای وارد شده، با موفقیت به اتمام رسید. مقاطع بتنی و آرماتورهای طولی و عرضی جهت تامین حاشیه ایمنی لازم طراحی گردیدند.")

    add_h("۲. تحلیل مالی مبتنی بر بازار زنده")
    add_p(f"وجه تمایز این گزارش، برآورد مالی بر پایه نرخ روز مصالح ساختمانی در تاریخ صدور این سند است. "
          f"هزینه کل احداث این بخش معادل {money_fa(data['boq']['total'])} تومان تخمین زده شده است که در فایل اکسل پیوست، آنالیز دقیق بهای مصالح و عملیات اجرایی تفکیک گردیده است.")

    doc.save(path)

def build_dxf(data, path, code):
    doc = ezdxf.new("R2010", setup=True)
    doc.units = units.M
    doc.styles.add('FA_TXT', font='arial.ttf')
    msp = doc.modelspace()
    for n, c in [("MAIN", 5), ("HATCH", 8), ("REBAR", 1), ("DIM", 3), ("TEXT", 7), ("BORDER", 6)]:
        doc.layers.add(n, color=c)

    def cad_txt(txt, x, y, sz=0.4, clr=7):
        msp.add_text(fix_cad(txt), dxfattribs={"style": "FA_TXT", "layer": "TEXT", "height": sz, "color": clr}).set_placement((x, y))

    ox, oy = 5.0, 5.0
    if data["type"] == "foundation":
        L, B, H = data['geom']['L'], data['geom']['B'], data['geom']['H']
        msp.add_lwpolyline([(ox, oy), (ox+L, oy), (ox+L, oy+B), (ox, oy+B), (ox, oy)], dxfattribs={"layer": "MAIN", "lineweight": 40})
        cad_txt(f"پلان فونداسیون | ابعاد: {num_fa(L)}x{num_fa(B)}m", ox, oy+B+1.0, 0.5, 5)
        doc.header["$EXTMAX"] = (ox+L+5, oy+B+5, 0)
    elif data["type"] == "beam":
        span, h = data['inputs']['span'], data['inputs']['h']/1000.0
        msp.add_lwpolyline([(ox, oy), (ox+span, oy), (ox+span, oy+h), (ox, oy+h), (ox, oy)], dxfattribs={"layer": "MAIN", "lineweight": 40})
        cad_txt(f"نمای طولی تیر | دهانه: {num_fa(span)}m", ox, oy+h+1.0, 0.5, 5)
        doc.header["$EXTMAX"] = (ox+span+5, oy+h+5, 0)
    elif data["type"] == "column":
        L_col, b = data['inputs']['L_col'], data['inputs']['b']/1000.0
        msp.add_lwpolyline([(ox, oy), (ox+b, oy), (ox+b, oy+L_col), (ox, oy+L_col), (ox, oy)], dxfattribs={"layer": "MAIN", "lineweight": 40})
        cad_txt(f"نمای ارتفاعی ستون | ارتفاع: {num_fa(L_col)}m", ox, oy+L_col+1.0, 0.5, 5)
        doc.header["$EXTMAX"] = (ox+b+5, oy+L_col+5, 0)

    cad_txt(f"CivilGenius - کد: {code}", ox, oy-3.0, 0.35, 6)
    doc.saveas(path)