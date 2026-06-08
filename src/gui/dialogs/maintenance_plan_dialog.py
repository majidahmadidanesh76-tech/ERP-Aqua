"""
دیالوگ ایجاد/ویرایش برنامه نت (تعمیرات و نگهداری)
"""

from PyQt5 import QtWidgets, QtCore

from ...widgets.jalali_date_edit import JalaliDateEdit

class MaintenancePlanDialog(QtWidgets.QDialog):
    def __init__(self, parent=None, plan=None):
        super().__init__(parent)
        self.plan = plan
        self.setWindowTitle("ایجاد برنامه نت جدید" if not plan else "ویرایش برنامه نت")
        self.setModal(True)
        self.resize(500, 550)
        self.setup_ui()
        if plan:
            self.load_plan_data()

    def setup_ui(self):
        layout = QtWidgets.QFormLayout(self)
        layout.setLabelAlignment(QtCore.Qt.AlignRight)
        layout.setSpacing(12)
        layout.setContentsMargins(20, 20, 20, 20)

        self.title_edit = QtWidgets.QLineEdit()
        self.title_edit.setPlaceholderText("عنوان برنامه نت")
        layout.addRow("عنوان برنامه:", self.title_edit)

        self.type_combo = QtWidgets.QComboBox()
        self.type_combo.addItems(["weekly", "monthly", "quarterly", "yearly"])
        layout.addRow("نوع برنامه:", self.type_combo)

        self.asset_type_combo = QtWidgets.QComboBox()
        self.asset_type_combo.setEditable(True)
        self.asset_type_combo.addItems(["mooring", "buoy", "anchor", "net", "cage", "collector"])
        layout.addRow("نوع تجهیز:", self.asset_type_combo)

        self.asset_id_edit = QtWidgets.QLineEdit()
        self.asset_id_edit.setPlaceholderText("شناسه تجهیز (اختیاری)")
        layout.addRow("شناسه تجهیز:", self.asset_id_edit)

        self.start_date = JalaliDateEdit()
        layout.addRow("تاریخ شروع:", self.start_date)

        self.end_date = JalaliDateEdit()
        layout.addRow("تاریخ پایان:", self.end_date)

        self.notes = QtWidgets.QTextEdit()
        self.notes.setMaximumHeight(80)
        self.notes.setPlaceholderText("یادداشت...")
        layout.addRow("یادداشت:", self.notes)

        btn_layout = QtWidgets.QHBoxLayout()
        ok_btn = QtWidgets.QPushButton("ذخیره")
        ok_btn.setStyleSheet("background-color: #2E8B57; color: white; font-weight: bold; padding: 8px;")
        ok_btn.clicked.connect(self.accept)

        cancel_btn = QtWidgets.QPushButton("انصراف")
        cancel_btn.setStyleSheet("background-color: #3C3C3C; color: #C8C8C8; padding: 8px;")
        cancel_btn.clicked.connect(self.reject)

        btn_layout.addWidget(ok_btn)
        btn_layout.addWidget(cancel_btn)
        layout.addRow(btn_layout)

    def load_plan_data(self):
        if self.plan:
            self.title_edit.setText(self.plan.get('plan_title', ''))
            idx = self.type_combo.findText(self.plan.get('plan_type', 'monthly'))
            if idx >= 0:
                self.type_combo.setCurrentIndex(idx)
            idx = self.asset_type_combo.findText(self.plan.get('asset_type', 'mooring'))
            if idx >= 0:
                self.asset_type_combo.setCurrentIndex(idx)
            self.asset_id_edit.setText(self.plan.get('asset_id', ''))
            self.start_date.set_jalali_date(self.plan.get('start_date', ''))
            self.end_date.set_jalali_date(self.plan.get('end_date', ''))
            self.notes.setText(self.plan.get('notes', ''))

    def accept(self):
        if not self.title_edit.text().strip():
            QtWidgets.QMessageBox.warning(self, "خطا", "لطفاً عنوان برنامه را وارد کنید")
            return

        start = self.start_date.get_jalali_date()
        end = self.end_date.get_jalali_date()
        if start > end:
            QtWidgets.QMessageBox.warning(self, "خطا", "تاریخ شروع نباید از تاریخ پایان بزرگتر باشد")
            return

        self.result_data = {
            "plan_title": self.title_edit.text().strip(),
            "plan_type": self.type_combo.currentText(),
            "start_date": start,
            "end_date": end,
            "asset_type": self.asset_type_combo.currentText(),
            "asset_id": self.asset_id_edit.text().strip() or None,
            "notes": self.notes.toPlainText()
        }

        super().accept()