"""
دیالوگ‌های مربوط به مدیریت مورینگ برای ERP-Aqua
شامل افزودن و ویرایش مورینگ
"""

from PyQt5 import QtWidgets, QtCore

from .base_dialog import BaseDialog
from ...core.models import Mooring


class AddMooringDialog(BaseDialog):
    """
    دیالوگ افزودن مورینگ جدید
    """
    
    def __init__(self, parent=None):
        super().__init__(parent, title="➕ افزودن مورینگ جدید", width=400, height=180)
        self.mooring = None
        self.setup_ui()
    
    def setup_ui(self):
        """تنظیم رابط کاربری دیالوگ"""
        layout = QtWidgets.QFormLayout(self)
        layout.setLabelAlignment(QtCore.Qt.AlignRight)
        
        # شناسه مورینگ
        self.id_edit = QtWidgets.QLineEdit()
        self.id_edit.setPlaceholderText("مثال: MOR-001")
        layout.addRow("شناسه مورینگ:", self.id_edit)
        
        # نام نمایشی مورینگ
        self.name_edit = QtWidgets.QLineEdit()
        self.name_edit.setPlaceholderText("نام نمایشی (اختیاری)")
        layout.addRow("نام مورینگ:", self.name_edit)
        
        # دکمه‌ها
        self.add_button_box(layout)
    
    def validate_data(self):
        """اعتبارسنجی داده‌ها"""
        if not self.id_edit.text().strip():
            self.show_error("لطفاً شناسه مورینگ را وارد کنید")
            self.id_edit.setFocus()
            return False
        return True
    
    def accept(self):
        """پذیرش دیالوگ و ساخت مورینگ جدید"""
        if not self.validate_data():
            return
        
        mooring_id = self.id_edit.text().strip()
        name = self.name_edit.text().strip() if self.name_edit.text().strip() else mooring_id
        self.mooring = Mooring(mooring_id, name)
        super().accept()


class EditMooringDialog(BaseDialog):
    """
    دیالوگ ویرایش اطلاعات مورینگ
    """
    
    def __init__(self, parent=None, mooring=None):
        super().__init__(parent, title="✏️ ویرایش مورینگ", width=400, height=180, edit_mode=True)
        self.mooring = None
        self.original_mooring = mooring
        self.setup_ui()
    
    def setup_ui(self):
        """تنظیم رابط کاربری دیالوگ"""
        layout = QtWidgets.QFormLayout(self)
        layout.setLabelAlignment(QtCore.Qt.AlignRight)
        
        # شناسه مورینگ
        self.id_edit = QtWidgets.QLineEdit()
        self.id_edit.setText(self.original_mooring.id)
        layout.addRow("شناسه مورینگ:", self.id_edit)
        
        # نام نمایشی مورینگ
        self.name_edit = QtWidgets.QLineEdit()
        self.name_edit.setText(self.original_mooring.name)
        layout.addRow("نام مورینگ:", self.name_edit)
        
        # دکمه‌ها
        self.add_button_box(layout)
    
    def validate_data(self):
        """اعتبارسنجی داده‌ها"""
        if not self.id_edit.text().strip():
            self.show_error("لطفاً شناسه مورینگ را وارد کنید")
            self.id_edit.setFocus()
            return False
        return True
    
    def accept(self):
        """پذیرش دیالوگ و ذخیره تغییرات"""
        if not self.validate_data():
            return
        
        mooring_id = self.id_edit.text().strip()
        name = self.name_edit.text().strip() if self.name_edit.text().strip() else mooring_id
        self.mooring = Mooring(mooring_id, name)
        super().accept()