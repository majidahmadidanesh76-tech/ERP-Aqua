"""
دیالوگ افزودن و ویرایش لنگر برای ERP-Aqua
"""

from PyQt5 import QtWidgets, QtCore

from .base_dialog import BaseDialog
from ...core.models import Anchor
from ...core.constants import COORDINATE_MIN, COORDINATE_MAX, DEFAULT_ANCHOR_COLOR
from ...widgets.color_button import ColorButton
from ...widgets.jalali_date_edit import JalaliDateEdit


class AnchorDialog(BaseDialog):
    
    def __init__(self, parent=None, anchor=None, edit_mode=False, mooring_id=""):
        self.anchor = anchor if anchor else Anchor()
        self.mooring_id = mooring_id
        title = "ویرایش لنگر" if edit_mode else "افزودن لنگر جدید"
        super().__init__(parent, title=title, edit_mode=edit_mode, width=450, height=600)
        self.setup_ui()
    
    def setup_ui(self):
        layout = QtWidgets.QFormLayout(self)
        layout.setLabelAlignment(QtCore.Qt.AlignRight)
        layout.setSpacing(10)
        
        # شناسه
        self.id_edit = QtWidgets.QLineEdit()
        self.id_edit.setText(self.anchor.id)
        layout.addRow("شناسه لنگر:", self.id_edit)
        
        # نوع لنگر
        self.anchor_type_combo = QtWidgets.QComboBox()
        self.anchor_type_combo.addItems(["فلزی (فولاد)", "بتنی"])
        if self.anchor.anchor_type == "steel":
            self.anchor_type_combo.setCurrentIndex(0)
        else:
            self.anchor_type_combo.setCurrentIndex(1)
        layout.addRow("نوع لنگر:", self.anchor_type_combo)
        
        # جنس لنگر
        self.material_combo = QtWidgets.QComboBox()
        self.material_combo.addItems(["فولاد", "چدن", "بتن", "سنگ", "آهنی"])
        current_material = getattr(self.anchor, 'material', 'فولاد')
        index = self.material_combo.findText(current_material)
        if index >= 0:
            self.material_combo.setCurrentIndex(index)
        layout.addRow("جنس لنگر:", self.material_combo)
        
        # مختصات
        self.utm_x = QtWidgets.QDoubleSpinBox()
        self.utm_x.setRange(COORDINATE_MIN, COORDINATE_MAX)
        self.utm_x.setValue(self.anchor.utm_x if self.anchor.utm_x != 0 else 520)
        layout.addRow("UTM X:", self.utm_x)
        
        self.utm_y = QtWidgets.QDoubleSpinBox()
        self.utm_y.setRange(COORDINATE_MIN, COORDINATE_MAX)
        self.utm_y.setValue(self.anchor.utm_y if self.anchor.utm_y != 0 else 480)
        layout.addRow("UTM Y:", self.utm_y)
        
        # وزن
        self.weight = QtWidgets.QDoubleSpinBox()
        self.weight.setRange(0, 5000)
        self.weight.setSuffix(" kg")
        self.weight.setValue(self.anchor.weight)
        layout.addRow("وزن:", self.weight)
        
        # عمق نصب
        self.install_depth = QtWidgets.QDoubleSpinBox()
        self.install_depth.setRange(0, 100)
        self.install_depth.setSuffix(" متر")
        self.install_depth.setValue(getattr(self.anchor, 'install_depth', 0))
        layout.addRow("عمق نصب:", self.install_depth)
        
        # تاریخ نصب
        self.install_date = JalaliDateEdit()
        if hasattr(self.anchor, 'install_date') and self.anchor.install_date:
            self.install_date.set_jalali_date(self.anchor.install_date)
        layout.addRow("تاریخ نصب:", self.install_date)
        
        # وضعیت
        self.status_combo = QtWidgets.QComboBox()
        self.status_combo.addItems(["سالم", "نیاز به تعمیر", "خراب", "در حال تعمیر"])
        current_status = getattr(self.anchor, 'status', 'سالم')
        index = self.status_combo.findText(current_status)
        if index >= 0:
            self.status_combo.setCurrentIndex(index)
        layout.addRow("وضعیت لنگر:", self.status_combo)
        
        # رنگ بدنه
        body_color_layout = QtWidgets.QHBoxLayout()
        current_body_color = getattr(self.anchor, 'body_color', '#6A9955')
        self.body_color_btn = ColorButton(current_body_color)
        body_color_layout.addWidget(self.body_color_btn)
        body_color_layout.addWidget(QtWidgets.QLabel("انتخاب رنگ بدنه"))
        body_color_layout.addStretch()
        layout.addRow("رنگ بدنه:", body_color_layout)
        
        # رنگ در نقشه
        map_color_layout = QtWidgets.QHBoxLayout()
        self.color_btn = ColorButton(self.anchor.color if self.anchor.color else DEFAULT_ANCHOR_COLOR)
        map_color_layout.addWidget(self.color_btn)
        map_color_layout.addWidget(QtWidgets.QLabel("رنگ در نقشه"))
        map_color_layout.addStretch()
        layout.addRow("رنگ نقشه:", map_color_layout)
        
        # یادداشت
        self.note = QtWidgets.QTextEdit()
        self.note.setMaximumHeight(80)
        self.note.setPlaceholderText("توضیحات اضافی...")
        self.note.setText(getattr(self.anchor, 'note', ''))
        layout.addRow("یادداشت:", self.note)
        
        self.add_button_box(layout)
    
    def validate_data(self):
        if not self.id_edit.text().strip():
            self.show_error("شناسه لنگر را وارد کنید")
            self.id_edit.setFocus()
            return False
        return True
    
    def accept(self):
        if not self.validate_data():
            return
        
        self.anchor.id = self.id_edit.text().strip()
        self.anchor.mooring_id = self.mooring_id
        
        if self.anchor_type_combo.currentIndex() == 0:
            self.anchor.anchor_type = "steel"
        else:
            self.anchor.anchor_type = "concrete"
        
        self.anchor.utm_x = self.utm_x.value()
        self.anchor.utm_y = self.utm_y.value()
        self.anchor.weight = self.weight.value()
        self.anchor.color = self.color_btn.get_color()
        self.anchor.material = self.material_combo.currentText()
        self.anchor.install_depth = self.install_depth.value()
        self.anchor.install_date = self.install_date.get_jalali_date()
        self.anchor.status = self.status_combo.currentText()
        self.anchor.body_color = self.body_color_btn.get_color()
        self.anchor.note = self.note.toPlainText()
        
        super().accept()