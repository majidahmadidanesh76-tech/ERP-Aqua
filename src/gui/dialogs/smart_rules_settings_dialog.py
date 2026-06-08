"""
دیالوگ تنظیمات قوانین هوشمند
"""

from PyQt5 import QtWidgets, QtCore, QtGui
from ...database.db_handler import DatabaseHandler
from .dialog_style import DIALOG_STYLE, BUTTON_STYLE, CANCEL_BUTTON_STYLE

class SmartRulesSettingsDialog(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet(DIALOG_STYLE)
        self.db = DatabaseHandler()
        self.setWindowTitle("⚙️ تنظیمات قوانین هوشمند")
        self.setModal(True)
        self.resize(650, 520)
        self.setup_ui()
        self.load_data()

    def setup_ui(self):
        layout = QtWidgets.QVBoxLayout(self)
        layout.setSpacing(12)
        layout.setContentsMargins(15, 15, 15, 15)

        # عنوان و توضیحات
        info_label = QtWidgets.QLabel(
            "تنظیمات زیر بر روی تولید پیشنهادات هوشمند تأثیر میگذارند.\n"
            "تغییر این مقادیر نیاز به دقت دارد."
        )
        info_label.setWordWrap(True)
        info_label.setStyleSheet("color: #569CD6; padding: 8px; background-color: #252526; border-radius: 4px;")
        layout.addWidget(info_label)

        # جدول تنظیمات
        self.table = QtWidgets.QTableWidget()
        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels(["قانون", "مقدار فعلی", "توضیحات"])
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.setColumnWidth(0, 200)
        self.table.setColumnWidth(1, 120)
        self.table.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self.table.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.table.setAlternatingRowColors(True)
        self.table.setStyleSheet("""
            QTableWidget {
                border: 1px solid #3E3E42;
                border-radius: 4px;
                background-color: #2D2D30;
                alternate-background-color: #252526;
                gridline-color: #3E3E42;
            }
            QTableWidget::item {
                padding: 8px 6px;
                color: #C8C8C8;
            }
            QTableWidget::item:selected {
                background-color: #3A3A3A;
            }
            QHeaderView::section {
                background-color: #252526;
                color: #569CD6;
                border: none;
                border-bottom: 1px solid #3E3E42;
                padding: 8px;
                font-weight: bold;
            }
        """)
        layout.addWidget(self.table)

        # دکمه‌ها
        btn_layout = QtWidgets.QHBoxLayout()
        btn_layout.setSpacing(12)

        self.reset_btn = QtWidgets.QPushButton("↺ بازنشانی به مقادیر پیشفرض")
        self.reset_btn.setFixedSize(180, 35)
        self.reset_btn.setStyleSheet("""
            QPushButton {
                background-color: #8B2C2C;
                color: white;
                border: none;
                border-radius: 4px;
                font-weight: bold;
                padding: 5px 12px;
            }
            QPushButton:hover {
                background-color: #A33C3C;
            }
        """)
        self.reset_btn.clicked.connect(self.reset_to_default)
        btn_layout.addWidget(self.reset_btn)

        btn_layout.addStretch()

        self.save_btn = QtWidgets.QPushButton("💾 ذخیره تغییرات")
        self.save_btn.setFixedSize(130, 35)
        self.save_btn.setStyleSheet(BUTTON_STYLE)
        self.save_btn.clicked.connect(self.save_changes)
        btn_layout.addWidget(self.save_btn)

        self.cancel_btn = QtWidgets.QPushButton("انصراف")
        self.cancel_btn.setFixedSize(100, 35)
        self.cancel_btn.setStyleSheet(CANCEL_BUTTON_STYLE)
        self.cancel_btn.clicked.connect(self.reject)
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
            
            # ستون 0: نام قانون
            name_item = QtWidgets.QTableWidgetItem(fa_name)
            name_item.setForeground(QtGui.QColor('#4EC9B0'))
            self.table.setItem(i, 0, name_item)

            # ستون 1: اسپین باکس مقدار
            spinbox = QtWidgets.QDoubleSpinBox()
            spinbox.setRange(0, 100)
            spinbox.setDecimals(1)
            spinbox.setSingleStep(0.5)
            spinbox.setValue(float(rule['rule_value']))
            spinbox.setMinimumWidth(100)
            spinbox.setStyleSheet("""
                QDoubleSpinBox {
                    background-color: #3C3C3C;
                    border: 1px solid #3E3E42;
                    border-radius: 4px;
                    padding: 4px;
                    color: #C8C8C8;
                }
                QDoubleSpinBox:focus {
                    border-color: #569CD6;
                }
            """)

            if 'days' in rule['rule_name'] or 'max_suggestions' in rule['rule_name']:
                spinbox.setDecimals(0)
                spinbox.setSingleStep(1)

            self.table.setCellWidget(i, 1, spinbox)
            self.inputs[rule['rule_name']] = spinbox

            # ستون 2: توضیحات
            desc_item = QtWidgets.QTableWidgetItem(rule.get('description', '-'))
            desc_item.setToolTip(rule.get('description', ''))
            self.table.setItem(i, 2, desc_item)

        self.table.verticalHeader().setDefaultSectionSize(45)

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
            "آیا از بازنشانی همه قوانین به مقادیر پیشفرض مطمئن هستید؟",
            QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No
        )
        if reply == QtWidgets.QMessageBox.Yes:
            self.db.reset_rules_to_default()
            self.load_data()
            QtWidgets.QMessageBox.information(self, "موفق", "قوانین به مقادیر پیشفرض بازنشانی شدند.")