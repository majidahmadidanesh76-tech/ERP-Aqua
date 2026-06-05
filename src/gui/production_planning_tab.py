"""
صفحه برنامه‌ریزی تولید حرفه‌ای
شامل دو تب: برنامه پرورش (متصل به قفس) و برنامه نت (متصل به تجهیزات)
"""

from PyQt5 import QtWidgets, QtCore, QtGui
import qtawesome as qta
from functools import partial
from datetime import datetime, timedelta

from ..database.db_handler import DatabaseHandler
from ..widgets.jalali_date_edit import JalaliDateEdit


class ProductionPlanningTab(QtWidgets.QWidget):
    """صفحه اصلی برنامه‌ریزی تولید"""

    def __init__(self, parent=None, farm=None, mooring=None):
        super().__init__(parent)
        self.db = DatabaseHandler()
        self.current_farm = farm
        self.current_mooring = mooring
        self.current_plan_id = None
        self.current_maintenance_plan_id = None
        self.setup_ui()
        self.load_data()

    def setup_ui(self):
        """تنظیم رابط کاربری اصلی"""
        layout = QtWidgets.QVBoxLayout(self)
        layout.setSpacing(10)
        layout.setContentsMargins(10, 10, 10, 10)

        # عنوان
        title = QtWidgets.QLabel("📋 برنامه‌ریزی تولید حرفه‌ای")
        title.setAlignment(QtCore.Qt.AlignCenter)
        title.setStyleSheet("font-size: 18px; font-weight: bold; color: #569CD6; padding: 10px;")
        layout.addWidget(title)

        # استایل شیشه‌ای برای دکمه‌ها
        glass_btn_style = """
            QToolButton {
                background-color: rgba(60, 60, 65, 180);
                border: none;
                border-radius: 4px;
                padding: 4px;
                min-width: 32px;
                min-height: 32px;
            }
            QToolButton:hover {
                background-color: rgba(86, 156, 214, 100);
            }
            QPushButton {
                background-color: rgba(60, 60, 65, 180);
                color: #C8C8C8;
                border: none;
                border-radius: 4px;
                padding: 6px 12px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: rgba(86, 156, 214, 100);
                color: white;
            }
        """

        # ========== تب‌ها ==========
        self.main_tabs = QtWidgets.QTabWidget()
        self.main_tabs.setStyleSheet("""
            QTabWidget::pane {
                border: 1px solid #3E3E42;
                border-radius: 4px;
                background: #1E1E1E;
            }
            QTabBar::tab {
                background-color: #2D2D30;
                color: #C8C8C8;
                padding: 8px 20px;
                margin: 2px;
                border-radius: 4px;
            }
            QTabBar::tab:selected {
                background-color: #3A3A3A;
                color: #C8C8C8;
            }
            QTabBar::tab:hover {
                background-color: #3E3E42;
            }
        """)

        # تب 1: برنامه پرورش
        self.production_tab = self.create_production_tab(glass_btn_style)
        self.main_tabs.addTab(self.production_tab, "🐟 برنامه پرورش")

        # تب 2: برنامه تعمیرات و نگهداری (نت)
        self.maintenance_tab = self.create_maintenance_tab(glass_btn_style)
        self.main_tabs.addTab(self.maintenance_tab, "🛠️ برنامه نت")

        layout.addWidget(self.main_tabs)

        # نوار وضعیت پایینی
        self.setup_status_bar(layout)

    def create_production_tab(self, glass_btn_style):
        """ایجاد تب برنامه پرورش (متصل به قفس)"""
        tab = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout(tab)
        layout.setSpacing(10)

        # ========== نوار ابزار ==========
        toolbar = QtWidgets.QHBoxLayout()
        toolbar.setSpacing(10)

        toolbar.addWidget(QtWidgets.QLabel("قفس:"))
        self.cage_combo = QtWidgets.QComboBox()
        self.cage_combo.setMinimumWidth(150)
        self.cage_combo.setMinimumHeight(30)
        self.cage_combo.setEditable(True)
        self.cage_combo.setInsertPolicy(QtWidgets.QComboBox.NoInsert)
        self.cage_combo.currentIndexChanged.connect(self.on_cage_changed)
        self.cage_combo.setStyleSheet("""
            QComboBox {
                background-color: #3C3C3C;
                color: #C8C8C8;
                border: 1px solid #3E3E42;
                border-radius: 4px;
                padding: 5px;
            }
            QComboBox:hover {
                border-color: #569CD6;
            }
        """)
        toolbar.addWidget(self.cage_combo)

        toolbar.addSpacing(20)

        self.new_production_btn = QtWidgets.QToolButton()
        self.new_production_btn.setIcon(qta.icon('fa5s.plus', color='#C8C8C8'))
        self.new_production_btn.setIconSize(QtCore.QSize(18, 18))
        self.new_production_btn.setToolTip("برنامه پرورش جدید")
        self.new_production_btn.setStyleSheet(glass_btn_style)
        self.new_production_btn.clicked.connect(self.create_new_production_plan)
        toolbar.addWidget(self.new_production_btn)

        self.submit_production_btn = QtWidgets.QToolButton()
        self.submit_production_btn.setIcon(qta.icon('fa5s.paper-plane', color='#C8C8C8'))
        self.submit_production_btn.setIconSize(QtCore.QSize(18, 18))
        self.submit_production_btn.setToolTip("ارسال برنامه")
        self.submit_production_btn.setStyleSheet(glass_btn_style)
        self.submit_production_btn.clicked.connect(self.submit_production_plan)
        self.submit_production_btn.setEnabled(False)
        toolbar.addWidget(self.submit_production_btn)

        self.refresh_production_btn = QtWidgets.QToolButton()
        self.refresh_production_btn.setIcon(qta.icon('fa5s.sync-alt', color='#C8C8C8'))
        self.refresh_production_btn.setIconSize(QtCore.QSize(18, 18))
        self.refresh_production_btn.setToolTip("به‌روزرسانی")
        self.refresh_production_btn.setStyleSheet(glass_btn_style)
        self.refresh_production_btn.clicked.connect(self.refresh_production_data)
        toolbar.addWidget(self.refresh_production_btn)

        toolbar.addStretch()
        layout.addLayout(toolbar)

        # ========== بخش اصلی ==========
        splitter = QtWidgets.QSplitter(QtCore.Qt.Horizontal)
        splitter.setSizes([300, 700])

        # سمت چپ: لیست برنامه‌ها
        left_widget = QtWidgets.QWidget()
        left_layout = QtWidgets.QVBoxLayout(left_widget)
        left_layout.setContentsMargins(0, 0, 5, 0)

        left_label = QtWidgets.QLabel("📌 برنامه‌های پرورش")
        left_label.setStyleSheet("color: #C8C8C8; font-weight: bold; padding: 5px;")
        left_layout.addWidget(left_label)

        self.production_plans_list = QtWidgets.QListWidget()
        self.production_plans_list.setMinimumHeight(200)
        self.production_plans_list.itemClicked.connect(self.on_production_plan_selected)
        self.production_plans_list.setStyleSheet("""
            QListWidget {
                background-color: #2D2D30;
                border: 1px solid #3E3E42;
                border-radius: 4px;
                color: #C8C8C8;
                padding: 5px;
            }
            QListWidget::item {
                padding: 8px;
                border-bottom: 1px solid #3E3E42;
            }
            QListWidget::item:selected {
                background-color: #3A3A3A;
            }
            QListWidget::item:hover {
                background-color: #353535;
            }
        """)
        left_layout.addWidget(self.production_plans_list)

        # دکمه‌های عملیات روی برنامه
        plan_btn_layout = QtWidgets.QHBoxLayout()
        plan_btn_layout.setSpacing(5)

        self.edit_production_btn = QtWidgets.QToolButton()
        self.edit_production_btn.setIcon(qta.icon('fa5s.edit', color='#C8C8C8'))
        self.edit_production_btn.setIconSize(QtCore.QSize(18, 18))
        self.edit_production_btn.setToolTip("ویرایش برنامه")
        self.edit_production_btn.clicked.connect(self.edit_production_plan)
        self.edit_production_btn.setEnabled(False)
        self.edit_production_btn.setFixedSize(32, 32)
        self.edit_production_btn.setStyleSheet(glass_btn_style)

        self.delete_production_btn = QtWidgets.QToolButton()
        self.delete_production_btn.setIcon(qta.icon('fa5s.trash-alt', color='#C8C8C8'))
        self.delete_production_btn.setIconSize(QtCore.QSize(18, 18))
        self.delete_production_btn.setToolTip("حذف برنامه")
        self.delete_production_btn.clicked.connect(self.delete_production_plan)
        self.delete_production_btn.setEnabled(False)
        self.delete_production_btn.setFixedSize(32, 32)
        self.delete_production_btn.setStyleSheet(glass_btn_style)

        plan_btn_layout.addWidget(self.edit_production_btn)
        plan_btn_layout.addWidget(self.delete_production_btn)
        plan_btn_layout.addStretch()
        left_layout.addLayout(plan_btn_layout)

        splitter.addWidget(left_widget)

        # سمت راست: جدول وظایف
        right_widget = QtWidgets.QWidget()
        right_layout = QtWidgets.QVBoxLayout(right_widget)
        right_layout.setContentsMargins(5, 0, 0, 0)

        self.production_plan_info = QtWidgets.QLabel("برنامه‌ای انتخاب نشده است")
        self.production_plan_info.setStyleSheet("color: #C8C8C8; font-size: 12px; padding: 8px; background-color: #252526; border-radius: 4px;")
        right_layout.addWidget(self.production_plan_info)

        task_toolbar = QtWidgets.QHBoxLayout()
        self.add_production_task_btn = QtWidgets.QToolButton()
        self.add_production_task_btn.setIcon(qta.icon('fa5s.plus', color='#C8C8C8'))
        self.add_production_task_btn.setIconSize(QtCore.QSize(16, 16))
        self.add_production_task_btn.setToolTip("افزودن وظیفه")
        self.add_production_task_btn.setStyleSheet(glass_btn_style)
        self.add_production_task_btn.clicked.connect(self.add_production_task)
        self.add_production_task_btn.setEnabled(False)

        task_toolbar.addWidget(self.add_production_task_btn)
        task_toolbar.addStretch()
        right_layout.addLayout(task_toolbar)

        self.production_tasks_table = QtWidgets.QTableWidget()
        self.production_tasks_table.setAlternatingRowColors(True)
        self.production_tasks_table.setMinimumHeight(300)
        self.production_tasks_table.setColumnCount(8)
        self.production_tasks_table.setHorizontalHeaderLabels(["شناسه", "وظیفه", "تاریخ", "زمان", "مدت", "مسئول", "اولویت", "وضعیت"])
        self.production_tasks_table.horizontalHeader().setStretchLastSection(True)
        self.production_tasks_table.setColumnWidth(0, 60)
        self.production_tasks_table.setColumnWidth(1, 220)
        self.production_tasks_table.setColumnWidth(2, 100)
        self.production_tasks_table.setColumnWidth(3, 80)
        self.production_tasks_table.setColumnWidth(4, 80)
        self.production_tasks_table.setColumnWidth(5, 120)
        self.production_tasks_table.setStyleSheet("""
            QTableWidget {
                border: 1px solid #3E3E42;
                border-radius: 4px;
                background-color: #2D2D30;
                alternate-background-color: #252526;
                gridline-color: #3E3E42;
            }
            QTableWidget::item {
                padding: 8px 5px;
            }
            QTableWidget::item:selected {
                background-color: #3A3A3A;
            }
            QTableWidget::item:hover {
                background-color: #353535;
            }
            QHeaderView::section {
                background-color: #252526;
                color: #C8C8C8;
                border: none;
                border-bottom: 1px solid #3E3E42;
                padding: 8px;
                font-weight: bold;
            }
        """)
        right_layout.addWidget(self.production_tasks_table)

        splitter.addWidget(right_widget)
        layout.addWidget(splitter, 1)

        return tab

    def create_maintenance_tab(self, glass_btn_style):
        """ایجاد تب برنامه نت (تعمیرات و نگهداری)"""
        tab = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout(tab)
        layout.setSpacing(10)

        # ========== نوار ابزار ==========
        toolbar = QtWidgets.QHBoxLayout()
        toolbar.setSpacing(10)

        toolbar.addWidget(QtWidgets.QLabel("نوع تجهیز:"))
        self.asset_type_combo = QtWidgets.QComboBox()
        self.asset_type_combo.setEditable(True)
        self.asset_type_combo.setInsertPolicy(QtWidgets.QComboBox.NoInsert)
        self.asset_type_combo.addItems(["همه تجهیزات", "mooring", "buoy", "anchor", "net", "cage", "collector"])
        self.asset_type_combo.setMinimumWidth(150)
        self.asset_type_combo.currentIndexChanged.connect(self.on_asset_type_changed)
        self.asset_type_combo.setStyleSheet("""
            QComboBox {
                background-color: #3C3C3C;
                color: #C8C8C8;
                border: 1px solid #3E3E42;
                border-radius: 4px;
                padding: 5px;
            }
            QComboBox:hover {
                border-color: #569CD6;
            }
        """)
        toolbar.addWidget(self.asset_type_combo)

        toolbar.addSpacing(20)

        self.new_maintenance_btn = QtWidgets.QToolButton()
        self.new_maintenance_btn.setIcon(qta.icon('fa5s.plus', color='#C8C8C8'))
        self.new_maintenance_btn.setIconSize(QtCore.QSize(18, 18))
        self.new_maintenance_btn.setToolTip("برنامه نت جدید")
        self.new_maintenance_btn.setStyleSheet(glass_btn_style)
        self.new_maintenance_btn.clicked.connect(self.create_new_maintenance_plan)
        toolbar.addWidget(self.new_maintenance_btn)

        self.refresh_maintenance_btn = QtWidgets.QToolButton()
        self.refresh_maintenance_btn.setIcon(qta.icon('fa5s.sync-alt', color='#C8C8C8'))
        self.refresh_maintenance_btn.setIconSize(QtCore.QSize(18, 18))
        self.refresh_maintenance_btn.setToolTip("به‌روزرسانی")
        self.refresh_maintenance_btn.setStyleSheet(glass_btn_style)
        self.refresh_maintenance_btn.clicked.connect(self.refresh_maintenance_data)
        toolbar.addWidget(self.refresh_maintenance_btn)

        toolbar.addStretch()
        layout.addLayout(toolbar)

        # ========== بخش اصلی ==========
        splitter = QtWidgets.QSplitter(QtCore.Qt.Horizontal)
        splitter.setSizes([300, 700])

        # سمت چپ: لیست برنامه‌های نت
        left_widget = QtWidgets.QWidget()
        left_layout = QtWidgets.QVBoxLayout(left_widget)
        left_layout.setContentsMargins(0, 0, 5, 0)

        left_label = QtWidgets.QLabel("📌 برنامه‌های تعمیرات و نگهداری")
        left_label.setStyleSheet("color: #C8C8C8; font-weight: bold; padding: 5px;")
        left_layout.addWidget(left_label)

        self.maintenance_plans_list = QtWidgets.QListWidget()
        self.maintenance_plans_list.setMinimumHeight(200)
        self.maintenance_plans_list.itemClicked.connect(self.on_maintenance_plan_selected)
        self.maintenance_plans_list.setStyleSheet("""
            QListWidget {
                background-color: #2D2D30;
                border: 1px solid #3E3E42;
                border-radius: 4px;
                color: #C8C8C8;
                padding: 5px;
            }
            QListWidget::item {
                padding: 8px;
                border-bottom: 1px solid #3E3E42;
            }
            QListWidget::item:selected {
                background-color: #3A3A3A;
            }
            QListWidget::item:hover {
                background-color: #353535;
            }
        """)
        left_layout.addWidget(self.maintenance_plans_list)

        # دکمه‌های عملیات روی برنامه نت
        plan_btn_layout = QtWidgets.QHBoxLayout()
        plan_btn_layout.setSpacing(5)

        self.edit_maintenance_btn = QtWidgets.QToolButton()
        self.edit_maintenance_btn.setIcon(qta.icon('fa5s.edit', color='#C8C8C8'))
        self.edit_maintenance_btn.setIconSize(QtCore.QSize(18, 18))
        self.edit_maintenance_btn.setToolTip("ویرایش برنامه نت")
        self.edit_maintenance_btn.clicked.connect(self.edit_maintenance_plan)
        self.edit_maintenance_btn.setEnabled(False)
        self.edit_maintenance_btn.setFixedSize(32, 32)
        self.edit_maintenance_btn.setStyleSheet(glass_btn_style)

        self.delete_maintenance_btn = QtWidgets.QToolButton()
        self.delete_maintenance_btn.setIcon(qta.icon('fa5s.trash-alt', color='#C8C8C8'))
        self.delete_maintenance_btn.setIconSize(QtCore.QSize(18, 18))
        self.delete_maintenance_btn.setToolTip("حذف برنامه نت")
        self.delete_maintenance_btn.clicked.connect(self.delete_maintenance_plan)
        self.delete_maintenance_btn.setEnabled(False)
        self.delete_maintenance_btn.setFixedSize(32, 32)
        self.delete_maintenance_btn.setStyleSheet(glass_btn_style)

        plan_btn_layout.addWidget(self.edit_maintenance_btn)
        plan_btn_layout.addWidget(self.delete_maintenance_btn)
        plan_btn_layout.addStretch()
        left_layout.addLayout(plan_btn_layout)

        splitter.addWidget(left_widget)

        # سمت راست
        right_widget = QtWidgets.QWidget()
        right_layout = QtWidgets.QVBoxLayout(right_widget)
        right_layout.setContentsMargins(5, 0, 0, 0)

        self.maintenance_plan_info = QtWidgets.QLabel("برنامه‌ای انتخاب نشده است")
        self.maintenance_plan_info.setStyleSheet("color: #C8C8C8; font-size: 12px; padding: 8px; background-color: #252526; border-radius: 4px;")
        right_layout.addWidget(self.maintenance_plan_info)

        task_toolbar = QtWidgets.QHBoxLayout()
        self.add_maintenance_task_btn = QtWidgets.QToolButton()
        self.add_maintenance_task_btn.setIcon(qta.icon('fa5s.plus', color='#C8C8C8'))
        self.add_maintenance_task_btn.setIconSize(QtCore.QSize(16, 16))
        self.add_maintenance_task_btn.setToolTip("افزودن وظیفه")
        self.add_maintenance_task_btn.setStyleSheet(glass_btn_style)
        self.add_maintenance_task_btn.clicked.connect(self.add_maintenance_task)
        self.add_maintenance_task_btn.setEnabled(False)

        task_toolbar.addWidget(self.add_maintenance_task_btn)
        task_toolbar.addStretch()
        right_layout.addLayout(task_toolbar)

        self.maintenance_tasks_table = QtWidgets.QTableWidget()
        self.maintenance_tasks_table.setAlternatingRowColors(True)
        self.maintenance_tasks_table.setMinimumHeight(300)
        self.maintenance_tasks_table.setColumnCount(8)
        self.maintenance_tasks_table.setHorizontalHeaderLabels(["شناسه", "وظیفه", "تاریخ", "زمان", "مدت", "تیم مسئول", "اولویت", "وضعیت"])
        self.maintenance_tasks_table.horizontalHeader().setStretchLastSection(True)
        self.maintenance_tasks_table.setColumnWidth(0, 60)
        self.maintenance_tasks_table.setColumnWidth(1, 220)
        self.maintenance_tasks_table.setColumnWidth(2, 100)
        self.maintenance_tasks_table.setColumnWidth(3, 80)
        self.maintenance_tasks_table.setColumnWidth(4, 80)
        self.maintenance_tasks_table.setColumnWidth(5, 120)
        self.maintenance_tasks_table.setStyleSheet("""
            QTableWidget {
                border: 1px solid #3E3E42;
                border-radius: 4px;
                background-color: #2D2D30;
                alternate-background-color: #252526;
                gridline-color: #3E3E42;
            }
            QTableWidget::item {
                padding: 8px 5px;
            }
            QTableWidget::item:selected {
                background-color: #3A3A3A;
            }
            QTableWidget::item:hover {
                background-color: #353535;
            }
            QHeaderView::section {
                background-color: #252526;
                color: #C8C8C8;
                border: none;
                border-bottom: 1px solid #3E3E42;
                padding: 8px;
                font-weight: bold;
            }
        """)
        right_layout.addWidget(self.maintenance_tasks_table)

        splitter.addWidget(right_widget)
        layout.addWidget(splitter, 1)

        return tab

    def setup_status_bar(self, parent_layout):
        """تنظیم نوار وضعیت پایینی"""
        status_frame = QtWidgets.QFrame()
        status_frame.setStyleSheet("""
            QFrame {
                background-color: #252526;
                border-radius: 8px;
                padding: 8px;
                margin-top: 5px;
            }
        """)
        status_layout = QtWidgets.QHBoxLayout(status_frame)
        status_layout.setSpacing(20)

        self.total_tasks_label = QtWidgets.QLabel("📋 کل وظایف: 0")
        self.completed_tasks_label = QtWidgets.QLabel("✅ انجام شده: 0")
        self.pending_tasks_label = QtWidgets.QLabel("⏳ در انتظار: 0")
        self.delayed_tasks_label = QtWidgets.QLabel("⚠️ تاخیر: 0")

        for label in [self.total_tasks_label, self.completed_tasks_label, self.pending_tasks_label, self.delayed_tasks_label]:
            label.setStyleSheet("color: #C8C8C8; font-size: 12px; padding: 5px;")
            status_layout.addWidget(label)

        status_layout.addStretch()
        parent_layout.addWidget(status_frame)

    # ==================== توابع برنامه پرورش ====================

    def load_data(self):
        """بارگذاری داده‌ها"""
        self.load_cages()
        self.load_production_plans()
        self.load_maintenance_plans()

    def refresh_production_data(self):
        """به‌روزرسانی داده‌های تب پرورش"""
        self.load_production_plans()
        if self.current_plan_id:
            self.load_production_tasks()
        QtWidgets.QMessageBox.information(self, "به‌روزرسانی", "داده‌های برنامه پرورش به‌روزرسانی شد")

    def refresh_maintenance_data(self):
        """به‌روزرسانی داده‌های تب نت"""
        self.load_maintenance_plans()
        if self.current_maintenance_plan_id:
            self.load_maintenance_tasks()
        QtWidgets.QMessageBox.information(self, "به‌روزرسانی", "داده‌های برنامه نت به‌روزرسانی شد")

    def load_cages(self):
        """بارگذاری لیست قفس‌ها"""
        self.cage_combo.clear()
        cages = self.db.fetch_all("SELECT id FROM cages ORDER BY id")
        if cages:
            for cage in cages:
                self.cage_combo.addItem(cage['id'], cage['id'])
            if self.cage_combo.count() > 0:
                self.cage_combo.setCurrentIndex(0)
        else:
            self.cage_combo.addItem("--- هیچ قفسی موجود نیست ---")

    def on_cage_changed(self):
        """تغییر قفس"""
        self.load_production_plans()
        self.current_plan_id = None
        self.production_plan_info.setText("برنامه‌ای انتخاب نشده است")
        self.production_tasks_table.setRowCount(0)
        self.submit_production_btn.setEnabled(False)
        self.add_production_task_btn.setEnabled(False)
        self.edit_production_btn.setEnabled(False)
        self.delete_production_btn.setEnabled(False)

    def load_production_plans(self):
        """بارگذاری لیست برنامه‌های پرورش"""
        self.production_plans_list.clear()
        cage_id = self.cage_combo.currentData()
        if not cage_id or cage_id == "--- هیچ قفسی موجود نیست ---":
            return

        plans = self.db.get_all_production_plans(cage_id)

        status_icons = {'draft': '📝', 'submitted': '📤', 'approved': '✅', 'in_progress': '⚙️', 'completed': '✔️', 'cancelled': '❌'}

        for plan in plans:
            icon = status_icons.get(plan['plan_status'], '📝')
            item_text = f"{icon} {plan['plan_title']} ({plan['start_date']} تا {plan['end_date']})"
            item = QtWidgets.QListWidgetItem(item_text)
            item.setData(QtCore.Qt.UserRole, plan['id'])
            self.production_plans_list.addItem(item)

    def on_production_plan_selected(self, item):
        """انتخاب برنامه پرورش"""
        self.current_plan_id = item.data(QtCore.Qt.UserRole)
        self.load_production_plan_info()
        self.load_production_tasks()
        self.submit_production_btn.setEnabled(True)
        self.add_production_task_btn.setEnabled(True)
        self.edit_production_btn.setEnabled(True)
        self.delete_production_btn.setEnabled(True)

    def load_production_plan_info(self):
        """بارگذاری اطلاعات برنامه پرورش"""
        if not self.current_plan_id:
            return
        plan = self.db.get_production_plan_by_id(self.current_plan_id)
        if plan:
            status_names = {'draft': 'پیش‌نویس', 'submitted': 'ارسال شده', 'approved': 'تایید شده', 'in_progress': 'در حال اجرا', 'completed': 'تکمیل شده', 'cancelled': 'لغو شده'}
            self.production_plan_info.setText(f"📋 {plan['plan_title']} | {plan['start_date']} تا {plan['end_date']} | وضعیت: {status_names.get(plan['plan_status'], plan['plan_status'])}")

    def load_production_tasks(self):
        """بارگذاری وظایف برنامه پرورش"""
        if not self.current_plan_id:
            return
        tasks = self.db.get_plan_tasks(self.current_plan_id)
        self.production_tasks_table.setRowCount(len(tasks))
        status_icons = {'pending': '⏳ در انتظار', 'in_progress': '🔄 در حال انجام', 'completed': '✅ انجام شده', 'delayed': '⚠️ تاخیر', 'cancelled': '❌ لغو شده'}
        priority_colors = {1: '#F48771', 2: '#DCDCAA', 3: '#C8C8C8'}

        for i, task in enumerate(tasks):
            self.production_tasks_table.setItem(i, 0, QtWidgets.QTableWidgetItem(str(task['id'])))
            self.production_tasks_table.setItem(i, 1, QtWidgets.QTableWidgetItem(task['task_title']))
            self.production_tasks_table.setItem(i, 2, QtWidgets.QTableWidgetItem(str(task['scheduled_date'])))
            self.production_tasks_table.setItem(i, 3, QtWidgets.QTableWidgetItem(str(task['scheduled_start_time'])[:5] if task['scheduled_start_time'] else "-"))
            self.production_tasks_table.setItem(i, 4, QtWidgets.QTableWidgetItem(str(task['estimated_duration_minutes'])))
            self.production_tasks_table.setItem(i, 5, QtWidgets.QTableWidgetItem(task['assigned_to_unit'] or "-"))
            priority_item = QtWidgets.QTableWidgetItem(str(task['priority_level']))
            priority_item.setForeground(QtGui.QColor(priority_colors.get(task['priority_level'], '#C8C8C8')))
            self.production_tasks_table.setItem(i, 6, priority_item)
            status_item = QtWidgets.QTableWidgetItem(status_icons.get(task['execution_status'], '⏳ در انتظار'))
            if task['execution_status'] == 'completed':
                status_item.setForeground(QtGui.QColor('#4EC9B0'))
            elif task['execution_status'] == 'delayed':
                status_item.setForeground(QtGui.QColor('#F48771'))
            self.production_tasks_table.setItem(i, 7, status_item)

        self.update_task_stats(tasks)

    def update_task_stats(self, tasks):
        """به‌روزرسانی آمار"""
        total = len(tasks)
        completed = sum(1 for t in tasks if t['execution_status'] == 'completed')
        pending = sum(1 for t in tasks if t['execution_status'] == 'pending')
        delayed = sum(1 for t in tasks if t['execution_status'] == 'delayed')
        self.total_tasks_label.setText(f"📋 کل وظایف: {total}")
        self.completed_tasks_label.setText(f"✅ انجام شده: {completed}")
        self.pending_tasks_label.setText(f"⏳ در انتظار: {pending}")
        self.delayed_tasks_label.setText(f"⚠️ تاخیر: {delayed}")

    def create_new_production_plan(self):
        """ایجاد برنامه پرورش جدید"""
        cage_id = self.cage_combo.currentData()
        if not cage_id or cage_id == "--- هیچ قفسی موجود نیست ---":
            QtWidgets.QMessageBox.warning(self, "خطا", "لطفاً ابتدا یک قفس را انتخاب کنید")
            return
        dialog = PlanDialog(self, cage_id)
        if dialog.exec_():
            self.load_production_plans()
            QtWidgets.QMessageBox.information(self, "موفق", "برنامه پرورش جدید با موفقیت ایجاد شد")

    def edit_production_plan(self):
        """ویرایش برنامه پرورش"""
        if not self.current_plan_id:
            return
        plan = self.db.get_production_plan_by_id(self.current_plan_id)
        if not plan:
            return
        if plan['plan_status'] not in ['draft', 'cancelled']:
            QtWidgets.QMessageBox.warning(self, "خطا", "فقط برنامه‌های در وضعیت پیش‌نویس یا لغو شده قابل ویرایش هستند")
            return
        dialog = PlanDialog(self, plan['cage_id'], plan)
        if dialog.exec_():
            self.load_production_plans()
            self.load_production_plan_info()
            self.load_production_tasks()

    def delete_production_plan(self):
        """حذف برنامه پرورش"""
        if not self.current_plan_id:
            return
        reply = QtWidgets.QMessageBox.question(self, "تأیید حذف", "آیا از حذف این برنامه و تمام وظایف آن مطمئن هستید؟", QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)
        if reply == QtWidgets.QMessageBox.Yes:
            self.db.delete_production_plan(self.current_plan_id)
            self.current_plan_id = None
            self.load_production_plans()
            self.production_tasks_table.setRowCount(0)
            self.production_plan_info.setText("برنامه‌ای انتخاب نشده است")
            self.submit_production_btn.setEnabled(False)
            self.add_production_task_btn.setEnabled(False)
            self.edit_production_btn.setEnabled(False)
            self.delete_production_btn.setEnabled(False)
            QtWidgets.QMessageBox.information(self, "موفق", "برنامه با موفقیت حذف شد")

    def submit_production_plan(self):
        """ارسال برنامه پرورش"""
        if not self.current_plan_id:
            return
        plan = self.db.get_production_plan_by_id(self.current_plan_id)
        if plan['plan_status'] != 'draft':
            QtWidgets.QMessageBox.warning(self, "خطا", "فقط برنامه‌های در وضعیت پیش‌نویس قابل ارسال هستند")
            return
        tasks = self.db.get_plan_tasks(self.current_plan_id)
        if len(tasks) == 0:
            QtWidgets.QMessageBox.warning(self, "خطا", "برنامه بدون وظیفه قابل ارسال نیست")
            return
        reply = QtWidgets.QMessageBox.question(self, "تأیید ارسال", "آیا از ارسال این برنامه به واحدها مطمئن هستید؟", QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)
        if reply == QtWidgets.QMessageBox.Yes:
            self.db.update_plan_status(self.current_plan_id, 'submitted')
            self.load_production_plan_info()
            self.load_production_plans()
            QtWidgets.QMessageBox.information(self, "موفق", "برنامه با موفقیت ارسال شد")

    def add_production_task(self):
        """افزودن وظیفه به برنامه پرورش"""
        if not self.current_plan_id:
            QtWidgets.QMessageBox.warning(self, "خطا", "لطفاً ابتدا یک برنامه را انتخاب کنید")
            return
        dialog = TaskDialog(self, self.current_plan_id, is_maintenance=False)
        if dialog.exec_():
            self.load_production_tasks()
            QtWidgets.QMessageBox.information(self, "موفق", "وظیفه با موفقیت اضافه شد")

    # ==================== توابع برنامه نت ====================

    def on_asset_type_changed(self):
        """تغییر نوع تجهیز"""
        self.load_maintenance_plans()
        self.current_maintenance_plan_id = None
        self.maintenance_plan_info.setText("برنامه‌ای انتخاب نشده است")
        self.maintenance_tasks_table.setRowCount(0)
        self.add_maintenance_task_btn.setEnabled(False)
        self.edit_maintenance_btn.setEnabled(False)
        self.delete_maintenance_btn.setEnabled(False)

    def load_maintenance_plans(self):
        """بارگذاری لیست برنامه‌های نت"""
        self.maintenance_plans_list.clear()
        
        asset_type = self.asset_type_combo.currentText()
        if asset_type == "همه تجهیزات":
            asset_type = None
        
        plans = self.db.get_maintenance_plans(asset_type)
        
        status_icons = {'draft': '📝', 'submitted': '📤', 'approved': '✅', 'in_progress': '⚙️', 'completed': '✔️', 'cancelled': '❌'}
        
        for plan in plans:
            icon = status_icons.get(plan['plan_status'], '📝')
            asset_name = plan['asset_type']
            item_text = f"{icon} {plan['plan_title']} ({asset_name}) - {plan['start_date']} تا {plan['end_date']}"
            item = QtWidgets.QListWidgetItem(item_text)
            item.setData(QtCore.Qt.UserRole, plan['id'])
            self.maintenance_plans_list.addItem(item)
        
        if len(plans) == 0:
            self.maintenance_plans_list.addItem("--- هیچ برنامه‌ای وجود ندارد ---")

    def on_maintenance_plan_selected(self, item):
        """انتخاب برنامه نت"""
        self.current_maintenance_plan_id = item.data(QtCore.Qt.UserRole)
        self.load_maintenance_plan_info()
        self.load_maintenance_tasks()
        self.add_maintenance_task_btn.setEnabled(True)
        self.edit_maintenance_btn.setEnabled(True)
        self.delete_maintenance_btn.setEnabled(True)

    def load_maintenance_plan_info(self):
        """بارگذاری اطلاعات برنامه نت"""
        if not self.current_maintenance_plan_id:
            return
        plan = self.db.fetch_one("SELECT * FROM maintenance_plans WHERE id = %s", (self.current_maintenance_plan_id,))
        if plan:
            status_names = {'draft': 'پیش‌نویس', 'submitted': 'ارسال شده', 'approved': 'تایید شده', 'in_progress': 'در حال اجرا', 'completed': 'تکمیل شده', 'cancelled': 'لغو شده'}
            self.maintenance_plan_info.setText(f"🛠️ {plan['plan_title']} | {plan['start_date']} تا {plan['end_date']} | وضعیت: {status_names.get(plan['plan_status'], plan['plan_status'])}")

    def load_maintenance_tasks(self):
        """بارگذاری وظایف برنامه نت"""
        if not self.current_maintenance_plan_id:
            return
        tasks = self.db.get_maintenance_tasks(self.current_maintenance_plan_id)
        self.maintenance_tasks_table.setRowCount(len(tasks))
        status_icons = {'pending': '⏳ در انتظار', 'in_progress': '🔄 در حال انجام', 'completed': '✅ انجام شده', 'delayed': '⚠️ تاخیر', 'cancelled': '❌ لغو شده'}
        priority_colors = {1: '#F48771', 2: '#DCDCAA', 3: '#C8C8C8'}

        for i, task in enumerate(tasks):
            self.maintenance_tasks_table.setItem(i, 0, QtWidgets.QTableWidgetItem(str(task['id'])))
            self.maintenance_tasks_table.setItem(i, 1, QtWidgets.QTableWidgetItem(task['task_title']))
            self.maintenance_tasks_table.setItem(i, 2, QtWidgets.QTableWidgetItem(str(task['scheduled_date'])))
            self.maintenance_tasks_table.setItem(i, 3, QtWidgets.QTableWidgetItem(str(task['scheduled_start_time'])[:5] if task['scheduled_start_time'] else "-"))
            self.maintenance_tasks_table.setItem(i, 4, QtWidgets.QTableWidgetItem(str(task['estimated_duration_minutes'])))
            self.maintenance_tasks_table.setItem(i, 5, QtWidgets.QTableWidgetItem(task['assigned_to_team'] or "-"))
            priority_item = QtWidgets.QTableWidgetItem(str(task['priority_level']))
            priority_item.setForeground(QtGui.QColor(priority_colors.get(task['priority_level'], '#C8C8C8')))
            self.maintenance_tasks_table.setItem(i, 6, priority_item)
            status_item = QtWidgets.QTableWidgetItem(status_icons.get(task['execution_status'], '⏳ در انتظار'))
            if task['execution_status'] == 'completed':
                status_item.setForeground(QtGui.QColor('#4EC9B0'))
            elif task['execution_status'] == 'delayed':
                status_item.setForeground(QtGui.QColor('#F48771'))
            self.maintenance_tasks_table.setItem(i, 7, status_item)

    def create_new_maintenance_plan(self):
        """ایجاد برنامه نت جدید"""
        dialog = MaintenancePlanDialog(self)
        if dialog.exec_():
            self.load_maintenance_plans()
            QtWidgets.QMessageBox.information(self, "موفق", "برنامه نت جدید با موفقیت ایجاد شد")

    def edit_maintenance_plan(self):
        """ویرایش برنامه نت"""
        if not self.current_maintenance_plan_id:
            return
        plan = self.db.fetch_one("SELECT * FROM maintenance_plans WHERE id = %s", (self.current_maintenance_plan_id,))
        if not plan:
            return
        if plan['plan_status'] not in ['draft', 'cancelled']:
            QtWidgets.QMessageBox.warning(self, "خطا", "فقط برنامه‌های در وضعیت پیش‌نویس یا لغو شده قابل ویرایش هستند")
            return
        dialog = MaintenancePlanDialog(self, plan)
        if dialog.exec_():
            self.load_maintenance_plans()
            self.load_maintenance_plan_info()
            self.load_maintenance_tasks()

    def delete_maintenance_plan(self):
        """حذف برنامه نت"""
        if not self.current_maintenance_plan_id:
            return
        reply = QtWidgets.QMessageBox.question(self, "تأیید حذف", "آیا از حذف این برنامه نت و تمام وظایف آن مطمئن هستید؟", QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)
        if reply == QtWidgets.QMessageBox.Yes:
            self.db.delete_maintenance_plan(self.current_maintenance_plan_id)
            self.current_maintenance_plan_id = None
            self.load_maintenance_plans()
            self.maintenance_tasks_table.setRowCount(0)
            self.maintenance_plan_info.setText("برنامه‌ای انتخاب نشده است")
            self.add_maintenance_task_btn.setEnabled(False)
            self.edit_maintenance_btn.setEnabled(False)
            self.delete_maintenance_btn.setEnabled(False)
            QtWidgets.QMessageBox.information(self, "موفق", "برنامه نت با موفقیت حذف شد")

    def add_maintenance_task(self):
        """افزودن وظیفه به برنامه نت"""
        if not self.current_maintenance_plan_id:
            QtWidgets.QMessageBox.warning(self, "خطا", "لطفاً ابتدا یک برنامه نت را انتخاب کنید")
            return
        dialog = MaintenanceTaskDialog(self, self.current_maintenance_plan_id)
        if dialog.exec_():
            self.load_maintenance_tasks()
            QtWidgets.QMessageBox.information(self, "موفق", "وظیفه با موفقیت اضافه شد")


