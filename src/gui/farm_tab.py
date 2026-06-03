"""
صفحه طراحی و مدیریت مزرعه (بخش اصلی برنامه) برای ERP-Aqua
نسخه دیتابیس - با دیباگ برای رفع مشکل ذخیره قفس
"""

from PyQt5 import QtWidgets, QtCore
from functools import partial
import qtawesome as qta

from ..core.models import Farm, Mooring, Buoy, Anchor, AnchorChain, AnchorRope, BuoyChain, Shackle, BridleRope, Cage, Net, Collector
from ..core.constants import (
    TABLE_ROW_HEIGHT, TABLE_ACTION_COLUMN_WIDTH,
    GLASS_BTN_STYLE, SMALL_ICON_STYLE, GLASS_PANEL_STYLE
)
from ..graphics.graphics_view import MooringGraphicsView
from ..widgets.color_button import ColorButton
from ..database.db_handler import DatabaseHandler
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
    شامل پنل آیکونها، جدول مدیریت اجزا و نقشه گرافیکی
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.db = DatabaseHandler()
        self.farms = []
        self.current_farm = None
        self.current_mooring = None
        self.current_table_index = 0
        self.setup_ui()
        self.load_data()

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

        # پنل آیکونهای کوچک
        self.setup_icon_panel(left_layout)

        # استک ویجت جدولها
        self.setup_table_stacked(left_layout)

        main_layout.addWidget(left_widget, 1)

        # ==================== سمت راست ====================
        right_widget = QtWidgets.QWidget()
        right_layout = QtWidgets.QVBoxLayout(right_widget)
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.setSpacing(8)

        # لیست مورینگها
        self.setup_mooring_list(right_layout)

        # نوار ابزار
        self.setup_toolbar(right_layout)

        # نقشه
        self.graphics_view = MooringGraphicsView()
        right_layout.addWidget(self.graphics_view)

        main_layout.addWidget(right_widget, 4)

        # انتخاب پیشفرض
        if self.small_icon_btns:
            self.small_icon_btns[0].setChecked(True)
            self.current_table_index = 0
            self.table_stacked.setCurrentIndex(0)

    def setup_icon_panel(self, parent_layout):
        """تنظیم پنل آیکونهای کوچک برای انتخاب جدول (فقط آیکون)"""
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
        """تنظیم استک ویجت جدولها"""
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
        """تنظیم لیست مورینگها (چکباکسها)"""
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

        # ردیف 1: کامبوباکسها و دکمههای عملیات
        row1 = QtWidgets.QHBoxLayout()
        row1.setSpacing(6)

        self.setup_farm_controls(row1)
        self.setup_mooring_controls(row1)

        row1.addStretch()
        self.setup_action_buttons(row1)

        toolbar_layout.addLayout(row1)

        # ردیف 2: آیکونهای افزودن اجزا
        row2 = QtWidgets.QHBoxLayout()
        row2.setSpacing(4)
        self.setup_add_buttons(row2)
        row2.addStretch()
        toolbar_layout.addLayout(row2)

        parent_layout.addWidget(toolbar_widget)

    def setup_farm_controls(self, layout):
        """تنظیم کنترلهای مربوط به مزرعه"""
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
        """تنظیم کنترلهای مربوط به مورینگ"""
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

        layout.addSpacing(15)

    def setup_action_buttons(self, layout):
        """تنظیم دکمههای عملیات (ذخیره، بارگذاری، لیست نهایی)"""
        self.save_btn = QtWidgets.QToolButton()
        self.save_btn.setIcon(qta.icon('fa5s.save', color='#C8C8C8'))
        self.save_btn.setIconSize(QtCore.QSize(18, 18))
        self.save_btn.setToolTip("ذخیره دادهها در دیتابیس")
        self.save_btn.clicked.connect(self.save_data)
        layout.addWidget(self.save_btn)

        self.load_btn = QtWidgets.QToolButton()
        self.load_btn.setIcon(qta.icon('fa5s.folder-open', color='#C8C8C8'))
        self.load_btn.setIconSize(QtCore.QSize(18, 18))
        self.load_btn.setToolTip("بارگذاری دادهها از دیتابیس")
        self.load_btn.clicked.connect(self.load_data)
        layout.addWidget(self.load_btn)

        self.final_list_btn = QtWidgets.QToolButton()
        self.final_list_btn.setIcon(qta.icon('fa5s.list-ul', color='#C8C8C8'))
        self.final_list_btn.setIconSize(QtCore.QSize(18, 18))
        self.final_list_btn.setToolTip("نمایش لیست کامل اجزای مورینگ")
        self.final_list_btn.clicked.connect(self.show_final_list)
        layout.addWidget(self.final_list_btn)

    def setup_add_buttons(self, layout):
        """تنظیم دکمههای افزودن اجزا (نوار ابزار شیشهای بالای نقشه)"""
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

    # ==================== توابع نمایش جدولها ====================
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

    # ==================== ذخیره و بارگذاری با دیتابیس ====================

    def load_data(self):
        """بارگذاری دادهها از دیتابیس"""
        self.farms = self.db.get_all_farms()
        print(f"DEBUG: تعداد مزارع بارگذاری شده: {len(self.farms)}")
        self.update_farm_combo()
        if self.farm_combo.count() > 0:
            self.on_farm_selected(0)

    def save_data(self):
        """ذخیره دادهها در دیتابیس"""
        QtWidgets.QMessageBox.information(self, "اطلاع", "دادهها در دیتابیس ذخیره هستند")

    # ==================== توابع مدیریت مزرعه ====================

    def add_farm(self):
        dialog = AddFarmDialog(self)
        if dialog.exec_() and dialog.farm:
            if self.db.save_farm(dialog.farm):
                self.farms.append(dialog.farm)
                self.update_farm_combo()
            else:
                QtWidgets.QMessageBox.warning(self, "خطا", "خطا در ذخیره مزرعه در دیتابیس")

    def edit_farm(self):
        if not self.current_farm:
            QtWidgets.QMessageBox.warning(self, "خطا", "هیچ مزرعهای انتخاب نشده است")
            return
        dialog = EditFarmDialog(self, self.current_farm)
        if dialog.exec_() and dialog.farm:
            self.current_farm.name = dialog.farm.name
            self.current_farm.id = dialog.farm.id
            self.current_farm.center_x = dialog.farm.center_x
            self.current_farm.center_y = dialog.farm.center_y
            if self.db.save_farm(self.current_farm):
                self.update_farm_combo()
                self.refresh_map()
            else:
                QtWidgets.QMessageBox.warning(self, "خطا", "خطا در ویرایش مزرعه")

    def delete_farm(self):
        if not self.current_farm:
            QtWidgets.QMessageBox.warning(self, "خطا", "هیچ مزرعهای انتخاب نشده است")
            return
        if not self.can_delete_farm(self.current_farm):
            dialog = DeleteConfirmDialog(self, "مزرعه", self.current_farm.name, True)
            dialog.exec_()
            return
        dialog = DeleteConfirmDialog(self, "مزرعه", self.current_farm.name, False)
        if dialog.exec_():
            if self.db.delete_farm(self.current_farm.id):
                self.farms.remove(self.current_farm)
                self.current_farm = None
                self.update_farm_combo()
                self.mooring_combo.clear()
                self.mooring_list_widget.clear()
                self.graphics_view.set_farm(None)
                QtWidgets.QMessageBox.information(self, "موفق", "مزرعه با موفقیت حذف شد")
            else:
                QtWidgets.QMessageBox.warning(self, "خطا", "خطا در حذف مزرعه")

    # ==================== توابع مدیریت مورینگ ====================

    def add_mooring(self):
        if not self.current_farm:
            QtWidgets.QMessageBox.warning(self, "خطا", "لطفاً ابتدا یک مزرعه انتخاب کنید")
            return
        dialog = AddMooringDialog(self)
        if dialog.exec_() and dialog.mooring:
            if self.db.save_mooring(dialog.mooring, self.current_farm.id):
                self.current_farm.moorings.append(dialog.mooring)
                self.update_mooring_combo()
                self.update_mooring_list()
                self.on_mooring_selected(0)
                self.refresh_map()
            else:
                QtWidgets.QMessageBox.warning(self, "خطا", "خطا در ذخیره مورینگ")

    def edit_mooring(self):
        if not self.current_mooring:
            QtWidgets.QMessageBox.warning(self, "خطا", "هیچ مورینگی انتخاب نشده است")
            return
        dialog = EditMooringDialog(self, self.current_mooring)
        if dialog.exec_() and dialog.mooring:
            old_id = self.current_mooring.id
            self.current_mooring.id = dialog.mooring.id
            self.current_mooring.name = dialog.mooring.name
            if self.db.save_mooring(self.current_mooring, self.current_farm.id):
                for buoy in self.current_mooring.buoys:
                    buoy.mooring_id = self.current_mooring.id
                    self.db.save_buoy(buoy, self.current_mooring.id)
                for anchor in self.current_mooring.anchors:
                    anchor.mooring_id = self.current_mooring.id
                    self.db.save_anchor(anchor, self.current_mooring.id)
                for cage in self.current_mooring.cages:
                    cage.mooring_id = self.current_mooring.id
                    self.db.save_cage(cage, self.current_mooring.id)
                self.update_mooring_combo()
                self.update_mooring_list()
                self.refresh_map()
            else:
                QtWidgets.QMessageBox.warning(self, "خطا", "خطا در ویرایش مورینگ")

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
            if self.db.delete_mooring(self.current_mooring.id):
                self.current_farm.moorings.remove(self.current_mooring)
                self.current_mooring = None
                self.update_mooring_combo()
                self.update_mooring_list()
                self.graphics_view.set_farm(self.current_farm)
                QtWidgets.QMessageBox.information(self, "موفق", "مورینگ با موفقیت حذف شد")
            else:
                QtWidgets.QMessageBox.warning(self, "خطا", "خطا در حذف مورینگ")

    def show_final_list(self):
        dialog = FinalConfirmDialog(self, self.farms, self.current_farm, self.current_mooring)
        dialog.exec_()

    # ==================== توابع مدیریت بویه ====================

    def add_buoy(self):
        if not self.current_mooring:
            QtWidgets.QMessageBox.warning(self, "خطا", "لطفاً ابتدا یک مورینگ انتخاب کنید")
            return
        dialog = BuoyDialog(self, edit_mode=False, mooring_id=self.current_mooring.id)
        if dialog.exec_() and dialog.buoy:
            if self.db.save_buoy(dialog.buoy, self.current_mooring.id):
                self.current_mooring.buoys.append(dialog.buoy)
                self.update_all_tables()
                self.refresh_map()
            else:
                QtWidgets.QMessageBox.warning(self, "خطا", "خطا در ذخیره بویه")

    def edit_buoy(self, index):
        buoy = self.current_mooring.buoys[index]
        dialog = BuoyDialog(self, buoy=buoy, edit_mode=True, mooring_id=self.current_mooring.id)
        if dialog.exec_():
            if self.db.save_buoy(dialog.buoy, self.current_mooring.id):
                self.current_mooring.buoys[index] = dialog.buoy
                self.update_all_tables()
                self.refresh_map()
            else:
                QtWidgets.QMessageBox.warning(self, "خطا", "خطا در ویرایش بویه")

    def delete_buoy(self, index):
        if QtWidgets.QMessageBox.question(self, "تأیید", "آیا از حذف این بویه مطمئن هستید؟") == QtWidgets.QMessageBox.Yes:
            buoy = self.current_mooring.buoys[index]
            self.db.execute_query("DELETE FROM buoys WHERE id = %s AND mooring_id = %s", (buoy.id, self.current_mooring.id))
            self.current_mooring.buoys.pop(index)
            self.update_all_tables()
            self.refresh_map()

    # ==================== توابع مدیریت لنگر ====================

    def add_anchor(self):
        if not self.current_mooring:
            QtWidgets.QMessageBox.warning(self, "خطا", "لطفاً ابتدا یک مورینگ انتخاب کنید")
            return
        dialog = AnchorDialog(self, edit_mode=False, mooring_id=self.current_mooring.id)
        if dialog.exec_() and dialog.anchor:
            if self.db.save_anchor(dialog.anchor, self.current_mooring.id):
                self.current_mooring.anchors.append(dialog.anchor)
                self.update_all_tables()
                self.refresh_map()
            else:
                QtWidgets.QMessageBox.warning(self, "خطا", "خطا در ذخیره لنگر")

    def edit_anchor(self, index):
        anchor = self.current_mooring.anchors[index]
        dialog = AnchorDialog(self, anchor=anchor, edit_mode=True, mooring_id=self.current_mooring.id)
        if dialog.exec_():
            if self.db.save_anchor(dialog.anchor, self.current_mooring.id):
                self.current_mooring.anchors[index] = dialog.anchor
                self.update_all_tables()
                self.refresh_map()
            else:
                QtWidgets.QMessageBox.warning(self, "خطا", "خطا در ویرایش لنگر")

    def delete_anchor(self, index):
        if QtWidgets.QMessageBox.question(self, "تأیید", "آیا از حذف این لنگر مطمئن هستید؟") == QtWidgets.QMessageBox.Yes:
            anchor = self.current_mooring.anchors[index]
            self.db.execute_query("DELETE FROM anchors WHERE id = %s AND mooring_id = %s", (anchor.id, self.current_mooring.id))
            self.current_mooring.anchors.pop(index)
            self.update_all_tables()
            self.refresh_map()

    # ==================== توابع مدیریت قفس ====================

    def add_cage(self):
        if not self.current_mooring:
            QtWidgets.QMessageBox.warning(self, "خطا", "لطفاً ابتدا یک مورینگ انتخاب کنید")
            return
        dialog = AddCageDialog(self, mooring_id=self.current_mooring.id)
        if dialog.exec_() and dialog.cage:
            if self.db.save_cage(dialog.cage, self.current_mooring.id):
                self.current_mooring.cages.append(dialog.cage)
                self.update_all_tables()
                self.refresh_map()
                QtWidgets.QMessageBox.information(self, "موفق", "قفس با موفقیت ذخیره شد")
            else:
                QtWidgets.QMessageBox.warning(self, "خطا", "خطا در ذخیره قفس")

    def edit_cage(self, index):
        cage = self.current_mooring.cages[index]
        dialog = AddCageDialog(self, cage=cage, mooring_id=self.current_mooring.id)
        if dialog.exec_():
            if self.db.save_cage(dialog.cage, self.current_mooring.id):
                self.current_mooring.cages[index] = dialog.cage
                self.update_all_tables()
                self.refresh_map()
            else:
                QtWidgets.QMessageBox.warning(self, "خطا", "خطا در ویرایش قفس")

    def delete_cage(self, index):
        if QtWidgets.QMessageBox.question(self, "تأیید", "آیا از حذف این قفس مطمئن هستید؟") == QtWidgets.QMessageBox.Yes:
            cage = self.current_mooring.cages[index]
            self.db.execute_query("DELETE FROM cages WHERE id = %s AND mooring_id = %s", (cage.id, self.current_mooring.id))
            self.current_mooring.cages.pop(index)
            self.update_all_tables()
            self.refresh_map()

    # ==================== توابع مدیریت زنجیر ====================

    def add_chain(self):
        if not self.current_mooring:
            QtWidgets.QMessageBox.warning(self, "خطا", "لطفاً ابتدا یک مورینگ انتخاب کنید")
            return
        dialog = AddChainDialog(self, self.current_mooring.anchors, self.current_mooring.anchor_ropes, mooring_id=self.current_mooring.id)
        if dialog.exec_() and dialog.chain:
            if self.db.save_anchor_chain(dialog.chain, self.current_mooring.id):
                self.current_mooring.anchor_chains.append(dialog.chain)
                self.update_all_tables()
                self.refresh_map()
            else:
                QtWidgets.QMessageBox.warning(self, "خطا", "خطا در ذخیره زنجیر")

    def edit_chain(self, index):
        chain = self.current_mooring.anchor_chains[index]
        dialog = AddChainDialog(self, self.current_mooring.anchors, self.current_mooring.anchor_ropes, chain=chain, mooring_id=self.current_mooring.id)
        if dialog.exec_() and dialog.chain:
            if self.db.save_anchor_chain(dialog.chain, self.current_mooring.id):
                self.current_mooring.anchor_chains[index] = dialog.chain
                self.update_all_tables()
                self.refresh_map()
            else:
                QtWidgets.QMessageBox.warning(self, "خطا", "خطا در ویرایش زنجیر")

    def delete_chain(self, index):
        if QtWidgets.QMessageBox.question(self, "تأیید", "آیا از حذف این زنجیر مطمئن هستید؟") == QtWidgets.QMessageBox.Yes:
            chain = self.current_mooring.anchor_chains[index]
            self.db.execute_query("DELETE FROM anchor_chains WHERE id = %s AND mooring_id = %s", (chain.id, self.current_mooring.id))
            self.current_mooring.anchor_chains.pop(index)
            self.update_all_tables()
            self.refresh_map()

    # ==================== توابع مدیریت طناب اصلی ====================

    def add_rope(self):
        if not self.current_mooring:
            QtWidgets.QMessageBox.warning(self, "خطا", "لطفاً ابتدا یک مورینگ انتخاب کنید")
            return
        dialog = AddRopeDialog(self, self.current_mooring.buoys, self.current_mooring.anchor_chains, mooring_id=self.current_mooring.id)
        if dialog.exec_() and dialog.rope:
            if self.db.save_anchor_rope(dialog.rope, self.current_mooring.id):
                self.current_mooring.anchor_ropes.append(dialog.rope)
                self.update_all_tables()
                self.refresh_map()
            else:
                QtWidgets.QMessageBox.warning(self, "خطا", "خطا در ذخیره طناب")

    def edit_rope(self, index):
        rope = self.current_mooring.anchor_ropes[index]
        dialog = AddRopeDialog(self, self.current_mooring.buoys, self.current_mooring.anchor_chains, rope=rope, mooring_id=self.current_mooring.id)
        if dialog.exec_() and dialog.rope:
            if self.db.save_anchor_rope(dialog.rope, self.current_mooring.id):
                self.current_mooring.anchor_ropes[index] = dialog.rope
                self.update_all_tables()
                self.refresh_map()
            else:
                QtWidgets.QMessageBox.warning(self, "خطا", "خطا در ویرایش طناب")

    def delete_rope(self, index):
        if QtWidgets.QMessageBox.question(self, "تأیید", "آیا از حذف این طناب مطمئن هستید؟") == QtWidgets.QMessageBox.Yes:
            rope = self.current_mooring.anchor_ropes[index]
            self.db.execute_query("DELETE FROM anchor_ropes WHERE id = %s AND mooring_id = %s", (rope.id, self.current_mooring.id))
            self.current_mooring.anchor_ropes.pop(index)
            self.update_all_tables()
            self.refresh_map()

    # ==================== توابع مدیریت زنجیر بویه ====================

    def add_buoy_chain(self):
        if not self.current_mooring:
            QtWidgets.QMessageBox.warning(self, "خطا", "لطفاً ابتدا یک مورینگ انتخاب کنید")
            return
        dialog = AddBuoyChainDialog(self, self.current_mooring.buoys, self.current_mooring.collectors, mooring_id=self.current_mooring.id)
        if dialog.exec_() and dialog.chain:
            if self.db.save_buoy_chain(dialog.chain, self.current_mooring.id):
                self.current_mooring.buoy_chains.append(dialog.chain)
                self.update_all_tables()
                self.refresh_map()
            else:
                QtWidgets.QMessageBox.warning(self, "خطا", "خطا در ذخیره زنجیر بویه")

    def edit_buoy_chain(self, index):
        chain = self.current_mooring.buoy_chains[index]
        dialog = AddBuoyChainDialog(self, self.current_mooring.buoys, self.current_mooring.collectors, chain=chain, mooring_id=self.current_mooring.id)
        if dialog.exec_() and dialog.chain:
            if self.db.save_buoy_chain(dialog.chain, self.current_mooring.id):
                self.current_mooring.buoy_chains[index] = dialog.chain
                self.update_all_tables()
                self.refresh_map()
            else:
                QtWidgets.QMessageBox.warning(self, "خطا", "خطا در ویرایش زنجیر بویه")

    def delete_buoy_chain(self, index):
        if QtWidgets.QMessageBox.question(self, "تأیید", "آیا از حذف این زنجیر بویه مطمئن هستید؟") == QtWidgets.QMessageBox.Yes:
            buoy_chain = self.current_mooring.buoy_chains[index]
            self.db.execute_query("DELETE FROM buoy_chains WHERE id = %s AND mooring_id = %s", (buoy_chain.id, self.current_mooring.id))
            self.current_mooring.buoy_chains.pop(index)
            self.update_all_tables()
            self.refresh_map()

    # ==================== توابع مدیریت شاکل ====================

    def add_shackle(self):
        if not self.current_mooring:
            QtWidgets.QMessageBox.warning(self, "خطا", "لطفاً ابتدا یک مورینگ انتخاب کنید")
            return
        dialog = AddShackleDialog(self, mooring_id=self.current_mooring.id)
        if dialog.exec_() and dialog.shackle:
            if self.db.save_shackle(dialog.shackle, self.current_mooring.id):
                self.current_mooring.shackles.append(dialog.shackle)
                self.update_all_tables()
                self.refresh_map()
            else:
                QtWidgets.QMessageBox.warning(self, "خطا", "خطا در ذخیره شاکل")

    def edit_shackle(self, index):
        shackle = self.current_mooring.shackles[index]
        dialog = AddShackleDialog(self, shackle=shackle, mooring_id=self.current_mooring.id)
        if dialog.exec_() and dialog.shackle:
            if self.db.save_shackle(dialog.shackle, self.current_mooring.id):
                self.current_mooring.shackles[index] = dialog.shackle
                self.update_all_tables()
                self.refresh_map()
            else:
                QtWidgets.QMessageBox.warning(self, "خطا", "خطا در ویرایش شاکل")

    def delete_shackle(self, index):
        if QtWidgets.QMessageBox.question(self, "تأیید", "آیا از حذف این شاکل مطمئن هستید؟") == QtWidgets.QMessageBox.Yes:
            shackle = self.current_mooring.shackles[index]
            self.db.execute_query("DELETE FROM shackles WHERE id = %s AND mooring_id = %s", (shackle.id, self.current_mooring.id))
            self.current_mooring.shackles.pop(index)
            self.update_all_tables()
            self.refresh_map()

    # ==================== توابع مدیریت طناب برایدل ====================

    def add_bridle(self):
        if not self.current_mooring:
            QtWidgets.QMessageBox.warning(self, "خطا", "لطفاً ابتدا یک مورینگ انتخاب کنید")
            return
        dialog = AddBridleRopeDialog(self, self.current_mooring.buoys, mooring_id=self.current_mooring.id)
        if dialog.exec_() and dialog.bridle:
            if self.db.save_bridle_rope(dialog.bridle, self.current_mooring.id):
                self.current_mooring.bridle_ropes.append(dialog.bridle)
                self.update_all_tables()
                self.refresh_map()
            else:
                QtWidgets.QMessageBox.warning(self, "خطا", "خطا در ذخیره طناب برایدل")

    def edit_bridle(self, index):
        bridle = self.current_mooring.bridle_ropes[index]
        dialog = AddBridleRopeDialog(self, self.current_mooring.buoys, bridle=bridle, mooring_id=self.current_mooring.id)
        if dialog.exec_() and dialog.bridle:
            if self.db.save_bridle_rope(dialog.bridle, self.current_mooring.id):
                self.current_mooring.bridle_ropes[index] = dialog.bridle
                self.update_all_tables()
                self.refresh_map()
            else:
                QtWidgets.QMessageBox.warning(self, "خطا", "خطا در ویرایش طناب برایدل")

    def delete_bridle(self, index):
        if QtWidgets.QMessageBox.question(self, "تأیید", "آیا از حذف این طناب برایدل مطمئن هستید؟") == QtWidgets.QMessageBox.Yes:
            bridle = self.current_mooring.bridle_ropes[index]
            self.db.execute_query("DELETE FROM bridle_ropes WHERE id = %s AND mooring_id = %s", (bridle.id, self.current_mooring.id))
            self.current_mooring.bridle_ropes.pop(index)
            self.update_all_tables()
            self.refresh_map()

    # ==================== توابع مدیریت تور ====================

    def add_net(self):
        if not self.current_mooring:
            QtWidgets.QMessageBox.warning(self, "خطا", "لطفاً ابتدا یک مورینگ انتخاب کنید")
            return
        dialog = AddNetDialog(self, self.current_mooring.cages, mooring_id=self.current_mooring.id)
        if dialog.exec_() and dialog.net:
            if self.db.save_net(dialog.net, self.current_mooring.id):
                self.current_mooring.nets.append(dialog.net)
                self.update_all_tables()
                self.refresh_map()
            else:
                QtWidgets.QMessageBox.warning(self, "خطا", "خطا در ذخیره تور")

    def edit_net(self, index):
        net = self.current_mooring.nets[index]
        dialog = AddNetDialog(self, self.current_mooring.cages, net=net, mooring_id=self.current_mooring.id)
        if dialog.exec_() and dialog.net:
            if self.db.save_net(dialog.net, self.current_mooring.id):
                self.current_mooring.nets[index] = dialog.net
                self.update_all_tables()
                self.refresh_map()
            else:
                QtWidgets.QMessageBox.warning(self, "خطا", "خطا در ویرایش تور")

    def delete_net(self, index):
        if QtWidgets.QMessageBox.question(self, "تأیید", "آیا از حذف این تور مطمئن هستید؟") == QtWidgets.QMessageBox.Yes:
            net = self.current_mooring.nets[index]
            self.db.execute_query("DELETE FROM nets WHERE id = %s AND mooring_id = %s", (net.id, self.current_mooring.id))
            self.current_mooring.nets.pop(index)
            self.update_all_tables()
            self.refresh_map()

    # ==================== توابع مدیریت کلکتور ====================

    def add_collector(self):
        if not self.current_mooring:
            QtWidgets.QMessageBox.warning(self, "خطا", "لطفاً ابتدا یک مورینگ انتخاب کنید")
            return
        dialog = AddCollectorDialog(self, self.current_mooring.buoys, mooring_id=self.current_mooring.id)
        if dialog.exec_() and dialog.collector:
            if self.db.save_collector(dialog.collector, self.current_mooring.id):
                self.current_mooring.collectors.append(dialog.collector)
                self.update_all_tables()
                self.refresh_map()
            else:
                QtWidgets.QMessageBox.warning(self, "خطا", "خطا در ذخیره کلکتور")

    def edit_collector(self, index):
        collector = self.current_mooring.collectors[index]
        dialog = AddCollectorDialog(self, self.current_mooring.buoys, collector=collector, mooring_id=self.current_mooring.id)
        if dialog.exec_() and dialog.collector:
            if self.db.save_collector(dialog.collector, self.current_mooring.id):
                self.current_mooring.collectors[index] = dialog.collector
                self.update_all_tables()
                self.refresh_map()
            else:
                QtWidgets.QMessageBox.warning(self, "خطا", "خطا در ویرایش کلکتور")

    def delete_collector(self, index):
        if QtWidgets.QMessageBox.question(self, "تأیید", "آیا از حذف این کلکتور مطمئن هستید؟") == QtWidgets.QMessageBox.Yes:
            collector = self.current_mooring.collectors[index]
            self.db.execute_query("DELETE FROM collectors WHERE id = %s AND mooring_id = %s", (collector.id, self.current_mooring.id))
            self.current_mooring.collectors.pop(index)
            self.update_all_tables()
            self.refresh_map()

    # ==================== توابع آپدیت جدولها ====================

    def update_all_tables(self):
        if not self.current_mooring:
            self.clear_all_tables()
            return

        # بویهها
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

        # قفسها
        self.cage_table.setRowCount(len(self.current_mooring.cages))
        for i, cg in enumerate(self.current_mooring.cages):
            self.cage_table.setItem(i, 0, QtWidgets.QTableWidgetItem(cg.id))
            btn_widget = self.create_action_buttons(partial(self.edit_cage, i), partial(self.delete_cage, i))
            self.cage_table.setCellWidget(i, 1, btn_widget)

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
        """پاک کردن تمام جدولها"""
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