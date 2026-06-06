"""
دیالوگ ثبت تغذیه روزانه برای ERP-Aqua
"""
""
from PyQt5 import QtWidgets, QtCore

from .base_dialog import BaseDialog
from ...core.models import DailyFeed
from ...widgets.jalali_date_edit import JalaliDateEdit


class FeedDialog(BaseDialog):
    """دیالوگ ثبت یا ویرایش تغذیه روزانه"""
    
    def __init__(self, parent=None, farms=None, current_farm=None, current_mooring=None, feed=None):
        self.farms = farms or []
        self.current_farm = current_farm
        self.current_mooring = current_mooring
        self.feed = feed if feed else DailyFeed()
        
        edit_mode = feed is not None
        title = "ویرایش تغذیه" if edit_mode else "ثبت تغذیه روزانه"
        super().__init__(parent, title=title, edit_mode=edit_mode, width=450, height=480)
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
        if self.feed.cage_id:
            idx = self.cage_combo.findData(self.feed.cage_id)
            if idx >= 0:
                self.cage_combo.setCurrentIndex(idx)
        layout.addRow("قفس:", self.cage_combo)
        
        # تاریخ
        self.date_edit = JalaliDateEdit()
        if self.feed.date:
            self.date_edit.set_jalali_date(self.feed.date)
        layout.addRow("تاریخ:", self.date_edit)
        
        # نوع غذا
        self.feed_type_combo = QtWidgets.QComboBox()
        self.feed_type_combo.addItems(["شروع (0-20 گرم)", "رشد (20-100 گرم)", "پایانی (100+ گرم)"])
        if self.feed.feed_type:
            idx = self.feed_type_combo.findText(self.feed.feed_type)
            if idx >= 0:
                self.feed_type_combo.setCurrentIndex(idx)
        layout.addRow("نوع غذا:", self.feed_type_combo)
        
        # مقدار غذا
        self.feed_amount = QtWidgets.QDoubleSpinBox()
        self.feed_amount.setRange(0, 10000)
        self.feed_amount.setSuffix(" kg")
        self.feed_amount.setValue(self.feed.feed_amount)
        layout.addRow("مقدار غذا:", self.feed_amount)
        
        # زمان تغذیه
        self.feed_time_combo = QtWidgets.QComboBox()
        self.feed_time_combo.addItems(["صبح (6-8)", "ظهر (12-14)", "عصر (16-18)", "شب (20-22)"])
        if self.feed.feed_time:
            idx = self.feed_time_combo.findText(self.feed.feed_time)
            if idx >= 0:
                self.feed_time_combo.setCurrentIndex(idx)
        layout.addRow("زمان تغذیه:", self.feed_time_combo)
        
        # یادداشت
        self.note = QtWidgets.QTextEdit()
        self.note.setMaximumHeight(80)
        self.note.setPlaceholderText("توضیحات اضافی...")
        self.note.setText(self.feed.note)
        layout.addRow("یادداشت:", self.note)
        
        self.add_button_box(layout)
    
    def validate_data(self):
        if not self.cage_combo.currentData():
            self.show_error("لطفاً قفس را انتخاب کنید")
            return False
        if self.feed_amount.value() == 0:
            self.show_error("لطفاً مقدار غذا را وارد کنید")
            return False
        return True
    
    def accept(self):
        if not self.validate_data():
            return
        
        self.feed.cage_id = self.cage_combo.currentData()
        self.feed.date = self.date_edit.get_jalali_date()
        self.feed.feed_type = self.feed_type_combo.currentText()
        self.feed.feed_amount = self.feed_amount.value()
        self.feed.feed_time = self.feed_time_combo.currentText()
        self.feed.note = self.note.toPlainText()
        
        if self.current_farm:
            self.feed.farm_id = self.current_farm.id
        if self.current_mooring:
            self.feed.mooring_id = self.current_mooring.id
        
        super().accept()