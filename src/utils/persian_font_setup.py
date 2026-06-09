# src/utils/persian_font_setup.py

import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import os

def setup_persian_font():
    """تنظیم فونت فارسی برای matplotlib"""
    
    # لیست مسیرهای احتمالی فونت فارسی
    font_paths = [
        "C:/Windows/Fonts/IRANSans.ttf",
        "C:/Windows/Fonts/IRANSansWeb.ttf",
        "C:/Windows/Fonts/B Nazanin.ttf",
        "C:/Windows/Fonts/BNazanin.ttf",
        "C:/Windows/Fonts/Tahoma.ttf",
        "C:/Windows/Fonts/Segoe UI.ttf",
    ]
    
    for font_path in font_paths:
        if os.path.exists(font_path):
            try:
                fm.fontManager.addfont(font_path)
                prop = fm.FontProperties(fname=font_path)
                plt.rcParams['font.family'] = prop.get_name()
                plt.rcParams['axes.unicode_minus'] = False
                print(f"✅ فونت فارسی بارگذاری شد: {font_path}")
                return prop
            except Exception as e:
                print(f"خطا در بارگذاری {font_path}: {e}")
                continue
    
    # اگر فونت فارسی پیدا نشد، از تنظیمات پیشفرض استفاده کن
    plt.rcParams['font.family'] = 'sans-serif'
    plt.rcParams['font.sans-serif'] = ['DejaVu Sans', 'Arial']
    plt.rcParams['axes.unicode_minus'] = False
    print("⚠️ فونت فارسی یافت نشد. از فونت پیشفرض استفاده می‌شود.")
    return None

PERSIAN_FONT = setup_persian_font()