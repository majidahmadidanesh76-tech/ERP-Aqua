"""
دیالوگ افزودن و ویرایش زنجیر برای ERP-Aqua
"""

from PyQt5 import QtWidgets, QtCore

from .base_dialog import BaseDialog
from ...core.models import AnchorChain
from ...core.constants import COORDINATE_MIN, COORDINATE_MAX, DEFAULT_CHAIN_COLOR
from ...widgets.color_button import ColorButton
from ...widgets.jalali_date_edit import JalaliDateEdit


class AddChainDialog(BaseDialog):
    """
    دیالوگ افزودن یا ویرایش زنجیر
    """
    
    def __init__(self, parent=None, anchors=None, ropes=None, chain=None, mooring_id=""):
        self.anchors = anchors or []
        self.ropes = ropes or []
        self.chain = chain if chain else AnchorChain()
        self.mooring_id = mooring_id
        edit_mode = chain is not None
        title = "ویرایش زنجیر" if edit_mode else "افزودن زنجیر جدید"
        super().__init__(parent, title=title, edit_mode=edit_mode, width=480, height=600)
        self.setup_ui()
    
    def setup_ui(self):
        """تنظیم رابط کاربری دیالوگ"""
        layout = QtWidgets.QFormLayout(self)
        layout.setLabelAlignment(QtCore.Qt.AlignRight)
        layout.setSpacing(10)
        
        # ========== شناسه زنجیر ==========
        self.id_edit = QtWidgets.QLineEdit()
        self.id_edit.setText(self.chain.id)
        layout.addRow("شناسه زنجیر:", self.id_edit)
        
        # ========== قطر زنجیر ==========
        self.diameter = QtWidgets.QDoubleSpinBox()
        self.diameter.setRange(10, 60)
        self.diameter.setSuffix(" mm")
        self.diameter.setValue(self.chain.diameter)
        layout.addRow("قطر زنجیر:", self.diameter)
        
        # ========== نوع زنجیر ==========
        self.chain_type_combo = QtWidgets.QComboBox()
        self.chain_type_combo.addItems(["ساده", "پل دار"])
        current_chain_type = getattr(self.chain, 'chain_type', 'ساده')
        index = self.chain_type_combo.findText(current_chain_type)
        if index >= 0:
            self.chain_type_combo.setCurrentIndex(index)
        layout.addRow("نوع زنجیر:", self.chain_type_combo)
        
        # ========== جنس زنجیر ==========
        self.material_combo = QtWidgets.QComboBox()
        self.material_combo.addItems(["فولاد", "گالوانیزه", "استیل", "آهنی", "برنجی"])
        current_material = getattr(self.chain, 'material', 'فولاد')
        index = self.material_combo.findText(current_material)
        if index >= 0:
            self.material_combo.setCurrentIndex(index)
        layout.addRow("جنس زنجیر:", self.material_combo)
        
        # ========== تاریخ نصب ==========
        self.install_date = JalaliDateEdit()
        if hasattr(self.chain, 'install_date') and self.chain.install_date:
            self.install_date.set_jalali_date(self.chain.install_date)
        layout.addRow("تاریخ نصب:", self.install_date)
        
        # ========== وضعیت زنجیر ==========
        self.status_combo = QtWidgets.QComboBox()
        self.status_combo.addItems(["سالم", "نیاز به تعمیر", "خراب", "در حال تعمیر"])
        current_status = getattr(self.chain, 'status', 'سالم')
        index = self.status_combo.findText(current_status)
        if index >= 0:
            self.status_combo.setCurrentIndex(index)
        layout.addRow("وضعیت زنجیر:", self.status_combo)
        
        # ========== رنگ در نقشه ==========
        color_layout = QtWidgets.QHBoxLayout()
        self.color_btn = ColorButton(self.chain.color if self.chain.color else DEFAULT_CHAIN_COLOR)
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
        
        # انتخاب لنگر
        self.start_combo = QtWidgets.QComboBox()
        self.start_combo.addItem("--- انتخاب لنگر ---")
        for a in self.anchors:
            self.start_combo.addItem(a.id, a.id)
        if self.chain.start_id and not self.chain.use_manual_start:
            idx = self.start_combo.findData(self.chain.start_id)
            if idx >= 0:
                self.start_combo.setCurrentIndex(idx)
        layout.addRow("انتخاب لنگر:", self.start_combo)
        
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
        
        # انتخاب طناب
        self.end_combo = QtWidgets.QComboBox()
        self.end_combo.addItem("--- انتخاب طناب ---")
        for r in self.ropes:
            self.end_combo.addItem(r.id, r.id)
        if self.chain.end_id and not self.chain.use_manual_end:
            idx = self.end_combo.findData(self.chain.end_id)
            if idx >= 0:
                self.end_combo.setCurrentIndex(idx)
        layout.addRow("انتخاب طناب:", self.end_combo)
        
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
        self.note.setText(getattr(self.chain, 'note', ''))
        layout.addRow("یادداشت:", self.note)
        
        # ========== دکمه‌ها ==========
        self.add_button_box(layout)
        
        # بارگذاری مقادیر قبلی در صورت وجود
        if self.chain.use_manual_start:
            self.start_type_combo.setCurrentIndex(1)
            self.start_x.setValue(self.chain.start_x)
            self.start_y.setValue(self.chain.start_y)
        if self.chain.use_manual_end:
            self.end_type_combo.setCurrentIndex(1)
            self.end_x.setValue(self.chain.end_x)
            self.end_y.setValue(self.chain.end_y)
    
    def on_start_type_changed(self, index):
        self.start_combo.setVisible(index == 0)
        self.start_manual_frame.setVisible(index == 1)
    
    def on_end_type_changed(self, index):
        self.end_combo.setVisible(index == 0)
        self.end_manual_frame.setVisible(index == 1)
    
    def validate_data(self):
        """اعتبارسنجی داده‌ها"""
        if not self.id_edit.text().strip():
            self.show_error("شناسه زنجیر را وارد کنید")
            self.id_edit.setFocus()
            return False
        
        # اعتبارسنجی نقطه شروع
        if self.start_type_combo.currentIndex() == 0:
            if not self.start_combo.currentData():
                self.show_error("لطفاً لنگر را انتخاب کنید")
                return False
        else:
            if self.start_x.value() == 0 and self.start_y.value() == 0:
                self.show_error("لطفاً مختصات شروع را وارد کنید")
                return False
        
        # اعتبارسنجی نقطه پایان
        if self.end_type_combo.currentIndex() == 0:
            if not self.end_combo.currentData():
                self.show_error("لطفاً طناب را انتخاب کنید")
                return False
        else:
            if self.end_x.value() == 0 and self.end_y.value() == 0:
                self.show_error("لطفاً مختصات پایان را وارد کنید")
                return False
        
        return True
    
    def accept(self):
        """پذیرش دیالوگ و ذخیره اطلاعات زنجیر"""
        if not self.validate_data():
            return
        
        # فیلدهای اصلی
        self.chain.id = self.id_edit.text().strip()
        self.chain.mooring_id = self.mooring_id
        self.chain.diameter = self.diameter.value()
        self.chain.chain_type = self.chain_type_combo.currentText()
        self.chain.material = self.material_combo.currentText()
        self.chain.install_date = self.install_date.get_jalali_date()
        self.chain.status = self.status_combo.currentText()
        self.chain.color = self.color_btn.get_color()
        self.chain.note = self.note.toPlainText()
        
        # نقطه شروع
        if self.start_type_combo.currentIndex() == 0:
            self.chain.start_id = self.start_combo.currentData()
            self.chain.use_manual_start = False
        else:
            self.chain.start_id = ""
            self.chain.start_x = self.start_x.value()
            self.chain.start_y = self.start_y.value()
            self.chain.use_manual_start = True
        
        # نقطه پایان
        if self.end_type_combo.currentIndex() == 0:
            self.chain.end_id = self.end_combo.currentData()
            self.chain.use_manual_end = False
        else:
            self.chain.end_id = ""
            self.chain.end_x = self.end_x.value()
            self.chain.end_y = self.end_y.value()
            self.chain.use_manual_end = True
        
        super().accept()