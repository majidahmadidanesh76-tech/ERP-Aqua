"""
دیالوگ ثبت برداشت مرحله‌ای از قفس برای ERP-Aqua
"""

from PyQt5 import QtWidgets, QtCore

from .base_dialog import BaseDialog
from ...widgets.jalali_date_edit import JalaliDateEdit


class HarvestDialog(BaseDialog):
    """دیالوگ ثبت برداشت مرحله‌ای"""
    
    def __init__(self, parent=None, current_farm=None, current_mooring=None, cycle=None, harvest=None):
        self.current_farm = current_farm
        self.current_mooring = current_mooring
        self.cycle = cycle
        self.harvest = harvest if harvest else None
        title = "ویرایش برداشت" if harvest else "ثبت برداشت مرحله‌ای"
        super().__init__(parent, title=title, width=500, height=520)
        self.setup_ui()
    
    def setup_ui(self):
        layout = QtWidgets.QFormLayout(self)
        layout.setLabelAlignment(QtCore.Qt.AlignRight)
        layout.setSpacing(8)
        layout.setContentsMargins(10, 10, 10, 10)
        
        # اطلاعات قفس و دوره
        if self.cycle:
            remaining = self.cycle.initial_count - self.cycle.total_harvested_count
            info_text = f"📦 قفس: {self.cycle.cage_id} | شروع دوره: {self.cycle.start_date}\n"
            info_text += f"🎣 تعداد اولیه: {self.cycle.initial_count:,} عدد | باقیمانده: {remaining:,} عدد"
            info_label = QtWidgets.QLabel(info_text)
        else:
            info_label = QtWidgets.QLabel("⚠️ هیچ دوره فعالی برای این قفس وجود ندارد")
        info_label.setStyleSheet("font-weight: bold; color: #569CD6; padding: 5px;")
        layout.addRow(info_label)
        
        # تاریخ برداشت
        self.harvest_date = JalaliDateEdit()
        if self.harvest:
            self.harvest_date.set_jalali_date(self.harvest.get('harvest_date', ''))
        layout.addRow("تاریخ برداشت:", self.harvest_date)
        
        # تعداد برداشت شده
        self.harvest_count = QtWidgets.QSpinBox()
        self.harvest_count.setRange(0, 1000000)
        self.harvest_count.setSingleStep(100)
        self.harvest_count.setSuffix(" عدد")
        if self.cycle:
            remaining = self.cycle.initial_count - self.cycle.total_harvested_count
            self.harvest_count.setMaximum(remaining)
        if self.harvest:
            self.harvest_count.setValue(self.harvest.get('harvest_count', 0))
        layout.addRow("تعداد برداشت شده:", self.harvest_count)
        
        # وزن متوسط
        self.average_weight = QtWidgets.QDoubleSpinBox()
        self.average_weight.setRange(0, 10000)
        self.average_weight.setSingleStep(50)
        self.average_weight.setSuffix(" گرم")
        if self.harvest:
            self.average_weight.setValue(self.harvest.get('average_weight', 0))
        layout.addRow("وزن متوسط:", self.average_weight)
        
        # کل وزن (محاسبه خودکار)
        self.total_weight = QtWidgets.QDoubleSpinBox()
        self.total_weight.setRange(0, 100000)
        self.total_weight.setSuffix(" kg")
        self.total_weight.setReadOnly(True)
        self.harvest_count.valueChanged.connect(self.calculate_total)
        self.average_weight.valueChanged.connect(self.calculate_total)
        layout.addRow("کل وزن (kg):", self.total_weight)
        
        # خط جداکننده
        line = QtWidgets.QFrame()
        line.setFrameShape(QtWidgets.QFrame.HLine)
        line.setStyleSheet("background-color: #3E3E42; margin: 5px 0;")
        layout.addRow(line)
        
        # مشتری
        self.customer = QtWidgets.QLineEdit()
        self.customer.setPlaceholderText("نام مشتری (اختیاری)")
        if self.harvest:
            self.customer.setText(self.harvest.get('customer', ''))
        layout.addRow("مشتری:", self.customer)
        
        # قیمت هر کیلو
        self.price_per_kg = QtWidgets.QDoubleSpinBox()
        self.price_per_kg.setRange(0, 1000000)
        self.price_per_kg.setSingleStep(1000)
        self.price_per_kg.setSuffix(" تومان")
        if self.harvest:
            self.price_per_kg.setValue(self.harvest.get('price_per_kg', 0))
        layout.addRow("قیمت هر کیلو:", self.price_per_kg)
        
        # کل مبلغ (محاسبه خودکار)
        self.total_amount = QtWidgets.QDoubleSpinBox()
        self.total_amount.setRange(0, 1000000000)
        self.total_amount.setSuffix(" تومان")
        self.total_amount.setReadOnly(True)
        self.price_per_kg.valueChanged.connect(self.calculate_amount)
        self.total_weight.valueChanged.connect(self.calculate_amount)
        layout.addRow("کل مبلغ:", self.total_amount)
        
        # آیا برداشت نهایی است؟
        self.is_final = QtWidgets.QCheckBox("این آخرین برداشت است (پایان دوره)")
        if self.harvest:
            self.is_final.setChecked(self.harvest.get('is_final', False))
        layout.addRow(self.is_final)
        
        # یادداشت
        self.note = QtWidgets.QTextEdit()
        self.note.setMaximumHeight(60)
        self.note.setPlaceholderText("توضیحات اضافی...")
        if self.harvest:
            self.note.setText(self.harvest.get('note', ''))
        layout.addRow("یادداشت:", self.note)
        
        self.add_button_box(layout)
        self.calculate_total()
        self.calculate_amount()
    
    def calculate_total(self):
        count = self.harvest_count.value()
        weight = self.average_weight.value()
        total = (count * weight) / 1000
        self.total_weight.setValue(total)
        self.calculate_amount()
    
    def calculate_amount(self):
        total = self.total_weight.value()
        price = self.price_per_kg.value()
        self.total_amount.setValue(total * price)
    
    def validate_data(self):
        if self.harvest_count.value() == 0:
            self.show_error("لطفاً تعداد برداشت شده را وارد کنید")
            return False
        if self.average_weight.value() == 0:
            self.show_error("لطفاً وزن متوسط را وارد کنید")
            return False
        return True
    
    def accept(self):
        if not self.validate_data():
            return
        
        self.result_data = {
            "harvest_date": self.harvest_date.get_jalali_date(),
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