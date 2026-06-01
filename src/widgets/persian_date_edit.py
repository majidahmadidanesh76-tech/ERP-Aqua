"""
ویجت انتخاب تاریخ شمسی برای ERP-Aqua
"""

from PyQt5 import QtWidgets, QtCore
import jdatetime

from .persian_calendar import PersianCalendar


class PersianDateEdit(QtWidgets.QWidget):
    """ویجت انتخاب تاریخ شمسی با تقویم فارسی"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._date = jdatetime.date.today()
        self.setup_ui()
        self.update_display()
    
    def setup_ui(self):
        layout = QtWidgets.QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(5)
        
        self.line_edit = QtWidgets.QLineEdit()
        self.line_edit.setReadOnly(True)
        self.line_edit.setMinimumHeight(32)
        self.line_edit.setMinimumWidth(120)
        self.line_edit.setStyleSheet("""
            QLineEdit {
                background-color: #3C3C3C;
                border: 1px solid #3E3E42;
                border-radius: 4px;
                padding: 6px 8px;
                color: #C8C8C8;
                font-size: 12px;
            }
        """)
        layout.addWidget(self.line_edit)
        
        self.calendar_btn = QtWidgets.QPushButton("📅")
        self.calendar_btn.setFixedSize(35, 32)
        self.calendar_btn.setToolTip("انتخاب تاریخ از تقویم")
        self.calendar_btn.setStyleSheet("""
            QPushButton {
                background-color: #0E639C;
                color: white;
                border: none;
                border-radius: 4px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #1177BB;
            }
        """)
        self.calendar_btn.clicked.connect(self.show_calendar)
        layout.addWidget(self.calendar_btn)
    
    def update_display(self):
        """بروزرسانی نمایش تاریخ"""
        self.line_edit.setText(f"{self._date.year}/{self._date.month:02d}/{self._date.day:02d}")
    
    def show_calendar(self):
        """نمایش تقویم شمسی"""
        dialog = PersianCalendar(self, self._date)
        if dialog.exec_():
            date_str = dialog.get_selected_date()
            parts = date_str.split('/')
            self._date = jdatetime.date(int(parts[0]), int(parts[1]), int(parts[2]))
            self.update_display()
    
    def get_date(self):
        """دریافت تاریخ شمسی به صورت رشته"""
        return f"{self._date.year}/{self._date.month:02d}/{self._date.day:02d}"
    
    def set_date(self, date_str):
        """تنظیم تاریخ از روی رشته شمسی"""
        try:
            parts = date_str.split('/')
            if len(parts) == 3:
                self._date = jdatetime.date(int(parts[0]), int(parts[1]), int(parts[2]))
                self.update_display()
                return True
        except Exception as e:
            print(f"خطا در تنظیم تاریخ: {e}")
        return False