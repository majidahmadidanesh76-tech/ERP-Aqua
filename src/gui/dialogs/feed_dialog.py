"""
دیالوگ ثبت تغذیه روزانه برای ERP-Aqua
با دکمه تقویم شمسی
"""

from PyQt5 import QtWidgets, QtCore

from .base_dialog import BaseDialog
from ...core.models import DailyFeed
from ...widgets.persian_calendar import PersianCalendar


class FeedDialog(BaseDialog):
    """دیالوگ ثبت یا ویرایش تغذیه روزانه"""

    def __init__(self, parent=None, farms=None, current_farm=None, current_mooring=None, feed=None):
        self.farms = farms or []
        self.current_farm = current_farm
        self.current_mooring = current_mooring
        self.feed = feed if feed else DailyFeed()

        edit_mode = feed is not None
        title = "ویرایش تغذیه" if edit_mode else "ثبت تغذیه روزانه"
        super().__init__(parent, title=title, edit_mode=edit_mode, width=500, height=420)
        self.setup_ui()

    def setup_ui(self):
        self.setMinimumSize(500, 420)
        
        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.setSpacing(10)
        main_layout.setContentsMargins(15, 15, 15, 15)

        label_style = "color: #C8C8C8; font-weight: bold;"
        field_style = """
            QComboBox, QDoubleSpinBox, QTextEdit, QLineEdit {
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
            QComboBox:focus, QDoubleSpinBox:focus, QTextEdit:focus, QLineEdit:focus {
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
            QDoubleSpinBox::up-button, QDoubleSpinBox::down-button {
                width: 18px;
                background-color: #3C3C3C;
            }
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
        if self.feed.cage_id:
            idx = self.cage_combo.findData(self.feed.cage_id)
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
        
        if self.feed.date:
            self.date_display.setText(self.feed.date)
        else:
            import jdatetime
            today = jdatetime.date.today()
            self.date_display.setText(f"{today.year}/{today.month:02d}/{today.day:02d}")
        
        row2.addWidget(label2)
        row2.addWidget(self.date_display, 1)
        row2.addWidget(self.calendar_btn)
        main_layout.addLayout(row2)

        # سطر 3: نوع غذا
        row3 = QtWidgets.QHBoxLayout()
        row3.setSpacing(5)
        label3 = QtWidgets.QLabel("نوع غذا:")
        label3.setStyleSheet(label_style)
        label3.setFixedWidth(70)
        self.feed_type_combo = QtWidgets.QComboBox()
        self.feed_type_combo.setStyleSheet(field_style)
        self.feed_type_combo.addItems(["شروع (0-20 گرم)", "رشد (20-100 گرم)", "پایانی (100+ گرم)"])
        if self.feed.feed_type:
            idx = self.feed_type_combo.findText(self.feed.feed_type)
            if idx >= 0:
                self.feed_type_combo.setCurrentIndex(idx)
        row3.addWidget(label3)
        row3.addWidget(self.feed_type_combo, 1)
        main_layout.addLayout(row3)

        # سطر 4: مقدار غذا
        row4 = QtWidgets.QHBoxLayout()
        row4.setSpacing(5)
        label4 = QtWidgets.QLabel("مقدار غذا:")
        label4.setStyleSheet(label_style)
        label4.setFixedWidth(70)
        self.feed_amount = QtWidgets.QDoubleSpinBox()
        self.feed_amount.setRange(0, 10000)
        self.feed_amount.setSuffix(" kg")
        self.feed_amount.setValue(self.feed.feed_amount)
        self.feed_amount.setStyleSheet(field_style)
        row4.addWidget(label4)
        row4.addWidget(self.feed_amount, 1)
        main_layout.addLayout(row4)

        # سطر 5: زمان تغذیه
        row5 = QtWidgets.QHBoxLayout()
        row5.setSpacing(5)
        label5 = QtWidgets.QLabel("زمان تغذیه:")
        label5.setStyleSheet(label_style)
        label5.setFixedWidth(70)
        self.feed_time_combo = QtWidgets.QComboBox()
        self.feed_time_combo.setStyleSheet(field_style)
        self.feed_time_combo.addItems(["صبح (6-8)", "ظهر (12-14)", "عصر (16-18)", "شب (20-22)"])
        if self.feed.feed_time:
            idx = self.feed_time_combo.findText(self.feed.feed_time)
            if idx >= 0:
                self.feed_time_combo.setCurrentIndex(idx)
        row5.addWidget(label5)
        row5.addWidget(self.feed_time_combo, 1)
        main_layout.addLayout(row5)

        # سطر 6: یادداشت
        row6 = QtWidgets.QHBoxLayout()
        row6.setSpacing(5)
        label6 = QtWidgets.QLabel("یادداشت:")
        label6.setStyleSheet(label_style)
        label6.setFixedWidth(70)
        self.note = QtWidgets.QTextEdit()
        self.note.setMaximumHeight(55)
        self.note.setMinimumHeight(55)
        self.note.setPlaceholderText("توضیحات اضافی...")
        self.note.setStyleSheet(field_style)
        self.note.setText(self.feed.note)
        row6.addWidget(label6)
        row6.addWidget(self.note, 1)
        main_layout.addLayout(row6)

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
        if not self.cage_combo.currentData():
            self.show_error("لطفاً قفس را انتخاب کنید")
            return False
        if self.feed_amount.value() == 0:
            self.show_error("لطفاً مقدار غذا را وارد کنید")
            return False
        if not self.date_display.text() or self.date_display.text() == "YYYY/MM/DD":
            self.show_error("لطفاً تاریخ را انتخاب کنید")
            return False
        return True

    def accept(self):
        if not self.validate_data():
            return

        self.feed.cage_id = self.cage_combo.currentData()
        self.feed.date = self.date_display.text()
        self.feed.feed_type = self.feed_type_combo.currentText()
        self.feed.feed_amount = self.feed_amount.value()
        self.feed.feed_time = self.feed_time_combo.currentText()
        self.feed.note = self.note.toPlainText()

        if self.current_farm:
            self.feed.farm_id = self.current_farm.id
        if self.current_mooring:
            self.feed.mooring_id = self.current_mooring.id

        super().accept()