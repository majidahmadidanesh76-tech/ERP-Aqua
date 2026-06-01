"""
صفحه طراحی و مدیریت مزرعه (بخش اصلی برنامه) برای ERP-Aqua
شامل جدول‌های مدیریت اجزا و نقشه گرافیکی
"""

from PyQt5 import QtWidgets, QtCore
from functools import partial
import qtawesome as qta

from ..core.models import Farm, Mooring
from ..core.constants import (
    TABLE_ROW_HEIGHT, TABLE_ACTION_COLUMN_WIDTH,
    GLASS_BTN_STYLE, SMALL_ICON_STYLE, GLASS_PANEL_STYLE
)
from ..graphics.graphics_view import MooringGraphicsView
from ..widgets.color_button import ColorButton
from .dialogs import (
    AddFarmDialog, EditFarmDialog, AddMooringDialog, EditMooringDialog,
    BuoyDialog, AnchorDialog, AddChainDialog, AddRopeDialog,
    AddBuoyChainDialog, AddShackleDialog, AddBridleRopeDialog,
    AddCageDialog, AddNetDialog, AddCollectorDialog,
    DeleteConfirmDialog, FinalConfirmDialog
)


class FarmDesignTab(QtWidgets.QWidget):
    """
    صفحه اصلی طراحی و مدیریت مزرعه
    شامل پنل آیکون‌ها، جدول مدیریت اجزا و نقشه گرافیکی
    """
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.farms = []
        self.current_farm = None
        self.current_mooring = None
        self.current_table_index = 0
        self.setup_ui()
    
    def setup_ui(self):
        """تنظیم رابط کاربری اصلی"""
        main_layout = QtWidgets.QHBoxLayout(self)
        main_layout.setContentsMargins(8, 8, 8, 8)
        main_layout.setSpacing(12)
        
        # ==================== سمت چپ ====================
        left_widget = QtWidgets.QWidget()
        left_layout = QtWidgets.QVBoxLayout(left_widget)
        left_layout.setContentsMargins(0, 0, 0, 0)
        left_layout.setSpacing(8)
        
        # پنل آیکون‌های کوچک
        self.setup_icon_panel(left_layout)
        
        # استک ویجت جدول‌ها
        self.setup_table_stacked(left_layout)
        
        main_layout.addWidget(left_widget, 1)
        
        # ==================== سمت راست ====================
        right_widget = QtWidgets.QWidget()
        right_layout = QtWidgets.QVBoxLayout(right_widget)
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.setSpacing(8)
        
        # لیست مورینگ‌ها
        self.setup_mooring_list(right_layout)
        
        # نوار ابزار
        self.setup_toolbar(right_layout)
        
        # نقشه
        self.graphics_view = MooringGraphicsView()
        right_layout.addWidget(self.graphics_view)
        
        main_layout.addWidget(right_widget, 4)
        
        # انتخاب پیش‌فرض
        if self.small_icon_btns:
            self.small_icon_btns[0].setChecked(True)
            self.current_table_index = 0
            self.table_stacked.setCurrentIndex(0)
    
    def setup_icon_panel(self, parent_layout):
        """تنظیم پنل آیکون‌های کوچک برای انتخاب جدول (فقط آیکون)"""
        icon_panel = QtWidgets.QWidget()
        icon_panel.setStyleSheet("""
            QWidget {
                background-color: rgba(37, 37, 38, 200);
                border-radius: 8px;
                border: 1px solid rgba(86, 156, 214, 80);
                margin: 2px;
            }
        """)
        icon_layout = QtWidgets.QGridLayout(icon_panel)
        icon_layout.setSpacing(4)
        icon_layout.setContentsMargins(6, 6, 6, 6)
        
        icon_buttons = [
            (0, 0, 'fa5s.square', '#A0A0A0', "بویه", self.show_buoy_table),
            (0, 1, 'fa5s.anchor', '#569CD6', "لنگر", self.show_anchor_table),
            (0, 2, 'fa5s.link', '#C8C8C8', "زنجیر", self.show_chain_table),
            (0, 3, 'fa5s.grip-lines', '#C8C8C8', "طناب اصلی", self.show_rope_table),
            (1, 0, 'fa5s.link', '#A0A0A0', "زنجیر بویه", self.show_buoy_chain_table),
            (1, 1, 'fa5s.shield-alt', '#C8C8C8', "شاکل", self.show_shackle_table),
            (1, 2, 'fa5s.code-branch', '#D4A574', "طناب برایدل", self.show_bridle_table),
            (1, 3, 'fa5s.circle', '#A0A0A0', "قفس", self.show_cage_table),
            (2, 0, 'fa5s.th', '#C8C8C8', "تور", self.show_net_table),
            (2, 1, 'fa5s.circle', '#569CD6', "کلکتور", self.show_collector_table),
        ]
        
        self.small_icon_btns = []
        self.small_icon_group = QtWidgets.QButtonGroup(self)
        self.small_icon_group.setExclusive(True)
        
        for row, col, icon_name, color, tooltip, show_func in icon_buttons:
            btn = QtWidgets.QToolButton()
            btn.setIcon(qta.icon(icon_name, color=color))
            btn.setIconSize(QtCore.QSize(16, 16))
            btn.setToolTip(tooltip)
            btn.setStyleSheet("""
                QToolButton {
                    background-color: rgba(60, 60, 65, 180);
                    border: none;
                    border-radius: 4px;
                    padding: 4px;
                    min-width: 28px;
                    min-height: 28px;
                }
                QToolButton:hover {
                    background-color: rgba(86, 156, 214, 100);
                }
                QToolButton:checked {
                    background-color: rgba(86, 156, 214, 160);
                    border: 1px solid rgba(86, 156, 214, 200);
                }
            """)
            btn.setCheckable(True)
            btn.clicked.connect(show_func)
            self.small_icon_group.addButton(btn)
            icon_layout.addWidget(btn, row, col)
            self.small_icon_btns.append(btn)
        
        parent_layout.addWidget(icon_panel)
    
    def setup_table_stacked(self, parent_layout):
        """تنظیم استک ویجت جدول‌ها"""
        self.table_stacked = QtWidgets.QStackedWidget()
        
        self.buoy_table_widget, self.buoy_table = self.create_simple_table()
        self.table_stacked.addWidget(self.buoy_table_widget)
        
        self.anchor_table_widget, self.anchor_table = self.create_simple_table()
        self.table_stacked.addWidget(self.anchor_table_widget)
        
        self.chain_table_widget, self.chain_table = self.create_simple_table()
        self.table_stacked.addWidget(self.chain_table_widget)
        
        self.rope_table_widget, self.rope_table = self.create_simple_table()
        self.table_stacked.addWidget(self.rope_table_widget)
        
        self.buoy_chain_table_widget, self.buoy_chain_table = self.create_simple_table()
        self.table_stacked.addWidget(self.buoy_chain_table_widget)
        
        self.shackle_table_widget, self.shackle_table = self.create_simple_table()
        self.table_stacked.addWidget(self.shackle_table_widget)
        
        self.bridle_table_widget, self.bridle_table = self.create_simple_table()
        self.table_stacked.addWidget(self.bridle_table_widget)
        
        self.cage_table_widget, self.cage_table = self.create_simple_table()
        self.table_stacked.addWidget(self.cage_table_widget)
        
        self.net_table_widget, self.net_table = self.create_simple_table()
        self.table_stacked.addWidget(self.net_table_widget)
        
        self.collector_table_widget, self.collector_table = self.create_simple_table()
        self.table_stacked.addWidget(self.collector_table_widget)
        
        parent_layout.addWidget(self.table_stacked)
    
    def setup_mooring_list(self, parent_layout):
        """تنظیم لیست مورینگ‌ها (چک‌باکس‌ها)"""
        self.mooring_list_widget = QtWidgets.QListWidget()
        self.mooring_list_widget.setFlow(QtWidgets.QListWidget.LeftToRight)
        self.mooring_list_widget.setMaximumHeight(36)
        self.mooring_list_widget.setMinimumHeight(32)
        self.mooring_list_widget.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.mooring_list_widget.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.mooring_list_widget.setSelectionMode(QtWidgets.QAbstractItemView.NoSelection)
        self.mooring_list_widget.itemChanged.connect(self.on_mooring_visibility_changed)
        self.mooring_list_widget.setStyleSheet("QListWidget::item { margin: 1px; padding: 1px 6px; }")
        parent_layout.addWidget(self.mooring_list_widget)
    
    def setup_toolbar(self, parent_layout):
        """تنظیم نوار ابزار بالای نقشه"""
        toolbar_widget = QtWidgets.QWidget()
        toolbar_widget.setStyleSheet(GLASS_PANEL_STYLE)
        toolbar_layout = QtWidgets.QVBoxLayout(toolbar_widget)
        toolbar_layout.setContentsMargins(8, 6, 8, 6)
        toolbar_layout.setSpacing(6)
        
        # ردیف 1: کامبوباکس‌ها و دکمه‌های عملیات
        row1 = QtWidgets.QHBoxLayout()
        row1.setSpacing(6)
        
        self.setup_farm_controls(row1)
        self.setup_mooring_controls(row1)
        
        row1.addStretch()
        self.setup_action_buttons(row1)
        
        toolbar_layout.addLayout(row1)
        
        # ردیف 2: آیکون‌های افزودن اجزا
        row2 = QtWidgets.QHBoxLayout()
        row2.setSpacing(4)
        self.setup_add_buttons(row2)
        row2.addStretch()
        toolbar_layout.addLayout(row2)
        
        parent_layout.addWidget(toolbar_widget)
    
    def setup_farm_controls(self, layout):
        """تنظیم کنترل‌های مربوط به مزرعه"""
        self.farm_combo = QtWidgets.QComboBox()
        self.farm_combo.setMinimumWidth(140)
        self.farm_combo.setToolTip("انتخاب مزرعه")
        self.farm_combo.currentIndexChanged.connect(self.on_farm_selected)
        layout.addWidget(self.farm_combo)
        
        self.add_farm_btn = QtWidgets.QToolButton()
        self.add_farm_btn.setIcon(qta.icon('fa5s.plus-circle', color='#C8C8C8'))
        self.add_farm_btn.setIconSize(QtCore.QSize(18, 18))
        self.add_farm_btn.setToolTip("افزودن مزرعه جدید")
        self.add_farm_btn.clicked.connect(self.add_farm)
        layout.addWidget(self.add_farm_btn)
        
        self.edit_farm_btn = QtWidgets.QToolButton()
        self.edit_farm_btn.setIcon(qta.icon('fa5s.edit', color='#C8C8C8'))
        self.edit_farm_btn.setIconSize(QtCore.QSize(18, 18))
        self.edit_farm_btn.setToolTip("ویرایش مزرعه")
        self.edit_farm_btn.clicked.connect(self.edit_farm)
        layout.addWidget(self.edit_farm_btn)
        
        self.delete_farm_btn = QtWidgets.QToolButton()
        self.delete_farm_btn.setIcon(qta.icon('fa5s.trash-alt', color='#C8C8C8'))
        self.delete_farm_btn.setIconSize(QtCore.QSize(16, 16))
        self.delete_farm_btn.setToolTip("حذف مزرعه")
        self.delete_farm_btn.clicked.connect(self.delete_farm)
        layout.addWidget(self.delete_farm_btn)
        
        layout.addSpacing(15)
    
    def setup_mooring_controls(self, layout):
        """تنظیم کنترل‌های مربوط به مورینگ"""
        self.mooring_combo = QtWidgets.QComboBox()
        self.mooring_combo.setMinimumWidth(140)
        self.mooring_combo.setToolTip("انتخاب مورینگ جاری")
        self.mooring_combo.currentIndexChanged.connect(self.on_mooring_selected)
        layout.addWidget(self.mooring_combo)
        
        self.add_mooring_btn = QtWidgets.QToolButton()
        self.add_mooring_btn.setIcon(qta.icon('fa5s.plus-circle', color='#C8C8C8'))
        self.add_mooring_btn.setIconSize(QtCore.QSize(18, 18))
        self.add_mooring_btn.setToolTip("افزودن مورینگ جدید")
        self.add_mooring_btn.clicked.connect(self.add_mooring)
        layout.addWidget(self.add_mooring_btn)
        
        self.edit_mooring_btn = QtWidgets.QToolButton()
        self.edit_mooring_btn.setIcon(qta.icon('fa5s.edit', color='#C8C8C8'))
        self.edit_mooring_btn.setIconSize(QtCore.QSize(18, 18))
        self.edit_mooring_btn.setToolTip("ویرایش مورینگ")
        self.edit_mooring_btn.clicked.connect(self.edit_mooring)
        layout.addWidget(self.edit_mooring_btn)
        
        self.delete_mooring_btn = QtWidgets.QToolButton()
        self.delete_mooring_btn.setIcon(qta.icon('fa5s.trash-alt', color='#C8C8C8'))
        self.delete_mooring_btn.setIconSize(QtCore.QSize(16, 16))
        self.delete_mooring_btn.setToolTip("حذف مورینگ")
        self.delete_mooring_btn.clicked.connect(self.delete_mooring)
        layout.addWidget(self.delete_mooring_btn)
    
    def setup_action_buttons(self, layout):
        """تنظیم دکمه‌های عملیات (ذخیره، بارگذاری، لیست نهایی)"""
        self.save_btn = QtWidgets.QToolButton()
        self.save_btn.setIcon(qta.icon('fa5s.save', color='#C8C8C8'))
        self.save_btn.setIconSize(QtCore.QSize(18, 18))
        self.save_btn.setToolTip("ذخیره داده‌ها در فایل")
        self.save_btn.clicked.connect(self.save_data)
        layout.addWidget(self.save_btn)
        
        self.load_btn = QtWidgets.QToolButton()
        self.load_btn.setIcon(qta.icon('fa5s.folder-open', color='#C8C8C8'))
        self.load_btn.setIconSize(QtCore.QSize(18, 18))
        self.load_btn.setToolTip("بارگذاری داده‌ها از فایل")
        self.load_btn.clicked.connect(self.load_data)
        layout.addWidget(self.load_btn)
        
        self.final_list_btn = QtWidgets.QToolButton()
        self.final_list_btn.setIcon(qta.icon('fa5s.list-ul', color='#C8C8C8'))
        self.final_list_btn.setIconSize(QtCore.QSize(18, 18))
        self.final_list_btn.setToolTip("نمایش لیست کامل اجزای مورینگ")
        self.final_list_btn.clicked.connect(self.show_final_list)
        layout.addWidget(self.final_list_btn)
    
    def setup_add_buttons(self, layout):
        """تنظیم دکمه‌های افزودن اجزا (نوار ابزار شیشه‌ای بالای نقشه)"""
        self.btn_group = QtWidgets.QButtonGroup(self)
        self.btn_group.setExclusive(True)
        
        buttons = [
            ('fa5s.square', '#C8C8C8', "افزودن بویه", self.add_buoy),
            ('fa5s.anchor', '#C8C8C8', "افزودن لنگر", self.add_anchor),
            ('fa5s.link', '#C8C8C8', "افزودن زنجیر", self.add_chain),
            ('fa5s.grip-lines', '#C8C8C8', "افزودن طناب اصلی", self.add_rope),
            ('fa5s.link', '#C8C8C8', "افزودن زنجیر بویه", self.add_buoy_chain),
            ('fa5s.shield-alt', '#C8C8C8', "افزودن شاکل", self.add_shackle),
            ('fa5s.code-branch', '#C8C8C8', "افزودن طناب برایدل", self.add_bridle),
            ('fa5s.circle', '#C8C8C8', "افزودن قفس", self.add_cage),
            ('fa5s.th', '#C8C8C8', "افزودن تور", self.add_net),
            ('fa5s.circle', '#C8C8C8', "افزودن کلکتور", self.add_collector),
        ]
        
        for icon_name, color, tooltip, callback in buttons:
            btn = QtWidgets.QToolButton()
            btn.setIcon(qta.icon(icon_name, color=color))
            btn.setIconSize(QtCore.QSize(18, 18))
            btn.setToolTip(tooltip)
            btn.setStyleSheet(GLASS_BTN_STYLE)
            btn.setCheckable(True)
            btn.clicked.connect(callback)
            self.btn_group.addButton(btn)
            layout.addWidget(btn)
    
    def create_simple_table(self):
        """ایجاد جدول ساده با 2 ستون: جزء و عملیات"""
        tab = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout(tab)
        layout.setContentsMargins(2, 2, 2, 2)
        
        table = QtWidgets.QTableWidget()
        table.setColumnCount(2)
        table.setHorizontalHeaderLabels(["جزء", "عملیات"])
        table.horizontalHeader().setStretchLastSection(True)
        table.verticalHeader().setDefaultSectionSize(TABLE_ROW_HEIGHT)
        table.setColumnWidth(1, TABLE_ACTION_COLUMN_WIDTH)
        
        layout.addWidget(table)
        return tab, table
    
    # ==================== توابع نمایش جدول‌ها ====================
    def show_buoy_table(self): self.table_stacked.setCurrentIndex(0); self.current_table_index = 0; self.update_all_tables()
    def show_anchor_table(self): self.table_stacked.setCurrentIndex(1); self.current_table_index = 1; self.update_all_tables()
    def show_chain_table(self): self.table_stacked.setCurrentIndex(2); self.current_table_index = 2; self.update_all_tables()
    def show_rope_table(self): self.table_stacked.setCurrentIndex(3); self.current_table_index = 3; self.update_all_tables()
    def show_buoy_chain_table(self): self.table_stacked.setCurrentIndex(4); self.current_table_index = 4; self.update_all_tables()
    def show_shackle_table(self): self.table_stacked.setCurrentIndex(5); self.current_table_index = 5; self.update_all_tables()
    def show_bridle_table(self): self.table_stacked.setCurrentIndex(6); self.current_table_index = 6; self.update_all_tables()
    def show_cage_table(self): self.table_stacked.setCurrentIndex(7); self.current_table_index = 7; self.update_all_tables()
    def show_net_table(self): self.table_stacked.setCurrentIndex(8); self.current_table_index = 8; self.update_all_tables()
    def show_collector_table(self): self.table_stacked.setCurrentIndex(9); self.current_table_index = 9; self.update_all_tables()
    
    # ==================== توابع کمکی ====================
    def update_mooring_list(self):
        self.mooring_list_widget.clear()
        if not self.current_farm:
            return
        for mooring in self.current_farm.moorings:
            item = QtWidgets.QListWidgetItem(f" {mooring.id} ")
            item.setFlags(item.flags() | QtCore.Qt.ItemIsUserCheckable)
            item.setCheckState(QtCore.Qt.Checked)
            self.mooring_list_widget.addItem(item)
        self.update_visibility()
    
    def update_visibility(self):
        if not self.current_farm:
            return
        visible_ids = []
        for i in range(self.mooring_list_widget.count()):
            item = self.mooring_list_widget.item(i)
            if item.checkState() == QtCore.Qt.Checked:
                visible_ids.append(item.text().strip())
        self.graphics_view.set_visible_moorings(visible_ids)
    
    def on_mooring_visibility_changed(self, item):
        self.update_visibility()
    
    def update_farm_combo(self):
        self.farm_combo.clear()
        if self.farms:
            for farm in self.farms:
                self.farm_combo.addItem(farm.name, farm.id)
            if self.farm_combo.count() > 0:
                self.farm_combo.setCurrentIndex(0)
    
    def update_mooring_combo(self):
        self.mooring_combo.clear()
        if self.current_farm:
            for mooring in self.current_farm.moorings:
                self.mooring_combo.addItem(mooring.id, mooring.id)
            if self.mooring_combo.count() > 0:
                self.mooring_combo.setCurrentIndex(0)
    
    def on_farm_selected(self, index):
        if index < 0 or not self.farms:
            self.current_farm = None
            self.mooring_combo.clear()
            self.mooring_list_widget.clear()
            self.graphics_view.set_farm(None)
            return
        farm_id = self.farm_combo.currentData()
        for farm in self.farms:
            if farm.id == farm_id:
                self.current_farm = farm
                break
        self.update_mooring_combo()
        self.update_mooring_list()
        self.graphics_view.set_farm(self.current_farm)
        self.graphics_view.draw_system()
    
    def on_mooring_selected(self, index):
        if index < 0 or not self.current_farm:
            self.current_mooring = None
        else:
            mooring_id = self.mooring_combo.currentData()
            for mooring in self.current_farm.moorings:
                if mooring.id == mooring_id:
                    self.current_mooring = mooring
                    break
        self.update_all_tables()
        self.graphics_view.draw_system()
    
    def refresh_map(self):
        if self.current_farm:
            self.graphics_view.set_farm(self.current_farm)
            self.update_visibility()
            self.graphics_view.draw_system()
    
    def create_action_buttons(self, edit_callback, delete_callback):
        btn_widget = QtWidgets.QWidget()
        btn_layout = QtWidgets.QHBoxLayout(btn_widget)
        btn_layout.setContentsMargins(0, 0, 0, 0)
        btn_layout.setSpacing(3)
        
        edit_btn = QtWidgets.QToolButton()
        edit_btn.setIcon(qta.icon('fa5s.edit', color='#78500B'))
        edit_btn.setIconSize(QtCore.QSize(16, 16))
        edit_btn.setToolTip("ویرایش")
        edit_btn.clicked.connect(edit_callback)
        
        delete_btn = QtWidgets.QToolButton()
        delete_btn.setIcon(qta.icon('fa5s.trash-alt', color='#8B2C2C'))
        delete_btn.setIconSize(QtCore.QSize(16, 16))
        delete_btn.setToolTip("حذف")
        delete_btn.clicked.connect(delete_callback)
        
        btn_layout.addWidget(edit_btn)
        btn_layout.addWidget(delete_btn)
        btn_layout.addStretch()
        return btn_widget
    
    def can_delete_farm(self, farm):
        return len(farm.moorings) == 0
    
    def can_delete_mooring(self, mooring):
        return (len(mooring.buoys) == 0 and len(mooring.anchors) == 0 and 
                len(mooring.anchor_chains) == 0 and len(mooring.anchor_ropes) == 0 and
                len(mooring.buoy_chains) == 0 and len(mooring.shackles) == 0 and
                len(mooring.bridle_ropes) == 0 and len(mooring.cages) == 0 and
                len(mooring.nets) == 0 and len(mooring.collectors) == 0)
    
    # ==================== توابع مدیریت مزرعه و مورینگ ====================
    def add_farm(self):
        dialog = AddFarmDialog(self)
        if dialog.exec_() and dialog.farm:
            self.farms.append(dialog.farm)
            self.update_farm_combo()
    
    def edit_farm(self):
        if not self.current_farm:
            QtWidgets.QMessageBox.warning(self, "خطا", "هیچ مزرعه‌ای انتخاب نشده است")
            return
        dialog = EditFarmDialog(self, self.current_farm)
        if dialog.exec_() and dialog.farm:
            self.current_farm.name = dialog.farm.name
            self.current_farm.id = dialog.farm.id
            self.current_farm.center_x = dialog.farm.center_x
            self.current_farm.center_y = dialog.farm.center_y
            self.update_farm_combo()
            self.refresh_map()
    
    def delete_farm(self):
        if not self.current_farm:
            QtWidgets.QMessageBox.warning(self, "خطا", "هیچ مزرعه‌ای انتخاب نشده است")
            return
        if not self.can_delete_farm(self.current_farm):
            dialog = DeleteConfirmDialog(self, "مزرعه", self.current_farm.name, True)
            dialog.exec_()
            return
        dialog = DeleteConfirmDialog(self, "مزرعه", self.current_farm.name, False)
        if dialog.exec_():
            self.farms.remove(self.current_farm)
            self.current_farm = None
            self.update_farm_combo()
            self.mooring_combo.clear()
            self.mooring_list_widget.clear()
            self.graphics_view.set_farm(None)
            QtWidgets.QMessageBox.information(self, "موفق", "مزرعه با موفقیت حذف شد")
    
    def add_mooring(self):
        if not self.current_farm:
            QtWidgets.QMessageBox.warning(self, "خطا", "لطفاً ابتدا یک مزرعه انتخاب کنید")
            return
        dialog = AddMooringDialog(self)
        if dialog.exec_() and dialog.mooring:
            self.current_farm.moorings.append(dialog.mooring)
            self.update_mooring_combo()
            self.update_mooring_list()
            self.on_mooring_selected(0)
            self.refresh_map()
    
    def edit_mooring(self):
        if not self.current_mooring:
            QtWidgets.QMessageBox.warning(self, "خطا", "هیچ مورینگی انتخاب نشده است")
            return
        dialog = EditMooringDialog(self, self.current_mooring)
        if dialog.exec_() and dialog.mooring:
            old_id = self.current_mooring.id
            self.current_mooring.id = dialog.mooring.id
            self.current_mooring.name = dialog.mooring.name
            for buoy in self.current_mooring.buoys:
                buoy.mooring_id = self.current_mooring.id
            for anchor in self.current_mooring.anchors:
                anchor.mooring_id = self.current_mooring.id
            for chain in self.current_mooring.anchor_chains:
                chain.mooring_id = self.current_mooring.id
            for rope in self.current_mooring.anchor_ropes:
                rope.mooring_id = self.current_mooring.id
            for buoy_chain in self.current_mooring.buoy_chains:
                buoy_chain.mooring_id = self.current_mooring.id
            for shackle in self.current_mooring.shackles:
                shackle.mooring_id = self.current_mooring.id
            for bridle in self.current_mooring.bridle_ropes:
                bridle.mooring_id = self.current_mooring.id
            for cage in self.current_mooring.cages:
                cage.mooring_id = self.current_mooring.id
            for net in self.current_mooring.nets:
                net.mooring_id = self.current_mooring.id
            for collector in self.current_mooring.collectors:
                collector.mooring_id = self.current_mooring.id
            self.update_mooring_combo()
            self.update_mooring_list()
            self.refresh_map()
    
    def delete_mooring(self):
        if not self.current_mooring:
            QtWidgets.QMessageBox.warning(self, "خطا", "هیچ مورینگی انتخاب نشده است")
            return
        if not self.can_delete_mooring(self.current_mooring):
            dialog = DeleteConfirmDialog(self, "مورینگ", self.current_mooring.id, True)
            dialog.exec_()
            return
        dialog = DeleteConfirmDialog(self, "مورینگ", self.current_mooring.id, False)
        if dialog.exec_() and self.current_farm:
            self.current_farm.moorings.remove(self.current_mooring)
            self.current_mooring = None
            self.update_mooring_combo()
            self.update_mooring_list()
            self.graphics_view.set_farm(self.current_farm)
            QtWidgets.QMessageBox.information(self, "موفق", "مورینگ با موفقیت حذف شد")
    
    def show_final_list(self):
        dialog = FinalConfirmDialog(self, self.farms, self.current_farm, self.current_mooring)
        dialog.exec_()
    
    # ==================== توابع مدیریت اجزا ====================
    def add_buoy(self):
        if not self.current_mooring:
            QtWidgets.QMessageBox.warning(self, "خطا", "لطفاً ابتدا یک مورینگ انتخاب کنید")
            return
        dialog = BuoyDialog(self, edit_mode=False, mooring_id=self.current_mooring.id)
        if dialog.exec_() and dialog.buoy:
            self.current_mooring.buoys.append(dialog.buoy)
            self.update_all_tables()
            self.refresh_map()
    
    def edit_buoy(self, index):
        buoy = self.current_mooring.buoys[index]
        dialog = BuoyDialog(self, buoy=buoy, edit_mode=True, mooring_id=self.current_mooring.id)
        if dialog.exec_():
            self.current_mooring.buoys[index] = dialog.buoy
            self.update_all_tables()
            self.refresh_map()
    
    def delete_buoy(self, index):
        if QtWidgets.QMessageBox.question(self, "تأیید", "آیا از حذف این بویه مطمئن هستید؟") == QtWidgets.QMessageBox.Yes:
            self.current_mooring.buoys.pop(index)
            self.update_all_tables()
            self.refresh_map()
    
    def add_anchor(self):
        if not self.current_mooring:
            QtWidgets.QMessageBox.warning(self, "خطا", "لطفاً ابتدا یک مورینگ انتخاب کنید")
            return
        dialog = AnchorDialog(self, edit_mode=False, mooring_id=self.current_mooring.id)
        if dialog.exec_() and dialog.anchor:
            self.current_mooring.anchors.append(dialog.anchor)
            self.update_all_tables()
            self.refresh_map()
    
    def edit_anchor(self, index):
        anchor = self.current_mooring.anchors[index]
        dialog = AnchorDialog(self, anchor=anchor, edit_mode=True, mooring_id=self.current_mooring.id)
        if dialog.exec_():
            self.current_mooring.anchors[index] = dialog.anchor
            self.update_all_tables()
            self.refresh_map()
    
    def delete_anchor(self, index):
        if QtWidgets.QMessageBox.question(self, "تأیید", "آیا از حذف این لنگر مطمئن هستید؟") == QtWidgets.QMessageBox.Yes:
            self.current_mooring.anchors.pop(index)
            self.update_all_tables()
            self.refresh_map()
    
    def add_chain(self):
        if not self.current_mooring:
            QtWidgets.QMessageBox.warning(self, "خطا", "لطفاً ابتدا یک مورینگ انتخاب کنید")
            return
        dialog = AddChainDialog(self, self.current_mooring.anchors, self.current_mooring.anchor_ropes, mooring_id=self.current_mooring.id)
        if dialog.exec_() and dialog.chain:
            self.current_mooring.anchor_chains.append(dialog.chain)
            self.update_all_tables()
            self.refresh_map()
    
    def edit_chain(self, index):
        chain = self.current_mooring.anchor_chains[index]
        dialog = AddChainDialog(self, self.current_mooring.anchors, self.current_mooring.anchor_ropes, chain=chain, mooring_id=self.current_mooring.id)
        if dialog.exec_() and dialog.chain:
            self.current_mooring.anchor_chains[index] = dialog.chain
            self.update_all_tables()
            self.refresh_map()
    
    def delete_chain(self, index):
        if QtWidgets.QMessageBox.question(self, "تأیید", "آیا از حذف این زنجیر مطمئن هستید؟") == QtWidgets.QMessageBox.Yes:
            self.current_mooring.anchor_chains.pop(index)
            self.update_all_tables()
            self.refresh_map()
    
    def add_rope(self):
        if not self.current_mooring:
            QtWidgets.QMessageBox.warning(self, "خطا", "لطفاً ابتدا یک مورینگ انتخاب کنید")
            return
        dialog = AddRopeDialog(self, self.current_mooring.buoys, self.current_mooring.anchor_chains, mooring_id=self.current_mooring.id)
        if dialog.exec_() and dialog.rope:
            self.current_mooring.anchor_ropes.append(dialog.rope)
            self.update_all_tables()
            self.refresh_map()
    
    def edit_rope(self, index):
        rope = self.current_mooring.anchor_ropes[index]
        dialog = AddRopeDialog(self, self.current_mooring.buoys, self.current_mooring.anchor_chains, rope=rope, mooring_id=self.current_mooring.id)
        if dialog.exec_() and dialog.rope:
            self.current_mooring.anchor_ropes[index] = dialog.rope
            self.update_all_tables()
            self.refresh_map()
    
    def delete_rope(self, index):
        if QtWidgets.QMessageBox.question(self, "تأیید", "آیا از حذف این طناب مطمئن هستید؟") == QtWidgets.QMessageBox.Yes:
            self.current_mooring.anchor_ropes.pop(index)
            self.update_all_tables()
            self.refresh_map()
    
    def add_buoy_chain(self):
        if not self.current_mooring:
            QtWidgets.QMessageBox.warning(self, "خطا", "لطفاً ابتدا یک مورینگ انتخاب کنید")
            return
        
        current_transform = self.graphics_view.transform()
        current_center = self.graphics_view.mapToScene(
            self.graphics_view.viewport().rect().center()
        )
        
        dialog = AddBuoyChainDialog(
            self, 
            self.current_mooring.buoys,
            self.current_mooring.collectors,
            mooring_id=self.current_mooring.id
        )
        if dialog.exec_() and dialog.chain:
            self.current_mooring.buoy_chains.append(dialog.chain)
            self.update_all_tables()
            
            self.graphics_view.setTransform(current_transform)
            self.graphics_view.centerOn(current_center)
            self.graphics_view.draw_system()
            
            self.refresh_map()
    
    def edit_buoy_chain(self, index):
        chain = self.current_mooring.buoy_chains[index]
        
        current_transform = self.graphics_view.transform()
        current_center = self.graphics_view.mapToScene(
            self.graphics_view.viewport().rect().center()
        )
        
        dialog = AddBuoyChainDialog(
            self, 
            self.current_mooring.buoys,
            self.current_mooring.collectors,
            chain=chain, 
            mooring_id=self.current_mooring.id
        )
        if dialog.exec_() and dialog.chain:
            self.current_mooring.buoy_chains[index] = dialog.chain
            self.update_all_tables()
            
            self.graphics_view.setTransform(current_transform)
            self.graphics_view.centerOn(current_center)
            self.graphics_view.draw_system()
            
            self.refresh_map()
    
    def delete_buoy_chain(self, index):
        if QtWidgets.QMessageBox.question(self, "تأیید", "آیا از حذف این زنجیر بویه مطمئن هستید؟") == QtWidgets.QMessageBox.Yes:
            self.current_mooring.buoy_chains.pop(index)
            self.update_all_tables()
            self.refresh_map()
    
    def add_shackle(self):
        if not self.current_mooring:
            QtWidgets.QMessageBox.warning(self, "خطا", "لطفاً ابتدا یک مورینگ انتخاب کنید")
            return
        dialog = AddShackleDialog(self, mooring_id=self.current_mooring.id)
        if dialog.exec_() and dialog.shackle:
            self.current_mooring.shackles.append(dialog.shackle)
            self.update_all_tables()
            self.refresh_map()
    
    def edit_shackle(self, index):
        shackle = self.current_mooring.shackles[index]
        dialog = AddShackleDialog(self, shackle=shackle, mooring_id=self.current_mooring.id)
        if dialog.exec_() and dialog.shackle:
            self.current_mooring.shackles[index] = dialog.shackle
            self.update_all_tables()
            self.refresh_map()
    
    def delete_shackle(self, index):
        if QtWidgets.QMessageBox.question(self, "تأیید", "آیا از حذف این شاکل مطمئن هستید؟") == QtWidgets.QMessageBox.Yes:
            self.current_mooring.shackles.pop(index)
            self.update_all_tables()
            self.refresh_map()
    
    def add_bridle(self):
        if not self.current_mooring:
            QtWidgets.QMessageBox.warning(self, "خطا", "لطفاً ابتدا یک مورینگ انتخاب کنید")
            return
        dialog = AddBridleRopeDialog(self, self.current_mooring.buoys, mooring_id=self.current_mooring.id)
        if dialog.exec_() and dialog.bridle:
            self.current_mooring.bridle_ropes.append(dialog.bridle)
            self.update_all_tables()
            self.refresh_map()
    
    def edit_bridle(self, index):
        bridle = self.current_mooring.bridle_ropes[index]
        dialog = AddBridleRopeDialog(self, self.current_mooring.buoys, bridle=bridle, mooring_id=self.current_mooring.id)
        if dialog.exec_() and dialog.bridle:
            self.current_mooring.bridle_ropes[index] = dialog.bridle
            self.update_all_tables()
            self.refresh_map()
    
    def delete_bridle(self, index):
        if QtWidgets.QMessageBox.question(self, "تأیید", "آیا از حذف این طناب برایدل مطمئن هستید؟") == QtWidgets.QMessageBox.Yes:
            self.current_mooring.bridle_ropes.pop(index)
            self.update_all_tables()
            self.refresh_map()
    
    def add_cage(self):
        if not self.current_mooring:
            QtWidgets.QMessageBox.warning(self, "خطا", "لطفاً ابتدا یک مورینگ انتخاب کنید")
            return
        dialog = AddCageDialog(self, mooring_id=self.current_mooring.id)
        if dialog.exec_() and dialog.cage:
            self.current_mooring.cages.append(dialog.cage)
            self.update_all_tables()
            self.refresh_map()
    
    def edit_cage(self, index):
        cage = self.current_mooring.cages[index]
        dialog = AddCageDialog(self, cage=cage, mooring_id=self.current_mooring.id)
        if dialog.exec_() and dialog.cage:
            self.current_mooring.cages[index] = dialog.cage
            self.update_all_tables()
            self.refresh_map()
    
    def delete_cage(self, index):
        if QtWidgets.QMessageBox.question(self, "تأیید", "آیا از حذف این قفس مطمئن هستید؟") == QtWidgets.QMessageBox.Yes:
            self.current_mooring.cages.pop(index)
            self.update_all_tables()
            self.refresh_map()
    
    def add_net(self):
        if not self.current_mooring:
            QtWidgets.QMessageBox.warning(self, "خطا", "لطفاً ابتدا یک مورینگ انتخاب کنید")
            return
        dialog = AddNetDialog(self, self.current_mooring.cages, mooring_id=self.current_mooring.id)
        if dialog.exec_() and dialog.net:
            self.current_mooring.nets.append(dialog.net)
            self.update_all_tables()
            self.refresh_map()
    
    def edit_net(self, index):
        net = self.current_mooring.nets[index]
        dialog = AddNetDialog(self, self.current_mooring.cages, net=net, mooring_id=self.current_mooring.id)
        if dialog.exec_() and dialog.net:
            self.current_mooring.nets[index] = dialog.net
            self.update_all_tables()
            self.refresh_map()
    
    def delete_net(self, index):
        if QtWidgets.QMessageBox.question(self, "تأیید", "آیا از حذف این تور مطمئن هستید؟") == QtWidgets.QMessageBox.Yes:
            self.current_mooring.nets.pop(index)
            self.update_all_tables()
            self.refresh_map()
    
    def add_collector(self):
        if not self.current_mooring:
            QtWidgets.QMessageBox.warning(self, "خطا", "لطفاً ابتدا یک مورینگ انتخاب کنید")
            return
        dialog = AddCollectorDialog(self, self.current_mooring.buoys, mooring_id=self.current_mooring.id)
        if dialog.exec_() and dialog.collector:
            self.current_mooring.collectors.append(dialog.collector)
            self.update_all_tables()
            self.refresh_map()
    
    def edit_collector(self, index):
        collector = self.current_mooring.collectors[index]
        dialog = AddCollectorDialog(self, self.current_mooring.buoys, collector=collector, mooring_id=self.current_mooring.id)
        if dialog.exec_() and dialog.collector:
            self.current_mooring.collectors[index] = dialog.collector
            self.update_all_tables()
            self.refresh_map()
    
    def delete_collector(self, index):
        if QtWidgets.QMessageBox.question(self, "تأیید", "آیا از حذف این کلکتور مطمئن هستید؟") == QtWidgets.QMessageBox.Yes:
            self.current_mooring.collectors.pop(index)
            self.update_all_tables()
            self.refresh_map()
    
    # ==================== توابع آپدیت جدول‌ها ====================
    def update_all_tables(self):
        if not self.current_mooring:
            self.clear_all_tables()
            return
        
        # بویه‌ها
        self.buoy_table.setRowCount(len(self.current_mooring.buoys))
        for i, b in enumerate(self.current_mooring.buoys):
            self.buoy_table.setItem(i, 0, QtWidgets.QTableWidgetItem(b.id))
            btn_widget = self.create_action_buttons(partial(self.edit_buoy, i), partial(self.delete_buoy, i))
            self.buoy_table.setCellWidget(i, 1, btn_widget)
        
        # لنگرها
        self.anchor_table.setRowCount(len(self.current_mooring.anchors))
        for i, a in enumerate(self.current_mooring.anchors):
            self.anchor_table.setItem(i, 0, QtWidgets.QTableWidgetItem(a.id))
            btn_widget = self.create_action_buttons(partial(self.edit_anchor, i), partial(self.delete_anchor, i))
            self.anchor_table.setCellWidget(i, 1, btn_widget)
        
        # زنجیرها
        self.chain_table.setRowCount(len(self.current_mooring.anchor_chains))
        for i, c in enumerate(self.current_mooring.anchor_chains):
            self.chain_table.setItem(i, 0, QtWidgets.QTableWidgetItem(c.id))
            btn_widget = self.create_action_buttons(partial(self.edit_chain, i), partial(self.delete_chain, i))
            self.chain_table.setCellWidget(i, 1, btn_widget)
        
        # طناب اصلی
        self.rope_table.setRowCount(len(self.current_mooring.anchor_ropes))
        for i, r in enumerate(self.current_mooring.anchor_ropes):
            self.rope_table.setItem(i, 0, QtWidgets.QTableWidgetItem(r.id))
            btn_widget = self.create_action_buttons(partial(self.edit_rope, i), partial(self.delete_rope, i))
            self.rope_table.setCellWidget(i, 1, btn_widget)
        
        # زنجیر بویه
        self.buoy_chain_table.setRowCount(len(self.current_mooring.buoy_chains))
        for i, bc in enumerate(self.current_mooring.buoy_chains):
            display_text = f"بویه: {bc.buoy_id} → کلکتور: {bc.collector_id}"
            self.buoy_chain_table.setItem(i, 0, QtWidgets.QTableWidgetItem(display_text))
            btn_widget = self.create_action_buttons(partial(self.edit_buoy_chain, i), partial(self.delete_buoy_chain, i))
            self.buoy_chain_table.setCellWidget(i, 1, btn_widget)
        
        # شاکل
        self.shackle_table.setRowCount(len(self.current_mooring.shackles))
        for i, sh in enumerate(self.current_mooring.shackles):
            display_text = f"{sh.id} (نوع: {sh.shackle_type}, سایز: {sh.size}mm, تناژ: {sh.capacity}تن, متصل به: {sh.connected_id})"
            self.shackle_table.setItem(i, 0, QtWidgets.QTableWidgetItem(display_text))
            btn_widget = self.create_action_buttons(partial(self.edit_shackle, i), partial(self.delete_shackle, i))
            self.shackle_table.setCellWidget(i, 1, btn_widget)
        
        # طناب برایدل
        self.bridle_table.setRowCount(len(self.current_mooring.bridle_ropes))
        for i, br in enumerate(self.current_mooring.bridle_ropes):
            display_text = f"{br.id} (قفس: {br.cage_x:.0f},{br.cage_y:.0f} → بویه: {br.buoy_id})"
            self.bridle_table.setItem(i, 0, QtWidgets.QTableWidgetItem(display_text))
            btn_widget = self.create_action_buttons(partial(self.edit_bridle, i), partial(self.delete_bridle, i))
            self.bridle_table.setCellWidget(i, 1, btn_widget)
        
        # قفس
        self.cage_table.setRowCount(len(self.current_mooring.cages))
        for i, cg in enumerate(self.current_mooring.cages):
            self.cage_table.setItem(i, 0, QtWidgets.QTableWidgetItem(cg.id))
            btn_widget = self.create_action_buttons(partial(self.edit_cage, i), partial(self.delete_cage, i))
            self.cage_table.setCellWidget(i, 1, btn_widget)
        
        # تور
        self.net_table.setRowCount(len(self.current_mooring.nets))
        for i, nt in enumerate(self.current_mooring.nets):
            display_text = f"{nt.id} (قفس: {nt.cage_id}, قطر: {nt.diameter}mm, چشمه: {nt.mesh_size}mm, جنس: {nt.material}, عمق: {nt.depth}m)"
            self.net_table.setItem(i, 0, QtWidgets.QTableWidgetItem(display_text))
            btn_widget = self.create_action_buttons(partial(self.edit_net, i), partial(self.delete_net, i))
            self.net_table.setCellWidget(i, 1, btn_widget)
        
        # کلکتور
        self.collector_table.setRowCount(len(self.current_mooring.collectors))
        for i, col in enumerate(self.current_mooring.collectors):
            self.collector_table.setItem(i, 0, QtWidgets.QTableWidgetItem(col.id))
            btn_widget = self.create_action_buttons(partial(self.edit_collector, i), partial(self.delete_collector, i))
            self.collector_table.setCellWidget(i, 1, btn_widget)
    
    def clear_all_tables(self):
        """پاک کردن تمام جدول‌ها"""
        self.buoy_table.setRowCount(0)
        self.anchor_table.setRowCount(0)
        self.chain_table.setRowCount(0)
        self.rope_table.setRowCount(0)
        self.buoy_chain_table.setRowCount(0)
        self.shackle_table.setRowCount(0)
        self.bridle_table.setRowCount(0)
        self.cage_table.setRowCount(0)
        self.net_table.setRowCount(0)
        self.collector_table.setRowCount(0)
    
    # ==================== توابع ذخیره و بارگذاری ====================
    def save_data(self):
        import json
        data = []
        for farm in self.farms:
            farm_data = {
                "id": farm.id, "name": farm.name, 
                "center_x": farm.center_x, "center_y": farm.center_y, 
                "moorings": []
            }
            for mooring in farm.moorings:
                mooring_data = {
                    "id": mooring.id, "name": mooring.name,
                    "buoys": [{"id": b.id, "buoy_type": b.buoy_type, "utm_x": b.utm_x, "utm_y": b.utm_y, 
                              "color": b.color, "material": b.material, "volume": b.volume, 
                              "install_date": b.install_date, "has_light": b.has_light, 
                              "body_color": b.body_color, "status": b.status, "note": b.note} for b in mooring.buoys],
                    "anchors": [{"id": a.id, "anchor_type": a.anchor_type, "utm_x": a.utm_x, "utm_y": a.utm_y, 
                                "weight": a.weight, "color": a.color, "material": a.material, 
                                "install_date": a.install_date, "install_depth": a.install_depth, 
                                "status": a.status, "body_color": a.body_color, "note": a.note} for a in mooring.anchors],
                    "anchor_chains": [{"id": c.id, "start_id": c.start_id, "end_id": c.end_id, "diameter": c.diameter,
                                "use_manual_start": c.use_manual_start, "start_x": c.start_x, "start_y": c.start_y,
                                "use_manual_end": c.use_manual_end, "end_x": c.end_x, "end_y": c.end_y, 
                                "color": c.color, "chain_type": c.chain_type, "material": c.material,
                                "install_date": c.install_date, "status": c.status, "note": c.note} for c in mooring.anchor_chains],
                    "anchor_ropes": [{"id": r.id, "start_id": r.start_id, "end_id": r.end_id, "material": r.material, 
                                    "diameter": r.diameter,
                                    "use_manual_start": r.use_manual_start, "start_x": r.start_x, "start_y": r.start_y,
                                    "use_manual_end": r.use_manual_end, "end_x": r.end_x, "end_y": r.end_y, 
                                    "color": r.color, "strand_count": r.strand_count, "length": r.length,
                                    "install_date": r.install_date, "status": r.status, "note": r.note} for r in mooring.anchor_ropes],
                    "buoy_chains": [{"id": bc.id, "diameter": bc.diameter, "length": bc.length, 
                                    "material": bc.material, "chain_type": bc.chain_type,
                                    "install_date": bc.install_date, "status": bc.status, 
                                    "buoy_id": bc.buoy_id, "collector_id": bc.collector_id, "note": bc.note} for bc in mooring.buoy_chains],
                    "shackles": [{"id": sh.id, "shackle_type": sh.shackle_type, "quantity": sh.quantity,
                                "size": sh.size, "capacity": sh.capacity, "material": sh.material, 
                                "connected_id": sh.connected_id, "install_date": sh.install_date, 
                                "status": sh.status, "note": sh.note} for sh in mooring.shackles],
                    "bridle_ropes": [{"id": br.id, "diameter": br.diameter, "length": br.length, 
                                    "material": br.material, "strand_count": br.strand_count,
                                    "install_date": br.install_date, "status": br.status,
                                    "cage_x": br.cage_x, "cage_y": br.cage_y,
                                    "buoy_id": br.buoy_id, "color": br.color, "note": br.note} for br in mooring.bridle_ropes],
                    "cages": [{"id": cg.id, "diameter": cg.diameter, "material": cg.material,
                              "install_date": cg.install_date, "status": cg.status,
                              "utm_x": cg.utm_x, "utm_y": cg.utm_y, "color": cg.color, "note": cg.note} for cg in mooring.cages],
                    "nets": [{"id": n.id, "cage_id": n.cage_id, "diameter": n.diameter,
                             "mesh_size": n.mesh_size, "material": n.material, "depth": n.depth,
                             "install_date": n.install_date, "status": n.status, "note": n.note} for n in mooring.nets],
                    "collectors": [{"id": col.id, "diameter": col.diameter, "thickness": col.thickness,
                                   "depth": col.depth, "material": col.material,
                                   "install_date": col.install_date, "status": col.status,
                                   "buoy_id": col.buoy_id, "color": col.color, "note": col.note} for col in mooring.collectors]
                }
                farm_data["moorings"].append(mooring_data)
            data.append(farm_data)
        
        with open("Farms_Data.json", "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        QtWidgets.QMessageBox.information(self, "ذخیره", "داده‌ها با موفقیت ذخیره شد")
    
    def load_data(self):
        import json
        try:
            with open("Farms_Data.json", "r", encoding="utf-8") as f:
                data = json.load(f)
            
            self.farms = []
            for farm_data in data:
                farm = Farm(farm_data["id"], farm_data["name"], farm_data["center_x"], farm_data["center_y"])
                for mooring_data in farm_data["moorings"]:
                    mooring = Mooring(mooring_data["id"], mooring_data["name"])
                    
                    for b in mooring_data["buoys"]:
                        from ..core.models import Buoy
                        buoy = Buoy()
                        buoy.id = b["id"]
                        buoy.mooring_id = mooring.id
                        buoy.buoy_type = b["buoy_type"]
                        buoy.utm_x = b["utm_x"]
                        buoy.utm_y = b["utm_y"]
                        buoy.color = b.get("color", "#A0A0A0")
                        buoy.material = b.get("material", "پلاستیک")
                        buoy.volume = b.get("volume", 0)
                        buoy.install_date = b.get("install_date", "")
                        buoy.has_light = b.get("has_light", False)
                        buoy.body_color = b.get("body_color", "#A0A0A0")
                        buoy.status = b.get("status", "سالم")
                        buoy.note = b.get("note", "")
                        mooring.buoys.append(buoy)
                    
                    for a in mooring_data["anchors"]:
                        from ..core.models import Anchor
                        anchor = Anchor()
                        anchor.id = a["id"]
                        anchor.mooring_id = mooring.id
                        anchor.anchor_type = a["anchor_type"]
                        anchor.utm_x = a["utm_x"]
                        anchor.utm_y = a["utm_y"]
                        anchor.weight = a["weight"]
                        anchor.color = a.get("color", "#6A9955")
                        anchor.material = a.get("material", "فولاد")
                        anchor.install_date = a.get("install_date", "")
                        anchor.install_depth = a.get("install_depth", 0)
                        anchor.status = a.get("status", "سالم")
                        anchor.body_color = a.get("body_color", "#6A9955")
                        anchor.note = a.get("note", "")
                        mooring.anchors.append(anchor)
                    
                    for c in mooring_data["anchor_chains"]:
                        from ..core.models import AnchorChain
                        chain = AnchorChain()
                        chain.id = c["id"]
                        chain.mooring_id = mooring.id
                        chain.start_id = c["start_id"]
                        chain.end_id = c["end_id"]
                        chain.diameter = c["diameter"]
                        chain.use_manual_start = c["use_manual_start"]
                        chain.start_x = c["start_x"]
                        chain.start_y = c["start_y"]
                        chain.use_manual_end = c["use_manual_end"]
                        chain.end_x = c["end_x"]
                        chain.end_y = c["end_y"]
                        chain.color = c.get("color", "#C58688")
                        chain.chain_type = c.get("chain_type", "ساده")
                        chain.material = c.get("material", "فولاد")
                        chain.install_date = c.get("install_date", "")
                        chain.status = c.get("status", "سالم")
                        chain.note = c.get("note", "")
                        mooring.anchor_chains.append(chain)
                    
                    for r in mooring_data["anchor_ropes"]:
                        from ..core.models import AnchorRope
                        rope = AnchorRope()
                        rope.id = r["id"]
                        rope.mooring_id = mooring.id
                        rope.start_id = r["start_id"]
                        rope.end_id = r["end_id"]
                        rope.material = r["material"]
                        rope.diameter = r["diameter"]
                        rope.use_manual_start = r["use_manual_start"]
                        rope.start_x = r["start_x"]
                        rope.start_y = r["start_y"]
                        rope.use_manual_end = r["use_manual_end"]
                        rope.end_x = r["end_x"]
                        rope.end_y = r["end_y"]
                        rope.color = r.get("color", "#C8C8C8")
                        rope.strand_count = r.get("strand_count", 3)
                        rope.length = r.get("length", 50)
                        rope.install_date = r.get("install_date", "")
                        rope.status = r.get("status", "سالم")
                        rope.note = r.get("note", "")
                        mooring.anchor_ropes.append(rope)
                    
                    for bc in mooring_data.get("buoy_chains", []):
                        from ..core.models import BuoyChain
                        buoy_chain = BuoyChain()
                        buoy_chain.id = bc["id"]
                        buoy_chain.mooring_id = mooring.id
                        buoy_chain.diameter = bc.get("diameter", 20)
                        buoy_chain.length = bc.get("length", 10)
                        buoy_chain.material = bc.get("material", "فولاد")
                        buoy_chain.chain_type = bc.get("chain_type", "ساده")
                        buoy_chain.install_date = bc.get("install_date", "")
                        buoy_chain.status = bc.get("status", "سالم")
                        buoy_chain.buoy_id = bc.get("buoy_id", "")
                        buoy_chain.collector_id = bc.get("collector_id", "")
                        buoy_chain.note = bc.get("note", "")
                        mooring.buoy_chains.append(buoy_chain)
                    
                    for sh in mooring_data.get("shackles", []):
                        from ..core.models import Shackle
                        shackle = Shackle()
                        shackle.id = sh["id"]
                        shackle.mooring_id = mooring.id
                        shackle.shackle_type = sh.get("shackle_type", "یو شکل")
                        shackle.quantity = sh.get("quantity", 1)
                        shackle.size = sh.get("size", 25)
                        shackle.capacity = sh.get("capacity", 5.0)
                        shackle.material = sh.get("material", "فولاد")
                        shackle.connected_id = sh.get("connected_id", "")
                        shackle.install_date = sh.get("install_date", "")
                        shackle.status = sh.get("status", "سالم")
                        shackle.note = sh.get("note", "")
                        mooring.shackles.append(shackle)
                    
                    for br in mooring_data.get("bridle_ropes", []):
                        from ..core.models import BridleRope
                        bridle = BridleRope()
                        bridle.id = br["id"]
                        bridle.mooring_id = mooring.id
                        bridle.diameter = br.get("diameter", 40)
                        bridle.length = br.get("length", 15.0)
                        bridle.material = br.get("material", "پلی پروپیلن")
                        bridle.strand_count = br.get("strand_count", 3)
                        bridle.install_date = br.get("install_date", "")
                        bridle.status = br.get("status", "سالم")
                        bridle.cage_x = br.get("cage_x", 0)
                        bridle.cage_y = br.get("cage_y", 0)
                        bridle.buoy_id = br.get("buoy_id", "")
                        bridle.color = br.get("color", "#D4A574")
                        bridle.note = br.get("note", "")
                        mooring.bridle_ropes.append(bridle)
                    
                    for cg in mooring_data.get("cages", []):
                        from ..core.models import Cage
                        cage = Cage()
                        cage.id = cg["id"]
                        cage.mooring_id = mooring.id
                        cage.diameter = cg.get("diameter", 10.0)
                        cage.material = cg.get("material", "فولاد")
                        cage.install_date = cg.get("install_date", "")
                        cage.status = cg.get("status", "سالم")
                        cage.utm_x = cg.get("utm_x", 0)
                        cage.utm_y = cg.get("utm_y", 0)
                        cage.color = cg.get("color", "#569CD6")
                        cage.note = cg.get("note", "")
                        mooring.cages.append(cage)
                    
                    for n in mooring_data.get("nets", []):
                        from ..core.models import Net
                        net = Net()
                        net.id = n["id"]
                        net.mooring_id = mooring.id
                        net.cage_id = n.get("cage_id", "")
                        net.diameter = n.get("diameter", 10)
                        net.mesh_size = n.get("mesh_size", 50)
                        net.material = n.get("material", "داینما")
                        net.depth = n.get("depth", 4.0)
                        net.install_date = n.get("install_date", "")
                        net.status = n.get("status", "سالم")
                        net.note = n.get("note", "")
                        mooring.nets.append(net)
                    
                    for col in mooring_data.get("collectors", []):
                        from ..core.models import Collector
                        collector = Collector()
                        collector.id = col["id"]
                        collector.mooring_id = mooring.id
                        collector.diameter = col.get("diameter", 1.0)
                        collector.thickness = col.get("thickness", 10)
                        collector.depth = col.get("depth", 12.0)
                        collector.material = col.get("material", "فولاد")
                        collector.install_date = col.get("install_date", "")
                        collector.status = col.get("status", "سالم")
                        collector.buoy_id = col.get("buoy_id", "")
                        collector.color = col.get("color", "#CE9178")
                        collector.note = col.get("note", "")
                        mooring.collectors.append(collector)
                    
                    farm.moorings.append(mooring)
                self.farms.append(farm)
            
            self.update_farm_combo()
            self.on_farm_selected(0)
            QtWidgets.QMessageBox.information(self, "بارگذاری", "داده‌ها با موفقیت بارگذاری شد")
        except FileNotFoundError:
            QtWidgets.QMessageBox.warning(self, "خطا", "فایل داده‌ای یافت نشد")