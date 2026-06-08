"""
دیالوگ ایجاد/ویرایش برنامه پرورش
"""

from PyQt5 import QtWidgets, QtCore
from ...widgets.jalali_date_edit import JalaliDateEdit
from ...database.db_handler import DatabaseHandler
from .dialog_style import DIALOG_STYLE, BUTTON_STYLE, CANCEL_BUTTON_STYLE


class PlanDialog(QtWidgets.QDialog):
    def __init__(self, parent=None, cage_id=None, plan=None):
        super().__init__(parent)
        self.setStyleSheet(DIALOG_STYLE)
        
        self.db = DatabaseHandler()
        self.cage_id = cage_id
        self.plan = plan
        self.setWindowTitle("➕ برنامه جدید" if not plan else "✏️ ویرایش برنامه")
        self.setModal(True)
        self.resize(450, 420)
        self.setup_ui()
        if plan:
            self.load_plan_data()

    def setup_ui(self):
        layout = QtWidgets.QFormLayout(self)
        layout.setLabelAlignment(QtCore.Qt.AlignRight)
        layout.setSpacing(12)
        layout.setContentsMargins(20, 20, 20, 20)

        # عنوان برنامه
        self.title_edit = QtWidgets.QLineEdit()
        self.title_edit.setPlaceholderText("عنوان برنامه")
        layout.addRow("عنوان:", self.title_edit)

        # نوع برنامه (فارسی)
        self.type_combo = QtWidgets.QComboBox()
        self.type_combo.addItems(["روزانه", "هفتگی", "ماهانه", "سالانه"])
        self.type_map = {
            "روزانه": "daily",
            "هفتگی": "weekly", 
            "ماهانه": "monthly",
            "سالانه": "yearly"
        }
        layout.addRow("نوع برنامه:", self.type_combo)

        # تاریخ شروع
        self.start_date = JalaliDateEdit()
        layout.addRow("از تاریخ:", self.start_date)

        # تاریخ پایان
        self.end_date = JalaliDateEdit()
        layout.addRow("تا تاریخ:", self.end_date)

        # یادداشت
        self.notes = QtWidgets.QTextEdit()
        self.notes.setPlaceholderText("یادداشت...")
        layout.addRow("یادداشت:", self.notes)

        # دکمه‌ها
        btn_layout = QtWidgets.QHBoxLayout()
        btn_layout.setSpacing(12)
        btn_layout.addStretch()

        ok_btn = QtWidgets.QPushButton("ذخیره")
        ok_btn.setFixedSize(90, 34)
        ok_btn.setStyleSheet(BUTTON_STYLE)
        ok_btn.clicked.connect(self.accept)

        cancel_btn = QtWidgets.QPushButton("انصراف")
        cancel_btn.setFixedSize(90, 34)
        cancel_btn.setStyleSheet(CANCEL_BUTTON_STYLE)
        cancel_btn.clicked.connect(self.reject)

        btn_layout.addWidget(ok_btn)
        btn_layout.addWidget(cancel_btn)
        layout.addRow(btn_layout)

    def load_plan_data(self):
        if self.plan:
            self.title_edit.setText(self.plan.get('plan_title', ''))
            type_en = self.plan.get('plan_type', 'monthly')
            for fa, en in self.type_map.items():
                if en == type_en:
                    self.type_combo.setCurrentText(fa)
                    break
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

        type_fa = self.type_combo.currentText()
        type_en = self.type_map.get(type_fa, "monthly")

        if self.plan:
            self.db.execute_query("""
                UPDATE production_plans 
                SET plan_title = %s, plan_type = %s, start_date = %s, end_date = %s, notes = %s
                WHERE id = %s
            """, (self.title_edit.text().strip(), type_en, start, end, 
                  self.notes.toPlainText(), self.plan['id']))
        else:
            self.db.execute_query("""
                INSERT INTO production_plans (plan_title, plan_type, start_date, end_date, cage_id, plan_status, notes)
                VALUES (%s, %s, %s, %s, %s, 'draft', %s)
            """, (self.title_edit.text().strip(), type_en, start, end, 
                  self.cage_id, self.notes.toPlainText()))

        super().accept()