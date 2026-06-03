"""
دیالوگ مدیریت گونه‌های ماهی برای برنامه‌ریزی تولید
"""

from PyQt5 import QtWidgets, QtCore
from functools import partial
from ...database.db_handler import DatabaseHandler


class SpeciesManagementDialog(QtWidgets.QDialog):
    """دیالوگ مدیریت گونه‌های ماهی"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.db = DatabaseHandler()
        self.setWindowTitle("🐟 مدیریت گونه‌های ماهی")
        self.setModal(True)
        self.resize(750, 500)
        self.setup_ui()
        self.load_species()

    def setup_ui(self):
        layout = QtWidgets.QVBoxLayout(self)

        # عنوان
        title = QtWidgets.QLabel("مدیریت گونه‌های ماهی")
        title.setAlignment(QtCore.Qt.AlignCenter)
        title.setStyleSheet("font-size: 16px; font-weight: bold; color: #569CD6; padding: 10px;")
        layout.addWidget(title)

        # جدول گونه‌ها
        self.table = QtWidgets.QTableWidget()
        self.table.setColumnCount(8)
        self.table.setHorizontalHeaderLabels([
            "شناسه", "نام گونه", "دمای بهینه (min)", "دمای بهینه (max)",
            "دمای بحرانی", "FCR هدف", "وزن هدف (گرم)", "نرخ رشد روزانه"
        ])
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.setColumnWidth(0, 50)
        self.table.setColumnWidth(1, 180)
        self.table.setColumnWidth(2, 100)
        self.table.setColumnWidth(3, 100)
        self.table.setColumnWidth(4, 100)
        self.table.setColumnWidth(5, 80)
        self.table.setColumnWidth(6, 100)
        self.table.setColumnWidth(7, 120)
        self.table.setStyleSheet("""
            QTableWidget {
                border: 1px solid #2D2D30;
                border-radius: 4px;
                background-color: #2D2D30;
                alternate-background-color: #252526;
            }
            QTableWidget::item:selected {
                background-color: #0E639C;
            }
            QHeaderView::section {
                background-color: #252526;
                color: #569CD6;
                border: none;
                border-bottom: 1px solid #2D2D30;
            }
        """)
        layout.addWidget(self.table)

        # دکمه‌های عملیات
        btn_layout = QtWidgets.QHBoxLayout()
        btn_layout.setSpacing(10)

        self.add_btn = QtWidgets.QPushButton("➕ افزودن گونه جدید")
        self.add_btn.setStyleSheet(self.get_button_style("#2E8B57"))
        self.add_btn.clicked.connect(self.add_species)

        self.edit_btn = QtWidgets.QPushButton("✏️ ویرایش انتخاب شده")
        self.edit_btn.setStyleSheet(self.get_button_style("#D4A574"))
        self.edit_btn.clicked.connect(self.edit_species)

        self.delete_btn = QtWidgets.QPushButton("🗑️ حذف انتخاب شده")
        self.delete_btn.setStyleSheet(self.get_button_style("#8B2C2C"))
        self.delete_btn.clicked.connect(self.delete_species)

        btn_layout.addWidget(self.add_btn)
        btn_layout.addWidget(self.edit_btn)
        btn_layout.addWidget(self.delete_btn)
        btn_layout.addStretch()

        close_btn = QtWidgets.QPushButton("بستن")
        close_btn.setStyleSheet(self.get_button_style("#3C3C3C"))
        close_btn.clicked.connect(self.accept)
        btn_layout.addWidget(close_btn)

        layout.addLayout(btn_layout)

    def get_button_style(self, color):
        return f"""
            QPushButton {{
                background-color: {color};
                color: white;
                font-weight: bold;
                padding: 6px 12px;
                border-radius: 4px;
                border: none;
            }}
            QPushButton:hover {{
                background-color: {self.get_hover_color(color)};
            }}
        """

    def get_hover_color(self, color):
        hover_map = {
            "#2E8B57": "#3CB371",
            "#D4A574": "#E0B080",
            "#8B2C2C": "#A33C3C",
            "#3C3C3C": "#4A4A4A"
        }
        return hover_map.get(color, "#569CD6")

    def load_species(self):
        """بارگذاری لیست گونه‌ها از دیتابیس"""
        species_list = self.db.get_all_species()
        self.table.setRowCount(len(species_list))

        for i, s in enumerate(species_list):
            self.table.setItem(i, 0, QtWidgets.QTableWidgetItem(str(s['id'])))
            self.table.setItem(i, 1, QtWidgets.QTableWidgetItem(s['name']))
            self.table.setItem(i, 2, QtWidgets.QTableWidgetItem(str(s['optimal_temp_min'])))
            self.table.setItem(i, 3, QtWidgets.QTableWidgetItem(str(s['optimal_temp_max'])))
            self.table.setItem(i, 4, QtWidgets.QTableWidgetItem(str(s['critical_temp_high'])))
            self.table.setItem(i, 5, QtWidgets.QTableWidgetItem(str(s['target_fcr'])))
            self.table.setItem(i, 6, QtWidgets.QTableWidgetItem(str(s['typical_harvest_weight'])))
            self.table.setItem(i, 7, QtWidgets.QTableWidgetItem(str(s['avg_daily_gain'])))

    def add_species(self):
        """افزودن گونه جدید"""
        dialog = SpeciesDialog(self)
        if dialog.exec_():
            data = dialog.get_data()
            self.db.add_species(
                data['name'],
                data['optimal_temp_min'],
                data['optimal_temp_max'],
                data['critical_temp_high'],
                data['target_fcr'],
                data['typical_harvest_weight'],
                data['avg_daily_gain'],
                data['description']
            )
            self.load_species()
            QtWidgets.QMessageBox.information(self, "موفق", f"گونه '{data['name']}' با موفقیت اضافه شد")

    def edit_species(self):
        """ویرایش گونه انتخاب شده"""
        current_row = self.table.currentRow()
        if current_row < 0:
            QtWidgets.QMessageBox.warning(self, "خطا", "لطفاً یک ردیف را انتخاب کنید")
            return

        species_id = int(self.table.item(current_row, 0).text())
        species = self.db.get_species_by_id(species_id)
        if not species:
            return

        dialog = SpeciesDialog(self, species)
        if dialog.exec_():
            data = dialog.get_data()
            self.db.update_species(
                species_id,
                data['name'],
                data['optimal_temp_min'],
                data['optimal_temp_max'],
                data['critical_temp_high'],
                data['target_fcr'],
                data['typical_harvest_weight'],
                data['avg_daily_gain'],
                data['description']
            )
            self.load_species()
            QtWidgets.QMessageBox.information(self, "موفق", f"گونه '{data['name']}' با موفقیت ویرایش شد")

    def delete_species(self):
        """حذف گونه انتخاب شده"""
        current_row = self.table.currentRow()
        if current_row < 0:
            QtWidgets.QMessageBox.warning(self, "خطا", "لطفاً یک ردیف را انتخاب کنید")
            return

        species_id = int(self.table.item(current_row, 0).text())
        species_name = self.table.item(current_row, 1).text()

        reply = QtWidgets.QMessageBox.question(
            self, "تأیید حذف",
            f"آیا از حذف گونه '{species_name}' مطمئن هستید؟",
            QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No
        )

        if reply == QtWidgets.QMessageBox.Yes:
            self.db.delete_species(species_id)
            self.load_species()
            QtWidgets.QMessageBox.information(self, "موفق", f"گونه '{species_name}' با موفقیت حذف شد")


class SpeciesDialog(QtWidgets.QDialog):
    """دیالوگ افزودن/ویرایش گونه ماهی"""

    def __init__(self, parent=None, species=None):
        super().__init__(parent)
        self.species = species
        self.setWindowTitle("➕ افزودن گونه جدید" if not species else "✏️ ویرایش گونه")
        self.setModal(True)
        self.resize(450, 500)
        self.setup_ui()
        if species:
            self.load_species_data()

    def setup_ui(self):
        layout = QtWidgets.QFormLayout(self)
        layout.setSpacing(12)
        layout.setLabelAlignment(QtCore.Qt.AlignRight)

        label_style = "color: #C8C8C8;"
        input_style = """
            background-color: #3C3C3C;
            color: #C8C8C8;
            border: 1px solid #2D2D30;
            border-radius: 4px;
            padding: 6px;
        """

        # نام گونه
        self.name_edit = QtWidgets.QLineEdit()
        self.name_edit.setPlaceholderText("مثال: ماهی آزاد دریای خزر")
        self.name_edit.setStyleSheet(input_style)
        name_label = QtWidgets.QLabel("نام گونه:")
        name_label.setStyleSheet(label_style)
        layout.addRow(name_label, self.name_edit)

        # دمای بهینه (حداقل)
        self.opt_temp_min = QtWidgets.QDoubleSpinBox()
        self.opt_temp_min.setRange(-5, 45)
        self.opt_temp_min.setSingleStep(0.5)
        self.opt_temp_min.setSuffix(" °C")
        self.opt_temp_min.setStyleSheet(input_style)
        opt_min_label = QtWidgets.QLabel("دمای بهینه (حداقل):")
        opt_min_label.setStyleSheet(label_style)
        layout.addRow(opt_min_label, self.opt_temp_min)

        # دمای بهینه (حداکثر)
        self.opt_temp_max = QtWidgets.QDoubleSpinBox()
        self.opt_temp_max.setRange(-5, 45)
        self.opt_temp_max.setSingleStep(0.5)
        self.opt_temp_max.setSuffix(" °C")
        self.opt_temp_max.setStyleSheet(input_style)
        opt_max_label = QtWidgets.QLabel("دمای بهینه (حداکثر):")
        opt_max_label.setStyleSheet(label_style)
        layout.addRow(opt_max_label, self.opt_temp_max)

        # دمای بحرانی
        self.critical_temp = QtWidgets.QDoubleSpinBox()
        self.critical_temp.setRange(-5, 50)
        self.critical_temp.setSingleStep(0.5)
        self.critical_temp.setSuffix(" °C")
        self.critical_temp.setStyleSheet(input_style)
        crit_label = QtWidgets.QLabel("دمای بحرانی (هشدار):")
        crit_label.setStyleSheet(label_style)
        layout.addRow(crit_label, self.critical_temp)

        # ضریب تبدیل هدف (FCR)
        self.target_fcr = QtWidgets.QDoubleSpinBox()
        self.target_fcr.setRange(0.5, 5.0)
        self.target_fcr.setSingleStep(0.05)
        self.target_fcr.setStyleSheet(input_style)
        fcr_label = QtWidgets.QLabel("ضریب تبدیل هدف (FCR):")
        fcr_label.setStyleSheet(label_style)
        layout.addRow(fcr_label, self.target_fcr)

        # وزن هدف برداشت
        self.harvest_weight = QtWidgets.QSpinBox()
        self.harvest_weight.setRange(100, 10000)
        self.harvest_weight.setSingleStep(100)
        self.harvest_weight.setSuffix(" گرم")
        self.harvest_weight.setStyleSheet(input_style)
        weight_label = QtWidgets.QLabel("وزن هدف برداشت:")
        weight_label.setStyleSheet(label_style)
        layout.addRow(weight_label, self.harvest_weight)

        # نرخ رشد روزانه
        self.daily_gain = QtWidgets.QDoubleSpinBox()
        self.daily_gain.setRange(0.5, 10.0)
        self.daily_gain.setSingleStep(0.1)
        self.daily_gain.setSuffix(" گرم/روز")
        self.daily_gain.setStyleSheet(input_style)
        gain_label = QtWidgets.QLabel("نرخ رشد روزانه:")
        gain_label.setStyleSheet(label_style)
        layout.addRow(gain_label, self.daily_gain)

        # توضیحات
        self.description = QtWidgets.QTextEdit()
        self.description.setMaximumHeight(80)
        self.description.setPlaceholderText("توضیحات اضافی...")
        self.description.setStyleSheet(f"{input_style} max-height: 80px;")
        desc_label = QtWidgets.QLabel("توضیحات:")
        desc_label.setStyleSheet(label_style)
        layout.addRow(desc_label, self.description)

        # دکمه‌ها
        btn_layout = QtWidgets.QHBoxLayout()
        ok_btn = QtWidgets.QPushButton("ذخیره")
        ok_btn.setStyleSheet("""
            QPushButton {
                background-color: #0E639C;
                color: white;
                font-weight: bold;
                padding: 8px;
                border-radius: 4px;
                border: none;
            }
            QPushButton:hover {
                background-color: #1177BB;
            }
        """)
        ok_btn.clicked.connect(self.accept)

        cancel_btn = QtWidgets.QPushButton("انصراف")
        cancel_btn.setStyleSheet("""
            QPushButton {
                background-color: #3C3C3C;
                color: #C8C8C8;
                border: 1px solid #2D2D30;
                border-radius: 4px;
                padding: 8px;
            }
            QPushButton:hover {
                background-color: #4A4A4A;
            }
        """)
        cancel_btn.clicked.connect(self.reject)

        btn_layout.addWidget(ok_btn)
        btn_layout.addWidget(cancel_btn)
        layout.addRow(btn_layout)

    def load_species_data(self):
        """بارگذاری داده‌های گونه برای ویرایش"""
        self.name_edit.setText(self.species['name'])
        self.opt_temp_min.setValue(self.species['optimal_temp_min'])
        self.opt_temp_max.setValue(self.species['optimal_temp_max'])
        self.critical_temp.setValue(self.species['critical_temp_high'])
        self.target_fcr.setValue(self.species['target_fcr'])
        self.harvest_weight.setValue(self.species['typical_harvest_weight'])
        self.daily_gain.setValue(self.species['avg_daily_gain'])
        self.description.setText(self.species['description'] or "")

    def get_data(self):
        return {
            'name': self.name_edit.text(),
            'optimal_temp_min': self.opt_temp_min.value(),
            'optimal_temp_max': self.opt_temp_max.value(),
            'critical_temp_high': self.critical_temp.value(),
            'target_fcr': self.target_fcr.value(),
            'typical_harvest_weight': self.harvest_weight.value(),
            'avg_daily_gain': self.daily_gain.value(),
            'description': self.description.toPlainText()
        }