class PlanDialog(QtWidgets.QDialog):
    """دیالوگ ایجاد/ویرایش برنامه پرورش"""

    def __init__(self, parent=None, cage_id=None, plan=None):
        super().__init__(parent)
        self.db = DatabaseHandler()
        self.cage_id = cage_id
        self.plan = plan
        self.setWindowTitle("ایجاد برنامه پرورش جدید" if not plan else "ویرایش برنامه پرورش")
        self.setModal(True)
        self.resize(500, 450)
        self.setup_ui()
        if plan:
            self.load_plan_data()

    def setup_ui(self):
        layout = QtWidgets.QFormLayout(self)
        layout.setLabelAlignment(QtCore.Qt.AlignRight)
        layout.setSpacing(12)
        layout.setContentsMargins(20, 20, 20, 20)

        self.title_edit = QtWidgets.QLineEdit()
        self.title_edit.setPlaceholderText("مثال: برنامه پرورش خرداد ۱۴۰۵")
        self.title_edit.setMinimumHeight(30)
        layout.addRow("عنوان برنامه:", self.title_edit)

        self.type_combo = QtWidgets.QComboBox()
        self.type_combo.addItems(["weekly", "monthly"])
        layout.addRow("نوع برنامه:", self.type_combo)

        self.start_date = JalaliDateEdit()
        layout.addRow("تاریخ شروع:", self.start_date)

        self.end_date = JalaliDateEdit()
        layout.addRow("تاریخ پایان:", self.end_date)

        self.notes = QtWidgets.QTextEdit()
        self.notes.setMaximumHeight(100)
        layout.addRow("یادداشت:", self.notes)

        btn_layout = QtWidgets.QHBoxLayout()
        ok_btn = QtWidgets.QPushButton("ذخیره")
        ok_btn.setMinimumHeight(35)
        ok_btn.setStyleSheet("background-color: rgba(60, 60, 65, 180); color: #C8C8C8; border-radius: 4px; padding: 6px 20px;")
        cancel_btn = QtWidgets.QPushButton("انصراف")
        cancel_btn.setMinimumHeight(35)
        cancel_btn.setStyleSheet("background-color: rgba(60, 60, 65, 180); color: #C8C8C8; border-radius: 4px; padding: 6px 20px;")
        cancel_btn.clicked.connect(self.reject)
        ok_btn.clicked.connect(self.accept)
        btn_layout.addWidget(ok_btn)
        btn_layout.addWidget(cancel_btn)
        layout.addRow(btn_layout)

    def load_plan_data(self):
        self.title_edit.setText(self.plan['plan_title'])
        idx = self.type_combo.findText(self.plan['plan_type'])
        if idx >= 0:
            self.type_combo.setCurrentIndex(idx)
        self.start_date.set_jalali_date(self.plan['start_date'])
        self.end_date.set_jalali_date(self.plan['end_date'])
        self.notes.setText(self.plan['notes'] or "")

    def accept(self):
        if not self.title_edit.text().strip():
            QtWidgets.QMessageBox.warning(self, "خطا", "لطفاً عنوان برنامه را وارد کنید")
            return
        if self.start_date.get_jalali_date() > self.end_date.get_jalali_date():
            QtWidgets.QMessageBox.warning(self, "خطا", "تاریخ شروع نباید از تاریخ پایان بزرگتر باشد")
            return
        if self.plan:
            self.db.update_production_plan(
                self.plan['id'],
                self.title_edit.text().strip(),
                self.type_combo.currentText(),
                self.start_date.get_jalali_date(),
                self.end_date.get_jalali_date(),
                self.notes.toPlainText()
            )
        else:
            self.db.create_production_plan(
                self.title_edit.text().strip(),
                self.type_combo.currentText(),
                self.start_date.get_jalali_date(),
                self.end_date.get_jalali_date(),
                self.cage_id,
                1,
                self.notes.toPlainText()
            )
        super().accept()


