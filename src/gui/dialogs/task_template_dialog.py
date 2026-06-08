"""
دیالوگ مدیریت الگوهای وظایف تکراری
"""

from PyQt5 import QtWidgets, QtCore


class TaskTemplateDialog(QtWidgets.QDialog):
    def __init__(self, parent=None, template=None, db=None):
        super().__init__(parent)
        self.db = db
        self.template = template
        self.setWindowTitle("➕ افزودن الگوی وظیفه جدید" if not template else "✏️ ویرایش الگوی وظیفه")
        self.setModal(True)
        self.resize(500, 480)
        self.setup_ui()
        if template:
            self.load_template_data()

    def get_glass_style(self):
        """استایل شیشه‌ای برای دکمه‌ها"""
        return """
            QPushButton {
                background-color: rgba(60, 60, 65, 200);
                color: #C8C8C8;
                border: 1px solid rgba(86, 156, 214, 80);
                border-radius: 4px;
                font-weight: bold;
                padding: 6px 12px;
            }
            QPushButton:hover {
                background-color: rgba(86, 156, 214, 100);
                border-color: rgba(86, 156, 214, 150);
                color: white;
            }
        """

    def setup_ui(self):
        layout = QtWidgets.QFormLayout(self)
        layout.setLabelAlignment(QtCore.Qt.AlignRight)
        layout.setSpacing(12)
        layout.setContentsMargins(20, 20, 20, 20)

        glass_style = self.get_glass_style()

        # نام الگو
        self.name_edit = QtWidgets.QLineEdit()
        self.name_edit.setPlaceholderText("مثال: شستشوی ماهانه تور")
        self.name_edit.setStyleSheet("""
            QLineEdit {
                background-color: #3C3C3C;
                border: 1px solid #3E3E42;
                border-radius: 4px;
                padding: 8px;
                color: #C8C8C8;
            }
        """)
        layout.addRow("نام الگو:", self.name_edit)

        # دسته‌بندی
        self.category_combo = QtWidgets.QComboBox()
        self.category_combo.addItems(["feeding", "cleaning", "inspection", "repair", "harvest", "water_quality", "other"])
        self.category_combo.setStyleSheet("""
            QComboBox {
                background-color: #3C3C3C;
                border: 1px solid #3E3E42;
                border-radius: 4px;
                padding: 8px;
                color: #C8C8C8;
            }
        """)
        layout.addRow("دسته‌بندی:", self.category_combo)

        # مدت زمان پیش‌فرض
        self.duration = QtWidgets.QSpinBox()
        self.duration.setRange(15, 1440)
        self.duration.setSuffix(" دقیقه")
        self.duration.setValue(60)
        self.duration.setStyleSheet("""
            QSpinBox {
                background-color: #3C3C3C;
                border: 1px solid #3E3E42;
                border-radius: 4px;
                padding: 6px;
                color: #C8C8C8;
            }
        """)
        layout.addRow("مدت زمان پیش‌فرض:", self.duration)

        # مسئول پیش‌فرض
        self.assigned_to = QtWidgets.QLineEdit()
        self.assigned_to.setPlaceholderText("مثال: واحد بهره برداری")
        self.assigned_to.setStyleSheet("""
            QLineEdit {
                background-color: #3C3C3C;
                border: 1px solid #3E3E42;
                border-radius: 4px;
                padding: 8px;
                color: #C8C8C8;
            }
        """)
        layout.addRow("مسئول پیش‌فرض:", self.assigned_to)

        # توضیحات
        self.desc_edit = QtWidgets.QTextEdit()
        self.desc_edit.setMaximumHeight(100)
        self.desc_edit.setPlaceholderText("توضیحات الگو...")
        self.desc_edit.setStyleSheet("""
            QTextEdit {
                background-color: #3C3C3C;
                border: 1px solid #3E3E42;
                border-radius: 4px;
                padding: 8px;
                color: #C8C8C8;
            }
        """)
        layout.addRow("توضیحات:", self.desc_edit)

        # دکمه‌ها
        btn_layout = QtWidgets.QHBoxLayout()
        btn_layout.setSpacing(10)
        btn_layout.addStretch()

        ok_btn = QtWidgets.QPushButton("💾 ذخیره الگو")
        ok_btn.setFixedSize(110, 35)
        ok_btn.setStyleSheet(glass_style)
        ok_btn.clicked.connect(self.accept)

        cancel_btn = QtWidgets.QPushButton("❌ انصراف")
        cancel_btn.setFixedSize(100, 35)
        cancel_btn.setStyleSheet(glass_style)
        cancel_btn.clicked.connect(self.reject)

        btn_layout.addWidget(ok_btn)
        btn_layout.addWidget(cancel_btn)
        layout.addRow(btn_layout)

    def load_template_data(self):
        """بارگذاری داده‌های الگو برای ویرایش"""
        if self.template:
            self.name_edit.setText(self.template.get('name', ''))
            idx = self.category_combo.findText(self.template.get('category', 'other'))
            if idx >= 0:
                self.category_combo.setCurrentIndex(idx)
            self.duration.setValue(self.template.get('default_duration_minutes', 60))
            self.assigned_to.setText(self.template.get('default_assigned_to', ''))
            self.desc_edit.setText(self.template.get('description', ''))

    def get_data(self):
        """دریافت داده‌های الگو"""
        return {
            'name': self.name_edit.text().strip(),
            'category': self.category_combo.currentText(),
            'duration': self.duration.value(),
            'assigned_to': self.assigned_to.text().strip(),
            'description': self.desc_edit.toPlainText()
        }