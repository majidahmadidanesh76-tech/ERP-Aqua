"""
صفحه برنامهریزی تولید حرفهای
نسخه نهایی - با تمام توابع
"""

from PyQt5 import QtWidgets, QtCore, QtGui
import qtawesome as qta
from datetime import datetime
import mysql.connector

from ..database.db_handler import DatabaseHandler
from ..widgets.jalali_date_edit import JalaliDateEdit
from ..widgets.gantt_chart_widget import EditableGanttWidget

from .dialogs.plan_dialog import PlanDialog
from .dialogs.task_dialog import TaskDialog
from .dialogs.maintenance_plan_dialog import MaintenancePlanDialog


class ProductionPlanningTab(QtWidgets.QWidget):
    def __init__(self, parent=None, farm=None, mooring=None):
        super().__init__(parent)
        self.db = DatabaseHandler()
        self.current_farm = farm
        self.current_mooring = mooring
        self.current_plan_id = None
        self.current_plan = None
        self.current_maintenance_plan_id = None
        self.setup_ui()
        self.load_data()

    def setup_ui(self):
        layout = QtWidgets.QVBoxLayout(self)
        layout.setSpacing(10)
        layout.setContentsMargins(10, 10, 10, 10)

        title = QtWidgets.QLabel("📋 برنامهریزی تولید حرفهای")
        title.setAlignment(QtCore.Qt.AlignCenter)
        title.setStyleSheet("font-size: 18px; font-weight: bold; color: #569CD6; padding: 10px;")
        layout.addWidget(title)

        self.main_tabs = QtWidgets.QTabWidget()
        self.main_tabs.setStyleSheet("""
            QTabWidget::pane { border: 1px solid #3E3E42; border-radius: 4px; background: #1E1E1E; }
            QTabBar::tab { background-color: #2D2D30; color: #C8C8C8; padding: 8px 20px; margin: 2px; border-radius: 4px; }
            QTabBar::tab:selected { background-color: #0E639C; color: white; }
        """)

        self.production_tab = self.create_production_tab()
        self.main_tabs.addTab(self.production_tab, "🐟 برنامه پرورش")
        self.maintenance_tab = self.create_maintenance_tab()
        self.main_tabs.addTab(self.maintenance_tab, "🛠️ برنامه نت")
        self.smart_tab = self.create_smart_tab()
        self.main_tabs.addTab(self.smart_tab, "🤖 پیشنهادات هوشمند")
        self.gantt_tab = self.create_gantt_tab()
        self.main_tabs.addTab(self.gantt_tab, "📊 نمای گانت")

        layout.addWidget(self.main_tabs)
        self.setup_status_bar(layout)

    def get_glass_button_style(self):
        return """
            QPushButton {
                background-color: rgba(60, 60, 65, 200);
                color: #C8C8C8;
                border: 1px solid rgba(86, 156, 214, 80);
                border-radius: 4px;
                font-weight: bold;
                padding: 5px 10px;
            }
            QPushButton:hover { background-color: rgba(86, 156, 214, 100); color: white; }
        """

    def get_glass_icon_style(self):
        return """
            QToolButton {
                background-color: rgba(60, 60, 65, 180);
                border: 1px solid rgba(86, 156, 214, 80);
                border-radius: 3px;
            }
            QToolButton:hover { background-color: rgba(86, 156, 214, 100); }
        """

    # ==================== تب برنامه پرورش ====================

    def create_production_tab(self):
        tab = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout(tab)
        layout.setSpacing(8)
        layout.setContentsMargins(8, 8, 8, 8)

        toolbar = QtWidgets.QHBoxLayout()
        toolbar.setSpacing(8)

        cage_label = QtWidgets.QLabel("قفس:")
        cage_label.setStyleSheet("color: #4EC9B0; font-weight: bold;")
        toolbar.addWidget(cage_label)

        self.cage_combo = QtWidgets.QComboBox()
        self.cage_combo.setMinimumWidth(150)
        self.cage_combo.setFixedHeight(30)
        self.cage_combo.currentIndexChanged.connect(self.on_cage_changed)
        toolbar.addWidget(self.cage_combo)

        glass_icon_style = self.get_glass_icon_style()

        self.new_production_btn = QtWidgets.QToolButton()
        self.new_production_btn.setIcon(qta.icon('fa5s.plus', color='#C8C8C8'))
        self.new_production_btn.setFixedSize(30, 30)
        self.new_production_btn.setStyleSheet(glass_icon_style)
        self.new_production_btn.clicked.connect(self.create_new_production_plan)
        toolbar.addWidget(self.new_production_btn)

        self.submit_production_btn = QtWidgets.QToolButton()
        self.submit_production_btn.setIcon(qta.icon('fa5s.paper-plane', color='#C8C8C8'))
        self.submit_production_btn.setFixedSize(30, 30)
        self.submit_production_btn.setStyleSheet(glass_icon_style)
        self.submit_production_btn.setEnabled(False)
        toolbar.addWidget(self.submit_production_btn)

        refresh_btn = QtWidgets.QToolButton()
        refresh_btn.setIcon(qta.icon('fa5s.sync-alt', color='#C8C8C8'))
        refresh_btn.setFixedSize(30, 30)
        refresh_btn.setStyleSheet(glass_icon_style)
        refresh_btn.clicked.connect(self.refresh_production_data)
        toolbar.addWidget(refresh_btn)

        toolbar.addStretch()
        layout.addLayout(toolbar)

        plans_label = QtWidgets.QLabel("📌 برنامه‌های پرورش")
        plans_label.setStyleSheet("color: #C8C8C8; font-weight: bold;")
        layout.addWidget(plans_label)

        self.production_plans_list = QtWidgets.QListWidget()
        self.production_plans_list.setFixedHeight(120)
        self.production_plans_list.itemClicked.connect(self.on_production_plan_selected)
        layout.addWidget(self.production_plans_list)

        glass_btn_style = self.get_glass_button_style()

        self.edit_production_btn = QtWidgets.QPushButton("✏️ ویرایش برنامه")
        self.edit_production_btn.setFixedSize(100, 28)
        self.edit_production_btn.setStyleSheet(glass_btn_style)
        self.edit_production_btn.setEnabled(False)
        self.edit_production_btn.clicked.connect(self.edit_production_plan)

        self.delete_production_btn = QtWidgets.QPushButton("🗑️ حذف برنامه")
        self.delete_production_btn.setFixedSize(100, 28)
        self.delete_production_btn.setStyleSheet(glass_btn_style)
        self.delete_production_btn.setEnabled(False)
        self.delete_production_btn.clicked.connect(self.delete_production_plan)

        plan_btn_layout = QtWidgets.QHBoxLayout()
        plan_btn_layout.addStretch()
        plan_btn_layout.addWidget(self.edit_production_btn)
        plan_btn_layout.addWidget(self.delete_production_btn)
        layout.addLayout(plan_btn_layout)

        task_toolbar = QtWidgets.QHBoxLayout()
        self.add_production_task_btn = QtWidgets.QPushButton("➕ افزودن وظیفه")
        self.add_production_task_btn.setFixedSize(110, 28)
        self.add_production_task_btn.setStyleSheet(glass_btn_style)
        self.add_production_task_btn.setEnabled(False)
        self.add_production_task_btn.clicked.connect(self.add_production_task)
        task_toolbar.addWidget(self.add_production_task_btn)

        self.production_plan_info = QtWidgets.QLabel("برنامهای انتخاب نشده است")
        self.production_plan_info.setStyleSheet("color: #569CD6; font-size: 11px;")
        task_toolbar.addWidget(self.production_plan_info)
        task_toolbar.addStretch()
        layout.addLayout(task_toolbar)

        self.production_tasks_table = QtWidgets.QTableWidget()
        self.production_tasks_table.setColumnCount(8)
        self.production_tasks_table.setHorizontalHeaderLabels(["شناسه", "وظیفه", "تاریخ", "زمان", "مدت", "مسئول", "وضعیت", "عملیات"])
        self.production_tasks_table.setColumnWidth(0, 40)
        self.production_tasks_table.setColumnWidth(1, 200)
        self.production_tasks_table.setColumnWidth(2, 85)
        self.production_tasks_table.setColumnWidth(3, 60)
        self.production_tasks_table.setColumnWidth(4, 50)
        self.production_tasks_table.setColumnWidth(5, 110)
        self.production_tasks_table.setColumnWidth(6, 85)
        self.production_tasks_table.setColumnWidth(7, 70)
        self.production_tasks_table.verticalHeader().setDefaultSectionSize(28)
        layout.addWidget(self.production_tasks_table)

        return tab

    # ==================== تب برنامه نت ====================

    def create_maintenance_tab(self):
        """ایجاد تب برنامه نت"""
        tab = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout(tab)
        layout.setSpacing(8)
        layout.setContentsMargins(8, 8, 8, 8)

        glass_icon_style = self.get_glass_icon_style()
        glass_btn_style = self.get_glass_button_style()

        toolbar = QtWidgets.QHBoxLayout()
        toolbar.setSpacing(10)

        asset_label = QtWidgets.QLabel("نوع تجهیز:")
        asset_label.setStyleSheet("color: #4EC9B0; font-weight: bold;")
        toolbar.addWidget(asset_label)

        self.asset_type_combo = QtWidgets.QComboBox()
        self.asset_type_combo.setMinimumWidth(200)
        self.asset_type_combo.setFixedHeight(32)
        self.asset_type_combo.setStyleSheet("""
            QComboBox {
                background-color: #3C3C3C;
                color: #C8C8C8;
                border: 1px solid #3E3E42;
                border-radius: 4px;
                padding: 4px 8px;
            }
            QComboBox:hover { border-color: #569CD6; }
        """)
        
        self.asset_type_combo.addItem("همه تجهیزات", None)
        self.asset_type_combo.addItem("سیستم مهار (Mooring)", "mooring")
        self.asset_type_combo.addItem("بویه (Buoy)", "buoy")
        self.asset_type_combo.addItem("لنگر (Anchor)", "anchor")
        self.asset_type_combo.addItem("تور (Net)", "net")
        self.asset_type_combo.addItem("قفس (Cage)", "cage")
        self.asset_type_combo.addItem("کلکتور (Collector)", "collector")
        
        self.asset_type_combo.setCurrentIndex(0)
        self.asset_type_combo.currentIndexChanged.connect(self.on_asset_type_changed)
        toolbar.addWidget(self.asset_type_combo, 1)

        # دکمه افزودن تجهیز
        self.add_equipment_btn = QtWidgets.QToolButton()
        self.add_equipment_btn.setIcon(qta.icon('fa5s.plus', color='#4EC9B0'))
        self.add_equipment_btn.setIconSize(QtCore.QSize(16, 16))
        self.add_equipment_btn.setToolTip("افزودن نوع تجهیز جدید")
        self.add_equipment_btn.setFixedSize(32, 32)
        self.add_equipment_btn.setStyleSheet(glass_icon_style)
        self.add_equipment_btn.clicked.connect(self.add_equipment_type)
        toolbar.addWidget(self.add_equipment_btn)

        # دکمه ویرایش تجهیز
        self.edit_equipment_btn = QtWidgets.QToolButton()
        self.edit_equipment_btn.setIcon(qta.icon('fa5s.edit', color='#569CD6'))
        self.edit_equipment_btn.setIconSize(QtCore.QSize(16, 16))
        self.edit_equipment_btn.setToolTip("ویرایش نوع تجهیز انتخاب شده")
        self.edit_equipment_btn.setFixedSize(32, 32)
        self.edit_equipment_btn.setStyleSheet(glass_icon_style)
        self.edit_equipment_btn.clicked.connect(self.edit_equipment_type)
        self.edit_equipment_btn.setEnabled(False)
        toolbar.addWidget(self.edit_equipment_btn)

        # دکمه حذف تجهیز
        self.delete_equipment_btn = QtWidgets.QToolButton()
        self.delete_equipment_btn.setIcon(qta.icon('fa5s.trash-alt', color='#F48771'))
        self.delete_equipment_btn.setIconSize(QtCore.QSize(16, 16))
        self.delete_equipment_btn.setToolTip("حذف نوع تجهیز انتخاب شده")
        self.delete_equipment_btn.setFixedSize(32, 32)
        self.delete_equipment_btn.setStyleSheet(glass_icon_style)
        self.delete_equipment_btn.clicked.connect(self.delete_equipment_type)
        self.delete_equipment_btn.setEnabled(False)
        toolbar.addWidget(self.delete_equipment_btn)

        toolbar.addSpacing(20)

        self.new_maintenance_btn = QtWidgets.QToolButton()
        self.new_maintenance_btn.setIcon(qta.icon('fa5s.plus', color='#C8C8C8'))
        self.new_maintenance_btn.setFixedSize(30, 30)
        self.new_maintenance_btn.setStyleSheet(glass_icon_style)
        self.new_maintenance_btn.clicked.connect(self.create_new_maintenance_plan)
        toolbar.addWidget(self.new_maintenance_btn)

        self.refresh_maintenance_btn = QtWidgets.QToolButton()
        self.refresh_maintenance_btn.setIcon(qta.icon('fa5s.sync-alt', color='#C8C8C8'))
        self.refresh_maintenance_btn.setFixedSize(30, 30)
        self.refresh_maintenance_btn.setStyleSheet(glass_icon_style)
        self.refresh_maintenance_btn.clicked.connect(self.refresh_maintenance_data)
        toolbar.addWidget(self.refresh_maintenance_btn)

        toolbar.addStretch()
        layout.addLayout(toolbar)

        plans_label = QtWidgets.QLabel("📌 برنامههای تعمیرات و نگهداری")
        plans_label.setStyleSheet("color: #C8C8C8; font-weight: bold;")
        layout.addWidget(plans_label)

        self.maintenance_plans_list = QtWidgets.QListWidget()
        self.maintenance_plans_list.setFixedHeight(120)
        self.maintenance_plans_list.itemClicked.connect(self.on_maintenance_plan_selected)
        layout.addWidget(self.maintenance_plans_list)

        plan_btn_layout = QtWidgets.QHBoxLayout()
        plan_btn_layout.addStretch()

        self.edit_maintenance_btn = QtWidgets.QPushButton("✏️ ویرایش برنامه")
        self.edit_maintenance_btn.setFixedSize(100, 28)
        self.edit_maintenance_btn.setStyleSheet(glass_btn_style)
        self.edit_maintenance_btn.setEnabled(False)
        self.edit_maintenance_btn.clicked.connect(self.edit_maintenance_plan)

        self.delete_maintenance_btn = QtWidgets.QPushButton("🗑️ حذف برنامه")
        self.delete_maintenance_btn.setFixedSize(100, 28)
        self.delete_maintenance_btn.setStyleSheet(glass_btn_style)
        self.delete_maintenance_btn.setEnabled(False)
        self.delete_maintenance_btn.clicked.connect(self.delete_maintenance_plan)

        plan_btn_layout.addWidget(self.edit_maintenance_btn)
        plan_btn_layout.addWidget(self.delete_maintenance_btn)
        layout.addLayout(plan_btn_layout)

        task_toolbar = QtWidgets.QHBoxLayout()
        self.add_maintenance_task_btn = QtWidgets.QPushButton("➕ افزودن وظیفه")
        self.add_maintenance_task_btn.setFixedSize(110, 28)
        self.add_maintenance_task_btn.setStyleSheet(glass_btn_style)
        self.add_maintenance_task_btn.setEnabled(False)
        self.add_maintenance_task_btn.clicked.connect(self.add_maintenance_task)
        task_toolbar.addWidget(self.add_maintenance_task_btn)

        self.maintenance_plan_info = QtWidgets.QLabel("برنامهای انتخاب نشده است")
        self.maintenance_plan_info.setStyleSheet("color: #569CD6; font-size: 11px;")
        task_toolbar.addWidget(self.maintenance_plan_info)
        task_toolbar.addStretch()
        layout.addLayout(task_toolbar)

        self.maintenance_tasks_table = QtWidgets.QTableWidget()
        self.maintenance_tasks_table.setColumnCount(8)
        self.maintenance_tasks_table.setHorizontalHeaderLabels(["شناسه", "وظیفه", "تاریخ", "زمان", "مدت", "تیم مسئول", "وضعیت", "عملیات"])
        self.maintenance_tasks_table.setColumnWidth(0, 40)
        self.maintenance_tasks_table.setColumnWidth(1, 200)
        self.maintenance_tasks_table.setColumnWidth(2, 85)
        self.maintenance_tasks_table.setColumnWidth(3, 60)
        self.maintenance_tasks_table.setColumnWidth(4, 50)
        self.maintenance_tasks_table.setColumnWidth(5, 110)
        self.maintenance_tasks_table.setColumnWidth(6, 85)
        self.maintenance_tasks_table.setColumnWidth(7, 70)
        self.maintenance_tasks_table.verticalHeader().setDefaultSectionSize(28)
        layout.addWidget(self.maintenance_tasks_table)

        return tab

    # ==================== تب پیشنهادات هوشمند ====================

    def create_smart_tab(self):
        tab = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout(tab)
        layout.setSpacing(10)

        glass_icon_style = self.get_glass_icon_style()
        glass_btn_style = self.get_glass_button_style()

        toolbar = QtWidgets.QHBoxLayout()
        self.refresh_smart_btn = QtWidgets.QToolButton()
        self.refresh_smart_btn.setIcon(qta.icon('fa5s.sync-alt', color='#C8C8C8'))
        self.refresh_smart_btn.setFixedSize(30, 30)
        self.refresh_smart_btn.setStyleSheet(glass_icon_style)
        self.refresh_smart_btn.clicked.connect(self.load_smart_suggestions)
        toolbar.addWidget(self.refresh_smart_btn)

        self.settings_btn = QtWidgets.QToolButton()
        self.settings_btn.setIcon(qta.icon('fa5s.cog', color='#C8C8C8'))
        self.settings_btn.setFixedSize(30, 30)
        self.settings_btn.setStyleSheet(glass_icon_style)
        self.settings_btn.clicked.connect(self.open_smart_rules_settings)
        toolbar.addWidget(self.settings_btn)

        toolbar.addStretch()
        layout.addLayout(toolbar)

        self.smart_table = QtWidgets.QTableWidget()
        self.smart_table.setColumnCount(7)
        self.smart_table.setHorizontalHeaderLabels(["نوع", "عنوان", "توضیحات", "اولویت", "تاریخ پیشنهادی", "دلیل", "عملیات"])
        self.smart_table.horizontalHeader().setStretchLastSection(True)
        self.smart_table.verticalHeader().setDefaultSectionSize(40)
        layout.addWidget(self.smart_table)

        self.load_smart_suggestions()
        return tab

    # ==================== تب گانت ====================

    def create_gantt_tab(self):
        tab = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout(tab)

        glass_btn_style = self.get_glass_button_style()
        refresh_btn = QtWidgets.QPushButton("🔄 بروزرسانی")
        refresh_btn.setFixedSize(100, 28)
        refresh_btn.setStyleSheet(glass_btn_style)
        refresh_btn.clicked.connect(self.refresh_gantt_chart)
        layout.addWidget(refresh_btn)

        self.gantt_widget = EditableGanttWidget()
        layout.addWidget(self.gantt_widget)

        self.refresh_gantt_chart()
        return tab

    # ==================== توابع کمکی ====================

    def setup_status_bar(self, parent_layout):
        status_frame = QtWidgets.QFrame()
        status_frame.setStyleSheet("background-color: #252526; border-radius: 8px; padding: 6px;")
        status_layout = QtWidgets.QHBoxLayout(status_frame)
        status_layout.setSpacing(20)

        self.total_tasks_label = QtWidgets.QLabel("📋 کل وظایف: 0")
        self.completed_tasks_label = QtWidgets.QLabel("✅ انجام شده: 0")
        self.pending_tasks_label = QtWidgets.QLabel("⏳ در انتظار: 0")
        self.delayed_tasks_label = QtWidgets.QLabel("⚠️ تاخیر: 0")

        for label in [self.total_tasks_label, self.completed_tasks_label, self.pending_tasks_label, self.delayed_tasks_label]:
            label.setStyleSheet("color: #C8C8C8; font-size: 11px;")
            status_layout.addWidget(label)

        status_layout.addStretch()
        parent_layout.addWidget(status_frame)

    def load_data(self):
        self.load_cages()
        self.load_production_plans()
        self.load_maintenance_plans()

    def load_cages(self):
        self.cage_combo.clear()
        cages = self.db.fetch_all("SELECT id FROM cages ORDER BY id")
        if cages:
            for cage in cages:
                self.cage_combo.addItem(cage['id'], cage['id'])
            if self.cage_combo.count() > 0:
                self.cage_combo.setCurrentIndex(0)
            self.cage_combo.setEnabled(True)
        else:
            self.cage_combo.addItem("--- هیچ قفسی موجود نیست ---")
            self.cage_combo.setEnabled(False)

    def on_cage_changed(self):
        self.load_production_plans()
        self.current_plan_id = None
        self.current_plan = None
        self.production_plan_info.setText("برنامهای انتخاب نشده است")
        self.production_tasks_table.setRowCount(0)
        self.submit_production_btn.setEnabled(False)
        self.add_production_task_btn.setEnabled(False)
        self.edit_production_btn.setEnabled(False)
        self.delete_production_btn.setEnabled(False)

    def on_asset_type_changed(self):
        current_index = self.asset_type_combo.currentIndex()
        can_edit_delete = current_index > 0
        self.edit_equipment_btn.setEnabled(can_edit_delete)
        self.delete_equipment_btn.setEnabled(can_edit_delete)
        
        self.load_maintenance_plans()
        self.current_maintenance_plan_id = None
        self.maintenance_plan_info.setText("برنامهای انتخاب نشده است")
        self.maintenance_tasks_table.setRowCount(0)
        self.add_maintenance_task_btn.setEnabled(False)
        self.edit_maintenance_btn.setEnabled(False)
        self.delete_maintenance_btn.setEnabled(False)

    def refresh_production_data(self):
        self.load_production_plans()
        if self.current_plan_id:
            self.load_production_tasks()
        QtWidgets.QMessageBox.information(self, "بهروزرسانی", "دادههای برنامه پرورش بهروزرسانی شد")

    def refresh_maintenance_data(self):
        self.load_maintenance_plans()
        if self.current_maintenance_plan_id:
            self.load_maintenance_tasks()
        QtWidgets.QMessageBox.information(self, "بهروزرسانی", "دادههای برنامه نت بهروزرسانی شد")

    # ==================== توابع برنامه پرورش ====================

    def load_production_plans(self):
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
        if not item:
            return
        self.current_plan_id = item.data(QtCore.Qt.UserRole)

        plan = self.db.get_production_plan_by_id(self.current_plan_id)
        self.current_plan = plan

        if plan:
            status_names = {'draft': 'پیشنویس', 'submitted': 'ارسال شده', 'approved': 'تایید شده', 
                           'in_progress': 'در حال اجرا', 'completed': 'تکمیل شده', 'cancelled': 'لغو شده'}
            self.production_plan_info.setText(f"📋 {plan['plan_title']} | {plan['start_date']} تا {plan['end_date']} | وضعیت: {status_names.get(plan['plan_status'], plan['plan_status'])}")

        self.load_production_tasks()

        if plan and plan['plan_status'] == 'draft':
            self.submit_production_btn.setEnabled(True)
            self.edit_production_btn.setEnabled(True)
            self.delete_production_btn.setEnabled(True)
            self.add_production_task_btn.setEnabled(True)
        else:
            self.submit_production_btn.setEnabled(False)
            self.edit_production_btn.setEnabled(False)
            self.delete_production_btn.setEnabled(False)
            self.add_production_task_btn.setEnabled(False)

    def load_production_tasks(self):
        if not self.current_plan_id:
            self.production_tasks_table.setRowCount(0)
            return

        tasks = self.db.fetch_all("SELECT * FROM plan_tasks WHERE plan_id = %s ORDER BY scheduled_date", (self.current_plan_id,))
        self.production_tasks_table.setRowCount(len(tasks))

        if len(tasks) == 0:
            self.production_tasks_table.setRowCount(1)
            self.production_tasks_table.setSpan(0, 0, 1, 8)
            empty_item = QtWidgets.QTableWidgetItem("هیچ وظیفهای ثبت نشده است")
            empty_item.setTextAlignment(QtCore.Qt.AlignCenter)
            self.production_tasks_table.setItem(0, 0, empty_item)
            return

        status_icons = {'pending': '⏳ در انتظار', 'in_progress': '🔄 در حال انجام', 'completed': '✅ انجام شده'}
        
        for i, task in enumerate(tasks):
            self.production_tasks_table.setItem(i, 0, QtWidgets.QTableWidgetItem(str(task.get('id', ''))))
            self.production_tasks_table.setItem(i, 1, QtWidgets.QTableWidgetItem(str(task.get('task_title', ''))))
            self.production_tasks_table.setItem(i, 2, QtWidgets.QTableWidgetItem(str(task.get('scheduled_date', '')) or "-"))
            self.production_tasks_table.setItem(i, 3, QtWidgets.QTableWidgetItem(str(task.get('scheduled_start_time', ''))[:5] if task.get('scheduled_start_time') else "-"))
            self.production_tasks_table.setItem(i, 4, QtWidgets.QTableWidgetItem(str(task.get('estimated_duration_minutes', '')) or "-"))
            self.production_tasks_table.setItem(i, 5, QtWidgets.QTableWidgetItem(str(task.get('assigned_to_unit', '')) or "-"))
            status_item = QtWidgets.QTableWidgetItem(status_icons.get(task.get('execution_status', 'pending'), '⏳ در انتظار'))
            if task.get('execution_status') == 'completed':
                status_item.setForeground(QtGui.QColor('#4EC9B0'))
            self.production_tasks_table.setItem(i, 6, status_item)
            
            btn_widget = QtWidgets.QWidget()
            btn_layout = QtWidgets.QHBoxLayout(btn_widget)
            complete_btn = QtWidgets.QPushButton("✓")
            complete_btn.setFixedSize(25, 25)
            complete_btn.clicked.connect(lambda checked, tid=task['id']: self.complete_production_task(tid))
            btn_layout.addWidget(complete_btn)
            btn_layout.addStretch()
            self.production_tasks_table.setCellWidget(i, 7, btn_widget)

    def create_new_production_plan(self):
        cage_id = self.cage_combo.currentData()
        if not cage_id:
            QtWidgets.QMessageBox.warning(self, "خطا", "لطفاً قفس را انتخاب کنید")
            return
        dialog = PlanDialog(self, cage_id)
        if dialog.exec_():
            self.load_production_plans()

    def edit_production_plan(self):
        QtWidgets.QMessageBox.information(self, "اطلاع", "ویرایش برنامه در حال توسعه...")

    def delete_production_plan(self):
        if not self.current_plan_id:
            return
        reply = QtWidgets.QMessageBox.question(self, "تأیید", "آیا از حذف این برنامه مطمئن هستید؟",
                                               QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)
        if reply == QtWidgets.QMessageBox.Yes:
            self.db.execute_query("DELETE FROM production_plans WHERE id = %s", (self.current_plan_id,))
            self.load_production_plans()
            self.production_tasks_table.setRowCount(0)

    def submit_production_plan(self):
        QtWidgets.QMessageBox.information(self, "اطلاع", "ارسال برنامه در حال توسعه...")

    def add_production_task(self):
        if not self.current_plan_id:
            QtWidgets.QMessageBox.warning(self, "خطا", "لطفاً برنامه را انتخاب کنید")
            return
        dialog = TaskDialog(self, self.current_plan_id)
        if dialog.exec_():
            self.load_production_tasks()

    def complete_production_task(self, task_id):
        self.db.execute_query("UPDATE plan_tasks SET execution_status = 'completed' WHERE id = %s", (task_id,))
        self.load_production_tasks()

    def edit_production_task(self, task_id):
        QtWidgets.QMessageBox.information(self, "اطلاع", "ویرایش وظیفه در حال توسعه...")

    def delete_production_task(self, task_id):
        reply = QtWidgets.QMessageBox.question(self, "تأیید", "آیا از حذف این وظیفه مطمئن هستید؟",
                                               QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)
        if reply == QtWidgets.QMessageBox.Yes:
            self.db.execute_query("DELETE FROM plan_tasks WHERE id = %s", (task_id,))
            self.load_production_tasks()

    # ==================== توابع برنامه نت ====================

    def load_maintenance_plans(self):
        self.maintenance_plans_list.clear()
        
        asset_type = self.asset_type_combo.currentData()
        if asset_type == "همه تجهیزات":
            asset_type = None

        if asset_type:
            plans = self.db.fetch_all("""
                SELECT id, plan_title, asset_type, start_date, end_date, plan_status 
                FROM maintenance_plans 
                WHERE asset_type = %s 
                ORDER BY id DESC
            """, (asset_type,))
        else:
            plans = self.db.fetch_all("""
                SELECT id, plan_title, asset_type, start_date, end_date, plan_status 
                FROM maintenance_plans 
                ORDER BY id DESC
            """)
        
        print(f"DEBUG: تعداد برنامه‌های نت یافت شده: {len(plans)}")

        for plan in plans:
            item_text = f"{plan['plan_title']} ({plan['asset_type']}) - {plan['start_date']} تا {plan['end_date']}"
            item = QtWidgets.QListWidgetItem(item_text)
            item.setData(QtCore.Qt.UserRole, plan['id'])
            self.maintenance_plans_list.addItem(item)

        if len(plans) == 0:
            self.maintenance_plans_list.addItem("--- هیچ برنامه‌ای وجود ندارد ---")

    def on_maintenance_plan_selected(self, item):
        if item.text() == "--- هیچ برنامه‌ای وجود ندارد ---":
            return
        self.current_maintenance_plan_id = item.data(QtCore.Qt.UserRole)
        self.load_maintenance_tasks()
        self.add_maintenance_task_btn.setEnabled(True)
        self.edit_maintenance_btn.setEnabled(True)
        self.delete_maintenance_btn.setEnabled(True)

    def load_maintenance_tasks(self):
        if not self.current_maintenance_plan_id:
            return
        tasks = self.db.get_maintenance_tasks(self.current_maintenance_plan_id)
        self.maintenance_tasks_table.setRowCount(len(tasks))
        
        if len(tasks) == 0:
            self.maintenance_tasks_table.setRowCount(1)
            self.maintenance_tasks_table.setSpan(0, 0, 1, 8)
            empty_item = QtWidgets.QTableWidgetItem("هیچ وظیفهای ثبت نشده است")
            empty_item.setTextAlignment(QtCore.Qt.AlignCenter)
            self.maintenance_tasks_table.setItem(0, 0, empty_item)
            return

        for i, task in enumerate(tasks):
            self.maintenance_tasks_table.setItem(i, 0, QtWidgets.QTableWidgetItem(str(task.get('id', ''))))
            self.maintenance_tasks_table.setItem(i, 1, QtWidgets.QTableWidgetItem(str(task.get('task_title', ''))))
            self.maintenance_tasks_table.setItem(i, 2, QtWidgets.QTableWidgetItem(str(task.get('scheduled_date', '')) or "-"))
            self.maintenance_tasks_table.setItem(i, 3, QtWidgets.QTableWidgetItem(str(task.get('scheduled_start_time', ''))[:5] if task.get('scheduled_start_time') else "-"))
            self.maintenance_tasks_table.setItem(i, 4, QtWidgets.QTableWidgetItem(str(task.get('estimated_duration_minutes', '')) or "-"))
            self.maintenance_tasks_table.setItem(i, 5, QtWidgets.QTableWidgetItem(str(task.get('assigned_to_team', '')) or "-"))
            status_text = "✅ انجام شده" if task.get('execution_status') == 'completed' else "⏳ در انتظار"
            self.maintenance_tasks_table.setItem(i, 6, QtWidgets.QTableWidgetItem(status_text))

    def create_new_maintenance_plan(self):
        dialog = MaintenancePlanDialog(self)
        if dialog.exec_():
            self.load_maintenance_plans()
            QtWidgets.QMessageBox.information(self, "موفق", "برنامه نت جدید با موفقیت ایجاد شد")

    def edit_maintenance_plan(self):
        QtWidgets.QMessageBox.information(self, "اطلاع", "ویرایش برنامه نت در حال توسعه...")

    def delete_maintenance_plan(self):
        if not self.current_maintenance_plan_id:
            return
        reply = QtWidgets.QMessageBox.question(self, "تأیید", "آیا از حذف این برنامه مطمئن هستید؟",
                                               QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)
        if reply == QtWidgets.QMessageBox.Yes:
            self.db.delete_maintenance_plan(self.current_maintenance_plan_id)
            self.load_maintenance_plans()
            self.maintenance_tasks_table.setRowCount(0)

    def add_maintenance_task(self):
        if not self.current_maintenance_plan_id:
            QtWidgets.QMessageBox.warning(self, "خطا", "لطفاً برنامه را انتخاب کنید")
            return
        dialog = TaskDialog(self, self.current_maintenance_plan_id, is_maintenance=True)
        if dialog.exec_():
            self.load_maintenance_tasks()

    # ==================== مدیریت تجهیزات ====================

    def add_equipment_type(self):
        text, ok = QtWidgets.QInputDialog.getText(self, "افزودن تجهیز", "نام تجهیز جدید:")
        if ok and text.strip():
            self.asset_type_combo.addItem(text.strip(), text.strip())
            QtWidgets.QMessageBox.information(self, "موفق", f"تجهیز '{text}' با موفقیت اضافه شد")

    def edit_equipment_type(self):
        current_index = self.asset_type_combo.currentIndex()
        if current_index <= 0:
            QtWidgets.QMessageBox.warning(self, "خطا", "لطفاً یک نوع تجهیز را انتخاب کنید")
            return
        
        current_text = self.asset_type_combo.currentText()
        new_text, ok = QtWidgets.QInputDialog.getText(self, "ویرایش تجهیز", "نام جدید:", text=current_text)
        if ok and new_text.strip():
            self.asset_type_combo.setItemText(current_index, new_text.strip())
            QtWidgets.QMessageBox.information(self, "موفق", f"تجهیز با موفقیت به '{new_text}' ویرایش شد")

    def delete_equipment_type(self):
        current_index = self.asset_type_combo.currentIndex()
        if current_index <= 0:
            QtWidgets.QMessageBox.warning(self, "خطا", "لطفاً یک نوع تجهیز را انتخاب کنید")
            return
        
        current_text = self.asset_type_combo.currentText()
        reply = QtWidgets.QMessageBox.question(self, "تأیید حذف", 
            f"آیا از حذف تجهیز '{current_text}' مطمئن هستید؟",
            QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)
        
        if reply == QtWidgets.QMessageBox.Yes:
            self.asset_type_combo.removeItem(current_index)
            QtWidgets.QMessageBox.information(self, "موفق", f"تجهیز '{current_text}' با موفقیت حذف شد")

    # ==================== توابع پیشنهادات هوشمند ====================

    def load_smart_suggestions(self):
        suggestions = self.db.get_ai_suggestions()
        self.smart_table.setRowCount(len(suggestions))
        for i, sug in enumerate(suggestions):
            self.smart_table.setItem(i, 0, QtWidgets.QTableWidgetItem(sug.get('suggestion_type', '')))
            self.smart_table.setItem(i, 1, QtWidgets.QTableWidgetItem(sug.get('title', '')[:50]))
            self.smart_table.setItem(i, 2, QtWidgets.QTableWidgetItem(sug.get('description', '')[:80]))
            self.smart_table.setItem(i, 3, QtWidgets.QTableWidgetItem(str(sug.get('priority', ''))))
            self.smart_table.setItem(i, 4, QtWidgets.QTableWidgetItem(str(sug.get('suggested_date', '') or '-')))
            self.smart_table.setItem(i, 5, QtWidgets.QTableWidgetItem(sug.get('reasoning', '')[:100]))

    def refresh_gantt_chart(self):
        self.show_sample_data()

    def show_sample_data(self):
        sample_tasks = [
            {'id': 1, 'title': 'تغذیه قفس 1', 'cage': 'Cage-001', 'type': 'feeding', 'start_day': 5, 'duration': 2},
            {'id': 2, 'title': 'زیست توده', 'cage': 'Cage-001', 'type': 'biomass', 'start_day': 10, 'duration': 1},
        ]
        self.gantt_widget.load_tasks(sample_tasks)

    def date_to_day_number(self, date_str):
        return 0

    def accept_smart_suggestion(self, suggestion_id):
        pass

    def reject_smart_suggestion(self, suggestion_id):
        pass

    def open_smart_rules_settings(self):
        try:
            from .dialogs.smart_rules_settings_dialog import SmartRulesSettingsDialog
            dialog = SmartRulesSettingsDialog(self)
            dialog.exec_()
        except Exception as e:
            QtWidgets.QMessageBox.warning(self, "خطا", str(e))