class MaintenancePlanDialog(QtWidgets.QDialog):
    """دیالوگ ایجاد برنامه نت جدید"""

    def __init__(self, parent=None, plan=None):
        super().__init__(parent)
        self.db = DatabaseHandler()
        self.plan = plan
        self.setWindowTitle("ایجاد برنامه نت جدید" if not plan else "ویرایش برنامه نت")
        self.setModal(True)
        self.resize(500, 550)
        self.setup_ui()
        if plan:
            self.load_plan_data()

    def setup_ui(self):
        layout = QtWidgets.QFormLayout(self)
        layout.setLabelAlignment(QtCore.Qt.AlignRight)
        layout.setSpacing(12)
        layout.setContentsMargins(20, 20, 20, 20)

        self.title_edit = QtWidgets.QLineEdit()
        self.title_edit.setPlaceholderText("مثال: برنامه شستشوی دوره‌ای تورها")
        self.title_edit.setMinimumHeight(30)
        layout.addRow("عنوان برنامه:", self.title_edit)

        self.type_combo = QtWidgets.QComboBox()
        self.type_combo.addItems(["weekly", "monthly", "quarterly", "yearly"])
        layout.addRow("نوع برنامه:", self.type_combo)

        self.asset_type_combo = QtWidgets.QComboBox()
        self.asset_type_combo.setEditable(True)
        self.asset_type_combo.addItems(["mooring", "buoy", "anchor", "net", "cage", "collector", "all"])
        layout.addRow("نوع تجهیز:", self.asset_type_combo)

        self.asset_id_edit = QtWidgets.QLineEdit()
        self.asset_id_edit.setPlaceholderText("اختیاری - شناسه خاص تجهیز (مثال: MOR-001)")
        layout.addRow("شناسه تجهیز (اختیاری):", self.asset_id_edit)

        self.start_date = JalaliDateEdit()
        layout.addRow("تاریخ شروع:", self.start_date)

        self.end_date = JalaliDateEdit()
        layout.addRow("تاریخ پایان:", self.end_date)

        self.notes = QtWidgets.QTextEdit()
        self.notes.setMaximumHeight(100)
        layout.addRow("یادداشت:", self.notes)

        btn_layout = QtWidgets.QHBoxLayout()
        ok_btn = QtWidgets.QPushButton("ذخیره")
        ok_btn.setMinimumHeight(35)
        ok_btn.setStyleSheet("background-color: rgba(60, 60, 65, 180); color: #C8C8C8; border-radius: 4px; padding: 6px 20px;")
        cancel_btn = QtWidgets.QPushButton("انصراف")
        cancel_btn.setMinimumHeight(35)
        cancel_btn.setStyleSheet("background-color: rgba(60, 60, 65, 180); color: #C8C8C8; border-radius: 4px; padding: 6px 20px;")
        cancel_btn.clicked.connect(self.reject)
        ok_btn.clicked.connect(self.accept)
        btn_layout.addWidget(ok_btn)
        btn_layout.addWidget(cancel_btn)
        layout.addRow(btn_layout)

    def load_plan_data(self):
        self.title_edit.setText(self.plan['plan_title'])
        idx = self.type_combo.findText(self.plan['plan_type'])
        if idx >= 0:
            self.type_combo.setCurrentIndex(idx)
        idx = self.asset_type_combo.findText(self.plan['asset_type'])
        if idx >= 0:
            self.asset_type_combo.setCurrentIndex(idx)
        self.asset_id_edit.setText(self.plan['asset_id'] or "")
        self.start_date.set_jalali_date(self.plan['start_date'])
        self.end_date.set_jalali_date(self.plan['end_date'])
        self.notes.setText(self.plan['notes'] or "")

    def accept(self):
        if not self.title_edit.text().strip():
            QtWidgets.QMessageBox.warning(self, "خطا", "لطفاً عنوان برنامه را وارد کنید")
            return
        if self.start_date.get_jalali_date() > self.end_date.get_jalali_date():
            QtWidgets.QMessageBox.warning(self, "خطا", "تاریخ شروع نباید از تاریخ پایان بزرگتر باشد")
            return
        
        asset_id = self.asset_id_edit.text().strip() if self.asset_id_edit.text().strip() else None
        asset_type = self.asset_type_combo.currentText()
        
        if self.plan:
            self.db.update_maintenance_plan(
                self.plan['id'],
                self.title_edit.text().strip(),
                self.type_combo.currentText(),
                self.start_date.get_jalali_date(),
                self.end_date.get_jalali_date(),
                asset_type,
                asset_id,
                self.notes.toPlainText()
            )
        else:
            self.db.create_maintenance_plan(
                self.title_edit.text().strip(),
                self.type_combo.currentText(),
                self.start_date.get_jalali_date(),
                self.end_date.get_jalali_date(),
                asset_type,
                asset_id,
                self.notes.toPlainText()
            )
        super().accept()


