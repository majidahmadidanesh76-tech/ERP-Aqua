"""
ویجت استاندارد انتخاب تاریخ شمسی با استفاده از QDateEdit و QCalendar
"""
from PyQt5 import QtWidgets, QtCore
from PyQt5.QtCore import QDate, QCalendar
import jdatetime

class JalaliDateEdit(QtWidgets.QDateEdit):
    """ویجت انتخاب تاریخ شمسی با پشتیبانی از تقویم جلالی"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # تنظیم تقویم جلالی (پشتیبانی شده در Qt >= 5.14)
        self._jalali_calendar = QCalendar(QCalendar.System.Jalali)
        
        # تنظیمات ظاهری
        self.setDisplayFormat("dd/MM/yyyy")
        self.setCalendarPopup(True)
        self.setCalendar(self._jalali_calendar)
        self.setAlignment(QtCore.Qt.AlignCenter)
        
        # محدودیت سال‌ها (1300 تا 1500)
        min_date = QDate.fromString("1300/01/01", "yyyy/MM/dd", self._jalali_calendar)
        max_date = QDate.fromString("1500/12/30", "yyyy/MM/dd", self._jalali_calendar)
        self.setDateRange(min_date, max_date)
        
        # تنظیم تاریخ امروز
        self.set_to_today()
    
    def set_to_today(self):
        """تنظیم تاریخ به امروز (شمسی)"""
        today_jalali = jdatetime.date.today()
        jalali_date = QDate.fromString(
            f"{today_jalali.year}/{today_jalali.month:02d}/{today_jalali.day:02d}",
            "yyyy/MM/dd",
            self._jalali_calendar
        )
        self.setDate(jalali_date)
    
    def get_jalali_date(self) -> str:
        """دریافت تاریخ شمسی به صورت رشته 'yyyy/mm/dd'"""
        return self.date().toString("yyyy/MM/dd")
    
    def set_jalali_date(self, date_str: str):
        """تنظیم تاریخ از روی رشته شمسی 'yyyy/mm/dd'"""
        try:
            qdate = QDate.fromString(date_str, "yyyy/MM/dd", self._jalali_calendar)
            if qdate.isValid():
                self.setDate(qdate)
                return True
        except:
            pass
        return False