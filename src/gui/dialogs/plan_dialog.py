"""
دیالوگ ایجاد/ویرایش برنامه پرورش
"""

from PyQt5 import QtWidgets, QtCore
from ...widgets.jalali_date_edit import JalaliDateEdit
from ...database.db_handler import DatabaseHandler


class PlanDialog(QtWidgets.QDialog):
    def __init__(self, parent=None, cage_id=None, plan=None):
        super().__init__(parent)
        self.db = DatabaseHandler()
        self.cage_id = cage_id
        self.plan = plan
        self.setWindowTitle("➕ ایجاد برنامه پرورش جدید" if not plan else "✏️ ویرایش برنامه پرورش")
        self.setModal(True)
        self.resize(500, 480)
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
        self.title_edit.setPlaceholderText("مثال: برنامه پرورش خرداد ۱۴۰۵")
        layout.addRow("عنوان برنامه:", self.title_edit)

        # نوع برنامه (فقط weekly و monthly مطابق دیتابیس)
        self.type_combo = QtWidgets.QComboBox()
        self.type_combo.addItems(["weekly", "monthly"])
        layout.addRow("نوع برنامه:", self.type_combo)

        # تاریخ شروع
        self.start_date = JalaliDateEdit()
        layout.addRow("تاریخ شروع:", self.start_date)

        # تاریخ پایان
        self.end_date = JalaliDateEdit()
        layout.addRow("تاریخ پایان:", self.end_date)

        # یادداشت
        self.notes = QtWidgets.QTextEdit()
        self.notes.setMaximumHeight(80)
        self.notes.setPlaceholderText("توضیحات اضافی...")
        layout.addRow("یادداشت:", self.notes)

        # دکمه‌ها
        btn_layout = QtWidgets.QHBoxLayout()
        ok_btn = QtWidgets.QPushButton("ذخیره")
        cancel_btn = QtWidgets.QPushButton("انصراف")
        cancel_btn.clicked.connect(self.reject)
        ok_btn.clicked.connect(self.accept)
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
        if start > end:
            QtWidgets.QMessageBox.warning(self, "خطا", "تاریخ شروع نباید از تاریخ پایان بزرگتر باشد")
            return

        if self.plan:
            # ویرایش برنامه موجود
            self.db.execute_query("""
                UPDATE production_plans 
                SET plan_title = %s, plan_type = %s, start_date = %s, end_date = %s, notes = %s
                WHERE id = %s
            """, (self.title_edit.text().strip(), self.type_combo.currentText(), start, end, 
                  self.notes.toPlainText(), self.plan['id']))
        else:
            # ایجاد برنامه جدید
            self.db.execute_query("""
                INSERT INTO production_plans (plan_title, plan_type, start_date, end_date, cage_id, plan_status, notes)
                VALUES (%s, %s, %s, %s, %s, 'draft', %s)
            """, (self.title_edit.text().strip(), self.type_combo.currentText(), start, end, 
                  self.cage_id, self.notes.toPlainText()))

        super().accept()