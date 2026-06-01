"""
ERP-Aqua - نرم‌افزار مدیریت مزارع پرورش ماهی
نسخه 1.0.0

این فایل نقطه ورود اصلی برنامه است
"""

import sys
import os

# اضافه کردن مسیر src برای import
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from PyQt5 import QtWidgets, QtCore
from src.gui.main_window import MainWindow
from src.core.constants import APP_NAME, APP_VERSION


def main():
    """
    تابع اصلی برنامه
    راه‌اندازی اپلیکیشن و نمایش پنجره اصلی
    """
    # ایجاد اپلیکیشن
    app = QtWidgets.QApplication(sys.argv)
    
    # تنظیم جهت راست به چپ برای زبان فارسی
    app.setLayoutDirection(QtCore.Qt.RightToLeft)
    
    # تنظیم اطلاعات برنامه
    app.setApplicationName(APP_NAME)
    app.setApplicationVersion(APP_VERSION)
    
    # ایجاد و نمایش پنجره اصلی
    window = MainWindow()
    window.show()
    
    # اجرای حلقه اصلی برنامه
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()