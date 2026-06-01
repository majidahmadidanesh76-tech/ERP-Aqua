"""
دیالوگ افزودن و ویرایش زنجیر بویه برای ERP-Aqua
(زنجیر عمودی بین بویه و کلکتور - در زیر آب)
"""

from PyQt5 import QtWidgets, QtCore

from .base_dialog import BaseDialog
from ...core.models import BuoyChain
from ...widgets.jalali_date_edit import JalaliDateEdit


class AddBuoyChainDialog(BaseDialog):
    """
    دیالوگ افزودن یا ویرایش زنجیر بویه (عمودی - زیر آب)
    """
    
    def __init__(self, parent=None, buoys=None, collectors=None, chain=None, mooring_id=""):
        self.buoys = buoys or []
        self.collectors = collectors or []
        self.chain = chain if chain else BuoyChain()
        self.mooring_id = mooring_id
        edit_mode = chain is not None
        title = "ویرایش زنجیر بویه" if edit_mode else "افزودن زنجیر بویه جدید"
        super().__init__(parent, title=title, edit_mode=edit_mode, width=450, height=520)
        self.setup_ui()
    
    def setup_ui(self):
        """تنظیم رابط کاربری دیالوگ"""
        layout = QtWidgets.QFormLayout(self)
        layout.setLabelAlignment(QtCore.Qt.AlignRight)
        layout.setSpacing(10)
        
        # ========== شناسه زنجیر بویه ==========
        self.id_edit = QtWidgets.QLineEdit()
        self.id_edit.setText(self.chain.id)
        layout.addRow("شناسه زنجیر بویه:", self.id_edit)
        
        # ========== قطر زنجیر ==========
        self.diameter = QtWidgets.QDoubleSpinBox()
        self.diameter.setRange(10, 50)
        self.diameter.setSuffix(" mm")
        self.diameter.setValue(self.chain.diameter)
        layout.addRow("قطر زنجیر:", self.diameter)
        
        # ========== طول زنجیر (عمق) ==========
        self.length = QtWidgets.QDoubleSpinBox()
        self.length.setRange(1, 100)
        self.length.setSuffix(" متر")
        self.length.setValue(self.chain.length)
        layout.addRow("طول زنجیر (عمق):", self.length)
        
        # ========== جنس زنجیر ==========
        self.material_combo = QtWidgets.QComboBox()
        self.material_combo.addItems(["فولاد", "گالوانیزه", "استیل", "آهنی", "برنجی"])
        current_material = getattr(self.chain, 'material', 'فولاد')
        index = self.material_combo.findText(current_material)
        if index >= 0:
            self.material_combo.setCurrentIndex(index)
        layout.addRow("جنس زنجیر:", self.material_combo)
        
        # ========== نوع زنجیر ==========
        self.chain_type_combo = QtWidgets.QComboBox()
        self.chain_type_combo.addItems(["ساده", "پل دار"])
        current_chain_type = getattr(self.chain, 'chain_type', 'ساده')
        index = self.chain_type_combo.findText(current_chain_type)
        if index >= 0:
            self.chain_type_combo.setCurrentIndex(index)
        layout.addRow("نوع زنجیر:", self.chain_type_combo)
        
        # ========== تاریخ نصب ==========
        self.install_date = JalaliDateEdit()
        if hasattr(self.chain, 'install_date') and self.chain.install_date:
            self.install_date.set_jalali_date(self.chain.install_date)
        layout.addRow("تاریخ نصب:", self.install_date)
        
        # ========== وضعیت زنجیر ==========
        self.status_combo = QtWidgets.QComboBox()
        self.status_combo.addItems(["سالم", "نیاز به تعمیر", "خراب", "در حال تعمیر"])
        current_status = getattr(self.chain, 'status', 'سالم')
        index = self.status_combo.findText(current_status)
        if index >= 0:
            self.status_combo.setCurrentIndex(index)
        layout.addRow("وضعیت زنجیر:", self.status_combo)
        
        # ========== بویه متصل ==========
        self.buoy_combo = QtWidgets.QComboBox()
        self.buoy_combo.addItem("--- انتخاب بویه ---")
        for b in self.buoys:
            self.buoy_combo.addItem(b.id, b.id)
        if self.chain.buoy_id:
            idx = self.buoy_combo.findData(self.chain.buoy_id)
            if idx >= 0:
                self.buoy_combo.setCurrentIndex(idx)
        layout.addRow("بویه متصل:", self.buoy_combo)
        
        # ========== کلکتور متصل (از لیست کلکتورها) ==========
        self.collector_combo = QtWidgets.QComboBox()
        self.collector_combo.addItem("--- انتخاب کلکتور ---")
        for c in self.collectors:
            self.collector_combo.addItem(c.id, c.id)
        if self.chain.collector_id:
            idx = self.collector_combo.findData(self.chain.collector_id)
            if idx >= 0:
                self.collector_combo.setCurrentIndex(idx)
        layout.addRow("کلکتور متصل:", self.collector_combo)
        
        # ========== یادداشت ==========
        self.note = QtWidgets.QTextEdit()
        self.note.setMaximumHeight(80)
        self.note.setPlaceholderText("توضیحات اضافی...")
        self.note.setText(getattr(self.chain, 'note', ''))
        layout.addRow("یادداشت:", self.note)
        
        # ========== دکمه‌ها ==========
        self.add_button_box(layout)
    
    def validate_data(self):
        """اعتبارسنجی داده‌ها"""
        if not self.id_edit.text().strip():
            self.show_error("شناسه زنجیر بویه را وارد کنید")
            self.id_edit.setFocus()
            return False
        
        if not self.buoy_combo.currentData():
            self.show_error("لطفاً بویه را انتخاب کنید")
            return False
        
        if not self.collector_combo.currentData():
            self.show_error("لطفاً کلکتور را انتخاب کنید")
            return False
        
        return True
    
    def accept(self):
        """پذیرش دیالوگ و ذخیره اطلاعات زنجیر بویه"""
        if not self.validate_data():
            return
        
        self.chain.id = self.id_edit.text().strip()
        self.chain.mooring_id = self.mooring_id
        self.chain.diameter = self.diameter.value()
        self.chain.length = self.length.value()
        self.chain.material = self.material_combo.currentText()
        self.chain.chain_type = self.chain_type_combo.currentText()
        self.chain.install_date = self.install_date.get_jalali_date()
        self.chain.status = self.status_combo.currentText()
        self.chain.buoy_id = self.buoy_combo.currentData()
        self.chain.collector_id = self.collector_combo.currentData()
        self.chain.note = self.note.toPlainText()
        
        super().accept()