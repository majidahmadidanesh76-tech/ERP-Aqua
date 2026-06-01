"""
دیالوگ افزودن و ویرایش قفس برای ERP-Aqua
"""

from PyQt5 import QtWidgets, QtCore

from .base_dialog import BaseDialog
from ...core.models import Cage
from ...core.constants import COORDINATE_MIN, COORDINATE_MAX, DEFAULT_CAGE_COLOR
from ...widgets.color_button import ColorButton
from ...widgets.jalali_date_edit import JalaliDateEdit


class AddCageDialog(BaseDialog):
    """
    دیالوگ افزودن یا ویرایش قفس
    """
    
    def __init__(self, parent=None, cage=None, mooring_id=""):
        self.cage = cage if cage else Cage()
        self.mooring_id = mooring_id
        edit_mode = cage is not None
        title = "ویرایش قفس" if edit_mode else "افزودن قفس جدید"
        super().__init__(parent, title=title, edit_mode=edit_mode, width=450, height=550)
        self.setup_ui()
    
    def setup_ui(self):
        """تنظیم رابط کاربری دیالوگ"""
        layout = QtWidgets.QFormLayout(self)
        layout.setLabelAlignment(QtCore.Qt.AlignRight)
        layout.setSpacing(10)
        
        # ========== شناسه قفس ==========
        self.id_edit = QtWidgets.QLineEdit()
        self.id_edit.setText(self.cage.id)
        layout.addRow("شناسه قفس:", self.id_edit)
        
        # ========== قطر قفس ==========
        self.diameter = QtWidgets.QDoubleSpinBox()
        self.diameter.setRange(1, 100)
        self.diameter.setSuffix(" متر")
        self.diameter.setValue(self.cage.diameter)
        layout.addRow("قطر قفس:", self.diameter)
        
        # ========== جنس قفس ==========
        self.material_combo = QtWidgets.QComboBox()
        self.material_combo.addItems(["فولاد", "گالوانیزه", "استیل", "پلاستیک", "فایبرگلاس"])
        current_material = getattr(self.cage, 'material', 'فولاد')
        index = self.material_combo.findText(current_material)
        if index >= 0:
            self.material_combo.setCurrentIndex(index)
        layout.addRow("جنس قفس:", self.material_combo)
        
        # ========== مختصات X ==========
        self.utm_x = QtWidgets.QDoubleSpinBox()
        self.utm_x.setRange(COORDINATE_MIN, COORDINATE_MAX)
        self.utm_x.setValue(self.cage.utm_x if self.cage.utm_x != 0 else 500)
        layout.addRow("مختصات X:", self.utm_x)
        
        # ========== مختصات Y ==========
        self.utm_y = QtWidgets.QDoubleSpinBox()
        self.utm_y.setRange(COORDINATE_MIN, COORDINATE_MAX)
        self.utm_y.setValue(self.cage.utm_y if self.cage.utm_y != 0 else 500)
        layout.addRow("مختصات Y:", self.utm_y)
        
        # ========== تاریخ نصب ==========
        self.install_date = JalaliDateEdit()
        if hasattr(self.cage, 'install_date') and self.cage.install_date:
            self.install_date.set_jalali_date(self.cage.install_date)
        layout.addRow("تاریخ نصب:", self.install_date)
        
        # ========== وضعیت قفس ==========
        self.status_combo = QtWidgets.QComboBox()
        self.status_combo.addItems(["سالم", "نیاز به تعمیر", "خراب", "در حال تعمیر"])
        current_status = getattr(self.cage, 'status', 'سالم')
        index = self.status_combo.findText(current_status)
        if index >= 0:
            self.status_combo.setCurrentIndex(index)
        layout.addRow("وضعیت قفس:", self.status_combo)
        
        # ========== رنگ در نقشه ==========
        color_layout = QtWidgets.QHBoxLayout()
        self.color_btn = ColorButton(self.cage.color if self.cage.color else DEFAULT_CAGE_COLOR)
        color_layout.addWidget(self.color_btn)
        color_layout.addWidget(QtWidgets.QLabel("رنگ دایره قفس در نقشه"))
        color_layout.addStretch()
        layout.addRow("رنگ نقشه:", color_layout)
        
        # ========== یادداشت ==========
        self.note = QtWidgets.QTextEdit()
        self.note.setMaximumHeight(80)
        self.note.setPlaceholderText("توضیحات اضافی...")
        self.note.setText(getattr(self.cage, 'note', ''))
        layout.addRow("یادداشت:", self.note)
        
        # ========== دکمه‌ها ==========
        self.add_button_box(layout)
    
    def validate_data(self):
        """اعتبارسنجی داده‌ها"""
        if not self.id_edit.text().strip():
            self.show_error("شناسه قفس را وارد کنید")
            self.id_edit.setFocus()
            return False
        return True
    
    def accept(self):
        """پذیرش دیالوگ و ذخیره اطلاعات قفس"""
        if not self.validate_data():
            return
        
        self.cage.id = self.id_edit.text().strip()
        self.cage.mooring_id = self.mooring_id
        self.cage.diameter = self.diameter.value()
        self.cage.material = self.material_combo.currentText()
        self.cage.utm_x = self.utm_x.value()
        self.cage.utm_y = self.utm_y.value()
        self.cage.install_date = self.install_date.get_jalali_date()
        self.cage.status = self.status_combo.currentText()
        self.cage.color = self.color_btn.get_color()
        self.cage.note = self.note.toPlainText()
        
        super().accept()