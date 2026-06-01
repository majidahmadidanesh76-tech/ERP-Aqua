"""
دیالوگ افزودن و ویرایش کلکتور برای ERP-Aqua
"""

from PyQt5 import QtWidgets, QtCore

from .base_dialog import BaseDialog
from ...core.models import Collector
from ...core.constants import COORDINATE_MIN, COORDINATE_MAX, DEFAULT_COLLECTOR_COLOR
from ...widgets.color_button import ColorButton
from ...widgets.jalali_date_edit import JalaliDateEdit


class AddCollectorDialog(BaseDialog):
    """
    دیالوگ افزودن یا ویرایش کلکتور
    """
    
    def __init__(self, parent=None, buoys=None, collector=None, mooring_id=""):
        self.buoys = buoys or []
        self.collector = collector if collector else Collector()
        self.mooring_id = mooring_id
        edit_mode = collector is not None
        title = "ویرایش کلکتور" if edit_mode else "افزودن کلکتور جدید"
        super().__init__(parent, title=title, edit_mode=edit_mode, width=450, height=550)
        self.setup_ui()
    
    def setup_ui(self):
        """تنظیم رابط کاربری دیالوگ"""
        layout = QtWidgets.QFormLayout(self)
        layout.setLabelAlignment(QtCore.Qt.AlignRight)
        layout.setSpacing(10)
        
        # ========== شناسه کلکتور ==========
        self.id_edit = QtWidgets.QLineEdit()
        self.id_edit.setText(self.collector.id)
        layout.addRow("شناسه کلکتور:", self.id_edit)
        
        # ========== قطر کلکتور ==========
        self.diameter = QtWidgets.QDoubleSpinBox()
        self.diameter.setRange(0.1, 10)
        self.diameter.setSuffix(" متر")
        self.diameter.setValue(self.collector.diameter)
        layout.addRow("قطر کلکتور:", self.diameter)
        
        # ========== ضخامت کلکتور ==========
        self.thickness = QtWidgets.QSpinBox()
        self.thickness.setRange(1, 50)
        self.thickness.setSuffix(" mm")
        self.thickness.setValue(getattr(self.collector, 'thickness', 10))
        layout.addRow("ضخامت کلکتور:", self.thickness)
        
        # ========== عمق کلکتور ==========
        self.depth = QtWidgets.QDoubleSpinBox()
        self.depth.setRange(0, 100)
        self.depth.setSuffix(" متر")
        self.depth.setValue(self.collector.depth)
        layout.addRow("عمق کلکتور:", self.depth)
        
        # ========== جنس بدنه ==========
        self.material_combo = QtWidgets.QComboBox()
        self.material_combo.addItems(["فولاد", "گالوانیزه", "استیل", "پلاستیک", "فایبرگلاس"])
        current_material = getattr(self.collector, 'material', 'فولاد')
        index = self.material_combo.findText(current_material)
        if index >= 0:
            self.material_combo.setCurrentIndex(index)
        layout.addRow("جنس بدنه:", self.material_combo)
        
        # ========== تاریخ نصب ==========
        self.install_date = JalaliDateEdit()
        if hasattr(self.collector, 'install_date') and self.collector.install_date:
            self.install_date.set_jalali_date(self.collector.install_date)
        layout.addRow("تاریخ نصب:", self.install_date)
        
        # ========== وضعیت کلکتور ==========
        self.status_combo = QtWidgets.QComboBox()
        self.status_combo.addItems(["سالم", "نیاز به تعمیر", "خراب", "در حال تعمیر"])
        current_status = getattr(self.collector, 'status', 'سالم')
        index = self.status_combo.findText(current_status)
        if index >= 0:
            self.status_combo.setCurrentIndex(index)
        layout.addRow("وضعیت کلکتور:", self.status_combo)
        
        # ========== بویه متصل ==========
        self.buoy_combo = QtWidgets.QComboBox()
        self.buoy_combo.addItem("--- انتخاب بویه ---")
        for b in self.buoys:
            self.buoy_combo.addItem(b.id, b.id)
        if self.collector.buoy_id:
            idx = self.buoy_combo.findData(self.collector.buoy_id)
            if idx >= 0:
                self.buoy_combo.setCurrentIndex(idx)
        layout.addRow("بویه متصل:", self.buoy_combo)
        
        # ========== رنگ در نقشه ==========
        color_layout = QtWidgets.QHBoxLayout()
        self.color_btn = ColorButton(self.collector.color if self.collector.color else DEFAULT_COLLECTOR_COLOR)
        color_layout.addWidget(self.color_btn)
        color_layout.addWidget(QtWidgets.QLabel("رنگ در نقشه (دایره زیر بویه)"))
        color_layout.addStretch()
        layout.addRow("رنگ نقشه:", color_layout)
        
        # ========== یادداشت ==========
        self.note = QtWidgets.QTextEdit()
        self.note.setMaximumHeight(80)
        self.note.setPlaceholderText("توضیحات اضافی...")
        self.note.setText(getattr(self.collector, 'note', ''))
        layout.addRow("یادداشت:", self.note)
        
        # ========== دکمه‌ها ==========
        self.add_button_box(layout)
    
    def validate_data(self):
        """اعتبارسنجی داده‌ها"""
        if not self.id_edit.text().strip():
            self.show_error("شناسه کلکتور را وارد کنید")
            self.id_edit.setFocus()
            return False
        
        if not self.buoy_combo.currentData():
            self.show_error("لطفاً بویه را انتخاب کنید")
            return False
        
        return True
    
    def accept(self):
        """پذیرش دیالوگ و ذخیره اطلاعات کلکتور"""
        if not self.validate_data():
            return
        
        self.collector.id = self.id_edit.text().strip()
        self.collector.mooring_id = self.mooring_id
        self.collector.diameter = self.diameter.value()
        self.collector.thickness = self.thickness.value()
        self.collector.depth = self.depth.value()
        self.collector.material = self.material_combo.currentText()
        self.collector.install_date = self.install_date.get_jalali_date()
        self.collector.status = self.status_combo.currentText()
        self.collector.buoy_id = self.buoy_combo.currentData()
        self.collector.color = self.color_btn.get_color()
        self.collector.note = self.note.toPlainText()
        
        super().accept()