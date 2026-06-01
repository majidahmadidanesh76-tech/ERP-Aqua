"""
دیالوگ افزودن و ویرایش طناب اصلی برای ERP-Aqua
"""

from PyQt5 import QtWidgets, QtCore

from .base_dialog import BaseDialog
from ...core.models import AnchorRope
from ...core.constants import COORDINATE_MIN, COORDINATE_MAX, DEFAULT_ROPE_COLOR
from ...widgets.color_button import ColorButton
from ...widgets.jalali_date_edit import JalaliDateEdit


class AddRopeDialog(BaseDialog):
    """
    دیالوگ افزودن یا ویرایش طناب اصلی
    """
    
    def __init__(self, parent=None, buoys=None, chains=None, rope=None, mooring_id=""):
        self.buoys = buoys or []
        self.chains = chains or []
        self.rope = rope if rope else AnchorRope()
        self.mooring_id = mooring_id
        edit_mode = rope is not None
        title = "ویرایش طناب" if edit_mode else "افزودن طناب جدید"
        super().__init__(parent, title=title, edit_mode=edit_mode, width=480, height=650)
        self.setup_ui()
    
    def setup_ui(self):
        """تنظیم رابط کاربری دیالوگ"""
        layout = QtWidgets.QFormLayout(self)
        layout.setLabelAlignment(QtCore.Qt.AlignRight)
        layout.setSpacing(10)
        
        # ========== شناسه طناب ==========
        self.id_edit = QtWidgets.QLineEdit()
        self.id_edit.setText(self.rope.id)
        layout.addRow("شناسه طناب:", self.id_edit)
        
        # ========== قطر طناب ==========
        self.diameter = QtWidgets.QDoubleSpinBox()
        self.diameter.setRange(10, 80)
        self.diameter.setSuffix(" mm")
        self.diameter.setValue(self.rope.diameter)
        layout.addRow("قطر طناب:", self.diameter)
        
        # ========== تعداد رشته ==========
        self.strand_count = QtWidgets.QSpinBox()
        self.strand_count.setRange(1, 20)
        self.strand_count.setValue(getattr(self.rope, 'strand_count', 3))
        layout.addRow("تعداد رشته:", self.strand_count)
        
        # ========== طول طناب ==========
        self.length = QtWidgets.QDoubleSpinBox()
        self.length.setRange(1, 500)
        self.length.setSuffix(" متر")
        self.length.setValue(getattr(self.rope, 'length', 50))
        layout.addRow("طول طناب:", self.length)
        
        # ========== جنس طناب ==========
        self.material_combo = QtWidgets.QComboBox()
        self.material_combo.addItems(["پلی پروپیلن", "پلی اتیلن", "داینما"])
        current_material = getattr(self.rope, 'material', 'پلی پروپیلن')
        index = self.material_combo.findText(current_material)
        if index >= 0:
            self.material_combo.setCurrentIndex(index)
        layout.addRow("جنس طناب:", self.material_combo)
        
        # ========== تاریخ نصب ==========
        self.install_date = JalaliDateEdit()
        if hasattr(self.rope, 'install_date') and self.rope.install_date:
            self.install_date.set_jalali_date(self.rope.install_date)
        layout.addRow("تاریخ نصب:", self.install_date)
        
        # ========== وضعیت طناب ==========
        self.status_combo = QtWidgets.QComboBox()
        self.status_combo.addItems(["سالم", "نیاز به تعمیر", "خراب", "در حال تعمیر"])
        current_status = getattr(self.rope, 'status', 'سالم')
        index = self.status_combo.findText(current_status)
        if index >= 0:
            self.status_combo.setCurrentIndex(index)
        layout.addRow("وضعیت طناب:", self.status_combo)
        
        # ========== رنگ در نقشه ==========
        color_layout = QtWidgets.QHBoxLayout()
        self.color_btn = ColorButton(self.rope.color if self.rope.color else DEFAULT_ROPE_COLOR)
        color_layout.addWidget(self.color_btn)
        color_layout.addWidget(QtWidgets.QLabel("انتخاب رنگ در نقشه"))
        color_layout.addStretch()
        layout.addRow("رنگ نقشه:", color_layout)
        
        # ========== خط جداکننده ==========
        line = QtWidgets.QFrame()
        line.setFrameShape(QtWidgets.QFrame.HLine)
        line.setStyleSheet("background-color: #3E3E42; margin: 5px 0;")
        layout.addRow(line)
        
        # ========== نقطه شروع ==========
        start_type_label = QtWidgets.QLabel("نوع نقطه شروع:")
        self.start_type_combo = QtWidgets.QComboBox()
        self.start_type_combo.addItems(["انتخاب از اجزا", "وارد کردن مختصات دستی"])
        self.start_type_combo.currentIndexChanged.connect(self.on_start_type_changed)
        layout.addRow(start_type_label, self.start_type_combo)
        
        # انتخاب از اجزا (زنجیر یا بویه)
        self.start_combo = QtWidgets.QComboBox()
        self.start_combo.addItem("--- انتخاب کنید ---")
        for c in self.chains:
            self.start_combo.addItem(f"🔗 زنجیر: {c.id}", c.id)
        for b in self.buoys:
            self.start_combo.addItem(f"■ بویه: {b.id}", b.id)
        if self.rope.start_id and not self.rope.use_manual_start:
            idx = self.start_combo.findData(self.rope.start_id)
            if idx >= 0:
                self.start_combo.setCurrentIndex(idx)
        layout.addRow("انتخاب نقطه شروع:", self.start_combo)
        
        # مختصات دستی شروع
        self.start_manual_frame = QtWidgets.QWidget()
        manual_layout = QtWidgets.QHBoxLayout(self.start_manual_frame)
        self.start_x = QtWidgets.QDoubleSpinBox()
        self.start_x.setRange(COORDINATE_MIN, COORDINATE_MAX)
        self.start_x.setPrefix("X: ")
        self.start_y = QtWidgets.QDoubleSpinBox()
        self.start_y.setRange(COORDINATE_MIN, COORDINATE_MAX)
        self.start_y.setPrefix("Y: ")
        manual_layout.addWidget(self.start_x)
        manual_layout.addWidget(self.start_y)
        layout.addRow("مختصات شروع:", self.start_manual_frame)
        self.start_manual_frame.setVisible(False)
        
        # ========== نقطه پایان ==========
        end_type_label = QtWidgets.QLabel("نوع نقطه پایان:")
        self.end_type_combo = QtWidgets.QComboBox()
        self.end_type_combo.addItems(["انتخاب از اجزا", "وارد کردن مختصات دستی"])
        self.end_type_combo.currentIndexChanged.connect(self.on_end_type_changed)
        layout.addRow(end_type_label, self.end_type_combo)
        
        # انتخاب بویه
        self.end_combo = QtWidgets.QComboBox()
        self.end_combo.addItem("--- انتخاب بویه ---")
        for b in self.buoys:
            self.end_combo.addItem(b.id, b.id)
        if self.rope.end_id and not self.rope.use_manual_end:
            idx = self.end_combo.findData(self.rope.end_id)
            if idx >= 0:
                self.end_combo.setCurrentIndex(idx)
        layout.addRow("انتخاب نقطه پایان:", self.end_combo)
        
        # مختصات دستی پایان
        self.end_manual_frame = QtWidgets.QWidget()
        manual_end_layout = QtWidgets.QHBoxLayout(self.end_manual_frame)
        self.end_x = QtWidgets.QDoubleSpinBox()
        self.end_x.setRange(COORDINATE_MIN, COORDINATE_MAX)
        self.end_x.setPrefix("X: ")
        self.end_y = QtWidgets.QDoubleSpinBox()
        self.end_y.setRange(COORDINATE_MIN, COORDINATE_MAX)
        self.end_y.setPrefix("Y: ")
        manual_end_layout.addWidget(self.end_x)
        manual_end_layout.addWidget(self.end_y)
        layout.addRow("مختصات پایان:", self.end_manual_frame)
        self.end_manual_frame.setVisible(False)
        
        # ========== یادداشت ==========
        self.note = QtWidgets.QTextEdit()
        self.note.setMaximumHeight(80)
        self.note.setPlaceholderText("توضیحات اضافی...")
        self.note.setText(getattr(self.rope, 'note', ''))
        layout.addRow("یادداشت:", self.note)
        
        # ========== دکمه‌ها ==========
        self.add_button_box(layout)
        
        # بارگذاری مقادیر قبلی در صورت وجود
        if self.rope.use_manual_start:
            self.start_type_combo.setCurrentIndex(1)
            self.start_x.setValue(self.rope.start_x)
            self.start_y.setValue(self.rope.start_y)
        if self.rope.use_manual_end:
            self.end_type_combo.setCurrentIndex(1)
            self.end_x.setValue(self.rope.end_x)
            self.end_y.setValue(self.rope.end_y)
    
    def on_start_type_changed(self, index):
        self.start_combo.setVisible(index == 0)
        self.start_manual_frame.setVisible(index == 1)
    
    def on_end_type_changed(self, index):
        self.end_combo.setVisible(index == 0)
        self.end_manual_frame.setVisible(index == 1)
    
    def validate_data(self):
        """اعتبارسنجی داده‌ها"""
        if not self.id_edit.text().strip():
            self.show_error("شناسه طناب را وارد کنید")
            self.id_edit.setFocus()
            return False
        
        # اعتبارسنجی نقطه شروع
        if self.start_type_combo.currentIndex() == 0:
            if not self.start_combo.currentData():
                self.show_error("لطفاً نقطه شروع را انتخاب کنید")
                return False
        
        # اعتبارسنجی نقطه پایان
        if self.end_type_combo.currentIndex() == 0:
            if not self.end_combo.currentData():
                self.show_error("لطفاً نقطه پایان را انتخاب کنید")
                return False
        
        return True
    
    def accept(self):
        """پذیرش دیالوگ و ذخیره اطلاعات طناب"""
        if not self.validate_data():
            return
        
        # فیلدهای اصلی
        self.rope.id = self.id_edit.text().strip()
        self.rope.mooring_id = self.mooring_id
        self.rope.diameter = self.diameter.value()
        self.rope.strand_count = self.strand_count.value()
        self.rope.length = self.length.value()
        self.rope.material = self.material_combo.currentText()
        self.rope.install_date = self.install_date.get_jalali_date()
        self.rope.status = self.status_combo.currentText()
        self.rope.color = self.color_btn.get_color()
        self.rope.note = self.note.toPlainText()
        
        # نقطه شروع
        if self.start_type_combo.currentIndex() == 0:
            self.rope.start_id = self.start_combo.currentData()
            self.rope.use_manual_start = False
        else:
            self.rope.start_id = ""
            self.rope.start_x = self.start_x.value()
            self.rope.start_y = self.start_y.value()
            self.rope.use_manual_start = True
        
        # نقطه پایان
        if self.end_type_combo.currentIndex() == 0:
            self.rope.end_id = self.end_combo.currentData()
            self.rope.use_manual_end = False
        else:
            self.rope.end_id = ""
            self.rope.end_x = self.end_x.value()
            self.rope.end_y = self.end_y.value()
            self.rope.use_manual_end = True
        
        super().accept()