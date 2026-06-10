# src/widgets/jalali_date_edit.py

"""
ویجت انتخاب تاریخ شمسی برای ERP-Aqua
"""

from PyQt5 import QtWidgets, QtCore
from PyQt5.QtCore import QCalendar, QDate
import jdatetime
import re

class JalaliDateEdit(QtWidgets.QDateEdit):
    def __init__(self, parent=None):
        super().__init__(parent)

        # تنظیم استایل یکپارچه با دیالوگها
        self.setStyleSheet("""
            QDateEdit {
                background-color: #3C3C3F;
                color: #FFFFFF;
                border: 1px solid #4A4A4F;
                border-radius: 4px;
                padding: 7px 10px;
                min-height: 32px;
            }
            QDateEdit:focus {
                border-color: #569CD6;
                background-color: #45454A;
            }
            QDateEdit::drop-down {
                border: none;
                width: 20px;
            }
            QDateEdit::down-arrow {
                image: none;
            }
            QCalendarWidget {
                background-color: #2D2D30;
                color: #C8C8C8;
            }
            QCalendarWidget QToolButton {
                background-color: #3C3C3C;
                color: #C8C8C8;
                border: 1px solid #3E3E42;
                border-radius: 3px;
            }
            QCalendarWidget QToolButton:hover {
                background-color: #0E639C;
                color: white;
            }
            QCalendarWidget QSpinBox {
                background-color: #3C3C3C;
                color: #C8C8C8;
                border: 1px solid #3E3E42;
                border-radius: 3px;
            }
            QCalendarWidget QAbstractItemView:enabled {
                background-color: #2D2D30;
                color: #C8C8C8;
                selection-background-color: #0E639C;
            }
        """)

        try:
            self.jalali_calendar = QCalendar(QCalendar.System.Jalali)
            self.setCalendar(self.jalali_calendar)
        except Exception as e:
            print(f"⚠️ تقویم شمسی پشتیبانی نمیشود: {e}")

        self.setDisplayFormat("yyyy/MM/dd")
        self.setCalendarPopup(True)
        self.setAlignment(QtCore.Qt.AlignCenter)

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
        try:
            today_jalali = jdatetime.date.today()
            self.set_jalali_date(f"{today_jalali.year}/{today_jalali.month:02d}/{today_jalali.day:02d}")
        except:
            self.setDate(QDate.currentDate())

    def get_jalali_date(self) -> str:
        try:
            qdate = self.date()
            if qdate.isValid():
                if hasattr(self, 'jalali_calendar'):
                    year = qdate.year(self.jalali_calendar)
                    month = qdate.month(self.jalali_calendar)
                    day = qdate.day(self.jalali_calendar)
                    return f"{year}/{month:02d}/{day:02d}"
                else:
                    gregorian_date = qdate.toPyDate()
                    jalali_date = jdatetime.date.fromgregorian(date=gregorian_date)
                    return f"{jalali_date.year}/{jalali_date.month:02d}/{jalali_date.day:02d}"
        except Exception as e:
            print(f"خطا در دریافت تاریخ شمسی: {e}")
        return ""

    def set_jalali_date(self, date_str: str):
        if not date_str:
            return False
        try:
            parts = re.findall(r'\d+', date_str)
            if len(parts) >= 3:
                year = int(parts[0])
                month = int(parts[1])
                day = int(parts[2])
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