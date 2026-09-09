"""
Market Engine Module (Enterprise Grade)
سیستم استخراج، شبیه‌سازی و تحلیل سری زمانی قیمت مصالح ساختمانی
طراحی شده با معماری Resilient (مقاوم در برابر قطعی شبکه)
"""
import time
import random
import datetime
import pandas as pd

class MarketAnalyzer:
    def __init__(self):
        self.last_update = None
        self.current_prices = {}
        self.historical_data = None
        self._initialize_market_data()

    def _initialize_market_data(self):
        """ساخت داده‌های پایه و تاریخچه ۶ ماهه با الگوریتم نوسانات تصادفی (Random Walk)"""
        # قیمت‌های پایه امروز (تومان)
        base = {
            "rebar": 34500,       # میلگرد
            "concrete": 2850000,  # بتن C25
            "excavation": 650000, # خاکبرداری
            "formwork": 550000,   # قالب‌بندی
            "lean_conc": 180000   # بتن مگر
        }
        
        # تولید تاریخچه ۶ ماه گذشته (180 روز)
        dates = pd.date_range(end=datetime.datetime.today(), periods=180)
        data = {"Date": dates}
        
        for item, price in base.items():
            # شبیه‌سازی تورم و نوسان بازار با ترکیب روند خطی و نویز
            trend = np_linspace(price * 0.75, price, 180) # 25% تورم در 6 ماه
            noise = [random.uniform(-price*0.02, price*0.02) for _ in range(180)]
            data[item] = [int(t + n) for t, n in zip(trend, noise)]
            
        self.historical_data = pd.DataFrame(data)
        self.update_live_prices()

    def update_live_prices(self):
        """دریافت قیمت‌های لحظه‌ای (در سیستم واقعی به API آهن‌آنلاین وصل می‌شود)"""
        # برای جلوگیری از خطای تحریم سرورها در رزومه، از شبیه‌ساز زنده استفاده می‌کنیم
        latest = self.historical_data.iloc[-1]
        
        # اعمال نوسان لحظه‌ای (ساعتی)
        fluctuation = random.uniform(0.995, 1.008)
        
        self.current_prices = {
            "rebar": int(latest["rebar"] * fluctuation),
            "concrete": int(latest["concrete"] * fluctuation),
            "excavation": int(latest["excavation"] * fluctuation),
            "formwork": int(latest["formwork"] * fluctuation),
            "lean_conc": int(latest["lean_conc"] * fluctuation),
        }
        self.last_update = datetime.datetime.now()

    def get_prices(self):
        """ارسال قیمت‌ها به موتور محاسبات عمران"""
        # اگر بیش از 1 ساعت از آخرین آپدیت گذشته بود، دوباره آپدیت کن (Caching)
        if (datetime.datetime.now() - self.last_update).total_seconds() > 3600:
            self.update_live_prices()
        return self.current_prices

    def get_historical_dataframe(self):
        return self.historical_data

def np_linspace(start, stop, num):
    """تابع کمکی برای تولید اعداد خطی (جایگزین numpy برای سبکی برنامه)"""
    step = (stop - start) / (num - 1)
    return [start + step * i for i in range(num)]