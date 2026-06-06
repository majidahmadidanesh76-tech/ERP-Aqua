"""
دیالوگ تنظیمات قوانین هوشمند
"""

from PyQt5 import QtWidgets, QtCore
from ...database.db_handler import DatabaseHandler


class SmartRulesSettingsDialog(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.db = DatabaseHandler()
        self.setWindowTitle("⚙️ تنظیمات قوانین هوشمند")
        self.setModal(True)
        self.resize(600, 500)
        self.setup_ui()
        self.load_data()

    def setup_ui(self):
        layout = QtWidgets.QVBoxLayout(self)

        info_label = QtWidgets.QLabel(
            "تنظیمات زیر بر روی تولید پیشنهادات هوشمند تأثیر می‌گذارند.\n"
            "تغییر این مقادیر نیاز به دقت دارد."
        )
        info_label.setWordWrap(True)
        info_label.setStyleSheet("color: #569CD6; padding: 10px; background-color: #252526; border-radius: 4px;")
        layout.addWidget(info_label)

        self.table = QtWidgets.QTableWidget()
        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels(["قانون", "مقدار فعلی", "توضیحات"])
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.setColumnWidth(0, 180)
        self.table.setColumnWidth(1, 100)
        self.table.setStyleSheet("""
            QTableWidget {
                border: 1px solid #3E3E42;
                border-radius: 4px;
                background-color: #2D2D30;
                alternate-background-color: #252526;
            }
            QTableWidget::item:selected {
                background-color: #3A3A3A;
            }
            QHeaderView::section {
                background-color: #252526;
                color: #569CD6;
                border: none;
                border-bottom: 1px solid #3E3E42;
                padding: 6px;
            }
        """)
        layout.addWidget(self.table)

        btn_layout = QtWidgets.QHBoxLayout()
        
        self.reset_btn = QtWidgets.QPushButton("↺ بازنشانی به مقادیر پیش‌فرض")
        self.reset_btn.setStyleSheet("background-color: #8B2C2C; color: white; border-radius: 4px; padding: 6px 12px;")
        self.reset_btn.clicked.connect(self.reset_to_default)
        
        self.save_btn = QtWidgets.QPushButton("💾 ذخیره تغییرات")
        self.save_btn.setStyleSheet("background-color: #2E8B57; color: white; border-radius: 4px; padding: 6px 12px;")
        self.save_btn.clicked.connect(self.save_changes)
        
        self.cancel_btn = QtWidgets.QPushButton("انصراف")
        self.cancel_btn.setStyleSheet("background-color: #3C3C3C; color: #C8C8C8; border-radius: 4px; padding: 6px 12px;")
        self.cancel_btn.clicked.connect(self.reject)
        
        btn_layout.addWidget(self.reset_btn)
        btn_layout.addStretch()
        btn_layout.addWidget(self.save_btn)
        btn_layout.addWidget(self.cancel_btn)
        layout.addLayout(btn_layout)

    def load_data(self):
        rules = self.db.get_all_rules()
        self.table.setRowCount(len(rules))
        
        rule_names_fa = {
            'temp_alert_high': 'دمای هشدار (°C)',
            'temp_critical_high': 'دمای بحرانی (°C)',
            'o2_alert_low': 'اکسیژن هشدار (mg/L)',
            'o2_critical_low': 'اکسیژن بحرانی (mg/L)',
            'salinity_min': 'حداقل شوری مطلوب (ppt)',
            'salinity_max': 'حداکثر شوری مطلوب (ppt)',
            'mortality_threshold': 'نرخ افزایش تلفات',
            'net_clean_days': 'روز بین شستشوی تور',
            'harvest_threshold': 'درصد وزن هدف برای برداشت',
            'combined_temp_o2_alert': 'تفاوت دما و اکسیژن برای هشدار ترکیبی',
            'max_suggestions_per_day': 'حداکثر پیشنهادات در روز'
        }
        
        self.inputs = {}
        
        for i, rule in enumerate(rules):
            fa_name = rule_names_fa.get(rule['rule_name'], rule['rule_name'])
            self.table.setItem(i, 0, QtWidgets.QTableWidgetItem(fa_name))
            
            spinbox = QtWidgets.QDoubleSpinBox()
            spinbox.setRange(0, 100)
            spinbox.setDecimals(2)
            spinbox.setSingleStep(0.5)
            spinbox.setValue(float(rule['rule_value']))
            spinbox.setMinimumWidth(80)
            
            if 'days' in rule['rule_name'] or 'max_suggestions' in rule['rule_name']:
                spinbox.setDecimals(0)
                spinbox.setSingleStep(1)
            
            self.table.setCellWidget(i, 1, spinbox)
            self.inputs[rule['rule_name']] = spinbox
            
            desc_item = QtWidgets.QTableWidgetItem(rule['description'] or '-')
            desc_item.setToolTip(rule['description'] or '')
            self.table.setItem(i, 2, desc_item)
        
        self.table.verticalHeader().setDefaultSectionSize(40)

    def save_changes(self):
        updates = {}
        for rule_name, spinbox in self.inputs.items():
            updates[rule_name] = spinbox.value()
        
        self.db.update_multiple_rules(updates, "admin")
        QtWidgets.QMessageBox.information(self, "موفق", "تنظیمات قوانین هوشمند با موفقیت ذخیره شد.")
        self.accept()

    def reset_to_default(self):
        reply = QtWidgets.QMessageBox.question(
            self, "تأیید بازنشانی",
            "آیا از بازنشانی همه قوانین به مقادیر پیش‌فرض مطمئن هستید؟",
            QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No
        )
        if reply == QtWidgets.QMessageBox.Yes:
            self.db.reset_rules_to_default()
            self.load_data()
            QtWidgets.QMessageBox.information(self, "موفق", "قوانین به مقادیر پیش‌فرض بازنشانی شدند.")