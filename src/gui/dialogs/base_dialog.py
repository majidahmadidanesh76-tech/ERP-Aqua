# src/gui/dialogs/base_dialog.py (نسخه بهبود یافته)

from PyQt5 import QtWidgets, QtCore

class BaseDialog(QtWidgets.QDialog):
    """
    کلاس پایه دیالوگ با قابلیت‌های مشترک و استایل یکسان
    """

    def __init__(self, parent=None, title="", edit_mode=False, width=450, height=400):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setModal(True)
        self.edit_mode = edit_mode
        self.resize(width, height)
        self.setup_common_style()
        self.setMinimumSize(width - 50, height - 50)

    def setup_common_style(self):
        """تنظیمات استایل مشترک برای همه دیالوگ‌ها (تم روشن)"""
        self.setStyleSheet("""
            QDialog {
                background-color: #FFFFFF;
                border-radius: 12px;
            }
            QLabel {
                color: #1A2C3E;
                background-color: transparent;
                font-weight: 500;
            }
            QLineEdit, QComboBox, QDoubleSpinBox, QSpinBox, 
            QTextEdit, QDateTimeEdit, QDateEdit, QTimeEdit {
                background-color: #FFFFFF;
                border: 1px solid #D0D5D9;
                border-radius: 8px;
                padding: 7px 10px;
                color: #1A2C3E;
                font-size: 12px;
                min-height: 32px;
            }
            QLineEdit:focus, QComboBox:focus, QDateTimeEdit:focus, 
            QDateEdit:focus, QTimeEdit:focus, QTextEdit:focus {
                border-color: #0078D4;
                outline: none;
            }
            QComboBox::drop-down {
                border: none;
                width: 24px;
            }
            QComboBox QAbstractItemView {
                background-color: #FFFFFF;
                color: #1A2C3E;
                selection-background-color: #E8F0FE;
                selection-color: #0078D4;
                border: 1px solid #E1E5E9;
                border-radius: 8px;
            }
            QSpinBox::up-button, QSpinBox::down-button,
            QDoubleSpinBox::up-button, QDoubleSpinBox::down-button {
                width: 20px;
                background-color: #F0F0F0;
                border-radius: 4px;
            }
            QSpinBox::up-button:hover, QSpinBox::down-button:hover,
            QDoubleSpinBox::up-button:hover, QDoubleSpinBox::down-button:hover {
                background-color: #0078D4;
            }
            QTextEdit {
                min-height: 70px;
            }
            QGroupBox {
                color: #0078D4;
                border: 1px solid #E1E5E9;
                border-radius: 10px;
                margin-top: 12px;
                font-weight: bold;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 12px;
                padding: 0 8px;
                color: #0078D4;
            }
            QPushButton {
                background-color: #0078D4;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 7px 16px;
                font-weight: 600;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #106EBE;
            }
            QPushButton:last-child {
                background-color: #F0F0F0;
                color: #1A2C3E;
                border: 1px solid #D0D5D9;
            }
            QPushButton:last-child:hover {
                background-color: #E8F0FE;
                border-color: #0078D4;
            }
        """)

    def show_error(self, message):
        QtWidgets.QMessageBox.warning(self, "خطا", message)

    def show_info(self, message):
        QtWidgets.QMessageBox.information(self, "اطلاع", message)

    def add_button_box(self, layout):
        """اضافه کردن دکمه‌های OK و Cancel به فرم"""
        btn_layout = QtWidgets.QHBoxLayout()
        btn_layout.setSpacing(12)
        btn_layout.addStretch()

        ok_btn = QtWidgets.QPushButton("تأیید")
        ok_btn.setMinimumWidth(90)
        ok_btn.clicked.connect(self.accept)

        cancel_btn = QtWidgets.QPushButton("انصراف")
        cancel_btn.setMinimumWidth(90)
        cancel_btn.clicked.connect(self.reject)

        btn_layout.addWidget(ok_btn)
        btn_layout.addWidget(cancel_btn)
        layout.addRow(btn_layout)