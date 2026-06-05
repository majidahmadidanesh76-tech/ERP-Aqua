"""
دیالوگ ثبت زیست توده (تخمین وزن و تعداد ماهی) برای ERP-Aqua
نسخه نهایی - بدون وزن کل تخمینی
"""

from PyQt5 import QtWidgets, QtCore

from .base_dialog import BaseDialog
from ...core.models import Biomass
from ...widgets.jalali_date_edit import JalaliDateEdit
from ...database.db_handler import DatabaseHandler


class BiomassDialog(BaseDialog):
    def __init__(self, parent=None, farms=None, current_farm=None, current_mooring=None, 
                 biomass=None, harvests=None, default_initial_count=0):
        self.db = DatabaseHandler()
        self.farms = farms or []
        self.current_farm = current_farm
        self.current_mooring = current_mooring
        self.biomass = biomass if biomass else Biomass()
        self.harvests = harvests if harvests else []
        self.default_initial_count = default_initial_count
        self.current_cycle_id = None
        
        # دریافت cycle_id جاری
        if current_farm and current_mooring and hasattr(current_mooring, 'cages') and current_mooring.cages:
            cage_id = current_mooring.cages[0].id if current_mooring.cages else None
            if cage_id:
                active_cycle = self.db.get_active_cycle(cage_id)
                if active_cycle:
                    self.current_cycle_id = active_cycle.id
        
        title = "ویرایش زیست توده" if biomass else "ثبت زیست توده"
        super().__init__(parent, title=title, edit_mode=biomass is not None, width=500, height=550)
        self.setup_ui()

    def get_total_mortality_and_harvest(self, cage_id):
        """محاسبه کل تلفات و برداشت از دیتابیس"""
        if not self.current_cycle_id:
            return 0
        
        # دریافت کل تلفات
        mortalities = self.db.fetch_one(
            "SELECT IFNULL(SUM(count), 0) as total FROM mortalities WHERE cycle_id = %s",
            (self.current_cycle_id,)
        )
        total_mortality = mortalities['total'] if mortalities else 0
        
        # دریافت کل برداشت
        harvests = self.db.fetch_one(
            "SELECT IFNULL(SUM(harvest_count), 0) as total FROM harvests WHERE cycle_id = %s",
            (self.current_cycle_id,)
        )
        total_harvest = harvests['total'] if harvests else 0
        
        return int(total_mortality) + int(total_harvest)

    def setup_ui(self):
        layout = QtWidgets.QFormLayout(self)
        layout.setLabelAlignment(QtCore.Qt.AlignRight)
        layout.setSpacing(12)
        layout.setContentsMargins(15, 15, 15, 15)

        # انتخاب قفس
        self.cage_combo = QtWidgets.QComboBox()
        self.cage_combo.addItem("--- انتخاب قفس ---")
        if self.current_farm and self.current_mooring:
            for cage in self.current_mooring.cages:
                self.cage_combo.addItem(f"{cage.id}", cage.id)
        
        if self.biomass.cage_id:
            idx = self.cage_combo.findData(self.biomass.cage_id)
            if idx >= 0:
                self.cage_combo.setCurrentIndex(idx)

        self.cage_combo.currentIndexChanged.connect(self.on_cage_changed)
        layout.addRow("قفس:", self.cage_combo)

        # تاریخ
        self.date_edit = JalaliDateEdit()
        if self.biomass.date:
            self.date_edit.set_jalali_date(self.biomass.date)
        else:
            import jdatetime
            today = jdatetime.date.today()
            self.date_edit.set_jalali_date(f"{today.year}/{today.month:02d}/{today.day:02d}")
        layout.addRow("تاریخ نمونه‌برداری:", self.date_edit)

        # تعداد اولیه رهاسازی
        self.initial_count = QtWidgets.QSpinBox()
        self.initial_count.setRange(0, 1000000)
        self.initial_count.setSingleStep(100)
        self.initial_count.setSuffix(" عدد")
        self.initial_count.valueChanged.connect(self.calculate_estimated_count)

        if self.biomass.initial_count > 0:
            self.initial_count.setValue(self.biomass.initial_count)
        elif self.default_initial_count > 0:
            self.initial_count.setValue(self.default_initial_count)
        layout.addRow("تعداد اولیه (رهاسازی):", self.initial_count)

        # تعداد نمونه
        self.sample_size = QtWidgets.QSpinBox()
        self.sample_size.setRange(0, 10000)
        self.sample_size.setSingleStep(10)
        self.sample_size.setSuffix(" عدد")
        self.sample_size.setValue(self.biomass.sample_size)
        layout.addRow("تعداد نمونه:", self.sample_size)

        # وزن تخمینی
        self.estimated_weight = QtWidgets.QDoubleSpinBox()
        self.estimated_weight.setRange(0, 100000)
        self.estimated_weight.setSingleStep(50)
        self.estimated_weight.setSuffix(" گرم")
        self.estimated_weight.setValue(self.biomass.estimated_weight)
        self.estimated_weight.valueChanged.connect(self.calculate_estimated_count)
        layout.addRow("وزن تخمینی (گرم):", self.estimated_weight)

        # تعداد تخمینی (فقط خواندنی)
        self.estimated_count = QtWidgets.QSpinBox()
        self.estimated_count.setRange(0, 1000000)
        self.estimated_count.setSingleStep(100)
        self.estimated_count.setSuffix(" عدد")
        self.estimated_count.setReadOnly(True)
        self.estimated_count.setStyleSheet("background-color: #2D2D30; color: #4EC9B0; font-weight: bold;")
        layout.addRow("تعداد تخمینی (باقیمانده):", self.estimated_count)

        # دکمه محاسبه
        self.calc_btn = QtWidgets.QPushButton("🔄 محاسبه از تلفات و برداشت")
        self.calc_btn.setStyleSheet("""
            QPushButton {
                background-color: #0E639C;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 6px 12px;
            }
            QPushButton:hover {
                background-color: #1177BB;
            }
        """)
        self.calc_btn.clicked.connect(self.calculate_estimated_count)
        layout.addRow("", self.calc_btn)

        # یادداشت
        self.note = QtWidgets.QTextEdit()
        self.note.setMaximumHeight(80)
        self.note.setPlaceholderText("توضیحات اضافی...")
        self.note.setText(self.biomass.note)
        layout.addRow("یادداشت:", self.note)

        self.add_button_box(layout)

        # محاسبه اولیه
        self.calculate_estimated_count()

    def on_cage_changed(self):
        self.calculate_estimated_count()

    def calculate_estimated_count(self):
        """محاسبه تعداد تخمینی"""
        if not hasattr(self, 'estimated_count'):
            return
        
        initial = self.initial_count.value()
        
        # اگر cycle_id نداریم، فقط تعداد اولیه را نشان بده
        if not self.current_cycle_id:
            self.estimated_count.setValue(initial)
            return
        
        total_removed = self.get_total_mortality_and_harvest(None)
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