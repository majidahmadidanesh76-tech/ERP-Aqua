"""
کلاس پایه برای همه دیالوگ‌های برنامه ERP-Aqua
"""

from PyQt5 import QtWidgets


class BaseDialog(QtWidgets.QDialog):
    """
    کلاس پایه دیالوگ با قابلیت‌های مشترک
    """
    
    def __init__(self, parent=None, title="", edit_mode=False, width=400, height=300):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setModal(True)
        self.edit_mode = edit_mode
        self.resize(width, height)
        self.setup_common_style()
    
    def setup_common_style(self):
        """تنظیمات استایل مشترک برای همه دیالوگ‌ها"""
        self.setStyleSheet("""
            QDialog {
                background-color: #252526;
            }
            QLabel {
                color: #C8C8C8;
                background-color: transparent;
            }
            QLineEdit, QComboBox, QDoubleSpinBox, QSpinBox, QTextEdit, QDateTimeEdit, QDateEdit {
                background-color: #3C3C3C;
                border: 1px solid #3E3E42;
                border-radius: 4px;
                padding: 4px 6px;
                color: #C8C8C8;
            }
            QLineEdit:focus, QComboBox:focus, QDateTimeEdit:focus, QDateEdit:focus {
                border-color: #569CD6;
            }
            QPushButton {
                background-color: #0E639C;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 4px 12px;
            }
            QPushButton:hover {
                background-color: #1177BB;
            }
            QPushButton:last-child {
                background-color: #3C3C3C;
                color: #C8C8C8;
                border: 1px solid #3E3E42;
            }
            QPushButton:last-child:hover {
                background-color: #4A4A4A;
                border-color: #569CD6;
            }
        """)
    
    def show_error(self, message):
        QtWidgets.QMessageBox.warning(self, "خطا", message)
    
    def show_info(self, message):
        QtWidgets.QMessageBox.information(self, "اطلاع", message)
    
    def add_button_box(self, layout):
        btn_box = QtWidgets.QDialogButtonBox(
            QtWidgets.QDialogButtonBox.Ok | QtWidgets.QDialogButtonBox.Cancel
        )
        btn_box.accepted.connect(self.accept)
        btn_box.rejected.connect(self.reject)
        layout.addRow(btn_box)