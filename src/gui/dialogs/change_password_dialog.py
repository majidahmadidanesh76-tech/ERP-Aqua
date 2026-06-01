"""
دیالوگ تغییر رمز عبور برای ERP-Aqua
"""

from PyQt5 import QtWidgets, QtCore

from .base_dialog import BaseDialog  # اصلاح مسیر
from ...core.user_manager import UserManager


class ChangePasswordDialog(BaseDialog):
    """
    دیالوگ تغییر رمز عبور کاربر
    """
    
    def __init__(self, parent=None, username=""):
        super().__init__(parent, title="تغییر رمز عبور", width=400, height=280)
        self.username = username
        self.user_manager = UserManager()
        self.setup_ui()
    
    def setup_ui(self):
        """تنظیم رابط کاربری دیالوگ"""
        layout = QtWidgets.QFormLayout(self)
        layout.setLabelAlignment(QtCore.Qt.AlignRight)
        layout.setSpacing(12)
        
        # رمز عبور فعلی
        self.old_password = QtWidgets.QLineEdit()
        self.old_password.setEchoMode(QtWidgets.QLineEdit.Password)
        self.old_password.setPlaceholderText("رمز عبور فعلی")
        self.old_password.setMinimumHeight(32)
        layout.addRow("رمز عبور فعلی:", self.old_password)
        
        # رمز عبور جدید
        self.new_password = QtWidgets.QLineEdit()
        self.new_password.setEchoMode(QtWidgets.QLineEdit.Password)
        self.new_password.setPlaceholderText("رمز عبور جدید (حداقل 4 کاراکتر)")
        self.new_password.setMinimumHeight(32)
        layout.addRow("رمز عبور جدید:", self.new_password)
        
        # تکرار رمز عبور جدید
        self.confirm_password = QtWidgets.QLineEdit()
        self.confirm_password.setEchoMode(QtWidgets.QLineEdit.Password)
        self.confirm_password.setPlaceholderText("تکرار رمز عبور جدید")
        self.confirm_password.setMinimumHeight(32)
        layout.addRow("تکرار رمز عبور:", self.confirm_password)
        
        # دکمه‌ها
        self.add_button_box(layout)
    
    def validate_data(self):
        """اعتبارسنجی داده‌ها"""
        if not self.old_password.text().strip():
            self.show_error("رمز عبور فعلی را وارد کنید")
            self.old_password.setFocus()
            return False
        
        if not self.new_password.text().strip():
            self.show_error("رمز عبور جدید را وارد کنید")
            self.new_password.setFocus()
            return False
        
        if len(self.new_password.text().strip()) < 4:
            self.show_error("رمز عبور جدید باید حداقل 4 کاراکتر باشد")
            self.new_password.setFocus()
            return False
        
        if self.new_password.text() != self.confirm_password.text():
            self.show_error("رمز عبور جدید و تکرار آن مطابقت ندارند")
            self.confirm_password.setFocus()
            return False
        
        return True
    
    def accept(self):
        """پذیرش دیالوگ و تغییر رمز عبور"""
        if not self.validate_data():
            return
        
        success, message = self.user_manager.change_password(
            self.username,
            self.old_password.text().strip(),
            self.new_password.text().strip()
        )
        
        if success:
            super().accept()
        else:
            self.show_error(message)