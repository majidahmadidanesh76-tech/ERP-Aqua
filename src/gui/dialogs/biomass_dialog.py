"""
دیالوگ ثبت زیست‌توده (تخمین وزن و تعداد ماهی) برای ERP-Aqua
"""

import json
import os

from PyQt5 import QtWidgets, QtCore

from .base_dialog import BaseDialog
from src.core.models import Biomass
from ...widgets.jalali_date_edit import JalaliDateEdit


class BiomassDialog(BaseDialog):
    def __init__(self, parent=None, farms=None, current_farm=None, current_mooring=None, 
                 biomass=None, harvests=None, default_initial_count=0):
        self.farms = farms or []
        self.current_farm = current_farm
        self.current_mooring = current_mooring
        self.biomass = biomass if biomass else Biomass()
        self.mortalities = []
        self.harvests = harvests if harvests else []
        self.previous_biomasses = []
        self.default_initial_count = default_initial_count
        self.load_mortality_data()
        self.load_previous_biomasses()
        title = "ویرایش زیست‌توده" if biomass else "ثبت زیست‌توده"
        super().__init__(parent, title=title, edit_mode=biomass is not None, width=500, height=620)
        self.setup_ui()
    
    def load_mortality_data(self):
        self.mortalities = []
        data_file = "aquaculture_data.json"
        if not self.current_farm or not self.current_mooring:
            return
        key = f"{self.current_farm.id}_{self.current_mooring.id}"
        if os.path.exists(data_file):
            try:
                with open(data_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    for item in data.get('mortalities', []):
                        if item.get('key') == key:
                            self.mortalities = item.get('mortalities', [])
                            break
            except:
                pass
    
    def load_previous_biomasses(self):
        self.previous_biomasses = []
        data_file = "aquaculture_data.json"
        if not self.current_farm or not self.current_mooring:
            return
        key = f"{self.current_farm.id}_{self.current_mooring.id}"
        if os.path.exists(data_file):
            try:
                with open(data_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    for item in data.get('biomasses', []):
                        if item.get('key') == key:
                            self.previous_biomasses = item.get('biomasses', [])
                            break
            except:
                pass
    
    def get_last_biomass(self, cage_id):
        last = None
        for b in self.previous_biomasses:
            if b.get('cage_id') == cage_id:
                if last is None or b.get('date', '') > last.get('date', ''):
                    last = b
        return last
    
    def get_total_mortality_and_harvest(self, cage_id):
        total = 0
        for m in self.mortalities:
            if m.get('cage_id') == cage_id:
                total += m.get('count', 0)
        for h in self.harvests:
            if hasattr(h, 'cage_id'):
                if h.cage_id == cage_id:
                    total += h.harvest_count
            elif isinstance(h, dict):
                if h.get('cage_id') == cage_id:
                    total += h.get('harvest_count', 0)
        return total
    
    def get_initial_count_from_previous(self, cage_id):
        last_biomass = self.get_last_biomass(cage_id)
        if last_biomass:
            return last_biomass.get('initial_count', 0)
        return 0
    
    def setup_ui(self):
        layout = QtWidgets.QFormLayout(self)
        layout.setLabelAlignment(QtCore.Qt.AlignRight)
        layout.setSpacing(10)

        self.cage_combo = QtWidgets.QComboBox()
        self.cage_combo.addItem("--- انتخاب قفس ---")
        if self.current_farm and self.current_mooring:
            for cage in self.current_mooring.cages:
                self.cage_combo.addItem(f"{cage.id} (قطر: {cage.diameter}m)", cage.id)
        if self.biomass.cage_id:
            idx = self.cage_combo.findData(self.biomass.cage_id)
            if idx >= 0:
                self.cage_combo.setCurrentIndex(idx)
        
        self.cage_combo.currentIndexChanged.connect(self.on_cage_changed)
        layout.addRow("قفس:", self.cage_combo)

        self.date_edit = JalaliDateEdit()
        if self.biomass.date:
            self.date_edit.set_jalali_date(self.biomass.date)
        layout.addRow("تاریخ نمونه‌برداری:", self.date_edit)

        self.initial_count = QtWidgets.QSpinBox()
        self.initial_count.setRange(0, 1000000)
        self.initial_count.setSingleStep(100)
        self.initial_count.setSuffix(" عدد")
        
        # اولویت: مقدار ذخیره شده > مقدار پیش‌فرض از دوره > مقدار از رکوردهای قبلی
        if self.biomass.initial_count > 0:
            self.initial_count.setValue(self.biomass.initial_count)
        elif self.default_initial_count > 0:
            self.initial_count.setValue(self.default_initial_count)
        else:
            initial = self.get_initial_count_from_previous(self.cage_combo.currentData())
            if initial > 0:
                self.initial_count.setValue(initial)
        layout.addRow("تعداد اولیه (رهاسازی):", self.initial_count)

        self.sample_size = QtWidgets.QSpinBox()
        self.sample_size.setRange(0, 1000)
        self.sample_size.setSuffix(" عدد")
        self.sample_size.setValue(self.biomass.sample_size)
        layout.addRow("تعداد نمونه:", self.sample_size)

        self.estimated_weight = QtWidgets.QDoubleSpinBox()
        self.estimated_weight.setRange(0, 10000)
        self.estimated_weight.setSingleStep(10)
        self.estimated_weight.setSuffix(" گرم")
        self.estimated_weight.setValue(self.biomass.estimated_weight)
        layout.addRow("وزن تخمینی:", self.estimated_weight)

        count_layout = QtWidgets.QHBoxLayout()
        self.estimated_count = QtWidgets.QSpinBox()
        self.estimated_count.setRange(0, 1000000)
        self.estimated_count.setSingleStep(100)
        self.estimated_count.setSuffix(" عدد")
        
        self.calc_btn = QtWidgets.QPushButton("🔢 محاسبه از تلفات و برداشت")
        self.calc_btn.setStyleSheet("QPushButton { background-color: #0E639C; color: white; border: none; border-radius: 4px; padding: 4px 8px; }")
        self.calc_btn.clicked.connect(self.calculate_estimated_count)
        
        count_layout.addWidget(self.estimated_count)
        count_layout.addWidget(self.calc_btn)
        count_layout.addStretch()
        layout.addRow("تعداد تخمینی:", count_layout)

        self.note = QtWidgets.QTextEdit()
        self.note.setMaximumHeight(80)
        self.note.setPlaceholderText("توضیحات اضافی...")
        self.note.setText(self.biomass.note)
        layout.addRow("یادداشت:", self.note)

        info_label = QtWidgets.QLabel("💡 تعداد تخمینی = تعداد اولیه - (تلفات کل + برداشت کل)")
        info_label.setStyleSheet("color: #569CD6; font-size: 11px; padding: 5px;")
        layout.addRow(info_label)

        self.add_button_box(layout)
        
        self.calculate_estimated_count()
    
    def on_cage_changed(self):
        cage_id = self.cage_combo.currentData()
        if cage_id:
            initial = self.get_initial_count_from_previous(cage_id)
            if initial > 0 and self.initial_count.value() == 0:
                self.initial_count.setValue(initial)
        self.calculate_estimated_count()
    
    def calculate_estimated_count(self):
        cage_id = self.cage_combo.currentData()
        if not cage_id:
            return
        initial = self.initial_count.value()
        total_removed = self.get_total_mortality_and_harvest(cage_id)
        estimated = initial - total_removed
        if estimated < 0:
            estimated = 0
        self.estimated_count.setValue(estimated)

    def validate_data(self):
        if not self.cage_combo.currentData():
            self.show_error("لطفاً قفس را انتخاب کنید")
            return False
        if self.initial_count.value() == 0:
            self.show_error("لطفاً تعداد اولیه ماهی را وارد کنید")
            return False
        if self.estimated_weight.value() == 0:
            self.show_error("لطفاً وزن تخمینی ماهی را وارد کنید")
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
        self.biomass.initial_count = self.initial_count.value()
        self.biomass.note = self.note.toPlainText()
        if self.current_farm:
            self.biomass.farm_id = self.current_farm.id
        if self.current_mooring:
            self.biomass.mooring_id = self.current_mooring.id
        super().accept()