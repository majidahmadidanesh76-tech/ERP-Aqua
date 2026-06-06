"""
دیالوگ شروع/ویرایش دوره پرورش قفس
"""
""
from PyQt5 import QtWidgets, QtCore

from .base_dialog import BaseDialog
from ...widgets.jalali_date_edit import JalaliDateEdit

class CycleDialog(BaseDialog):
    """دیالوگ شروع یا ویرایش دوره پرورش قفس"""

    def __init__(self, parent=None, mode="start", current_cycle=None):
        self.mode = mode
        self.current_cycle = current_cycle
        if mode == "edit" and current_cycle:
            title = "✏️ ویرایش دوره پرورش"
        else:
            title = "🚀 شروع دوره پرورش"
        super().__init__(parent, title=title, width=450, height=480)
        self.setup_ui()
        if mode == "edit" and current_cycle:
            self.load_cycle_data()

    def setup_ui(self):
        layout = QtWidgets.QFormLayout(self)
        layout.setLabelAlignment(QtCore.Qt.AlignRight)
        layout.setSpacing(10)

        self.date_edit = JalaliDateEdit()
        layout.addRow("تاریخ رهاسازی:", self.date_edit)

        self.species_combo = QtWidgets.QComboBox()
        self.species_combo.addItems(["قزلآلا", "کپور", "تیلاپیا", "ماهیان خاویاری", "سفید", "کفال", "سایر"])
        layout.addRow("گونه ماهی:", self.species_combo)

        self.initial_count = QtWidgets.QSpinBox()
        self.initial_count.setRange(0, 1000000)
        self.initial_count.setSingleStep(100)
        self.initial_count.setSuffix(" عدد")
        layout.addRow("تعداد ماهی رهاسازی شده:", self.initial_count)

        self.initial_weight = QtWidgets.QDoubleSpinBox()
        self.initial_weight.setRange(0, 10000)
        self.initial_weight.setSingleStep(10)
        self.initial_weight.setSuffix(" گرم")
        layout.addRow("وزن اولیه ماهی:", self.initial_weight)

        self.target_weight = QtWidgets.QDoubleSpinBox()
        self.target_weight.setRange(0, 10000)
        self.target_weight.setSingleStep(50)
        self.target_weight.setSuffix(" گرم")
        layout.addRow("وزن هدف برای برداشت:", self.target_weight)

        self.note = QtWidgets.QTextEdit()
        self.note.setMaximumHeight(80)
        self.note.setPlaceholderText("توضیحات اضافی...")
        layout.addRow("یادداشت:", self.note)

        self.add_button_box(layout)

    def load_cycle_data(self):
        """بارگذاری داده‌های دوره برای ویرایش"""
        if self.current_cycle:
            self.date_edit.set_jalali_date(self.current_cycle.start_date)
            idx = self.species_combo.findText(self.current_cycle.species)
            if idx >= 0:
                self.species_combo.setCurrentIndex(idx)
            self.initial_count.setValue(self.current_cycle.initial_count)
            self.initial_weight.setValue(self.current_cycle.initial_weight)
            self.target_weight.setValue(self.current_cycle.target_weight)
            self.note.setText(self.current_cycle.note)

    def validate_data(self):
        if self.initial_count.value() == 0:
            self.show_error("لطفاً تعداد ماهی رهاسازی شده را وارد کنید")
            return False
        if self.initial_weight.value() == 0:
            self.show_error("لطفاً وزن اولیه ماهی را وارد کنید")
            return False
        if self.target_weight.value() == 0:
            self.show_error("لطفاً وزن هدف برای برداشت را وارد کنید")
            return False
        return True

    def accept(self):
        if not self.validate_data():
            return

        self.result_data = {
            "date": self.date_edit.get_jalali_date(),
            "species": self.species_combo.currentText(),
            "initial_count": self.initial_count.value(),
            "initial_weight": self.initial_weight.value(),
            "target_weight": self.target_weight.value(),
            "note": self.note.toPlainText()
        }

        super().accept()