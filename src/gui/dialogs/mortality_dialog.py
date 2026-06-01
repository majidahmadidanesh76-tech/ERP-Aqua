"""
دیالوگ ثبت تلفات روزانه برای ERP-Aqua
"""

from PyQt5 import QtWidgets, QtCore

from .base_dialog import BaseDialog
from src.core.models import DailyMortality
from ...widgets.jalali_date_edit import JalaliDateEdit


class MortalityDialog(BaseDialog):
    """دیالوگ ثبت یا ویرایش تلفات روزانه"""
    
    def __init__(self, parent=None, farms=None, current_farm=None, current_mooring=None, mortality=None):
        self.farms = farms or []
        self.current_farm = current_farm
        self.current_mooring = current_mooring
        self.mortality = mortality if mortality else DailyMortality()
        
        edit_mode = mortality is not None
        title = "ویرایش تلفات" if edit_mode else "ثبت تلفات روزانه"
        super().__init__(parent, title=title, edit_mode=edit_mode, width=450, height=500)
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
        if self.mortality.cage_id:
            idx = self.cage_combo.findData(self.mortality.cage_id)
            if idx >= 0:
                self.cage_combo.setCurrentIndex(idx)
        layout.addRow("قفس:", self.cage_combo)
        
        # تاریخ
        self.date_edit = JalaliDateEdit()
        if self.mortality.date:
            self.date_edit.set_jalali_date(self.mortality.date)
        layout.addRow("تاریخ:", self.date_edit)
        
        # تعداد تلفات
        self.count_spin = QtWidgets.QSpinBox()
        self.count_spin.setRange(0, 100000)
        self.count_spin.setValue(self.mortality.count)
        self.count_spin.setSuffix(" عدد")
        layout.addRow("تعداد تلفات:", self.count_spin)
        
        # علت تلفات
        self.cause_combo = QtWidgets.QComboBox()
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
            "کمبود غذا",
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
        layout.addRow("علت تلفات:", self.cause_combo)
        
        # یادداشت
        self.note = QtWidgets.QTextEdit()
        self.note.setMaximumHeight(80)
        self.note.setPlaceholderText("توضیحات اضافی...")
        self.note.setText(self.mortality.note)
        layout.addRow("یادداشت:", self.note)
        
        self.add_button_box(layout)
    
    def validate_data(self):
        if not self.cage_combo.currentData():
            self.show_error("لطفاً قفس را انتخاب کنید")
            return False
        if self.count_spin.value() == 0:
            self.show_error("لطفاً تعداد تلفات را وارد کنید")
            return False
        if self.cause_combo.currentIndex() == 0:
            self.show_error("لطفاً علت تلفات را انتخاب کنید")
            return False
        return True
    
    def accept(self):
        if not self.validate_data():
            return
        
        self.mortality.cage_id = self.cage_combo.currentData()
        self.mortality.date = self.date_edit.get_jalali_date()
        self.mortality.count = self.count_spin.value()
        self.mortality.cause = self.cause_combo.currentText()
        self.mortality.note = self.note.toPlainText()
        
        if self.current_farm:
            self.mortality.farm_id = self.current_farm.id
        if self.current_mooring:
            self.mortality.mooring_id = self.current_mooring.id
        
        super().accept()