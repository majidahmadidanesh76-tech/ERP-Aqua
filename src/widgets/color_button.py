"""
ویجت انتخاب رنگ ساده برای ERP-Aqua
"""

from PyQt5 import QtWidgets, QtGui


class ColorButton(QtWidgets.QPushButton):
    """
    دکمه انتخاب رنگ
    با کلیک روی دکمه، پنجره انتخاب رنگ باز می‌شود
    """
    
    def __init__(self, color="#569CD6", parent=None):
        super().__init__(parent)
        self._color = color
        self.setFixedSize(35, 35)
        self.setToolTip("برای انتخاب رنگ کلیک کنید")
        self.update_style()
        self.clicked.connect(self.select_color)
    
    def update_style(self):
        """بروزرسانی استایل دکمه بر اساس رنگ فعلی"""
        self.setStyleSheet(f"""
            QPushButton {{
                background-color: {self._color};
                border: 2px solid #3E3E42;
                border-radius: 17px;
            }}
            QPushButton:hover {{
                border: 2px solid #569CD6;
            }}
            QPushButton:pressed {{
                background-color: {self._color};
                border: 2px solid #FFFFFF;
            }}
        """)
    
    def select_color(self):
        """باز کردن دیالوگ انتخاب رنگ"""
        color = QtWidgets.QColorDialog.getColor(
            QtGui.QColor(self._color),
            self,
            "انتخاب رنگ"
        )
        if color.isValid():
            self._color = color.name()
            self.update_style()
    
    def get_color(self):
        """دریافت رنگ فعلی"""
        return self._color
    
    def set_color(self, color):
        """تنظیم رنگ جدید"""
        self._color = color
        self.update_style()