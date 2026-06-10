"""
دیالوگ ثبت برداشت مرحلهای از قفس برای ERP-Aqua
با دکمه تقویم شمسی
"""

from PyQt5 import QtWidgets, QtCore

from .base_dialog import BaseDialog
from ...widgets.persian_calendar import PersianCalendar


class HarvestDialog(BaseDialog):
    """دیالوگ ثبت برداشت مرحلهای"""

    def __init__(self, parent=None, current_farm=None, current_mooring=None, cycle=None, harvest=None):
        self.current_farm = current_farm
        self.current_mooring = current_mooring
        self.cycle = cycle
        self.harvest = harvest if harvest else None
        title = "ویرایش برداشت" if harvest else "ثبت برداشت مرحلهای"
        super().__init__(parent, title=title, width=520, height=520)
        self.setup_ui()

    def setup_ui(self):
        self.setMinimumSize(520, 520)
        
        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.setSpacing(10)
        main_layout.setContentsMargins(15, 15, 15, 15)

        label_style = "color: #C8C8C8; font-weight: bold;"
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

        # اطلاعات قفس و دوره
        if self.cycle:
            remaining = self.cycle.initial_count - self.cycle.total_harvested_count
            info_text = f"📦 قفس: {self.cycle.cage_id} | شروع دوره: {self.cycle.start_date}\n🎣 تعداد اولیه: {self.cycle.initial_count:,} عدد | باقیمانده: {remaining:,} عدد"
            info_label = QtWidgets.QLabel(info_text)
            info_label.setWordWrap(True)
            info_label.setStyleSheet("color: #4EC9B0; background-color: #252526; padding: 8px; border-radius: 4px;")
        else:
            info_label = QtWidgets.QLabel("⚠️ هیچ دوره فعالی برای این قفس وجود ندارد")
            info_label.setStyleSheet("color: #F48771; padding: 8px;")
        main_layout.addWidget(info_label)

        # سطر 1: تاریخ برداشت با دکمه تقویم
        row1 = QtWidgets.QHBoxLayout()
        row1.setSpacing(5)
        label1 = QtWidgets.QLabel("تاریخ برداشت:")
        label1.setStyleSheet(label_style)
        label1.setFixedWidth(100)
        
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
        
        if self.harvest:
            self.date_display.setText(self.harvest.get('harvest_date', ''))
        else:
            import jdatetime
            today = jdatetime.date.today()
            self.date_display.setText(f"{today.year}/{today.month:02d}/{today.day:02d}")
        
        row1.addWidget(label1)
        row1.addWidget(self.date_display, 1)
        row1.addWidget(self.calendar_btn)
        main_layout.addLayout(row1)

        # سطر 2: تعداد برداشت شده
        row2 = QtWidgets.QHBoxLayout()
        row2.setSpacing(5)
        label2 = QtWidgets.QLabel("تعداد برداشت شده:")
        label2.setStyleSheet(label_style)
        label2.setFixedWidth(100)
        self.harvest_count = QtWidgets.QSpinBox()
        self.harvest_count.setRange(0, 1000000)
        self.harvest_count.setSingleStep(100)
        self.harvest_count.setSuffix(" عدد")
        if self.cycle:
            remaining = self.cycle.initial_count - self.cycle.total_harvested_count
            self.harvest_count.setMaximum(remaining)
        if self.harvest:
            self.harvest_count.setValue(self.harvest.get('harvest_count', 0))
        self.harvest_count.setStyleSheet(field_style)
        row2.addWidget(label2)
        row2.addWidget(self.harvest_count, 1)
        main_layout.addLayout(row2)

        # سطر 3: وزن متوسط
        row3 = QtWidgets.QHBoxLayout()
        row3.setSpacing(5)
        label3 = QtWidgets.QLabel("وزن متوسط:")
        label3.setStyleSheet(label_style)
        label3.setFixedWidth(100)
        self.average_weight = QtWidgets.QDoubleSpinBox()
        self.average_weight.setRange(0, 10000)
        self.average_weight.setSingleStep(50)
        self.average_weight.setSuffix(" گرم")
        if self.harvest:
            self.average_weight.setValue(self.harvest.get('average_weight', 0))
        self.average_weight.setStyleSheet(field_style)
        row3.addWidget(label3)
        row3.addWidget(self.average_weight, 1)
        main_layout.addLayout(row3)

        # سطر 4: کل وزن (فقط خواندنی) - قبل از تعریف price_per_kg
        row4 = QtWidgets.QHBoxLayout()
        row4.setSpacing(5)
        label4 = QtWidgets.QLabel("کل وزن:")
        label4.setStyleSheet(label_style)
        label4.setFixedWidth(100)
        self.total_weight = QtWidgets.QDoubleSpinBox()
        self.total_weight.setRange(0, 100000)
        self.total_weight.setSuffix(" kg")
        self.total_weight.setReadOnly(True)
        self.total_weight.setStyleSheet(field_style + "background-color: #2D2D30; color: #4EC9B0; font-weight: bold;")
        row4.addWidget(label4)
        row4.addWidget(self.total_weight, 1)
        main_layout.addLayout(row4)

        # سطر 5: مشتری
        row5 = QtWidgets.QHBoxLayout()
        row5.setSpacing(5)
        label5 = QtWidgets.QLabel("مشتری:")
        label5.setStyleSheet(label_style)
        label5.setFixedWidth(100)
        self.customer = QtWidgets.QLineEdit()
        self.customer.setPlaceholderText("نام مشتری (اختیاری)")
        self.customer.setStyleSheet(field_style)
        if self.harvest:
            self.customer.setText(self.harvest.get('customer', ''))
        row5.addWidget(label5)
        row5.addWidget(self.customer, 1)
        main_layout.addLayout(row5)

        # سطر 6: قیمت هر کیلو (تعریف قبل از calculate_amount)
        row6 = QtWidgets.QHBoxLayout()
        row6.setSpacing(5)
        label6 = QtWidgets.QLabel("قیمت هر کیلو:")
        label6.setStyleSheet(label_style)
        label6.setFixedWidth(100)
        self.price_per_kg = QtWidgets.QDoubleSpinBox()
        self.price_per_kg.setRange(0, 1000000)
        self.price_per_kg.setSingleStep(1000)
        self.price_per_kg.setSuffix(" تومان")
        if self.harvest:
            self.price_per_kg.setValue(self.harvest.get('price_per_kg', 0))
        self.price_per_kg.setStyleSheet(field_style)
        row6.addWidget(label6)
        row6.addWidget(self.price_per_kg, 1)
        main_layout.addLayout(row6)

        # سطر 7: کل مبلغ (فقط خواندنی)
        row7 = QtWidgets.QHBoxLayout()
        row7.setSpacing(5)
        label7 = QtWidgets.QLabel("کل مبلغ:")
        label7.setStyleSheet(label_style)
        label7.setFixedWidth(100)
        self.total_amount = QtWidgets.QDoubleSpinBox()
        self.total_amount.setRange(0, 1000000000)
        self.total_amount.setSuffix(" تومان")
        self.total_amount.setReadOnly(True)
        self.total_amount.setStyleSheet(field_style + "background-color: #2D2D30; color: #4EC9B0; font-weight: bold;")
        row7.addWidget(label7)
        row7.addWidget(self.total_amount, 1)
        main_layout.addLayout(row7)

        # سطر 8: برداشت نهایی
        row8 = QtWidgets.QHBoxLayout()
        row8.setSpacing(5)
        self.is_final = QtWidgets.QCheckBox("این آخرین برداشت است (پایان دوره)")
        self.is_final.setStyleSheet("color: #C8C8C8;")
        if self.harvest:
            self.is_final.setChecked(self.harvest.get('is_final', False))
        row8.addStretch()
        row8.addWidget(self.is_final)
        row8.addStretch()
        main_layout.addLayout(row8)

        # سطر 9: یادداشت
        row9 = QtWidgets.QHBoxLayout()
        row9.setSpacing(5)
        label9 = QtWidgets.QLabel("یادداشت:")
        label9.setStyleSheet(label_style)
        label9.setFixedWidth(100)
        self.note = QtWidgets.QTextEdit()
        self.note.setMaximumHeight(55)
        self.note.setMinimumHeight(55)
        self.note.setPlaceholderText("توضیحات اضافی...")
        self.note.setStyleSheet(field_style)
        if self.harvest:
            self.note.setText(self.harvest.get('note', ''))
        row9.addWidget(label9)
        row9.addWidget(self.note, 1)
        main_layout.addLayout(row9)

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
        
        # اتصال سیگنال‌ها بعد از تعریف همه ویجت‌ها
        self.harvest_count.valueChanged.connect(self.calculate_total)
        self.average_weight.valueChanged.connect(self.calculate_total)
        self.price_per_kg.valueChanged.connect(self.calculate_amount)
        self.total_weight.valueChanged.connect(self.calculate_amount)
        
        # محاسبه اولیه
        self.calculate_total()

    def open_persian_calendar(self):
        """باز کردن دیالوگ تقویم شمسی برای انتخاب تاریخ"""
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

    def calculate_total(self):
        count = self.harvest_count.value() if hasattr(self, 'harvest_count') else 0
        weight = self.average_weight.value() if hasattr(self, 'average_weight') else 0
        total = (count * weight) / 1000
        if hasattr(self, 'total_weight'):
            self.total_weight.setValue(total)
        self.calculate_amount()

    def calculate_amount(self):
        total = self.total_weight.value() if hasattr(self, 'total_weight') else 0
        price = self.price_per_kg.value() if hasattr(self, 'price_per_kg') else 0
        if hasattr(self, 'total_amount'):
            self.total_amount.setValue(total * price)

    def validate_data(self):
        if self.harvest_count.value() == 0:
            self.show_error("لطفاً تعداد برداشت شده را وارد کنید")
            return False
        if self.average_weight.value() == 0:
            self.show_error("لطفاً وزن متوسط را وارد کنید")
            return False
        if not self.date_display.text() or self.date_display.text() == "YYYY/MM/DD":
            self.show_error("لطفاً تاریخ برداشت را انتخاب کنید")
            return False
        return True

    def accept(self):
        if not self.validate_data():
            return

        self.result_data = {
            "harvest_date": self.date_display.text(),
            "harvest_count": self.harvest_count.value(),
            "average_weight": self.average_weight.value(),
            "total_weight_kg": self.total_weight.value(),
            "customer": self.customer.text(),
            "price_per_kg": self.price_per_kg.value(),
            "total_amount": self.total_amount.value(),
            "is_final": self.is_final.isChecked(),
            "note": self.note.toPlainText()
        }

        super().accept()