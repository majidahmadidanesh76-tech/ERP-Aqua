"""
دیالوگ ثبت پارامترهای آب برای ERP-Aqua
"""

from PyQt5 import QtWidgets, QtCore

from .base_dialog import BaseDialog
from src.core.models import WaterParameter
from ...widgets.jalali_date_edit import JalaliDateEdit


class WaterParameterDialog(BaseDialog):
    """دیالوگ ثبت یا ویرایش پارامترهای آب"""

    def __init__(self, parent=None, farms=None, current_farm=None, current_mooring=None, parameter=None):
        self.farms = farms or []
        self.current_farm = current_farm
        self.current_mooring = current_mooring
        self.parameter = parameter if parameter else WaterParameter()

        edit_mode = parameter is not None
        title = "ویرایش پارامترهای آب" if edit_mode else "ثبت پارامترهای آب"
        super().__init__(parent, title=title, edit_mode=edit_mode, width=450, height=520)
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
        if self.parameter.cage_id:
            idx = self.cage_combo.findData(self.parameter.cage_id)
            if idx >= 0:
                self.cage_combo.setCurrentIndex(idx)
        layout.addRow("قفس:", self.cage_combo)

        # تاریخ
        self.date_edit = JalaliDateEdit()
        if self.parameter.date:
            self.date_edit.set_jalali_date(self.parameter.date)
        layout.addRow("تاریخ:", self.date_edit)

        # زمان
        self.time_combo = QtWidgets.QComboBox()
        self.time_combo.addItems([
            "صبح (6-8)",
            "ظهر (12-14)",
            "عصر (16-18)",
            "شب (20-22)"
        ])
        if self.parameter.time:
            idx = self.time_combo.findText(self.parameter.time)
            if idx >= 0:
                self.time_combo.setCurrentIndex(idx)
        layout.addRow("زمان اندازه‌گیری:", self.time_combo)

        # دما
        self.temperature = QtWidgets.QDoubleSpinBox()
        self.temperature.setRange(-5, 45)
        self.temperature.setSingleStep(0.1)
        self.temperature.setSuffix(" °C")
        self.temperature.setValue(self.parameter.temperature)
        layout.addRow("دما:", self.temperature)

        # اکسیژن محلول
        self.dissolved_oxygen = QtWidgets.QDoubleSpinBox()
        self.dissolved_oxygen.setRange(0, 20)
        self.dissolved_oxygen.setSingleStep(0.1)
        self.dissolved_oxygen.setSuffix(" mg/L")
        self.dissolved_oxygen.setValue(self.parameter.dissolved_oxygen)
        layout.addRow("اکسیژن محلول:", self.dissolved_oxygen)

        # شوری
        self.salinity = QtWidgets.QDoubleSpinBox()
        self.salinity.setRange(0, 50)
        self.salinity.setSingleStep(0.5)
        self.salinity.setSuffix(" ppt")
        self.salinity.setValue(self.parameter.salinity)
        layout.addRow("شوری:", self.salinity)

        # pH
        self.ph = QtWidgets.QDoubleSpinBox()
        self.ph.setRange(0, 14)
        self.ph.setSingleStep(0.1)
        self.ph.setValue(self.parameter.ph)
        layout.addRow("pH:", self.ph)

        # یادداشت
        self.note = QtWidgets.QTextEdit()
        self.note.setMaximumHeight(80)
        self.note.setPlaceholderText("توضیحات اضافی...")
        self.note.setText(self.parameter.note)
        layout.addRow("یادداشت:", self.note)

        self.add_button_box(layout)

    def validate_data(self):
        if not self.cage_combo.currentData():
            self.show_error("لطفاً قفس را انتخاب کنید")
            return False
        if self.temperature.value() == 0 and self.dissolved_oxygen.value() == 0:
            self.show_error("لطفاً حداقل دما یا اکسیژن را وارد کنید")
            return False
        return True

    def accept(self):
        if not self.validate_data():
            return

        self.parameter.cage_id = self.cage_combo.currentData()
        self.parameter.date = self.date_edit.get_jalali_date()
        self.parameter.time = self.time_combo.currentText()
        self.parameter.temperature = self.temperature.value()
        self.parameter.dissolved_oxygen = self.dissolved_oxygen.value()
        self.parameter.salinity = self.salinity.value()
        self.parameter.ph = self.ph.value()
        self.parameter.note = self.note.toPlainText()

        if self.current_farm:
            self.parameter.farm_id = self.current_farm.id
        if self.current_mooring:
            self.parameter.mooring_id = self.current_mooring.id

        super().accept()