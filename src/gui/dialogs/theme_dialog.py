"""
دیالوگ انتخاب تم - نسخه هماهنگ با تم ویندوز 11
"""

from PyQt5 import QtWidgets, QtCore
import json
import os

class ThemeDialog(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("🎨 انتخاب تم نرمافزار")
        self.setModal(True)
        self.resize(420, 320)
        self.parent_window = parent
        self.setup_ui()
        self.load_current_theme()

    def setup_ui(self):
        layout = QtWidgets.QVBoxLayout(self)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)

        # عنوان
        title = QtWidgets.QLabel("🎨 انتخاب تم نرمافزار")
        title.setAlignment(QtCore.Qt.AlignCenter)
        title.setStyleSheet("font-size: 16px; font-weight: bold; color: #1A73E8; padding: 5px;")
        layout.addWidget(title)

        # دکمه‌های رادیویی
        self.theme_light = QtWidgets.QRadioButton("🪟 تم مدرن ویندوز 11 (پیش‌فرض)")
        self.theme_light.setStyleSheet("color: #202124; padding: 8px; font-weight: 500;")
        self.theme_light.toggled.connect(self.on_theme_changed)

        self.theme_classic = QtWidgets.QRadioButton("🌊 تم کلاسیک آبی - موج دریا")
        self.theme_classic.setStyleSheet("color: #202124; padding: 8px; font-weight: 500;")
        self.theme_classic.toggled.connect(self.on_theme_changed)

        layout.addWidget(self.theme_light)
        layout.addWidget(self.theme_classic)

        # پیش‌نمایش
        self.preview_label = QtWidgets.QLabel()
        self.preview_label.setFixedHeight(50)
        self.preview_label.setAlignment(QtCore.Qt.AlignCenter)
        self.preview_label.setStyleSheet("""
            QLabel {
                background-color: #1A73E8;
                color: white;
                border-radius: 10px;
                padding: 10px;
                font-size: 12px;
            }
        """)
        self.preview_label.setText("پیش‌نمایش تم ویندوز 11")
        layout.addWidget(self.preview_label)

        # توضیحات
        info_label = QtWidgets.QLabel("ℹ️ تم جدید بلافاصله اعمال می‌شود")
        info_label.setAlignment(QtCore.Qt.AlignCenter)
        info_label.setStyleSheet("color: #5F6368; font-size: 11px; margin-top: 5px;")
        layout.addWidget(info_label)

        # دکمه‌ها
        btn_layout = QtWidgets.QHBoxLayout()
        btn_layout.setSpacing(12)

        self.apply_btn = QtWidgets.QPushButton("✓ اعمال")
        self.apply_btn.setStyleSheet("""
            QPushButton {
                background-color: #1A73E8;
                color: white;
                font-weight: 600;
                padding: 8px 20px;
                border-radius: 8px;
                border: none;
            }
            QPushButton:hover {
                background-color: #1557B0;
            }
        """)
        self.apply_btn.clicked.connect(self.apply_and_save)

        self.cancel_btn = QtWidgets.QPushButton("انصراف")
        self.cancel_btn.setStyleSheet("""
            QPushButton {
                background-color: #F1F3F4;
                color: #202124;
                border: 1px solid rgba(0, 0, 0, 0.12);
                border-radius: 8px;
                padding: 8px 20px;
            }
            QPushButton:hover {
                background-color: #E8EAED;
                border-color: #1A73E8;
            }
        """)
        self.cancel_btn.clicked.connect(self.reject)

        btn_layout.addWidget(self.apply_btn)
        btn_layout.addWidget(self.cancel_btn)
        layout.addLayout(btn_layout)

    def on_theme_changed(self):
        if self.theme_light.isChecked():
            self.preview_label.setStyleSheet("""
                QLabel {
                    background-color: #1A73E8;
                    color: white;
                    border-radius: 10px;
                    padding: 10px;
                    font-size: 12px;
                }
            """)
            self.preview_label.setText("پیش‌نمایش تم ویندوز 11 - شیشه‌ای مدرن")
        else:
            self.preview_label.setStyleSheet("""
                QLabel {
                    background-color: #0078D4;
                    color: white;
                    border-radius: 10px;
                    padding: 10px;
                    font-size: 12px;
                }
            """)
            self.preview_label.setText("پیش‌نمایش تم کلاسیک آبی - موج دریا")

    def load_current_theme(self):
        settings_file = "data/settings.json"
        theme = 'light'
        if os.path.exists(settings_file):
            try:
                with open(settings_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    theme = data.get('theme', 'light')
            except:
                pass
        if theme == 'classic':
            self.theme_classic.setChecked(True)
        else:
            self.theme_light.setChecked(True)

    def apply_and_save(self):
        theme = 'classic' if self.theme_classic.isChecked() else 'light'
        
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
        
        QtWidgets.QMessageBox.information(
            self, "موفق", 
            f"تم با موفقیت ذخیره شد.\nبرای اعمال کامل، برنامه را مجدداً راه‌اندازی کنید."
        )
        self.accept()