"""
دیالوگ ثبت زیست توده (تخمین وزن و تعداد ماهی) برای ERP-Aqua
با دکمه تقویم شمسی
"""

from PyQt5 import QtWidgets, QtCore

from .base_dialog import BaseDialog
from ...core.models import Biomass
from ...widgets.persian_calendar import PersianCalendar
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
        self.current_cage_id = None

        title = "ویرایش زیست توده" if biomass else "ثبت زیست توده"
        super().__init__(parent, title=title, edit_mode=biomass is not None, width=580, height=520)
        self.setup_ui()

    def get_total_mortality_and_harvest(self, cycle_id, cage_id):
        """محاسبه کل تلفات و برداشت برای یک دوره و قفس خاص"""
        if not cycle_id or not cage_id:
            return 0

        mortalities = self.db.fetch_one(
            "SELECT IFNULL(SUM(count), 0) as total FROM mortalities WHERE cycle_id = %s",
            (cycle_id,)
        )
        total_mortality = mortalities['total'] if mortalities else 0

        harvests_result = self.db.fetch_one(
            "SELECT IFNULL(SUM(harvest_count), 0) as total FROM harvests WHERE cycle_id = %s",
            (cycle_id,)
        )
        total_harvest = harvests_result['total'] if harvests_result else 0

        return int(total_mortality) + int(total_harvest)

    def get_active_cycle_for_cage(self, cage_id):
        if not cage_id:
            return None
        return self.db.get_active_cycle(cage_id)

    def setup_ui(self):
        self.setMinimumSize(580, 520)
        
        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.setSpacing(10)
        main_layout.setContentsMargins(15, 15, 15, 15)

        label_style = "color: #C8C8C8; font-weight: bold; min-width: 120px;"
        field_style = """
            QComboBox, QSpinBox, QDoubleSpinBox, QTextEdit, QLineEdit {
                background-color: #3C3C3C;
                border: 1px solid #3E3E42;
                border-radius: 4px;
                padding: 5px 8px;
                color: #C8C8C8;
                font-size: 12px;
                min-height: 28px;
                max-height: 28px;
            }
            QTextEdit {
                min-height: 55px;
                max-height: 55px;
            }
            QComboBox:focus, QSpinBox:focus, QDoubleSpinBox:focus, QTextEdit:focus, QLineEdit:focus {
                border-color: #569CD6;
            }
            QComboBox::drop-down {
                border: none;
                width: 20px;
            }
            QComboBox QAbstractItemView {
                background-color: #3C3C3C;
                color: #C8C8C8;
                selection-background-color: #0E639C;
            }
            QSpinBox::up-button, QSpinBox::down-button,
            QDoubleSpinBox::up-button, QDoubleSpinBox::down-button {
                width: 18px;
                background-color: #3C3C3C;
            }
            QSpinBox::up-button:hover, QSpinBox::down-button:hover,
            QDoubleSpinBox::up-button:hover, QDoubleSpinBox::down-button:hover {
                background-color: #569CD6;
            }
            QPushButton {
                background-color: #0E639C;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 5px 12px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #1177BB;
            }
        """

        # سطر 1: قفس
        row1 = QtWidgets.QHBoxLayout()
        row1.setSpacing(8)
        label1 = QtWidgets.QLabel("قفس:")
        label1.setStyleSheet(label_style)
        self.cage_combo = QtWidgets.QComboBox()
        self.cage_combo.setStyleSheet(field_style)
        self.cage_combo.addItem("--- انتخاب قفس ---", None)
        if self.current_farm and self.current_mooring:
            for cage in self.current_mooring.cages:
                self.cage_combo.addItem(cage.id, cage.id)
        if self.biomass.cage_id:
            idx = self.cage_combo.findData(self.biomass.cage_id)
            if idx >= 0:
                self.cage_combo.setCurrentIndex(idx)
        self.cage_combo.currentIndexChanged.connect(self.on_cage_changed)
        row1.addWidget(label1)
        row1.addWidget(self.cage_combo, 1)
        main_layout.addLayout(row1)

        # سطر 2: تاریخ با دکمه تقویم
        row2 = QtWidgets.QHBoxLayout()
        row2.setSpacing(8)
        label2 = QtWidgets.QLabel("تاریخ نمونه‌برداری:")
        label2.setStyleSheet(label_style)
        
        self.date_display = QtWidgets.QLineEdit()
        self.date_display.setReadOnly(True)
        self.date_display.setPlaceholderText("YYYY/MM/DD")
        self.date_display.setStyleSheet(field_style)
        self.date_display.setMinimumHeight(28)
        self.date_display.setMaximumHeight(28)
        
        self.calendar_btn = QtWidgets.QPushButton("📅")
        self.calendar_btn.setFixedSize(32, 28)
        self.calendar_btn.setToolTip("انتخاب تاریخ از تقویم شمسی")
        self.calendar_btn.clicked.connect(self.open_persian_calendar)
        self.calendar_btn.setStyleSheet("""
            QPushButton {
                background-color: #3C3C3C;
                border: 1px solid #3E3E42;
                border-radius: 4px;
                color: #C8C8C8;
                padding: 5px;
                font-weight: normal;
            }
            QPushButton:hover {
                background-color: #0E639C;
                border-color: #569CD6;
                color: white;
            }
        """)
        
        if self.biomass.date:
            self.date_display.setText(self.biomass.date)
        else:
            import jdatetime
            today = jdatetime.date.today()
            self.date_display.setText(f"{today.year}/{today.month:02d}/{today.day:02d}")
        
        row2.addWidget(label2)
        row2.addWidget(self.date_display, 1)
        row2.addWidget(self.calendar_btn)
        main_layout.addLayout(row2)

        # سطر 3: تعداد اولیه
        row3 = QtWidgets.QHBoxLayout()
        row3.setSpacing(8)
        label3 = QtWidgets.QLabel("تعداد اولیه (رهاسازی):")
        label3.setStyleSheet(label_style)
        self.initial_count = QtWidgets.QSpinBox()
        self.initial_count.setRange(0, 1000000)
        self.initial_count.setSingleStep(100)
        self.initial_count.setSuffix(" عدد")
        self.initial_count.valueChanged.connect(self.calculate_estimated_count)
        self.initial_count.setStyleSheet(field_style)
        
        if self.biomass.initial_count > 0:
            self.initial_count.setValue(self.biomass.initial_count)
        elif self.default_initial_count > 0:
            self.initial_count.setValue(self.default_initial_count)
        
        row3.addWidget(label3)
        row3.addWidget(self.initial_count, 1)
        main_layout.addLayout(row3)

        # سطر 4: تعداد نمونه
        row4 = QtWidgets.QHBoxLayout()
        row4.setSpacing(8)
        label4 = QtWidgets.QLabel("تعداد نمونه:")
        label4.setStyleSheet(label_style)
        self.sample_size = QtWidgets.QSpinBox()
        self.sample_size.setRange(0, 10000)
        self.sample_size.setSingleStep(10)
        self.sample_size.setSuffix(" عدد")
        self.sample_size.setValue(self.biomass.sample_size)
        self.sample_size.setStyleSheet(field_style)
        row4.addWidget(label4)
        row4.addWidget(self.sample_size, 1)
        main_layout.addLayout(row4)

        # سطر 5: وزن تخمینی
        row5 = QtWidgets.QHBoxLayout()
        row5.setSpacing(8)
        label5 = QtWidgets.QLabel("وزن تخمینی:")
        label5.setStyleSheet(label_style)
        self.estimated_weight = QtWidgets.QDoubleSpinBox()
        self.estimated_weight.setRange(0, 100000)
        self.estimated_weight.setSingleStep(50)
        self.estimated_weight.setSuffix(" گرم")
        self.estimated_weight.setValue(self.biomass.estimated_weight)
        self.estimated_weight.valueChanged.connect(self.calculate_estimated_count)
        self.estimated_weight.setStyleSheet(field_style)
        row5.addWidget(label5)
        row5.addWidget(self.estimated_weight, 1)
        main_layout.addLayout(row5)

        # سطر 6: تعداد تخمینی (فقط خواندنی)
        row6 = QtWidgets.QHBoxLayout()
        row6.setSpacing(8)
        label6 = QtWidgets.QLabel("تعداد تخمینی (باقیمانده):")
        label6.setStyleSheet(label_style)
        self.estimated_count = QtWidgets.QSpinBox()
        self.estimated_count.setRange(0, 1000000)
        self.estimated_count.setSingleStep(100)
        self.estimated_count.setSuffix(" عدد")
        self.estimated_count.setReadOnly(True)
        self.estimated_count.setStyleSheet(field_style + "background-color: #2D2D30; color: #4EC9B0; font-weight: bold;")
        row6.addWidget(label6)
        row6.addWidget(self.estimated_count, 1)
        main_layout.addLayout(row6)

        # دکمه محاسبه
        row7 = QtWidgets.QHBoxLayout()
        row7.setSpacing(8)
        self.calc_btn = QtWidgets.QPushButton("🔄 محاسبه از تلفات و برداشت")
        self.calc_btn.setFixedSize(200, 30)
        self.calc_btn.clicked.connect(self.calculate_estimated_count)
        row7.addStretch()
        row7.addWidget(self.calc_btn)
        row7.addStretch()
        main_layout.addLayout(row7)

        # سطر 8: یادداشت
        row8 = QtWidgets.QHBoxLayout()
        row8.setSpacing(8)
        label8 = QtWidgets.QLabel("یادداشت:")
        label8.setStyleSheet(label_style)
        self.note = QtWidgets.QTextEdit()
        self.note.setMaximumHeight(55)
        self.note.setMinimumHeight(55)
        self.note.setPlaceholderText("توضیحات اضافی...")
        self.note.setStyleSheet(field_style)
        self.note.setText(self.biomass.note)
        row8.addWidget(label8)
        row8.addWidget(self.note, 1)
        main_layout.addLayout(row8)

        # دکمه‌ها
        btn_layout = QtWidgets.QHBoxLayout()
        btn_layout.setContentsMargins(0, 10, 0, 0)
        btn_layout.addStretch()
        
        ok_btn = QtWidgets.QPushButton("ذخیره")
        ok_btn.setFixedSize(80, 30)
        ok_btn.clicked.connect(self.accept)
        btn_layout.addWidget(ok_btn)
        
        cancel_btn = QtWidgets.QPushButton("انصراف")
        cancel_btn.setFixedSize(80, 30)
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(cancel_btn)
        
        main_layout.addLayout(btn_layout)

        self.calculate_estimated_count()

    def open_persian_calendar(self):
        current_text = self.date_display.text()
        selected_date = None
        if current_text and current_text != "YYYY/MM/DD":
            try:
                import jdatetime
                parts = current_text.split('/')
                if len(parts) == 3:
                    selected_date = jdatetime.date(int(parts[0]), int(parts[1]), int(parts[2]))
            except:
                pass
        
        dialog = PersianCalendar(self, selected_date)
        if dialog.exec_():
            selected_date = dialog.get_selected_date()
            self.date_display.setText(selected_date)

    def on_cage_changed(self):
        cage_id = self.cage_combo.currentData()
        
        if cage_id:
            active_cycle = self.get_active_cycle_for_cage(cage_id)
            if active_cycle:
                self.current_cycle_id = active_cycle.id
                self.current_cage_id = cage_id
                
                self.initial_count.blockSignals(True)
                self.initial_count.setValue(active_cycle.initial_count)
                self.initial_count.blockSignals(False)
            else:
                self.current_cycle_id = None
                self.current_cage_id = None
                self.initial_count.blockSignals(True)
                self.initial_count.setValue(0)
                self.initial_count.blockSignals(False)
        else:
            self.current_cycle_id = None
            self.current_cage_id = None
            self.initial_count.blockSignals(True)
            self.initial_count.setValue(0)
            self.initial_count.blockSignals(False)
        
        self.calculate_estimated_count()

    def calculate_estimated_count(self):
        if not hasattr(self, 'estimated_count'):
            return

        initial = self.initial_count.value()
        cage_id = self.cage_combo.currentData()

        if not cage_id or not self.current_cycle_id:
            self.estimated_count.setValue(initial)
            return

        total_removed = self.get_total_mortality_and_harvest(self.current_cycle_id, cage_id)
        estimated = initial - total_removed
        if estimated < 0:
            estimated = 0

        self.estimated_count.setValue(estimated)

    def validate_data(self):
        if not self.cage_combo.currentData():
            self.show_error("لطفاً قفس را انتخاب کنید")
            return False
        if self.initial_count.value() == 0:
            self.show_error("لطفاً تعداد اولیه ماهی را وارد کنید (ابتدا قفس را انتخاب کنید)")
            return False
        if self.estimated_weight.value() == 0:
            self.show_error("لطفاً وزن تخمینی ماهی را وارد کنید")
            return False
        if not self.date_display.text() or self.date_display.text() == "YYYY/MM/DD":
            self.show_error("لطفاً تاریخ نمونه‌برداری را انتخاب کنید")
            return False
        return True

    def accept(self):
        if not self.validate_data():
            return

        self.biomass.cage_id = self.cage_combo.currentData()
        self.biomass.date = self.date_display.text()
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