"""
دیالوگ مدیریت تجهیزات (نوع تجهیز) برای برنامه نت
"""

from PyQt5 import QtWidgets, QtCore


class EquipmentDialog(QtWidgets.QDialog):
    def __init__(self, parent=None, equipment=None, db=None):
        super().__init__(parent)
        self.db = db
        self.equipment = equipment
        self.setWindowTitle("➕ افزودن تجهیز جدید" if not equipment else "✏️ ویرایش تجهیز")
        self.setModal(True)
        self.resize(400, 250)
        self.setup_ui()
        if equipment:
            self.load_equipment_data()

    def get_glass_style(self):
        return """
            QPushButton {
                background-color: rgba(60, 60, 65, 200);
                color: #C8C8C8;
                border: 1px solid rgba(86, 156, 214, 80);
                border-radius: 4px;
                font-weight: bold;
                padding: 6px 12px;
            }
            QPushButton:hover {
                background-color: rgba(86, 156, 214, 100);
                border-color: rgba(86, 156, 214, 150);
                color: white;
            }
        """

    def setup_ui(self):
        layout = QtWidgets.QFormLayout(self)
        layout.setLabelAlignment(QtCore.Qt.AlignRight)
        layout.setSpacing(12)
        layout.setContentsMargins(20, 20, 20, 20)

        glass_style = self.get_glass_style()

        self.name_edit = QtWidgets.QLineEdit()
        self.name_edit.setPlaceholderText("مثال: mooring, buoy, anchor, net, cage, collector")
        self.name_edit.setStyleSheet("""
            QLineEdit {
                background-color: #3C3C3C;
                border: 1px solid #3E3E42;
                border-radius: 4px;
                padding: 8px;
                color: #C8C8C8;
            }
        """)
        layout.addRow("نام تجهیز:", self.name_edit)

        self.display_name_edit = QtWidgets.QLineEdit()
        self.display_name_edit.setPlaceholderText("عنوان نمایشی (مثال: سیستم مهار, بویه, لنگر)")
        self.display_name_edit.setStyleSheet("""
            QLineEdit {
                background-color: #3C3C3C;
                border: 1px solid #3E3E42;
                border-radius: 4px;
                padding: 8px;
                color: #C8C8C8;
            }
        """)
        layout.addRow("عنوان نمایشی:", self.display_name_edit)

        btn_layout = QtWidgets.QHBoxLayout()
        btn_layout.setSpacing(10)
        btn_layout.addStretch()

        ok_btn = QtWidgets.QPushButton("💾 ذخیره")
        ok_btn.setFixedSize(100, 35)
        ok_btn.setStyleSheet(glass_style)
        ok_btn.clicked.connect(self.accept)

        cancel_btn = QtWidgets.QPushButton("❌ انصراف")
        cancel_btn.setFixedSize(100, 35)
        cancel_btn.setStyleSheet(glass_style)
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