class TaskDialog(QtWidgets.QDialog):
    """دیالوگ افزودن/ویرایش وظیفه برای برنامه پرورش"""

    def __init__(self, parent=None, plan_id=None, task_id=None, is_maintenance=False):
        super().__init__(parent)
        self.db = DatabaseHandler()
        self.plan_id = plan_id
        self.task_id = task_id
        self.is_maintenance = is_maintenance
        self.setWindowTitle("افزودن وظیفه جدید" if not task_id else "ویرایش وظیفه")
        self.setModal(True)
        self.resize(550, 600)
        self.setup_ui()
        if task_id:
            self.load_task_data()

    def setup_ui(self):
        layout = QtWidgets.QFormLayout(self)
        layout.setLabelAlignment(QtCore.Qt.AlignRight)
        layout.setSpacing(12)
        layout.setContentsMargins(20, 20, 20, 20)

        # انتخاب از الگوهای تکراری
        self.template_combo = QtWidgets.QComboBox()
        self.template_combo.addItem("--- انتخاب از الگوها (اختیاری) ---", None)
        templates = self.db.get_all_task_templates(only_active=True)
        for t in templates:
            self.template_combo.addItem(f"{t['title']} ({t['category']})", t['id'])
        self.template_combo.currentIndexChanged.connect(self.on_template_selected)
        layout.addRow("📚 الگوهای تکراری:", self.template_combo)

        # دکمه مدیریت الگوها
        manage_templates_btn = QtWidgets.QPushButton("✏️ مدیریت الگوها")
        manage_templates_btn.setStyleSheet("background-color: rgba(60, 60, 65, 180); color: #C8C8C8; border-radius: 4px; padding: 4px 8px;")
        manage_templates_btn.clicked.connect(self.manage_templates)
        layout.addRow("", manage_templates_btn)

        line = QtWidgets.QFrame()
        line.setFrameShape(QtWidgets.QFrame.HLine)
        line.setStyleSheet("background-color: #3E3E42; margin: 5px 0;")
        layout.addRow(line)

        self.title_edit = QtWidgets.QLineEdit()
        self.title_edit.setPlaceholderText("مثال: شستشوی تور قفس")
        self.title_edit.setMinimumHeight(30)
        layout.addRow("عنوان وظیفه:", self.title_edit)

        self.desc_edit = QtWidgets.QTextEdit()
        self.desc_edit.setMaximumHeight(80)
        layout.addRow("توضیحات:", self.desc_edit)

        self.category_combo = QtWidgets.QComboBox()
        self.category_combo.addItems(["feeding", "cleaning", "inspection", "repair", "harvest", "water_quality", "other"])
        layout.addRow("دسته‌بندی:", self.category_combo)

        self.scheduled_date = JalaliDateEdit()
        layout.addRow("تاریخ انجام:", self.scheduled_date)

        self.start_time = QtWidgets.QTimeEdit()
        self.start_time.setTime(QtCore.QTime(8, 0))
        layout.addRow("ساعت شروع:", self.start_time)

        self.duration = QtWidgets.QSpinBox()
        self.duration.setRange(15, 1440)
        self.duration.setSuffix(" دقیقه")
        self.duration.setValue(60)
        layout.addRow("مدت زمان:", self.duration)

        # مسئول (با قابلیت انتخاب)
        self.responsible_combo = QtWidgets.QComboBox()
        self.responsible_combo.setEditable(True)
        self.responsible_combo.addItems(["واحد بهره برداری", "واحد فنی", "واحد تغذیه", "واحد تعمیرات", "واحد زیست‌توده"])
        layout.addRow("مسئول:", self.responsible_combo)

        self.priority = QtWidgets.QComboBox()
        self.priority.addItems(["1 - بالا", "2 - متوسط", "3 - پایین"])
        layout.addRow("اولویت:", self.priority)

        btn_layout = QtWidgets.QHBoxLayout()
        ok_btn = QtWidgets.QPushButton("ذخیره")
        ok_btn.setMinimumHeight(40)
        ok_btn.setStyleSheet("background-color: rgba(60, 60, 65, 180); color: #C8C8C8; border-radius: 4px; padding: 6px 20px;")
        cancel_btn = QtWidgets.QPushButton("انصراف")
        cancel_btn.setMinimumHeight(40)
        cancel_btn.setStyleSheet("background-color: rgba(60, 60, 65, 180); color: #C8C8C8; border-radius: 4px; padding: 6px 20px;")
        cancel_btn.clicked.connect(self.reject)
        ok_btn.clicked.connect(self.accept)
        btn_layout.addWidget(ok_btn)
        btn_layout.addWidget(cancel_btn)
        layout.addRow(btn_layout)

    def manage_templates(self):
        """مدیریت الگوهای وظایف"""
        dialog = TemplateManagerDialog(self)
        dialog.exec_()
        # به‌روزرسانی لیست الگوها
        self.template_combo.clear()
        self.template_combo.addItem("--- انتخاب از الگوها (اختیاری) ---", None)
        templates = self.db.get_all_task_templates(only_active=True)
        for t in templates:
            self.template_combo.addItem(f"{t['title']} ({t['category']})", t['id'])

    def on_template_selected(self, index):
        template_id = self.template_combo.currentData()
        if template_id:
            template = self.db.get_task_template_by_id(template_id)
            if template:
                self.title_edit.setText(template['title'])
                self.desc_edit.setText(template['description'] or "")
                idx = self.category_combo.findText(template['category'])
                if idx >= 0:
                    self.category_combo.setCurrentIndex(idx)
                self.duration.setValue(template['estimated_duration_minutes'])
                self.priority.setCurrentIndex(template['default_priority'] - 1)

    def load_task_data(self):
        if self.is_maintenance:
            tasks = self.db.get_maintenance_tasks(self.plan_id)
        else:
            tasks = self.db.get_plan_tasks(self.plan_id)
        task = None
        for t in tasks:
            if t['id'] == self.task_id:
                task = t
                break
        if task:
            self.title_edit.setText(task['task_title'])
            self.desc_edit.setText(task['task_description'] or "")
            idx = self.category_combo.findText(task['category'])
            if idx >= 0:
                self.category_combo.setCurrentIndex(idx)
            self.scheduled_date.set_jalali_date(str(task['scheduled_date']))
            if task['scheduled_start_time']:
                self.start_time.setTime(QtCore.QTime.fromString(str(task['scheduled_start_time'])[:5], "hh:mm"))
            self.duration.setValue(task['estimated_duration_minutes'])
            responsible = task.get('assigned_to_unit') or task.get('assigned_to_team') or ""
            idx = self.responsible_combo.findText(responsible)
            if idx >= 0:
                self.responsible_combo.setCurrentIndex(idx)
            else:
                self.responsible_combo.setEditText(responsible)
            self.priority.setCurrentIndex(task['priority_level'] - 1)

    def accept(self):
        if not self.title_edit.text().strip():
            QtWidgets.QMessageBox.warning(self, "خطا", "لطفاً عنوان وظیفه را وارد کنید")
            return
        if not self.responsible_combo.currentText().strip():
            QtWidgets.QMessageBox.warning(self, "خطا", "لطفاً مسئول را وارد کنید")
            return
        priority_map = {"1 - بالا": 1, "2 - متوسط": 2, "3 - پایین": 3}
        responsible = self.responsible_combo.currentText().strip()
        
        if self.task_id:
            if self.is_maintenance:
                self.db.execute_query("""
                    UPDATE maintenance_plan_tasks 
                    SET task_title = %s, task_description = %s, category = %s,
                        scheduled_date = %s, scheduled_start_time = %s, estimated_duration_minutes = %s,
                        assigned_to_team = %s, priority_level = %s
                    WHERE id = %s
                """, (self.title_edit.text().strip(), self.desc_edit.toPlainText(), self.category_combo.currentText(),
                      self.scheduled_date.get_jalali_date(), self.start_time.time().toString("hh:mm:ss"),
                      self.duration.value(), responsible, priority_map[self.priority.currentText()], self.task_id))
            else:
                self.db.update_plan_task(
                    self.task_id,
                    self.title_edit.text().strip(),
                    self.desc_edit.toPlainText(),
                    self.category_combo.currentText(),
                    self.scheduled_date.get_jalali_date(),
                    self.start_time.time().toString("hh:mm:ss"),
                    self.duration.value(),
                    None,
                    responsible,
                    priority_map[self.priority.currentText()]
                )
        else:
            if self.is_maintenance:
                self.db.add_maintenance_task(
                    self.plan_id,
                    self.template_combo.currentData(),
                    self.title_edit.text().strip(),
                    self.desc_edit.toPlainText(),
                    self.category_combo.currentText(),
                    self.scheduled_date.get_jalali_date(),
                    self.start_time.time().toString("hh:mm:ss"),
                    self.duration.value(),
                    responsible,
                    priority_map[self.priority.currentText()]
                )
            else:
                self.db.add_plan_task(
                    self.plan_id,
                    self.template_combo.currentData(),
                    self.title_edit.text().strip(),
                    self.desc_edit.toPlainText(),
                    self.category_combo.currentText(),
                    self.scheduled_date.get_jalali_date(),
                    self.start_time.time().toString("hh:mm:ss"),
                    self.duration.value(),
                    None,
                    responsible,
                    priority_map[self.priority.currentText()]
                )
        super().accept()


