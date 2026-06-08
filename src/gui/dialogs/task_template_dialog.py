"""
دیالوگ مدیریت الگوهای وظایف تکراری
"""

from PyQt5 import QtWidgets, QtCore
from .dialog_style import DIALOG_STYLE, BUTTON_STYLE, CANCEL_BUTTON_STYLE


class TaskTemplateDialog(QtWidgets.QDialog):
    def __init__(self, parent=None, template=None, db=None):
        super().__init__(parent)
        self.setStyleSheet(DIALOG_STYLE)
        
        self.db = db
        self.template = template
        self.setWindowTitle("➕ الگوی جدید" if not template else "✏️ ویرایش الگو")
        self.setModal(True)
        self.resize(420, 400)
        self.setup_ui()
        if template:
            self.load_template_data()

    def setup_ui(self):
        layout = QtWidgets.QFormLayout(self)
        layout.setLabelAlignment(QtCore.Qt.AlignRight)
        layout.setSpacing(12)
        layout.setContentsMargins(20, 20, 20, 20)

        # نام الگو
        self.name_edit = QtWidgets.QLineEdit()
        self.name_edit.setPlaceholderText("مثال: شستشوی ماهانه تور")
        layout.addRow("نام الگو:", self.name_edit)

        # مدت زمان پیش‌فرض
        self.duration = QtWidgets.QSpinBox()
        self.duration.setRange(15, 1440)
        self.duration.setSuffix(" دقیقه")
        self.duration.setValue(60)
        layout.addRow("مدت زمان:", self.duration)

        # مسئول پیش‌فرض
        self.assigned_to = QtWidgets.QLineEdit()
        self.assigned_to.setPlaceholderText("مثال: واحد بهره برداری")
        layout.addRow("مسئول:", self.assigned_to)

        # توضیحات
        self.desc_edit = QtWidgets.QTextEdit()
        self.desc_edit.setPlaceholderText("توضیحات الگو...")
        layout.addRow("توضیحات:", self.desc_edit)

        # دکمه‌ها
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

    def load_template_data(self):
        if self.template:
            self.name_edit.setText(self.template.get('name', ''))
            self.duration.setValue(self.template.get('default_duration_minutes', 60))
            self.assigned_to.setText(self.template.get('default_assigned_to', ''))
            self.desc_edit.setText(self.template.get('description', ''))

    def get_data(self):
        return {
            'name': self.name_edit.text().strip(),
            'category': 'other',
            'duration': self.duration.value(),
            'assigned_to': self.assigned_to.text().strip(),
            'description': self.desc_edit.toPlainText()
        }