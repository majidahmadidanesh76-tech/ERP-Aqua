"""
دیالوگ افزودن و ویرایش شاکل برای ERP-Aqua
"""

from PyQt5 import QtWidgets, QtCore

from .base_dialog import BaseDialog
from ...core.models import Shackle
from ...widgets.jalali_date_edit import JalaliDateEdit


class AddShackleDialog(BaseDialog):
    
    def __init__(self, parent=None, shackle=None, mooring_id=""):
        self.shackle = shackle if shackle else Shackle()
        self.mooring_id = mooring_id
        edit_mode = shackle is not None
        title = "ویرایش شاکل" if edit_mode else "افزودن شاکل جدید"
        super().__init__(parent, title=title, edit_mode=edit_mode, width=450, height=500)
        self.setup_ui()
    
    def setup_ui(self):
        layout = QtWidgets.QFormLayout(self)
        layout.setLabelAlignment(QtCore.Qt.AlignRight)
        layout.setSpacing(10)
        
        self.id_edit = QtWidgets.QLineEdit()
        self.id_edit.setText(self.shackle.id)
        layout.addRow("شناسه شاکل:", self.id_edit)
        
        self.shackle_type_combo = QtWidgets.QComboBox()
        self.shackle_type_combo.addItems(["یو شکل", "نعلی"])
        current_type = getattr(self.shackle, 'shackle_type', 'یو شکل')
        idx = self.shackle_type_combo.findText(current_type)
        if idx >= 0:
            self.shackle_type_combo.setCurrentIndex(idx)
        layout.addRow("نوع شاکل:", self.shackle_type_combo)
        
        self.quantity = QtWidgets.QSpinBox()
        self.quantity.setRange(1, 100)
        self.quantity.setValue(getattr(self.shackle, 'quantity', 1))
        layout.addRow("تعداد شاکل:", self.quantity)
        
        self.size = QtWidgets.QSpinBox()
        self.size.setRange(10, 100)
        self.size.setSuffix(" mm")
        self.size.setValue(self.shackle.size)
        layout.addRow("سایز شاکل:", self.size)
        
        self.capacity = QtWidgets.QDoubleSpinBox()
        self.capacity.setRange(0.5, 50)
        self.capacity.setSuffix(" تن")
        self.capacity.setValue(getattr(self.shackle, 'capacity', 5.0))
        layout.addRow("تناژ شاکل:", self.capacity)
        
        self.material_combo = QtWidgets.QComboBox()
        self.material_combo.addItems(["فولاد", "استیل", "گالوانیزه", "آهنی"])
        current_material = getattr(self.shackle, 'material', 'فولاد')
        idx = self.material_combo.findText(current_material)
        if idx >= 0:
            self.material_combo.setCurrentIndex(idx)
        layout.addRow("جنس شاکل:", self.material_combo)
        
        self.connected_id = QtWidgets.QLineEdit()
        self.connected_id.setText(self.shackle.connected_id)
        self.connected_id.setPlaceholderText("شناسه قطعه متصل (زنجیر/طناب)")
        layout.addRow("قطعه متصل:", self.connected_id)
        
        # ========== تاریخ نصب (با ویجت استاندارد شمسی) ==========
        self.install_date = JalaliDateEdit()
        if self.shackle.install_date:
            self.install_date.set_jalali_date(self.shackle.install_date)
        layout.addRow("تاریخ نصب:", self.install_date)
        
        self.status_combo = QtWidgets.QComboBox()
        self.status_combo.addItems(["سالم", "نیاز به تعمیر", "خراب", "در حال تعمیر"])
        current_status = getattr(self.shackle, 'status', 'سالم')
        idx = self.status_combo.findText(current_status)
        if idx >= 0:
            self.status_combo.setCurrentIndex(idx)
        layout.addRow("وضعیت شاکل:", self.status_combo)
        
        self.note = QtWidgets.QTextEdit()
        self.note.setMaximumHeight(80)
        self.note.setPlaceholderText("توضیحات اضافی...")
        self.note.setText(self.shackle.note)
        layout.addRow("یادداشت:", self.note)
        
        self.add_button_box(layout)
    
    def validate_data(self):
        if not self.id_edit.text().strip():
            self.show_error("شناسه شاکل را وارد کنید")
            self.id_edit.setFocus()
            return False
        
        if not self.connected_id.text().strip():
            self.show_error("لطفاً شناسه قطعه متصل را وارد کنید")
            self.connected_id.setFocus()
            return False
        
        return True
    
    def accept(self):
        if not self.validate_data():
            return
        
        self.shackle.id = self.id_edit.text().strip()
        self.shackle.mooring_id = self.mooring_id
        self.shackle.shackle_type = self.shackle_type_combo.currentText()
        self.shackle.quantity = self.quantity.value()
        self.shackle.size = self.size.value()
        self.shackle.capacity = self.capacity.value()
        self.shackle.material = self.material_combo.currentText()
        self.shackle.connected_id = self.connected_id.text().strip()
        self.shackle.install_date = self.install_date.get_jalali_date()
        self.shackle.status = self.status_combo.currentText()
        self.shackle.note = self.note.toPlainText()
        
        super().accept()