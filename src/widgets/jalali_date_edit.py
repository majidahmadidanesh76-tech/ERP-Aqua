"""
ویجت انتخاب تاریخ شمسی برای ERP-Aqua
نسخه مقاوم در برابر خطا - هم میلادی و هم شمسی را پشتیبانی می‌کند
"""

from PyQt5 import QtWidgets, QtCore
import jdatetime
import re


class JalaliDateEdit(QtWidgets.QDateEdit):
    """ویجت انتخاب تاریخ شمسی با پشتیبانی از تقویم جلالی"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.setDisplayFormat("yyyy/MM/dd")
        self.setCalendarPopup(True)
        self.setAlignment(QtCore.Qt.AlignCenter)
        
        self.set_to_today()
    
    def set_to_today(self):
        """تنظیم تاریخ به امروز (شمسی)"""
        today_jalali = jdatetime.date.today()
        self.set_jalali_date(f"{today_jalali.year}/{today_jalali.month:02d}/{today_jalali.day:02d}")
    
    def get_jalali_date(self) -> str:
        """دریافت تاریخ شمسی به صورت رشته 'yyyy/mm/dd'"""
        qdate = self.date()
        if qdate.isValid():
            jalali_date = jdatetime.date.fromgregorian(date=qdate.toPyDate())
            return f"{jalali_date.year}/{jalali_date.month:02d}/{jalali_date.day:02d}"
        return ""
    
    def set_jalali_date(self, date_str: str):
        """تنظیم تاریخ - هم میلادی و هم شمسی را قبول می‌کند"""
        if not date_str:
            return False
        
        try:
            # استخراج اعداد از رشته
            parts = re.findall(r'\d+', date_str)
            if len(parts) >= 3:
                year = int(parts[0])
                month = int(parts[1])
                day = int(parts[2])
                
                # محدوده سال شمسی: 1300-1500
                if 1300 <= year <= 1500:
                    # تاریخ شمسی است
                    gregorian_date = jdatetime.date(year, month, day).togregorian()
                    qdate = QtCore.QDate(gregorian_date.year, gregorian_date.month, gregorian_date.day)
                    if qdate.isValid():
                        self.setDate(qdate)
                        return True
                # محدوده سال میلادی: 1900-2100
                elif 1900 <= year <= 2100:
                    # تاریخ میلادی است، مستقیم تنظیم کن
                    qdate = QtCore.QDate(year, month, day)
                    if qdate.isValid():
                        self.setDate(qdate)
                        return True
                # اگر هیچکدام نبود، سعی کن مستقیم تنظیم کنی
                else:
                    qdate = QtCore.QDate(year, month, day)
                    if qdate.isValid():
                        self.setDate(qdate)
                        return True
            return False
        except Exception as e:
            print(f"خطا در تنظیم تاریخ '{date_str}': {e}")
            return False