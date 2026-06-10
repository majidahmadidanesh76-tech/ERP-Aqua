"""
دیالوگ ثبت تلفات روزانه برای ERP-Aqua
با دکمه تقویم شمسی
"""

from PyQt5 import QtWidgets, QtCore

from .base_dialog import BaseDialog
from ...core.models import DailyMortality
from ...widgets.persian_calendar import PersianCalendar


class MortalityDialog(BaseDialog):
    """دیالوگ ثبت یا ویرایش تلفات روزانه"""

    def __init__(self, parent=None, farms=None, current_farm=None, current_mooring=None, mortality=None):
        self.farms = farms or []
        self.current_farm = current_farm
        self.current_mooring = current_mooring
        self.mortality = mortality if mortality else DailyMortality()

        edit_mode = mortality is not None
        title = "ویرایش تلفات" if edit_mode else "ثبت تلفات روزانه"
        super().__init__(parent, title=title, edit_mode=edit_mode, width=500, height=380)
        self.setup_ui()

    def setup_ui(self):
        self.setMinimumSize(500, 380)
        
        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.setSpacing(10)
        main_layout.setContentsMargins(15, 15, 15, 15)

        label_style = "color: #C8C8C8; font-weight: bold;"
        field_style = """
            QComboBox, QSpinBox, QTextEdit, QLineEdit {
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
            QComboBox:focus, QSpinBox:focus, QTextEdit:focus, QLineEdit:focus {
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
            QSpinBox::up-button, QSpinBox::down-button {
                width: 18px;
                background-color: #3C3C3C;
            }
            QSpinBox::up-button:hover, QSpinBox::down-button:hover {
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
        row1.setSpacing(5)
        label1 = QtWidgets.QLabel("قفس:")
        label1.setStyleSheet(label_style)
        label1.setFixedWidth(70)
        self.cage_combo = QtWidgets.QComboBox()
        self.cage_combo.setStyleSheet(field_style)
        self.cage_combo.addItem("--- انتخاب قفس ---", None)
        if self.current_farm and self.current_mooring:
            for cage in self.current_mooring.cages:
                self.cage_combo.addItem(cage.id, cage.id)
        if self.mortality.cage_id:
            idx = self.cage_combo.findData(self.mortality.cage_id)
            if idx >= 0:
                self.cage_combo.setCurrentIndex(idx)
        row1.addWidget(label1)
        row1.addWidget(self.cage_combo, 1)
        main_layout.addLayout(row1)

        # سطر 2: تاریخ با دکمه تقویم
        row2 = QtWidgets.QHBoxLayout()
        row2.setSpacing(5)
        label2 = QtWidgets.QLabel("تاریخ:")
        label2.setStyleSheet(label_style)
        label2.setFixedWidth(70)
        
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
        
        if self.mortality.date:
            self.date_display.setText(self.mortality.date)
        else:
            import jdatetime
            today = jdatetime.date.today()
            self.date_display.setText(f"{today.year}/{today.month:02d}/{today.day:02d}")
        
        row2.addWidget(label2)
        row2.addWidget(self.date_display, 1)
        row2.addWidget(self.calendar_btn)
        main_layout.addLayout(row2)

        # سطر 3: تعداد تلفات
        row3 = QtWidgets.QHBoxLayout()
        row3.setSpacing(5)
        label3 = QtWidgets.QLabel("تعداد تلفات:")
        label3.setStyleSheet(label_style)
        label3.setFixedWidth(70)
        self.count_spin = QtWidgets.QSpinBox()
        self.count_spin.setRange(0, 100000)
        self.count_spin.setValue(self.mortality.count)
        self.count_spin.setSuffix(" عدد")
        self.count_spin.setStyleSheet(field_style)
        row3.addWidget(label3)
        row3.addWidget(self.count_spin, 1)
        main_layout.addLayout(row3)

        # سطر 4: علت تلفات
        row4 = QtWidgets.QHBoxLayout()
        row4.setSpacing(5)
        label4 = QtWidgets.QLabel("علت تلفات:")
        label4.setStyleSheet(label_style)
        label4.setFixedWidth(70)
        self.cause_combo = QtWidgets.QComboBox()
        self.cause_combo.setStyleSheet(field_style)
        self.cause_combo.addItems([
            "--- انتخاب علت ---",
            "بیماری باکتریایی",
            "بیماری ویروسی",
            "بیماری قارچی",
            "انگل",
            "کمبود اکسیژن",
            "دمای بالا",
            "دمای پایین",
            "تغییر ناگهانی دما",
            "کیفیت نامناسب آب",
            "استرس حمل و نقل",
            "حمله پرندگان",
            "سرقت",
            "پیری طبیعی",
            "نامعلوم"
        ])
        if self.mortality.cause:
            idx = self.cause_combo.findText(self.mortality.cause)
            if idx >= 0:
                self.cause_combo.setCurrentIndex(idx)
        row4.addWidget(label4)
        row4.addWidget(self.cause_combo, 1)
        main_layout.addLayout(row4)

        # سطر 5: یادداشت
        row5 = QtWidgets.QHBoxLayout()
        row5.setSpacing(5)
        label5 = QtWidgets.QLabel("یادداشت:")
        label5.setStyleSheet(label_style)
        label5.setFixedWidth(70)
        self.note = QtWidgets.QTextEdit()
        self.note.setMaximumHeight(55)
        self.note.setMinimumHeight(55)
        self.note.setPlaceholderText("توضیحات اضافی...")
        self.note.setStyleSheet(field_style)
        self.note.setText(self.mortality.note)
        row5.addWidget(label5)
        row5.addWidget(self.note, 1)
        main_layout.addLayout(row5)

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

    def validate_data(self):
        cage_id = self.cage_combo.currentData()
        if not cage_id:
            self.show_error("لطفاً قفس را انتخاب کنید")
            return False
        if self.count_spin.value() == 0:
            self.show_error("لطفاً تعداد تلفات را وارد کنید")
            return False
        if self.cause_combo.currentIndex() == 0:
            self.show_error("لطفاً علت تلفات را انتخاب کنید")
            return False
        if not self.date_display.text() or self.date_display.text() == "YYYY/MM/DD":
            self.show_error("لطفاً تاریخ را انتخاب کنید")
            return False
        return True

    def accept(self):
        if not self.validate_data():
            return

        self.mortality.cage_id = self.cage_combo.currentData()
        self.mortality.date = self.date_display.text()
        self.mortality.count = self.count_spin.value()
        self.mortality.cause = self.cause_combo.currentText()
        self.mortality.note = self.note.toPlainText()

        if self.current_farm:
            self.mortality.farm_id = self.current_farm.id
        if self.current_mooring:
            self.mortality.mooring_id = self.current_mooring.id

        super().accept()