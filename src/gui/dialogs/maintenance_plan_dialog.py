"""
دیالوگ ایجاد/ویرایش برنامه نت (تعمیرات و نگهداری)
"""

from PyQt5 import QtWidgets, QtCore
from ...widgets.jalali_date_edit import JalaliDateEdit


class MaintenancePlanDialog(QtWidgets.QDialog):
    def __init__(self, parent=None, plan=None):
        super().__init__(parent)
        self.plan = plan
        self.setWindowTitle("➕ ایجاد برنامه نت جدید" if not plan else "✏️ ویرایش برنامه نت")
        self.setModal(True)
        self.resize(500, 550)
        self.setup_ui()
        if plan:
            self.load_plan_data()

    def get_glass_style(self):
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
                color: white;
            }
        """

    def setup_ui(self):
        layout = QtWidgets.QFormLayout(self)
        layout.setLabelAlignment(QtCore.Qt.AlignRight)
        layout.setSpacing(12)
        layout.setContentsMargins(20, 20, 20, 20)

        glass_style = self.get_glass_style()

        # عنوان برنامه
        self.title_edit = QtWidgets.QLineEdit()
        self.title_edit.setPlaceholderText("مثال: برنامه شستشوی دورهای تورها")
        self.title_edit.setStyleSheet("""
            QLineEdit {
                background-color: #3C3C3C;
                border: 1px solid #3E3E42;
                border-radius: 4px;
                padding: 8px;
                color: #C8C8C8;
            }
        """)
        layout.addRow("عنوان برنامه:", self.title_edit)

        # نوع برنامه
        self.type_combo = QtWidgets.QComboBox()
        self.type_combo.addItems(["weekly", "monthly", "quarterly", "yearly"])
        self.type_combo.setStyleSheet("""
            QComboBox {
                background-color: #3C3C3C;
                border: 1px solid #3E3E42;
                border-radius: 4px;
                padding: 8px;
                color: #C8C8C8;
            }
        """)
        layout.addRow("نوع برنامه:", self.type_combo)

        # نوع تجهیز
        self.asset_type_combo = QtWidgets.QComboBox()
        self.asset_type_combo.setEditable(True)
        self.asset_type_combo.addItems(["mooring", "buoy", "anchor", "net", "cage", "collector"])
        self.asset_type_combo.setStyleSheet("""
            QComboBox {
                background-color: #3C3C3C;
                border: 1px solid #3E3E42;
                border-radius: 4px;
                padding: 8px;
                color: #C8C8C8;
            }
        """)
        layout.addRow("نوع تجهیز:", self.asset_type_combo)

        # شناسه تجهیز (اختیاری)
        self.asset_id_edit = QtWidgets.QLineEdit()
        self.asset_id_edit.setPlaceholderText("اختیاری - مثال: MOR-001")
        self.asset_id_edit.setStyleSheet("""
            QLineEdit {
                background-color: #3C3C3C;
                border: 1px solid #3E3E42;
                border-radius: 4px;
                padding: 8px;
                color: #C8C8C8;
            }
        """)
        layout.addRow("شناسه تجهیز (اختیاری):", self.asset_id_edit)

        # تاریخ شروع
        self.start_date = JalaliDateEdit()
        self.start_date.setStyleSheet("""
            QDateEdit {
                background-color: #3C3C3C;
                border: 1px solid #3E3E42;
                border-radius: 4px;
                padding: 6px;
                color: #C8C8C8;
            }
        """)
        layout.addRow("تاریخ شروع:", self.start_date)

        # تاریخ پایان
        self.end_date = JalaliDateEdit()
        self.end_date.setStyleSheet("""
            QDateEdit {
                background-color: #3C3C3C;
                border: 1px solid #3E3E42;
                border-radius: 4px;
                padding: 6px;
                color: #C8C8C8;
            }
        """)
        layout.addRow("تاریخ پایان:", self.end_date)

        # یادداشت
        self.notes = QtWidgets.QTextEdit()
        self.notes.setMaximumHeight(80)
        self.notes.setPlaceholderText("توضیحات اضافی...")
        self.notes.setStyleSheet("""
            QTextEdit {
                background-color: #3C3C3C;
                border: 1px solid #3E3E42;
                border-radius: 4px;
                padding: 8px;
                color: #C8C8C8;
            }
        """)
        layout.addRow("یادداشت:", self.notes)

        # دکمه‌ها
        btn_layout = QtWidgets.QHBoxLayout()
        btn_layout.setSpacing(10)
        btn_layout.addStretch()

        ok_btn = QtWidgets.QPushButton("💾 ذخیره")
        ok_btn.setFixedSize(100, 35)
        ok_btn.setStyleSheet(glass_style)
        ok_btn.clicked.connect(self.accept)

        cancel_btn = QtWidgets.QPushButton("❌ انصراف")
        cancel_btn.setFixedSize(100, 35)
        cancel_btn.setStyleSheet(glass_style)
        cancel_btn.clicked.connect(self.reject)

        btn_layout.addWidget(ok_btn)
        btn_layout.addWidget(cancel_btn)
        layout.addRow(btn_layout)

    def load_plan_data(self):
        """بارگذاری داده‌های برنامه برای ویرایش"""
        if self.plan:
            self.title_edit.setText(self.plan.get('plan_title', ''))
            idx = self.type_combo.findText(self.plan.get('plan_type', 'monthly'))
            if idx >= 0:
                self.type_combo.setCurrentIndex(idx)
            idx = self.asset_type_combo.findText(self.plan.get('asset_type', ''))
            if idx >= 0:
                self.asset_type_combo.setCurrentIndex(idx)
            self.asset_id_edit.setText(self.plan.get('asset_id', ''))
            self.start_date.set_jalali_date(self.plan.get('start_date', ''))
            self.end_date.set_jalali_date(self.plan.get('end_date', ''))
            self.notes.setText(self.plan.get('notes', ''))

    def accept(self):
        """ذخیره برنامه"""
        if not self.title_edit.text().strip():
            QtWidgets.QMessageBox.warning(self, "خطا", "لطفاً عنوان برنامه را وارد کنید")
            return

        start = self.start_date.get_jalali_date()
        end = self.end_date.get_jalali_date()
        
        print(f"DEBUG: تاریخ شروع: {start}, تاریخ پایان: {end}")
        
        if start > end:
            QtWidgets.QMessageBox.warning(self, "خطا", "تاریخ شروع نباید از تاریخ پایان بزرگتر باشد")
            return

        asset_id = self.asset_id_edit.text().strip()
        if not asset_id:
            asset_id = None

        self.result_data = {
            "plan_title": self.title_edit.text().strip(),
            "plan_type": self.type_combo.currentText(),
            "start_date": start,
            "end_date": end,
            "asset_type": self.asset_type_combo.currentText(),
            "asset_id": asset_id,
            "notes": self.notes.toPlainText()
        }
        
        print(f"DEBUG: result_data: {self.result_data}")

        super().accept()