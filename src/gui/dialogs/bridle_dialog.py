"""
دیالوگ افزودن و ویرایش طناب برایدل برای ERP-Aqua
(اتصال قفس به بویه - قفس با مختصات مشخص می‌شود)
"""

from PyQt5 import QtWidgets, QtCore

from .base_dialog import BaseDialog
from ...core.models import BridleRope
from ...core.constants import COORDINATE_MIN, COORDINATE_MAX, DEFAULT_BRIDLE_COLOR
from ...widgets.color_button import ColorButton
from ...widgets.jalali_date_edit import JalaliDateEdit


class AddBridleRopeDialog(BaseDialog):
    """
    دیالوگ افزودن یا ویرایش طناب برایدل (اتصال قفس به بویه)
    """
    
    def __init__(self, parent=None, buoys=None, bridle=None, mooring_id=""):
        self.buoys = buoys or []
        self.bridle = bridle if bridle else BridleRope()
        self.mooring_id = mooring_id
        edit_mode = bridle is not None
        title = "ویرایش طناب برایدل" if edit_mode else "افزودن طناب برایدل جدید"
        super().__init__(parent, title=title, edit_mode=edit_mode, width=450, height=620)
        self.setup_ui()
    
    def setup_ui(self):
        """تنظیم رابط کاربری دیالوگ"""
        layout = QtWidgets.QFormLayout(self)
        layout.setLabelAlignment(QtCore.Qt.AlignRight)
        layout.setSpacing(10)
        
        # ========== شناسه طناب برایدل ==========
        self.id_edit = QtWidgets.QLineEdit()
        self.id_edit.setText(self.bridle.id)
        layout.addRow("شناسه طناب برایدل:", self.id_edit)
        
        # ========== قطر طناب ==========
        self.diameter = QtWidgets.QDoubleSpinBox()
        self.diameter.setRange(10, 80)
        self.diameter.setSuffix(" mm")
        self.diameter.setValue(self.bridle.diameter)
        layout.addRow("قطر طناب:", self.diameter)
        
        # ========== طول طناب ==========
        self.length = QtWidgets.QDoubleSpinBox()
        self.length.setRange(1, 100)
        self.length.setSuffix(" متر")
        self.length.setValue(self.bridle.length)
        layout.addRow("طول طناب:", self.length)
        
        # ========== جنس طناب ==========
        self.material_combo = QtWidgets.QComboBox()
        self.material_combo.addItems(["پلی پروپیلن", "پلی اتیلن", "داینما", "نایلون", "فولاد"])
        current_material = getattr(self.bridle, 'material', 'پلی پروپیلن')
        index = self.material_combo.findText(current_material)
        if index >= 0:
            self.material_combo.setCurrentIndex(index)
        layout.addRow("جنس طناب:", self.material_combo)
        
        # ========== تعداد رشته ==========
        self.strand_count = QtWidgets.QSpinBox()
        self.strand_count.setRange(1, 20)
        self.strand_count.setValue(getattr(self.bridle, 'strand_count', 3))
        layout.addRow("تعداد رشته:", self.strand_count)
        
        # ========== تاریخ نصب ==========
        self.install_date = JalaliDateEdit()
        if hasattr(self.bridle, 'install_date') and self.bridle.install_date:
            self.install_date.set_jalali_date(self.bridle.install_date)
        layout.addRow("تاریخ نصب:", self.install_date)
        
        # ========== وضعیت طناب ==========
        self.status_combo = QtWidgets.QComboBox()
        self.status_combo.addItems(["سالم", "نیاز به تعمیر", "خراب", "در حال تعمیر"])
        current_status = getattr(self.bridle, 'status', 'سالم')
        index = self.status_combo.findText(current_status)
        if index >= 0:
            self.status_combo.setCurrentIndex(index)
        layout.addRow("وضعیت طناب:", self.status_combo)
        
        # ========== مختصات قفس ==========
        self.cage_x = QtWidgets.QDoubleSpinBox()
        self.cage_x.setRange(COORDINATE_MIN, COORDINATE_MAX)
        self.cage_x.setValue(self.bridle.cage_x if self.bridle.cage_x != 0 else 500)
        layout.addRow("مختصات قفس X:", self.cage_x)
        
        self.cage_y = QtWidgets.QDoubleSpinBox()
        self.cage_y.setRange(COORDINATE_MIN, COORDINATE_MAX)
        self.cage_y.setValue(self.bridle.cage_y if self.bridle.cage_y != 0 else 500)
        layout.addRow("مختصات قفس Y:", self.cage_y)
        
        # ========== بویه متصل ==========
        self.buoy_combo = QtWidgets.QComboBox()
        self.buoy_combo.addItem("--- انتخاب بویه ---")
        for b in self.buoys:
            self.buoy_combo.addItem(b.id, b.id)
        if self.bridle.buoy_id:
            idx = self.buoy_combo.findData(self.bridle.buoy_id)
            if idx >= 0:
                self.buoy_combo.setCurrentIndex(idx)
        layout.addRow("بویه متصل:", self.buoy_combo)
        
        # ========== رنگ در نقشه ==========
        color_layout = QtWidgets.QHBoxLayout()
        self.color_btn = ColorButton(self.bridle.color if self.bridle.color else DEFAULT_BRIDLE_COLOR)
        color_layout.addWidget(self.color_btn)
        color_layout.addWidget(QtWidgets.QLabel("رنگ خط در نقشه"))
        color_layout.addStretch()
        layout.addRow("رنگ نقشه:", color_layout)
        
        # ========== یادداشت ==========
        self.note = QtWidgets.QTextEdit()
        self.note.setMaximumHeight(80)
        self.note.setPlaceholderText("توضیحات اضافی...")
        self.note.setText(getattr(self.bridle, 'note', ''))
        layout.addRow("یادداشت:", self.note)
        
        # ========== دکمه‌ها ==========
        self.add_button_box(layout)
    
    def validate_data(self):
        """اعتبارسنجی داده‌ها"""
        if not self.id_edit.text().strip():
            self.show_error("شناسه طناب برایدل را وارد کنید")
            self.id_edit.setFocus()
            return False
        
        if not self.buoy_combo.currentData():
            self.show_error("لطفاً بویه را انتخاب کنید")
            return False
        
        return True
    
    def accept(self):
        """پذیرش دیالوگ و ذخیره اطلاعات طناب برایدل"""
        if not self.validate_data():
            return
        
        self.bridle.id = self.id_edit.text().strip()
        self.bridle.mooring_id = self.mooring_id
        self.bridle.diameter = self.diameter.value()
        self.bridle.length = self.length.value()
        self.bridle.material = self.material_combo.currentText()
        self.bridle.strand_count = self.strand_count.value()
        self.bridle.install_date = self.install_date.get_jalali_date()
        self.bridle.status = self.status_combo.currentText()
        self.bridle.cage_x = self.cage_x.value()
        self.bridle.cage_y = self.cage_y.value()
        self.bridle.buoy_id = self.buoy_combo.currentData()
        self.bridle.color = self.color_btn.get_color()
        self.bridle.note = self.note.toPlainText()
        
        super().accept()