"""
دیالوگ مدیریت کاربران برای ERP-Aqua (فقط ادمین)
"""

from PyQt5 import QtWidgets, QtCore

from .base_dialog import BaseDialog  # اصلاح مسیر
from ...core.user_manager import UserManager


class ManageUsersDialog(BaseDialog):
    """
    دیالوگ مدیریت کاربران
    """
    
    def __init__(self, parent=None):
        super().__init__(parent, title="مدیریت کاربران", width=650, height=500)
        self.user_manager = UserManager()
        self.setup_ui()
        self.load_users()
    
    def setup_ui(self):
        """تنظیم رابط کاربری دیالوگ"""
        layout = QtWidgets.QVBoxLayout(self)
        layout.setSpacing(15)
        
        # ========== جدول کاربران ==========
        self.users_table = QtWidgets.QTableWidget()
        self.users_table.setColumnCount(5)
        self.users_table.setHorizontalHeaderLabels(["نام کاربری", "نام نمایشی", "نقش", "تاریخ ثبت", "عملیات"])
        self.users_table.horizontalHeader().setStretchLastSection(True)
        self.users_table.verticalHeader().setDefaultSectionSize(35)
        self.users_table.setColumnWidth(0, 120)
        self.users_table.setColumnWidth(1, 150)
        self.users_table.setColumnWidth(2, 80)
        self.users_table.setColumnWidth(3, 130)
        self.users_table.setColumnWidth(4, 70)
        layout.addWidget(self.users_table)
        
        # ========== فرم افزودن کاربر جدید ==========
        form_group = QtWidgets.QGroupBox("➕ افزودن کاربر جدید")
        form_layout = QtWidgets.QFormLayout(form_group)
        form_layout.setLabelAlignment(QtCore.Qt.AlignRight)
        form_layout.setSpacing(10)
        
        # نام کاربری
        self.new_username = QtWidgets.QLineEdit()
        self.new_username.setPlaceholderText("نام کاربری")
        self.new_username.setMinimumHeight(32)
        form_layout.addRow("نام کاربری:", self.new_username)
        
        # نام نمایشی
        self.new_name = QtWidgets.QLineEdit()
        self.new_name.setPlaceholderText("نام نمایشی")
        self.new_name.setMinimumHeight(32)
        form_layout.addRow("نام نمایشی:", self.new_name)
        
        # رمز عبور
        self.new_password = QtWidgets.QLineEdit()
        self.new_password.setEchoMode(QtWidgets.QLineEdit.Password)
        self.new_password.setPlaceholderText("رمز عبور (حداقل 4 کاراکتر)")
        self.new_password.setMinimumHeight(32)
        form_layout.addRow("رمز عبور:", self.new_password)
        
        # نقش
        self.new_role = QtWidgets.QComboBox()
        self.new_role.addItems(["user", "admin"])
        self.new_role.setMinimumHeight(32)
        form_layout.addRow("نقش:", self.new_role)
        
        # دکمه افزودن
        self.add_btn = QtWidgets.QPushButton("➕ افزودن کاربر")
        self.add_btn.setMinimumHeight(35)
        self.add_btn.setStyleSheet("""
            QPushButton {
                background-color: #0E639C;
                color: white;
                border: none;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #1177BB;
            }
        """)
        self.add_btn.clicked.connect(self.add_user)
        form_layout.addRow(self.add_btn)
        
        layout.addWidget(form_group)
        
        # ========== دکمه بستن ==========
        close_btn = QtWidgets.QPushButton("بستن")
        close_btn.setMinimumHeight(35)
        close_btn.setStyleSheet("""
            QPushButton {
                background-color: #3C3C3C;
                color: #C8C8C8;
                border: 1px solid #3E3E42;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #4A4A4A;
                border-color: #569CD6;
            }
        """)
        close_btn.clicked.connect(self.accept)
        layout.addWidget(close_btn)
    
    def load_users(self):
        """بارگذاری و نمایش لیست کاربران"""
        users = self.user_manager.load_users()
        self.users_table.setRowCount(len(users))
        
        for i, user in enumerate(users):
            # نام کاربری
            self.users_table.setItem(i, 0, QtWidgets.QTableWidgetItem(user["username"]))
            # نام نمایشی
            self.users_table.setItem(i, 1, QtWidgets.QTableWidgetItem(user["name"]))
            # نقش
            self.users_table.setItem(i, 2, QtWidgets.QTableWidgetItem(user["role"]))
            # تاریخ ثبت
            self.users_table.setItem(i, 3, QtWidgets.QTableWidgetItem(user.get("created_at", "-")))
            
            # دکمه حذف
            delete_btn = QtWidgets.QPushButton("🗑️")
            delete_btn.setFixedSize(35, 30)
            delete_btn.setToolTip(f"حذف کاربر {user['username']}")
            delete_btn.setStyleSheet("""
                QPushButton {
                    background-color: #8B2C2C;
                    color: white;
                    border: none;
                    border-radius: 4px;
                }
                QPushButton:hover {
                    background-color: #A33C3C;
                }
            """)
            # بررسی اینکه کاربر admin قابل حذف نباشد
            if user["username"] == "admin":
                delete_btn.setEnabled(False)
                delete_btn.setToolTip("کاربر admin قابل حذف نیست")
            else:
                delete_btn.clicked.connect(lambda checked, u=user["username"]: self.delete_user(u))
            
            self.users_table.setCellWidget(i, 4, delete_btn)
    
    def add_user(self):
        """افزودن کاربر جدید"""
        username = self.new_username.text().strip()
        name = self.new_name.text().strip()
        password = self.new_password.text().strip()
        role = self.new_role.currentText()
        
        # اعتبارسنجی
        if not username:
            self.show_error("نام کاربری را وارد کنید")
            self.new_username.setFocus()
            return
        
        if not name:
            self.show_error("نام نمایشی را وارد کنید")
            self.new_name.setFocus()
            return
        
        if not password:
            self.show_error("رمز عبور را وارد کنید")
            self.new_password.setFocus()
            return
        
        if len(password) < 4:
            self.show_error("رمز عبور باید حداقل 4 کاراکتر باشد")
            self.new_password.setFocus()
            return
        
        # افزودن کاربر
        success, message = self.user_manager.add_user(username, password, name, role)
        
        if success:
            # پاک کردن فرم
            self.new_username.clear()
            self.new_name.clear()
            self.new_password.clear()
            # بارگذاری مجدد جدول
            self.load_users()
            self.show_info(message)
        else:
            self.show_error(message)
    
    def delete_user(self, username):
        """حذف کاربر"""
        reply = QtWidgets.QMessageBox.question(
            self, 
            "تأیید حذف", 
            f"آیا از حذف کاربر '{username}' مطمئن هستید؟",
            QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No
        )
        
        if reply == QtWidgets.QMessageBox.Yes:
            success, message = self.user_manager.delete_user(username)
            if success:
                self.load_users()
                self.show_info(message)
            else:
                self.show_error(message)