"""
دیالوگ افزودن و ویرایش تور برای ERP-Aqua
"""

from PyQt5 import QtWidgets, QtCore

from .base_dialog import BaseDialog
from ...core.models import Net
from ...widgets.jalali_date_edit import JalaliDateEdit


class AddNetDialog(BaseDialog):
    """
    دیالوگ افزودن یا ویرایش تور
    """
    
    def __init__(self, parent=None, cages=None, net=None, mooring_id=""):
        self.cages = cages or []
        self.net = net if net else Net()
        self.mooring_id = mooring_id
        edit_mode = net is not None
        title = "ویرایش تور" if edit_mode else "افزودن تور جدید"
        super().__init__(parent, title=title, edit_mode=edit_mode, width=450, height=550)
        self.setup_ui()
    
    def setup_ui(self):
        layout = QtWidgets.QFormLayout(self)
        layout.setLabelAlignment(QtCore.Qt.AlignRight)
        layout.setSpacing(10)
        
        # شناسه تور
        self.id_edit = QtWidgets.QLineEdit()
        self.id_edit.setText(self.net.id)
        layout.addRow("شناسه تور:", self.id_edit)
        
        # قفس متصل
        self.cage_combo = QtWidgets.QComboBox()
        self.cage_combo.addItem("--- انتخاب قفس ---")
        for c in self.cages:
            self.cage_combo.addItem(c.id, c.id)
        if self.net.cage_id:
            idx = self.cage_combo.findData(self.net.cage_id)
            if idx >= 0:
                self.cage_combo.setCurrentIndex(idx)
        layout.addRow("قفس متصل:", self.cage_combo)
        
        # قطر تور
        self.diameter = QtWidgets.QSpinBox()
        self.diameter.setRange(1, 50)
        self.diameter.setSuffix(" mm")
        self.diameter.setValue(getattr(self.net, 'diameter', 10))
        layout.addRow("قطر تور:", self.diameter)
        
        # اندازه چشمه
        self.mesh_size = QtWidgets.QSpinBox()
        self.mesh_size.setRange(10, 200)
        self.mesh_size.setSuffix(" mm")
        self.mesh_size.setValue(self.net.mesh_size)
        layout.addRow("اندازه چشمه:", self.mesh_size)
        
        # جنس تور
        self.material_combo = QtWidgets.QComboBox()
        self.material_combo.addItems(["داینما", "نایلون", "پلی‌اتیلن", "پلی‌استر", "فولاد"])
        current_material = getattr(self.net, 'material', 'داینما')
        index = self.material_combo.findText(current_material)
        if index >= 0:
            self.material_combo.setCurrentIndex(index)
        layout.addRow("جنس تور:", self.material_combo)
        
        # عمق تور
        self.depth = QtWidgets.QDoubleSpinBox()
        self.depth.setRange(1, 20)
        self.depth.setSuffix(" متر")
        self.depth.setValue(self.net.depth)
        layout.addRow("عمق تور:", self.depth)
        
        # وضعیت تور
        self.status_combo = QtWidgets.QComboBox()
        self.status_combo.addItems(["سالم", "نیاز به تعمیر", "خراب", "در حال تعمیر"])
        current_status = getattr(self.net, 'status', 'سالم')
        index = self.status_combo.findText(current_status)
        if index >= 0:
            self.status_combo.setCurrentIndex(index)
        layout.addRow("وضعیت تور:", self.status_combo)
        
        # یادداشت
        self.note = QtWidgets.QTextEdit()
        self.note.setMaximumHeight(80)
        self.note.setPlaceholderText("توضیحات اضافی...")
        self.note.setText(getattr(self.net, 'note', ''))
        layout.addRow("یادداشت:", self.note)
        
        # تاریخ نصب (در انتها)
        self.install_date = JalaliDateEdit()
        if hasattr(self.net, 'install_date') and self.net.install_date:
            self.install_date.set_jalali_date(self.net.install_date)
        layout.addRow("تاریخ نصب:", self.install_date)
        
        self.add_button_box(layout)
    
    def validate_data(self):
        if not self.id_edit.text().strip():
            self.show_error("شناسه تور را وارد کنید")
            self.id_edit.setFocus()
            return False
        
        if not self.cage_combo.currentData():
            self.show_error("لطفاً قفس را انتخاب کنید")
            return False
        
        return True
    
    def accept(self):
        if not self.validate_data():
            return
        
        self.net.id = self.id_edit.text().strip()
        self.net.mooring_id = self.mooring_id
        self.net.cage_id = self.cage_combo.currentData()
        self.net.diameter = self.diameter.value()
        self.net.mesh_size = self.mesh_size.value()
        self.net.material = self.material_combo.currentText()
        self.net.depth = self.depth.value()
        self.net.install_date = self.install_date.get_jalali_date()
        self.net.status = self.status_combo.currentText()
        self.net.note = self.note.toPlainText()
        
        super().accept()