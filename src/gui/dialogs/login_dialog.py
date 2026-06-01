"""
دیالوگ ورود به سیستم برای ERP-Aqua
"""

from PyQt5 import QtWidgets, QtCore
import hashlib
import json
import os


class LoginDialog(QtWidgets.QDialog):
    """
    دیالوگ ورود به سیستم
    """
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("ورود به سیستم ERP-Aqua")
        self.setModal(True)
        self.resize(400, 300)
        self.login_successful = False
        self.current_user = None
        self.setup_ui()
        self.create_default_user()
    
    def setup_ui(self):
        """تنظیم رابط کاربری دیالوگ"""
        layout = QtWidgets.QVBoxLayout(self)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # عنوان
        title = QtWidgets.QLabel("🐟 ERP-Aqua")
        title.setAlignment(QtCore.Qt.AlignCenter)
        title.setStyleSheet("font-size: 24px; font-weight: bold; color: #569CD6; padding: 10px;")
        layout.addWidget(title)
        
        # فرم ورود
        form_layout = QtWidgets.QFormLayout()
        form_layout.setLabelAlignment(QtCore.Qt.AlignRight)
        form_layout.setSpacing(12)
        
        # نام کاربری
        self.username_edit = QtWidgets.QLineEdit()
        self.username_edit.setPlaceholderText("نام کاربری")
        self.username_edit.setMinimumHeight(32)
        self.username_edit.setStyleSheet("""
            QLineEdit {
                background-color: #3C3C3C;
                border: 1px solid #3E3E42;
                border-radius: 4px;
                padding: 6px 10px;
                color: #C8C8C8;
            }
        """)
        form_layout.addRow("نام کاربری:", self.username_edit)
        
        # رمز عبور
        self.password_edit = QtWidgets.QLineEdit()
        self.password_edit.setPlaceholderText("رمز عبور")
        self.password_edit.setEchoMode(QtWidgets.QLineEdit.Password)
        self.password_edit.setMinimumHeight(32)
        self.password_edit.setStyleSheet("""
            QLineEdit {
                background-color: #3C3C3C;
                border: 1px solid #3E3E42;
                border-radius: 4px;
                padding: 6px 10px;
                color: #C8C8C8;
            }
        """)
        form_layout.addRow("رمز عبور:", self.password_edit)
        
        layout.addLayout(form_layout)
        
        # دکمه‌ها
        btn_layout = QtWidgets.QHBoxLayout()
        btn_layout.setSpacing(15)
        
        self.login_btn = QtWidgets.QPushButton("ورود")
        self.login_btn.setMinimumHeight(35)
        self.login_btn.setMinimumWidth(100)
        self.login_btn.setStyleSheet("""
            QPushButton {
                background-color: #0E639C;
                color: white;
                border: none;
                border-radius: 4px;
                font-size: 13px;
            }
            QPushButton:hover {
                background-color: #1177BB;
            }
        """)
        self.login_btn.clicked.connect(self.check_login)
        btn_layout.addWidget(self.login_btn)
        
        self.exit_btn = QtWidgets.QPushButton("خروج")
        self.exit_btn.setMinimumHeight(35)
        self.exit_btn.setMinimumWidth(100)
        self.exit_btn.setStyleSheet("""
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
        self.exit_btn.clicked.connect(self.reject)
        btn_layout.addWidget(self.exit_btn)
        
        layout.addLayout(btn_layout)
        
        # پیام خطا
        self.error_label = QtWidgets.QLabel("")
        self.error_label.setAlignment(QtCore.Qt.AlignCenter)
        self.error_label.setStyleSheet("color: #F48771; font-size: 12px;")
        self.error_label.setVisible(False)
        layout.addWidget(self.error_label)
        
        # تنظیم focus
        self.username_edit.setFocus()
    
    def create_default_user(self):
        """ایجاد کاربر پیش‌فرض در صورت نبودن"""
        users_file = "data/users.json"
        if not os.path.exists("data"):
            os.makedirs("data")
        
        if not os.path.exists(users_file):
            default_users = {
                "users": [
                    {
                        "username": "admin",
                        "password": hashlib.sha256("admin123".encode()).hexdigest(),
                        "name": "مدیر سیستم",
                        "role": "admin",
                        "created_at": ""
                    },
                    {
                        "username": "user",
                        "password": hashlib.sha256("user123".encode()).hexdigest(),
                        "name": "کاربر عادی",
                        "role": "user",
                        "created_at": ""
                    }
                ]
            }
            with open(users_file, "w", encoding="utf-8") as f:
                json.dump(default_users, f, indent=2, ensure_ascii=False)
            print("کاربران پیش‌فرض ایجاد شدند")
    
    def check_login(self):
        """بررسی اعتبار ورود"""
        username = self.username_edit.text().strip()
        password = self.password_edit.text().strip()
        
        print(f"تلاش برای ورود: {username}")
        
        if not username or not password:
            self.show_error_message("لطفاً نام کاربری و رمز عبور را وارد کنید")
            return
        
        # هش کردن رمز عبور
        hashed_password = hashlib.sha256(password.encode()).hexdigest()
        
        # بررسی در فایل کاربران
        try:
            with open("data/users.json", "r", encoding="utf-8") as f:
                data = json.load(f)
                users = data.get("users", [])
                
                print(f"تعداد کاربران موجود: {len(users)}")
                
                for user in users:
                    if user["username"] == username and user["password"] == hashed_password:
                        self.login_successful = True
                        self.current_user = {
                            "username": user["username"],
                            "name": user["name"],
                            "role": user["role"]
                        }
                        print(f"ورود موفق: {username}")
                        self.accept()
                        return
                
                self.show_error_message("نام کاربری یا رمز عبور اشتباه است")
        except Exception as e:
            print(f"خطا: {e}")
            self.show_error_message(f"خطا در خواندن اطلاعات کاربران: {e}")
    
    def show_error_message(self, message):
        """نمایش پیام خطا"""
        self.error_label.setText(message)
        self.error_label.setVisible(True)
        self.password_edit.clear()
        self.password_edit.setFocus()
    
    def get_current_user(self):
        """دریافت اطلاعات کاربر جاری"""
        return self.current_user