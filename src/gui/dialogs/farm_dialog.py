"""
دیالوگ‌های مربوط به مدیریت مزرعه برای ERP-Aqua
شامل افزودن و ویرایش مزرعه
"""

from PyQt5 import QtWidgets, QtCore

from .base_dialog import BaseDialog
from ...core.models import Farm
from ...core.constants import COORDINATE_MIN, COORDINATE_MAX


class AddFarmDialog(BaseDialog):
    """
    دیالوگ افزودن مزرعه جدید
    """
    
    def __init__(self, parent=None):
        super().__init__(parent, title="➕ افزودن مزرعه جدید", width=400, height=200)
        self.farm = None
        self.setup_ui()
    
    def setup_ui(self):
        """تنظیم رابط کاربری دیالوگ"""
        layout = QtWidgets.QFormLayout(self)
        layout.setLabelAlignment(QtCore.Qt.AlignRight)
        
        # نام مزرعه
        self.name_edit = QtWidgets.QLineEdit()
        self.name_edit.setPlaceholderText("مثال: مزرعه بوشهر")
        layout.addRow("نام مزرعه:", self.name_edit)
        
        # مختصات مرکز X
        self.x_edit = QtWidgets.QDoubleSpinBox()
        self.x_edit.setRange(COORDINATE_MIN, COORDINATE_MAX)
        self.x_edit.setValue(0)
        layout.addRow("مختصات مرکز X:", self.x_edit)
        
        # مختصات مرکز Y
        self.y_edit = QtWidgets.QDoubleSpinBox()
        self.y_edit.setRange(COORDINATE_MIN, COORDINATE_MAX)
        self.y_edit.setValue(0)
        layout.addRow("مختصات مرکز Y:", self.y_edit)
        
        # دکمه‌ها
        self.add_button_box(layout)
    
    def validate_data(self):
        """اعتبارسنجی داده‌ها"""
        if not self.name_edit.text().strip():
            self.show_error("لطفاً نام مزرعه را وارد کنید")
            self.name_edit.setFocus()
            return False
        return True
    
    def accept(self):
        """پذیرش دیالوگ و ساخت مزرعه جدید"""
        if not self.validate_data():
            return
        
        name = self.name_edit.text().strip()
        farm_id = name.replace(" ", "_")
        self.farm = Farm(farm_id, name, self.x_edit.value(), self.y_edit.value())
        super().accept()


class EditFarmDialog(BaseDialog):
    """
    دیالوگ ویرایش اطلاعات مزرعه
    """
    
    def __init__(self, parent=None, farm=None):
        super().__init__(parent, title="✏️ ویرایش مزرعه", width=400, height=200, edit_mode=True)
        self.farm = None
        self.original_farm = farm
        self.setup_ui()
    
    def setup_ui(self):
        """تنظیم رابط کاربری دیالوگ"""
        layout = QtWidgets.QFormLayout(self)
        layout.setLabelAlignment(QtCore.Qt.AlignRight)
        
        # نام مزرعه
        self.name_edit = QtWidgets.QLineEdit()
        self.name_edit.setText(self.original_farm.name)
        layout.addRow("نام مزرعه:", self.name_edit)
        
        # مختصات مرکز X
        self.x_edit = QtWidgets.QDoubleSpinBox()
        self.x_edit.setRange(COORDINATE_MIN, COORDINATE_MAX)
        self.x_edit.setValue(self.original_farm.center_x)
        layout.addRow("مختصات مرکز X:", self.x_edit)
        
        # مختصات مرکز Y
        self.y_edit = QtWidgets.QDoubleSpinBox()
        self.y_edit.setRange(COORDINATE_MIN, COORDINATE_MAX)
        self.y_edit.setValue(self.original_farm.center_y)
        layout.addRow("مختصات مرکز Y:", self.y_edit)
        
        # دکمه‌ها
        self.add_button_box(layout)
    
    def validate_data(self):
        """اعتبارسنجی داده‌ها"""
        if not self.name_edit.text().strip():
            self.show_error("لطفاً نام مزرعه را وارد کنید")
            self.name_edit.setFocus()
            return False
        return True
    
    def accept(self):
        """پذیرش دیالوگ و ذخیره تغییرات"""
        if not self.validate_data():
            return
        
        name = self.name_edit.text().strip()
        farm_id = name.replace(" ", "_")
        self.farm = Farm(farm_id, name, self.x_edit.value(), self.y_edit.value())
        super().accept()