class MaintenanceTaskDialog(QtWidgets.QDialog):
    """دیالوگ افزودن/ویرایش وظیفه برای برنامه نت"""

    def __init__(self, parent=None, plan_id=None, task_id=None):
        super().__init__(parent)
        self.db = DatabaseHandler()
        self.plan_id = plan_id
        self.task_id = task_id
        self.setWindowTitle("افزودن وظیفه جدید" if not task_id else "ویرایش وظیفه")
        self.setModal(True)
        self.resize(550, 600)
        self.setup_ui()
        if task_id:
            self.load_task_data()

    def setup_ui(self):
        layout = QtWidgets.QFormLayout(self)
        layout.setLabelAlignment(QtCore.Qt.AlignRight)
        layout.setSpacing(12)
        layout.setContentsMargins(20, 20, 20, 20)

        self.template_combo = QtWidgets.QComboBox()
        self.template_combo.addItem("--- انتخاب از الگوها (اختیاری) ---", None)
        templates = self.db.get_all_task_templates(only_active=True)
        for t in templates:
            self.template_combo.addItem(f"{t['title']} ({t['category']})", t['id'])
        self.template_combo.currentIndexChanged.connect(self.on_template_selected)
        layout.addRow("📚 الگوهای تکراری:", self.template_combo)

        line = QtWidgets.QFrame()
        line.setFrameShape(QtWidgets.QFrame.HLine)
        line.setStyleSheet("background-color: #3E3E42; margin: 5px 0;")
        layout.addRow(line)

        self.title_edit = QtWidgets.QLineEdit()
        self.title_edit.setPlaceholderText("مثال: شستشوی تور قفس")
        self.title_edit.setMinimumHeight(30)
        layout.addRow("عنوان وظیفه:", self.title_edit)

        self.desc_edit = QtWidgets.QTextEdit()
        self.desc_edit.setMaximumHeight(80)
        layout.addRow("توضیحات:", self.desc_edit)

        self.category_combo = QtWidgets.QComboBox()
        self.category_combo.addItems(["cleaning", "inspection", "repair", "replacement", "other"])
        layout.addRow("دسته‌بندی:", self.category_combo)

        self.scheduled_date = JalaliDateEdit()
        layout.addRow("تاریخ انجام:", self.scheduled_date)

        self.start_time = QtWidgets.QTimeEdit()
        self.start_time.setTime(QtCore.QTime(8, 0))
        layout.addRow("ساعت شروع:", self.start_time)

        self.duration = QtWidgets.QSpinBox()
        self.duration.setRange(15, 1440)
        self.duration.setSuffix(" دقیقه")
        self.duration.setValue(60)
        layout.addRow("مدت زمان:", self.duration)

        self.team_combo = QtWidgets.QComboBox()
        self.team_combo.setEditable(True)
        self.team_combo.addItems(["تیم بهره برداری", "تیم فنی", "تیم تعمیرات", "تیم بازرسی"])
        layout.addRow("تیم مسئول:", self.team_combo)

        self.priority = QtWidgets.QComboBox()
        self.priority.addItems(["1 - بالا", "2 - متوسط", "3 - پایین"])
        layout.addRow("اولویت:", self.priority)

        btn_layout = QtWidgets.QHBoxLayout()
        ok_btn = QtWidgets.QPushButton("ذخیره")
        ok_btn.setMinimumHeight(40)
        ok_btn.setStyleSheet("background-color: rgba(60, 60, 65, 180); color: #C8C8C8; border-radius: 4px; padding: 6px 20px;")
        cancel_btn = QtWidgets.QPushButton("انصراف")
        cancel_btn.setMinimumHeight(40)
        cancel_btn.setStyleSheet("background-color: rgba(60, 60, 65, 180); color: #C8C8C8; border-radius: 4px; padding: 6px 20px;")
        cancel_btn.clicked.connect(self.reject)
        ok_btn.clicked.connect(self.accept)
        btn_layout.addWidget(ok_btn)
        btn_layout.addWidget(cancel_btn)
        layout.addRow(btn_layout)

    def on_template_selected(self, index):
        template_id = self.template_combo.currentData()
        if template_id:
            template = self.db.get_task_template_by_id(template_id)
            if template:
                self.title_edit.setText(template['title'])
                self.desc_edit.setText(template['description'] or "")
                idx = self.category_combo.findText(template['category'])
                if idx >= 0:
                    self.category_combo.setCurrentIndex(idx)
                self.duration.setValue(template['estimated_duration_minutes'])
                self.priority.setCurrentIndex(template['default_priority'] - 1)

    def load_task_data(self):
        tasks = self.db.get_maintenance_tasks(self.plan_id)
        task = None
        for t in tasks:
            if t['id'] == self.task_id:
                task = t
                break
        if task:
            self.title_edit.setText(task['task_title'])
            self.desc_edit.setText(task['task_description'] or "")
            idx = self.category_combo.findText(task['category'])
            if idx >= 0:
                self.category_combo.setCurrentIndex(idx)
            self.scheduled_date.set_jalali_date(str(task['scheduled_date']))
            if task['scheduled_start_time']:
                self.start_time.setTime(QtCore.QTime.fromString(str(task['scheduled_start_time'])[:5], "hh:mm"))
            self.duration.setValue(task['estimated_duration_minutes'])
            idx = self.team_combo.findText(task['assigned_to_team'] or "")
            if idx >= 0:
                self.team_combo.setCurrentIndex(idx)
            else:
                self.team_combo.setEditText(task['assigned_to_team'] or "")
            self.priority.setCurrentIndex(task['priority_level'] - 1)

    def accept(self):
        if not self.title_edit.text().strip():
            QtWidgets.QMessageBox.warning(self, "خطا", "لطفاً عنوان وظیفه را وارد کنید")
            return
        if not self.team_combo.currentText().strip():
            QtWidgets.QMessageBox.warning(self, "خطا", "لطفاً تیم مسئول را وارد کنید")
            return
        priority_map = {"1 - بالا": 1, "2 - متوسط": 2, "3 - پایین": 3}
        
        if self.task_id:
            self.db.execute_query("""
                UPDATE maintenance_plan_tasks 
                SET task_title = %s, task_description = %s, category = %s,
                    scheduled_date = %s, scheduled_start_time = %s, estimated_duration_minutes = %s,
                    assigned_to_team = %s, priority_level = %s
                WHERE id = %s
            """, (self.title_edit.text().strip(), self.desc_edit.toPlainText(), self.category_combo.currentText(),
                  self.scheduled_date.get_jalali_date(), self.start_time.time().toString("hh:mm:ss"),
                  self.duration.value(), self.team_combo.currentText().strip(), 
                  priority_map[self.priority.currentText()], self.task_id))
        else:
            self.db.add_maintenance_task(
                self.plan_id,
                self.template_combo.currentData(),
                self.title_edit.text().strip(),
                self.desc_edit.toPlainText(),
                self.category_combo.currentText(),
                self.scheduled_date.get_jalali_date(),
                self.start_time.time().toString("hh:mm:ss"),
                self.duration.value(),
                self.team_combo.currentText().strip(),
                priority_map[self.priority.currentText()]
            )
        super().accept()


