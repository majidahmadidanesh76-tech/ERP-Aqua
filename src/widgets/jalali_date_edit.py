"""
ویجت انتخاب تاریخ شمسی برای ERP-Aqua
نسخه نهایی با پشتیبانی رسمی از تقویم جلالی در Qt
"""

from PyQt5 import QtWidgets, QtCore
from PyQt5.QtCore import QCalendar, QDate
import jdatetime
import re

class JalaliDateEdit(QtWidgets.QDateEdit):
    """ویجت انتخاب تاریخ شمسی با پشتیبانی از تقویم جلالی Qt"""

    def __init__(self, parent=None):
        super().__init__(parent)

        # تنظیم تقویم شمسی (جلالی) - این خط کلیدی است
        try:
            # در Qt 5.14+ تقویم Jalali پشتیبانی می‌شود
            self.jalali_calendar = QCalendar(QCalendar.System.Jalali)
            self.setCalendar(self.jalali_calendar)
            print("✅ تقویم شمسی با موفقیت فعال شد")
        except Exception as e:
            print(f"⚠️ تقویم شمسی پشتیبانی نمی‌شود: {e}")
            print("   از روش جایگزین استفاده می‌شود")

        self.setDisplayFormat("yyyy/MM/dd")
        self.setCalendarPopup(True)
        self.setAlignment(QtCore.Qt.AlignCenter)
        
        # تنظیم محدوده سال‌های معتبر (1300 تا 1500 شمسی)
        try:
            min_jalali = jdatetime.date(1300, 1, 1)
            max_jalali = jdatetime.date(1500, 12, 29)
            min_gregorian = min_jalali.togregorian()
            max_gregorian = max_jalali.togregorian()
            self.setMinimumDate(QDate(min_gregorian.year, min_gregorian.month, min_gregorian.day))
            self.setMaximumDate(QDate(max_gregorian.year, max_gregorian.month, max_gregorian.day))
        except:
            pass

        self.set_to_today()

    def set_to_today(self):
        """تنظیم تاریخ به امروز (شمسی)"""
        try:
            today_jalali = jdatetime.date.today()
            self.set_jalali_date(f"{today_jalali.year}/{today_jalali.month:02d}/{today_jalali.day:02d}")
        except:
            self.setDate(QDate.currentDate())

    def get_jalali_date(self) -> str:
        """دریافت تاریخ شمسی به صورت رشته 'yyyy/mm/dd'"""
        try:
            qdate = self.date()
            if qdate.isValid():
                # استفاده از تقویم جلالی برای تبدیل
                if hasattr(self, 'jalali_calendar'):
                    year = qdate.year(self.jalali_calendar)
                    month = qdate.month(self.jalali_calendar)
                    day = qdate.day(self.jalali_calendar)
                    return f"{year}/{month:02d}/{day:02d}"
                else:
                    # روش جایگزین با jdatetime
                    gregorian_date = qdate.toPyDate()
                    jalali_date = jdatetime.date.fromgregorian(date=gregorian_date)
                    return f"{jalali_date.year}/{jalali_date.month:02d}/{jalali_date.day:02d}"
        except Exception as e:
            print(f"خطا در دریافت تاریخ شمسی: {e}")
        return ""

    def set_jalali_date(self, date_str: str):
        """تنظیم تاریخ شمسی"""
        if not date_str:
            return False

        try:
            parts = re.findall(r'\d+', date_str)
            if len(parts) >= 3:
                year = int(parts[0])
                month = int(parts[1])
                day = int(parts[2])

                # تبدیل تاریخ شمسی به میلادی
                jalali_date = jdatetime.date(year, month, day)
                gregorian_date = jalali_date.togregorian()
                
                qdate = QDate(gregorian_date.year, gregorian_date.month, gregorian_date.day)
                if qdate.isValid():
                    self.setDate(qdate)
                    return True
            return False
        except Exception as e:
            print(f"خطا در تنظیم تاریخ '{date_str}': {e}")
            return False