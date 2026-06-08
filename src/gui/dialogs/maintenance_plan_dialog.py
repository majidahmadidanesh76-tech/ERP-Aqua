"""
دیالوگ ایجاد/ویرایش برنامه نت - بدون فیلد نوع تجهیزات
"""

from PyQt5 import QtWidgets, QtCore
from ...widgets.jalali_date_edit import JalaliDateEdit
from .dialog_style import DIALOG_STYLE, BUTTON_STYLE, CANCEL_BUTTON_STYLE

class MaintenancePlanDialog(QtWidgets.QDialog):
    def __init__(self, parent=None, plan=None):
        super().__init__(parent)
        self.setStyleSheet(DIALOG_STYLE)
        self.plan = plan
        self.setWindowTitle("➕ ایجاد برنامه نت جدید" if not plan else "✏️ ویرایش برنامه نت")
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

        self.title_edit = QtWidgets.QLineEdit()
        self.title_edit.setPlaceholderText("مثال: برنامه شستشوی دورهای تورها")
        layout.addRow("عنوان برنامه:", self.title_edit)

        self.type_combo = QtWidgets.QComboBox()
        self.type_combo.addItems(["روزانه", "هفتگی", "ماهانه", "سالانه"])
        self.type_map = {
            "روزانه": "daily",
            "هفتگی": "weekly",
            "ماهانه": "monthly",
            "سالانه": "yearly"
        }
        layout.addRow("نوع برنامه:", self.type_combo)

        self.start_date = JalaliDateEdit()
        layout.addRow("تاریخ شروع:", self.start_date)

        self.end_date = JalaliDateEdit()
        layout.addRow("تاریخ پایان:", self.end_date)

        self.notes = QtWidgets.QTextEdit()
        self.notes.setMaximumHeight(80)
        self.notes.setPlaceholderText("توضیحات اضافی...")
        layout.addRow("یادداشت:", self.notes)

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
            plan_type = self.plan.get('plan_type', 'monthly')
            for fa, en in self.type_map.items():
                if en == plan_type:
                    self.type_combo.setCurrentText(fa)
                    break
            
            start = self.plan.get('start_date', '')
            if start and hasattr(start, 'strftime'):
                start = start.strftime('%Y/%m/%d')
            elif start and '-' in str(start):
                start = str(start).replace('-', '/')
            else:
                start = str(start) if start else ''
            
            end = self.plan.get('end_date', '')
            if end and hasattr(end, 'strftime'):
                end = end.strftime('%Y/%m/%d')
            elif end and '-' in str(end):
                end = str(end).replace('-', '/')
            else:
                end = str(end) if end else ''
            
            self.start_date.set_jalali_date(start)
            self.end_date.set_jalali_date(end)
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
            "plan_type": self.type_map.get(self.type_combo.currentText(), "monthly"),
            "start_date": start,
            "end_date": end,
            "notes": self.notes.toPlainText()
        }

        super().accept()