# src/widgets/jalali_date_picker.py

"""
ویجت انتخاب تاریخ شمسی برای ERP-Aqua
با استفاده از کتابخانه pyqtjalalidatepicker
"""

from PyQt5 import QtWidgets, QtCore
from pyqtjalalidatepicker import JalaliDatePicker
import jdatetime


class JalaliDatePickerWidget(QtWidgets.QWidget):
    """ویجت انتخاب تاریخ شمسی با استایل هماهنگ ERP-Aqua"""
    
    dateChanged = QtCore.pyqtSignal(str)  # تاریخ شمسی به فرمت YYYY/MM/DD
    
    def __init__(self, parent=None, initial_date=None):
        super().__init__(parent)
        self.setup_ui(initial_date)
    
    def setup_ui(self, initial_date):
        layout = QtWidgets.QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # ایجاد ویجت اصلی
        self.date_picker = JalaliDatePicker()
        
        # تنظیم استایل هماهنگ با برنامه
        self.date_picker.setStyleSheet("""
            jdp-container {
                background: #252526;
                border: 1px solid #3E3E42;
                border-radius: 4px;
            }
            jdp-container .jdp-day {
                color: #C8C8C8;
            }
            jdp-container .jdp-day.selected {
                background: #0E639C;
                color: white;
            }
            jdp-container .jdp-day:hover {
                background: #3E3E42;
            }
            jdp-container .jdp-btn {
                background: #0E639C;
                color: white;
            }
        """)
        
        # تنظیم تاریخ اولیه
        if initial_date:
            self.set_date(initial_date)
        
        self.date_picker.dateChanged.connect(self._on_date_changed)
        layout.addWidget(self.date_picker)
    
    def _on_date_changed(self, date):
        """هنگام تغییر تاریخ، سیگنال ارسال می‌کند"""
        # date از نوع datetime.date است
        jalali_date = jdatetime.date.fromgregorian(date=date)
        date_str = f"{jalali_date.year}/{jalali_date.month:02d}/{jalali_date.day:02d}"
        self.dateChanged.emit(date_str)
    
    def get_date(self):
        """دریافت تاریخ انتخاب شده به صورت رشته شمسی"""
        date = self.date_picker.getDate()
        if date:
            jalali_date = jdatetime.date.fromgregorian(date=date)
            return f"{jalali_date.year}/{jalali_date.month:02d}/{jalali_date.day:02d}"
        return None
    
    def get_date_gregorian(self):
        """دریافت تاریخ میلادی"""
        return self.date_picker.getDate()
    
    def set_date(self, jalali_date_str):
        """تنظیم تاریخ با رشته شمسی (فرمت YYYY/MM/DD)"""
        try:
            parts = jalali_date_str.split('/')
            if len(parts) == 3:
                year, month, day = int(parts[0]), int(parts[1]), int(parts[2])
                jalali_date = jdatetime.date(year, month, day)
                gregorian_date = jalali_date.togregorian()
                self.date_picker.setDate(gregorian_date)
        except Exception as e:
            print(f"خطا در تنظیم تاریخ: {e}")