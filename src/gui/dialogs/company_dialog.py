"""
دیالوگ ثبت و ویرایش شرکت برای ERP-Aqua
"""

import os
import shutil
from PyQt5 import QtWidgets, QtCore, QtGui

from .base_dialog import BaseDialog
from ...core.models import Company


class CompanyDialog(BaseDialog):
    """
    دیالوگ ثبت شرکت جدید یا ویرایش اطلاعات شرکت
    """
    
    def __init__(self, parent=None, company=None):
        """
        سازنده کلاس CompanyDialog
        
        Parameters:
        -----------
        parent : QWidget
            ویجت والد
        company : Company
            شیء شرکت برای ویرایش (در صورت وجود)
        """
        self.company = company if company else Company()
        self.logo_path = ""
        super().__init__(parent, title="🏢 ثبت شرکت جدید", edit_mode=company is not None, width=450, height=520)
        self.setup_ui()
    
    def setup_ui(self):
        """تنظیم رابط کاربری دیالوگ"""
        layout = QtWidgets.QFormLayout(self)
        layout.setLabelAlignment(QtCore.Qt.AlignRight)
        layout.setSpacing(12)
        
        # ==================== بخش لوگو ====================
        logo_layout = QtWidgets.QHBoxLayout()
        
        self.logo_label = QtWidgets.QLabel()
        self.logo_label.setFixedSize(80, 80)
        self.logo_label.setStyleSheet("border: 1px solid #3E3E42; border-radius: 8px; background-color: #3C3C3C;")
        self.logo_label.setAlignment(QtCore.Qt.AlignCenter)
        self.logo_label.setText("🖼️\nلوگو")
        logo_layout.addWidget(self.logo_label)
        
        self.select_logo_btn = QtWidgets.QPushButton("انتخاب لوگو")
        self.select_logo_btn.clicked.connect(self.select_logo)
        logo_layout.addWidget(self.select_logo_btn)
        logo_layout.addStretch()
        layout.addRow("لوگو شرکت:", logo_layout)
        
        # ==================== فیلدهای اطلاعات شرکت ====================
        self.name_edit = QtWidgets.QLineEdit()
        self.name_edit.setText(self.company.name)
        self.name_edit.setPlaceholderText("نام شرکت")
        layout.addRow("نام شرکت:", self.name_edit)
        
        self.reg_no_edit = QtWidgets.QLineEdit()
        self.reg_no_edit.setText(self.company.reg_no)
        self.reg_no_edit.setPlaceholderText("شماره ثبت")
        layout.addRow("شماره ثبت:", self.reg_no_edit)
        
        self.address_edit = QtWidgets.QTextEdit()
        self.address_edit.setPlainText(self.company.address)
        self.address_edit.setMaximumHeight(80)
        layout.addRow("آدرس:", self.address_edit)
        
        self.phone_edit = QtWidgets.QLineEdit()
        self.phone_edit.setText(self.company.phone)
        self.phone_edit.setPlaceholderText("تلفن")
        layout.addRow("تلفن:", self.phone_edit)
        
        self.email_edit = QtWidgets.QLineEdit()
        self.email_edit.setText(self.company.email)
        self.email_edit.setPlaceholderText("ایمیل")
        layout.addRow("ایمیل:", self.email_edit)
        
        # ==================== دکمه‌ها ====================
        self.add_button_box(layout)
    
    def select_logo(self):
        """
        انتخاب فایل لوگو از روی دیسک
        """
        file_path, _ = QtWidgets.QFileDialog.getOpenFileName(
            self, "انتخاب لوگو شرکت", "", "Image Files (*.png *.jpg *.jpeg *.bmp)"
        )
        if file_path:
            pixmap = QtGui.QPixmap(file_path)
            if not pixmap.isNull():
                scaled = pixmap.scaled(80, 80, QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation)
                self.logo_label.setPixmap(scaled)
                self.logo_path = file_path
    
    def validate_data(self):
        """
        اعتبارسنجی داده‌ها قبل از ذخیره
        
        Returns:
        --------
        bool : True اگر داده‌ها معتبر باشند
        """
        if not self.name_edit.text().strip():
            self.show_error("لطفاً نام شرکت را وارد کنید")
            self.name_edit.setFocus()
            return False
        return True
    
    def accept(self):
        """
        پذیرش دیالوگ و ذخیره اطلاعات شرکت
        """
        if not self.validate_data():
            return
        
        # ذخیره اطلاعات
        self.company.name = self.name_edit.text()
        self.company.reg_no = self.reg_no_edit.text()
        self.company.address = self.address_edit.toPlainText()
        self.company.phone = self.phone_edit.text()
        self.company.email = self.email_edit.text()
        
        # ذخیره لوگو
        if self.logo_path:
            os.makedirs("company_logos", exist_ok=True)
            ext = self.logo_path.split('.')[-1]
            new_path = f"company_logos/{self.company.name.replace(' ', '_')}.{ext}"
            shutil.copy(self.logo_path, new_path)
            self.company.logo_path = new_path
        
        super().accept()