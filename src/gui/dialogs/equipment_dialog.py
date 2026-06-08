"""
دیالوگ مدیریت تجهیزات (نوع تجهیز) برای برنامه نت
"""

from PyQt5 import QtWidgets, QtCore
from .dialog_style import DIALOG_STYLE, BUTTON_STYLE, CANCEL_BUTTON_STYLE

class EquipmentDialog(QtWidgets.QDialog):
    def __init__(self, parent=None, equipment=None, db=None):
        super().__init__(parent)
        self.setStyleSheet(DIALOG_STYLE)
        self.db = db
        self.equipment = equipment
        self.setWindowTitle("➕ افزودن تجهیز جدید" if not equipment else "✏️ ویرایش تجهیز")
        self.setModal(True)
        self.resize(450, 220)
        self.setup_ui()
        if equipment:
            self.load_equipment_data()

    def setup_ui(self):
        layout = QtWidgets.QFormLayout(self)
        layout.setLabelAlignment(QtCore.Qt.AlignRight)
        layout.setSpacing(12)
        layout.setContentsMargins(20, 20, 20, 20)

        self.name_edit = QtWidgets.QLineEdit()
        self.name_edit.setPlaceholderText("مثال: mooring, buoy, anchor, net, cage, collector")
        layout.addRow("نام تجهیز:", self.name_edit)

        self.display_name_edit = QtWidgets.QLineEdit()
        self.display_name_edit.setPlaceholderText("عنوان نمایشی (مثال: سیستم مهار, بویه, لنگر)")
        layout.addRow("عنوان نمایشی:", self.display_name_edit)

        btn_layout = QtWidgets.QHBoxLayout()
        btn_layout.setSpacing(12)
        btn_layout.addStretch()

        ok_btn = QtWidgets.QPushButton("ذخیره")
        ok_btn.setFixedSize(90, 34)
        ok_btn.setStyleSheet(BUTTON_STYLE)
        ok_btn.clicked.connect(self.accept)

        cancel_btn = QtWidgets.QPushButton("انصراف")
        cancel_btn.setFixedSize(90, 34)
        cancel_btn.setStyleSheet(CANCEL_BUTTON_STYLE)
        cancel_btn.clicked.connect(self.reject)

        btn_layout.addWidget(ok_btn)
        btn_layout.addWidget(cancel_btn)
        layout.addRow(btn_layout)

    def load_equipment_data(self):
        if self.equipment:
            self.name_edit.setText(self.equipment.get('name', ''))
            self.display_name_edit.setText(self.equipment.get('display_name', ''))

    def get_data(self):
        return {
            'name': self.name_edit.text().strip(),
            'display_name': self.display_name_edit.text().strip()
        }