class TemplateManagerDialog(QtWidgets.QDialog):
    """دیالوگ مدیریت الگوهای وظایف"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.db = DatabaseHandler()
        self.setWindowTitle("مدیریت الگوهای وظایف")
        self.setModal(True)
        self.resize(600, 400)
        self.setup_ui()
        self.load_templates()

    def setup_ui(self):
        layout = QtWidgets.QVBoxLayout(self)

        self.templates_table = QtWidgets.QTableWidget()
        self.templates_table.setColumnCount(6)
        self.templates_table.setHorizontalHeaderLabels(["شناسه", "عنوان", "دسته‌بندی", "مدت(دقیقه)", "اولویت", "فعال"])
        self.templates_table.horizontalHeader().setStretchLastSection(True)
        self.templates_table.setStyleSheet("""
            QTableWidget {
                border: 1px solid #3E3E42;
                border-radius: 4px;
                background-color: #2D2D30;
                alternate-background-color: #252526;
            }
            QTableWidget::item:selected { background-color: #3A3A3A; }
            QHeaderView::section {
                background-color: #252526;
                color: #C8C8C8;
                border: none;
                border-bottom: 1px solid #3E3E42;
                padding: 6px;
            }
        """)
        layout.addWidget(self.templates_table)

        btn_layout = QtWidgets.QHBoxLayout()
        add_btn = QtWidgets.QPushButton("➕ افزودن")
        add_btn.setStyleSheet("background-color: rgba(60, 60, 65, 180); color: #C8C8C8; border-radius: 4px; padding: 6px 12px;")
        add_btn.clicked.connect(self.add_template)
        
        close_btn = QtWidgets.QPushButton("بستن")
        close_btn.setStyleSheet("background-color: rgba(60, 60, 65, 180); color: #C8C8C8; border-radius: 4px; padding: 6px 12px;")
        close_btn.clicked.connect(self.accept)
        
        btn_layout.addWidget(add_btn)
        btn_layout.addStretch()
        btn_layout.addWidget(close_btn)
        layout.addLayout(btn_layout)

    def load_templates(self):
        templates = self.db.get_all_task_templates(only_active=False)
        self.templates_table.setRowCount(len(templates))
        for i, t in enumerate(templates):
            self.templates_table.setItem(i, 0, QtWidgets.QTableWidgetItem(str(t['id'])))
            self.templates_table.setItem(i, 1, QtWidgets.QTableWidgetItem(t['title']))
            self.templates_table.setItem(i, 2, QtWidgets.QTableWidgetItem(t['category']))
            self.templates_table.setItem(i, 3, QtWidgets.QTableWidgetItem(str(t['estimated_duration_minutes'])))
            self.templates_table.setItem(i, 4, QtWidgets.QTableWidgetItem(str(t['default_priority'])))
            self.templates_table.setItem(i, 5, QtWidgets.QTableWidgetItem("✅" if t['is_active'] else "❌"))

    def add_template(self):
        title, ok = QtWidgets.QInputDialog.getText(self, "الگوی جدید", "عنوان وظیفه:")
        if ok and title.strip():
            self.db.add_task_template(title.strip(), "", "other", 60, 2, 1)
            self.load_templates()
            QtWidgets.QMessageBox.information(self, "موفق", "الگو با موفقیت اضافه شد")