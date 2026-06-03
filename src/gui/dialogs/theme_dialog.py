"""
دیالوگ انتخاب تم (رنگ‌بندی) نرم‌افزار
"""

from PyQt5 import QtWidgets, QtCore
import json
import os
import sys


class ThemeDialog(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("🎨 انتخاب تم نرم‌افزار")
        self.setModal(True)
        self.resize(350, 250)
        self.setup_ui()
        self.load_current_theme()

    def setup_ui(self):
        layout = QtWidgets.QVBoxLayout(self)
        layout.setSpacing(15)

        title = QtWidgets.QLabel("انتخاب رنگ‌بندی محیط")
        title.setAlignment(QtCore.Qt.AlignCenter)
        title.setStyleSheet("font-size: 14px; font-weight: bold; color: #569CD6;")
        layout.addWidget(title)

        # دکمه‌های رادیویی برای انتخاب تم
        self.theme_dark = QtWidgets.QRadioButton("🌙 تم تاریک (Dark)")
        self.theme_dark.setStyleSheet("color: #C8C8C8; padding: 5px;")
        
        self.theme_light = QtWidgets.QRadioButton("☀️ تم روشن آبی (Light Blue)")
        self.theme_light.setStyleSheet("color: #C8C8C8; padding: 5px;")

        layout.addWidget(self.theme_dark)
        layout.addWidget(self.theme_light)

        # توضیحات
        info_label = QtWidgets.QLabel("⚠️ پس از اعمال، برنامه مجدداً راه‌اندازی می‌شود")
        info_label.setAlignment(QtCore.Qt.AlignCenter)
        info_label.setStyleSheet("color: #F48771; font-size: 10px; margin-top: 10px;")
        layout.addWidget(info_label)

        # دکمه‌ها
        btn_layout = QtWidgets.QHBoxLayout()
        
        self.apply_btn = QtWidgets.QPushButton("اعمال و راه‌اندازی مجدد")
        self.apply_btn.setStyleSheet("""
            QPushButton {
                background-color: #0E639C;
                color: white;
                font-weight: bold;
                padding: 8px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #1177BB;
            }
        """)
        self.apply_btn.clicked.connect(self.apply_and_restart)
        
        self.cancel_btn = QtWidgets.QPushButton("انصراف")
        self.cancel_btn.setStyleSheet("""
            QPushButton {
                background-color: #3C3C3C;
                color: #C8C8C8;
                border: 1px solid #3E3E42;
                border-radius: 4px;
                padding: 8px;
            }
            QPushButton:hover {
                background-color: #4A4A4A;
            }
        """)
        self.cancel_btn.clicked.connect(self.reject)
        
        btn_layout.addWidget(self.apply_btn)
        btn_layout.addWidget(self.cancel_btn)
        layout.addLayout(btn_layout)

    def load_current_theme(self):
        """بارگذاری تم فعلی از فایل تنظیمات"""
        settings_file = "data/settings.json"
        theme = 'dark'
        if os.path.exists(settings_file):
            try:
                with open(settings_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    theme = data.get('theme', 'dark')
                    print(f"DEBUG: تم فعلی خوانده شده: {theme}")
            except:
                pass
        
        if theme == 'dark':
            self.theme_dark.setChecked(True)
            print("DEBUG: دکمه Dark انتخاب شد")
        else:
            self.theme_light.setChecked(True)
            print("DEBUG: دکمه Light انتخاب شد")

    def apply_and_restart(self):
        """اعمال تم انتخاب شده و راه‌اندازی مجدد برنامه"""
        theme = 'dark' if self.theme_dark.isChecked() else 'light'
        print(f"DEBUG: تم انتخاب شده برای ذخیره: {theme}")
        
        # ذخیره در فایل تنظیمات
        settings_file = "data/settings.json"
        os.makedirs("data", exist_ok=True)
        
        data = {}
        if os.path.exists(settings_file):
            try:
                with open(settings_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
            except:
                pass
        
        data['theme'] = theme
        
        with open(settings_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        print(f"DEBUG: تم {theme} در فایل settings.json ذخیره شد")
        
        # راه‌اندازی مجدد برنامه
        self.accept()
        QtCore.QCoreApplication.quit()
        os.execl(sys.executable, sys.executable, *sys.argv)