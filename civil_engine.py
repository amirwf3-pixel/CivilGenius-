"""
Civil Engine Module (v20.0 Enterprise)
موتور محاسبات یکپارچه با سیستم قیمت‌گذاری زنده بازار
"""
import math

def calculate_foundation(L, B, H, c, gamma, market_prices):
    Df = max(1.0, H)
    Nc, Nq, Ng = 30.14, 18.40, 15.67
    q_ult = (c * Nc) + (gamma * Df * Nq) + (0.5 * gamma * B * Ng)
    q_all = q_ult / 3.0

    fc, col_size = 25, 0.4
    d = max(0.1, H - 0.1)
    vc_punching = 0.33 * math.sqrt(fc) * (4 * (col_size + d)) * d * 1000

    area, vol = L * B, L * B * H
    rebar_kg = vol * 95

    # تزریق قیمت‌های زنده از بازار به جای اعداد ثابت
    p = market_prices
    items = [
        ("EX-01", "خاکبرداری و تسطیح بستر پی", "m³", area * (H + 0.3), p['excavation']),
        ("CO-01", "بتن مگر (ضخامت ۱۰ سانتی‌متر)", "m²", area, p['lean_conc']),
        ("FW-01", "قالب‌بندی فلزی محیطی فونداسیون", "m²", 2 * (L + B) * H, p['formwork']),
        ("RB-01", "آرماتوربندی آجدار (نرخ روز)", "kg", rebar_kg, p['rebar']),
        ("CO-02", "بتن‌ریزی سازه‌ای C25 (نرخ روز)", "m³", vol, p['concrete']),
    ]
    return {
        "type": "foundation", "geom": {"L": L, "B": B, "H": H, "area": area, "vol": vol},
        "geo": {"c": c, "gamma": gamma, "q_all": q_all, "q_ult": q_ult},
        "struc": {"vc_punch": vc_punching},
        "boq": {"rebar": rebar_kg, "items": items, "total": sum(qty * pr for _, _, _, qty, pr in items)}
    }

def calculate_beam(span, wd, wl, b_mm, h_mm, market_prices):
    wu = (1.2 * wd) + (1.6 * wl)
    Mu = (wu * (span ** 2)) / 8.0
    Vu = (wu * span) / 2.0

    fc, fy, b_m, d_mm = 25, 400, b_mm / 1000.0, h_mm - 50
    Rn = (Mu * 1e6) / (0.9 * b_mm * (d_mm ** 2))
    m = fy / (0.85 * fc)
    rho = (1 / m) * (1 - math.sqrt(max(0, 1 - (2 * m * Rn / fy))))
    As_mm2 = max(rho, max(1.4 / fy, (0.25 * math.sqrt(fc)) / fy)) * b_mm * d_mm
    
    num_bars = max(2, math.ceil(As_mm2 / 314.0))
    stirrup_spacing = min(20, round((d_mm / 2) / 10))

    x_pts = [i * (span / 50.0) for i in range(51)]
    M_pts = [((wu * x / 2.0) * (span - x)) for x in x_pts]
    V_pts = [(wu * (span / 2.0 - x)) for x in x_pts]

    vol = b_m * (h_mm / 1000.0) * span
    formwork = (2 * (h_mm / 1000.0) + b_m) * span
    total_rebar = (num_bars * 2.47 * span * 2) + (math.ceil(span * 100 / stirrup_spacing) * 2 * (b_m + h_mm/1000) * 0.395)

    p = market_prices
    items = [
        ("FW-02", "قالب‌بندی زیرین و جانبی تیر", "m²", formwork, p['formwork']),
        ("RB-02", "آرماتوربندی طولی و خاموت تیر", "kg", total_rebar, p['rebar']),
        ("CO-03", "بتن‌ریزی سازه‌ای C25 تیر", "m³", vol, p['concrete']),
    ]
    return {
        "type": "beam", "inputs": {"span": span, "b": b_mm, "h": h_mm, "wd": wd, "wl": wl},
        "struc": {"wu": wu, "Mu": Mu, "Vu": Vu, "As": As_mm2, "num_bars": num_bars, "stirrup_spacing": stirrup_spacing},
        "diagrams": {"x": x_pts, "M": M_pts, "V": V_pts},
        "geom": {"vol": vol, "formwork": formwork},
        "boq": {"rebar": total_rebar, "items": items, "total": sum(q * pr for _, _, _, q, pr in items)}
    }

def calculate_column(L_col, Pu, Mu, b_mm, h_mm, market_prices):
    fc, fy = 25, 400
    b_m, h_m = b_mm / 1000.0, h_mm / 1000.0
    Ag = b_mm * h_mm

    As_req = max(0.01 * Ag, (Pu * 1000) / (0.80 * 0.65 * fy))
    num_bars = max(4, math.ceil(As_req / 314.0))
    if num_bars % 2 != 0: num_bars += 1
    tie_spacing = min(20, round(min(b_mm, h_mm) / 20.0))

    Po = (0.85 * fc * (Ag - As_req) + fy * As_req) / 1000.0
    P_max = 0.80 * Po
    M_max = (Po * h_mm * 0.15) / 1000.0
    
    pm_P, pm_M = [], []
    for i in range(16):
        t = i / 15.0
        P = P_max * (1 - t * 0.95)
        M = M_max * (t / 0.4) * 0.7 if t < 0.4 else M_max * (0.7 + 0.3 * ((1 - t) / 0.6))
        pm_P.append(P); pm_M.append(M)

    vol = b_m * h_m * L_col
    formwork = 2 * (b_m + h_m) * L_col
    rebar_kg = (num_bars * 2.47 * L_col) + (math.ceil(L_col * 100 / tie_spacing) * 2 * (b_m + h_m) * 0.617)

    p = market_prices
    items = [
        ("FW-03", "قالب‌بندی سطوح قائم ستون", "m²", formwork, p['formwork']),
        ("RB-03", "آرماتور طولی و خاموت ستون", "kg", rebar_kg, p['rebar']),
        ("CO-04", "بتن‌ریزی سازه‌ای C25 ستون", "m³", vol, p['concrete']),
    ]
    return {
        "type": "column", "inputs": {"L_col": L_col, "Pu": Pu, "Mu": Mu, "b": b_mm, "h": h_mm},
        "struc": {"Pn_max": P_max, "As": As_req, "num_bars": num_bars, "tie_spacing": tie_spacing},
        "pm_curve": {"P": pm_P, "M": pm_M, "user_P": Pu, "user_M": Mu, "Po": Po, "M_max": M_max},
        "geom": {"vol": vol, "formwork": formwork},
        "boq": {"rebar": rebar_kg, "items": items, "total": sum(q * pr for _, _, _, q, pr in items)}
    }