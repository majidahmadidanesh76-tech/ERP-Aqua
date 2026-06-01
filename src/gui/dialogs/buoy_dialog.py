"""
دیالوگ افزودن و ویرایش بویه برای ERP-Aqua
"""

from PyQt5 import QtWidgets, QtCore

from .base_dialog import BaseDialog
from ...core.models import Buoy
from ...core.constants import COORDINATE_MIN, COORDINATE_MAX, DEFAULT_BUOY_COLOR
from ...widgets.color_button import ColorButton
from ...widgets.jalali_date_edit import JalaliDateEdit


class BuoyDialog(BaseDialog):
    """
    دیالوگ افزودن یا ویرایش بویه
    """
    
    def __init__(self, parent=None, buoy=None, edit_mode=False, mooring_id=""):
        self.buoy = buoy if buoy else Buoy()
        self.mooring_id = mooring_id
        title = "ویرایش بویه" if edit_mode else "افزودن بویه جدید"
        super().__init__(parent, title=title, edit_mode=edit_mode, width=450, height=620)
        self.setup_ui()
    
    def setup_ui(self):
        """تنظیم رابط کاربری دیالوگ"""
        layout = QtWidgets.QFormLayout(self)
        layout.setLabelAlignment(QtCore.Qt.AlignRight)
        layout.setSpacing(10)
        
        # ========== شناسه بویه ==========
        self.id_edit = QtWidgets.QLineEdit()
        self.id_edit.setText(self.buoy.id)
        layout.addRow("شناسه بویه:", self.id_edit)
        
        # ========== نوع بویه ==========
        self.buoy_type_combo = QtWidgets.QComboBox()
        self.buoy_type_combo.addItems(["اصلی", "نشانه‌گر"])
        self.buoy_type_combo.setCurrentIndex(0 if self.buoy.buoy_type == "main" else 1)
        layout.addRow("نوع بویه:", self.buoy_type_combo)
        
        # ========== جنس بویه ==========
        self.material_combo = QtWidgets.QComboBox()
        self.material_combo.addItems(["پلاستیک", "فولاد", "فایبرگلاس", "چوب", "بتن"])
        current_material = getattr(self.buoy, 'material', 'پلاستیک')
        index = self.material_combo.findText(current_material)
        if index >= 0:
            self.material_combo.setCurrentIndex(index)
        layout.addRow("جنس بویه:", self.material_combo)
        
        # ========== مختصات ==========
        self.utm_x = QtWidgets.QDoubleSpinBox()
        self.utm_x.setRange(COORDINATE_MIN, COORDINATE_MAX)
        self.utm_x.setValue(self.buoy.utm_x if self.buoy.utm_x != 0 else 500)
        layout.addRow("UTM X:", self.utm_x)
        
        self.utm_y = QtWidgets.QDoubleSpinBox()
        self.utm_y.setRange(COORDINATE_MIN, COORDINATE_MAX)
        self.utm_y.setValue(self.buoy.utm_y if self.buoy.utm_y != 0 else 500)
        layout.addRow("UTM Y:", self.utm_y)
        
        # ========== حجم بویه ==========
        self.volume = QtWidgets.QDoubleSpinBox()
        self.volume.setRange(0, 10000)
        self.volume.setSuffix(" لیتر")
        self.volume.setValue(getattr(self.buoy, 'volume', 0))
        layout.addRow("حجم بویه:", self.volume)
        
        # ========== تاریخ نصب ==========
        self.install_date = JalaliDateEdit()
        if hasattr(self.buoy, 'install_date') and self.buoy.install_date:
            self.install_date.set_jalali_date(self.buoy.install_date)
        layout.addRow("تاریخ نصب:", self.install_date)
        
        # ========== وضعیت بویه ==========
        self.status_combo = QtWidgets.QComboBox()
        self.status_combo.addItems(["سالم", "نیاز به تعمیر", "خراب", "در حال تعمیر", "منسوخ"])
        current_status = getattr(self.buoy, 'status', 'سالم')
        index = self.status_combo.findText(current_status)
        if index >= 0:
            self.status_combo.setCurrentIndex(index)
        layout.addRow("وضعیت بویه:", self.status_combo)
        
        # ========== چراغ چشمک زن ==========
        self.has_light = QtWidgets.QCheckBox()
        self.has_light.setChecked(getattr(self.buoy, 'has_light', False))
        layout.addRow("چراغ چشمک زن:", self.has_light)
        
        # ========== رنگ بدنه ==========
        body_color_layout = QtWidgets.QHBoxLayout()
        current_body_color = getattr(self.buoy, 'body_color', '#A0A0A0')
        self.body_color_btn = ColorButton(current_body_color)
        body_color_layout.addWidget(self.body_color_btn)
        body_color_layout.addWidget(QtWidgets.QLabel("انتخاب رنگ بدنه"))
        body_color_layout.addStretch()
        layout.addRow("رنگ بدنه:", body_color_layout)
        
        # ========== رنگ در نقشه ==========
        map_color_layout = QtWidgets.QHBoxLayout()
        self.color_btn = ColorButton(self.buoy.color if self.buoy.color else DEFAULT_BUOY_COLOR)
        map_color_layout.addWidget(self.color_btn)
        map_color_layout.addWidget(QtWidgets.QLabel("رنگ در نقشه"))
        map_color_layout.addStretch()
        layout.addRow("رنگ نقشه:", map_color_layout)
        
        # ========== یادداشت ==========
        self.note = QtWidgets.QTextEdit()
        self.note.setMaximumHeight(80)
        self.note.setPlaceholderText("توضیحات اضافی...")
        self.note.setText(getattr(self.buoy, 'note', ''))
        layout.addRow("یادداشت:", self.note)
        
        # ========== دکمه‌ها ==========
        self.add_button_box(layout)
    
    def validate_data(self):
        """اعتبارسنجی داده‌ها"""
        if not self.id_edit.text().strip():
            self.show_error("شناسه بویه را وارد کنید")
            self.id_edit.setFocus()
            return False
        return True
    
    def accept(self):
        """پذیرش دیالوگ و ذخیره اطلاعات بویه"""
        if not self.validate_data():
            return
        
        # فیلدهای اصلی
        self.buoy.id = self.id_edit.text().strip()
        self.buoy.mooring_id = self.mooring_id
        self.buoy.buoy_type = "main" if self.buoy_type_combo.currentIndex() == 0 else "marker"
        self.buoy.utm_x = self.utm_x.value()
        self.buoy.utm_y = self.utm_y.value()
        self.buoy.color = self.color_btn.get_color()
        
        # فیلدهای جدید
        self.buoy.material = self.material_combo.currentText()
        self.buoy.volume = self.volume.value()
        self.buoy.install_date = self.install_date.get_jalali_date()
        self.buoy.status = self.status_combo.currentText()
        self.buoy.has_light = self.has_light.isChecked()
        self.buoy.body_color = self.body_color_btn.get_color()
        self.buoy.note = self.note.toPlainText()
        
        super().accept()