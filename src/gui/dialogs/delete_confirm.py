"""
دیالوگ تأیید حذف برای ERP-Aqua
"""

from PyQt5 import QtWidgets, QtCore

from .base_dialog import BaseDialog


class DeleteConfirmDialog(BaseDialog):
    """
    دیالوگ تأیید حذف آیتم‌ها
    با نمایش پیام مناسب و دکمه حذف قرمز رنگ
    """
    
    def __init__(self, parent=None, item_type="", item_name="", has_children=False):
        """
        سازنده کلاس DeleteConfirmDialog
        
        Parameters:
        -----------
        parent : QWidget
            ویجت والد
        item_type : str
            نوع آیتم (مزرعه، مورینگ، بویه، ...)
        item_name : str
            نام یا شناسه آیتم
        has_children : bool
            آیا آیتم زیرمجموعه دارد؟
        """
        self.item_type = item_type
        self.item_name = item_name
        self.has_children = has_children
        
        title = "تأیید حذف"
        super().__init__(parent, title=title, width=400, height=180)
        self.setup_ui()
    
    def setup_ui(self):
        """تنظیم رابط کاربری دیالوگ"""
        layout = QtWidgets.QVBoxLayout(self)
        
        # استایل مخصوص دیالوگ حذف
        self.setStyleSheet("""
            QDialog { background-color: #252526; }
            QLabel { color: #C8C8C8; }
            QPushButton { background-color: #0E639C; color: white; border: none; border-radius: 4px; padding: 5px 14px; }
            QPushButton:hover { background-color: #1177BB; }
            QPushButton:last-child { background-color: #3C3C3C; color: #C8C8C8; border: 1px solid #3E3E42; }
            QPushButton:last-child:hover { background-color: #4A4A4A; border-color: #569CD6; }
        """)
        
        # پیام متناسب با وضعیت
        if self.has_children:
            lbl = QtWidgets.QLabel(
                f"⚠️ نمی‌توانید {self.item_type} '{self.item_name}' را حذف کنید.\n"
                f"زیرمجموعه دارد. ابتدا زیرمجموعه‌ها را حذف کنید."
            )
            lbl.setStyleSheet("color: #F48771; font-size: 13px;")
        else:
            lbl = QtWidgets.QLabel(f"آیا از حذف {self.item_type} '{self.item_name}' مطمئن هستید؟")
        
        lbl.setAlignment(QtCore.Qt.AlignCenter)
        lbl.setWordWrap(True)
        layout.addWidget(lbl)
        
        # دکمه‌ها
        btn_layout = QtWidgets.QHBoxLayout()
        
        if not self.has_children:
            confirm_btn = QtWidgets.QPushButton("🗑️ حذف")
            confirm_btn.setStyleSheet("background-color: #8B2C2C; color: white;")
            confirm_btn.clicked.connect(self.accept)
            btn_layout.addWidget(confirm_btn)
        
        cancel_btn = QtWidgets.QPushButton("انصراف")
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(cancel_btn)
        
        layout.addLayout(btn_layout)
    
    def accept(self):
        """پذیرش حذف (فقط در صورت نداشتن زیرمجموعه)"""
        if not self.has_children:
            super().accept()