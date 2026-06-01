"""
دیالوگ ثبت زیست‌توده (تخمین وزن و تعداد ماهی) برای ERP-Aqua
"""

from PyQt5 import QtWidgets, QtCore

from .base_dialog import BaseDialog
from src.core.models import Biomass
from ...widgets.jalali_date_edit import JalaliDateEdit


class BiomassDialog(BaseDialog):
    """دیالوگ ثبت یا ویرایش زیست‌توده قفس"""

    def __init__(self, parent=None, farms=None, current_farm=None, current_mooring=None, biomass=None):
        self.farms = farms or []
        self.current_farm = current_farm
        self.current_mooring = current_mooring
        self.biomass = biomass if biomass else Biomass()

        edit_mode = biomass is not None
        title = "ویرایش زیست‌توده" if edit_mode else "ثبت زیست‌توده (تخمین وزن و تعداد)"
        super().__init__(parent, title=title, edit_mode=edit_mode, width=450, height=500)
        self.setup_ui()

    def setup_ui(self):
        layout = QtWidgets.QFormLayout(self)
        layout.setLabelAlignment(QtCore.Qt.AlignRight)
        layout.setSpacing(10)

        # انتخاب قفس
        self.cage_combo = QtWidgets.QComboBox()
        self.cage_combo.addItem("--- انتخاب قفس ---")
        if self.current_farm and self.current_mooring:
            for cage in self.current_mooring.cages:
                self.cage_combo.addItem(f"{cage.id} (قطر: {cage.diameter}m)", cage.id)
        if self.biomass.cage_id:
            idx = self.cage_combo.findData(self.biomass.cage_id)
            if idx >= 0:
                self.cage_combo.setCurrentIndex(idx)
        layout.addRow("قفس:", self.cage_combo)

        # تاریخ نمونه‌برداری
        self.date_edit = JalaliDateEdit()
        if self.biomass.date:
            self.date_edit.set_jalali_date(self.biomass.date)
        layout.addRow("تاریخ نمونه‌برداری:", self.date_edit)

        # وزن تخمینی (گرم)
        self.estimated_weight = QtWidgets.QDoubleSpinBox()
        self.estimated_weight.setRange(0, 10000)
        self.estimated_weight.setSingleStep(10)
        self.estimated_weight.setSuffix(" گرم")
        self.estimated_weight.setValue(self.biomass.estimated_weight)
        layout.addRow("وزن تخمینی ماهی:", self.estimated_weight)

        # تعداد تخمینی باقیمانده
        self.estimated_count = QtWidgets.QSpinBox()
        self.estimated_count.setRange(0, 1000000)
        self.estimated_count.setSingleStep(100)
        self.estimated_count.setSuffix(" عدد")
        self.estimated_count.setValue(self.biomass.estimated_count)
        layout.addRow("تعداد تخمینی ماهی:", self.estimated_count)

        # تعداد نمونه گرفته شده
        self.sample_size = QtWidgets.QSpinBox()
        self.sample_size.setRange(0, 1000)
        self.sample_size.setSuffix(" عدد")
        self.sample_size.setValue(self.biomass.sample_size)
        layout.addRow("تعداد نمونه (برای تخمین):", self.sample_size)

        # یادداشت
        self.note = QtWidgets.QTextEdit()
        self.note.setMaximumHeight(80)
        self.note.setPlaceholderText("توضیحات اضافی (روش نمونه‌برداری، ...)")
        self.note.setText(self.biomass.note)
        layout.addRow("یادداشت:", self.note)

        self.add_button_box(layout)

    def validate_data(self):
        if not self.cage_combo.currentData():
            self.show_error("لطفاً قفس را انتخاب کنید")
            return False
        if self.estimated_weight.value() == 0 and self.estimated_count.value() == 0:
            self.show_error("لطفاً حداقل وزن یا تعداد را وارد کنید")
            return False
        return True

    def accept(self):
        if not self.validate_data():
            return

        self.biomass.cage_id = self.cage_combo.currentData()
        self.biomass.date = self.date_edit.get_jalali_date()
        self.biomass.estimated_weight = self.estimated_weight.value()
        self.biomass.estimated_count = self.estimated_count.value()
        self.biomass.sample_size = self.sample_size.value()
        self.biomass.note = self.note.toPlainText()

        if self.current_farm:
            self.biomass.farm_id = self.current_farm.id
        if self.current_mooring:
            self.biomass.mooring_id = self.current_mooring.id

        super().accept()