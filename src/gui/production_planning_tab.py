"""
صفحه برنامه‌ریزی تولید حرفه‌ای
شامل سه تب: برنامه پرورش، برنامه نت، پیشنهادات هوشمند
"""

from PyQt5 import QtWidgets, QtCore, QtGui
import qtawesome as qta
from functools import partial
from datetime import datetime, timedelta

from ..database.db_handler import DatabaseHandler
from ..widgets.jalali_date_edit import JalaliDateEdit
from ..widgets.gantt_chart_widget import EditableGanttWidget

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

        title = QtWidgets.QLabel("📋 برنامه‌ریزی تولید حرفه‌ای")
        title.setAlignment(QtCore.Qt.AlignCenter)
        title.setStyleSheet("font-size: 18px; font-weight: bold; color: #569CD6; padding: 10px;")
        layout.addWidget(title)

        glass_btn_style = """
            QToolButton {
                background-color: rgba(60, 60, 65, 180);
                border: none;
                border-radius: 4px;
                padding: 0px;
                min-width: 28px;
                min-height: 28px;
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

        self.production_tab = self.create_production_tab(glass_btn_style)
        self.main_tabs.addTab(self.production_tab, "🐟 برنامه پرورش")

        self.maintenance_tab = self.create_maintenance_tab(glass_btn_style)
        self.main_tabs.addTab(self.maintenance_tab, "🛠️ برنامه نت")

        self.smart_tab = self.create_smart_tab(glass_btn_style)
        self.main_tabs.addTab(self.smart_tab, "🤖 پیشنهادات هوشمند")

        self.gantt_tab = self.create_gantt_tab()
        self.main_tabs.addTab(self.gantt_tab, "📊 نمای گانت")

        layout.addWidget(self.main_tabs)
        self.setup_status_bar(layout)

    def on_production_plan_selected(self, item):
        """انتخاب برنامه پرورش"""
        if not item:
            return
        self.current_plan_id = item.data(QtCore.Qt.UserRole)
        
        # تغییر عنوان وظایف به همراه نام برنامه
        plan_title = item.text()
        self.tasks_label.setText(f"📋 وظایف برنامه: {plan_title}")
        
        self.load_production_plan_info()
        self.load_production_tasks()
        
        self.submit_production_btn.setEnabled(True)
        self.add_production_task_btn.setEnabled(True)
        self.edit_production_btn.setEnabled(True)
        self.delete_production_btn.setEnabled(True)

    def create_maintenance_tab(self, glass_btn_style):
        """ایجاد تب برنامه نت (تعمیرات و نگهداری)"""
        tab = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout(tab)
        layout.setSpacing(10)

        # نوار ابزار
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

        # بخش اصلی
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

        # سمت راست: جدول وظایف نت
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
                color: #C8C8C8;
            }
            QHeaderView::section {
                background-color: #252526;
                color: #569CD6;
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

    def create_smart_tab(self, glass_btn_style):
        """ایجاد تب پیشنهادات هوشمند"""
        tab = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout(tab)
        layout.setSpacing(10)

        toolbar = QtWidgets.QHBoxLayout()
        
        self.refresh_smart_btn = QtWidgets.QToolButton()
        self.refresh_smart_btn.setIcon(qta.icon('fa5s.sync-alt', color='#C8C8C8'))
        self.refresh_smart_btn.setIconSize(QtCore.QSize(18, 18))
        self.refresh_smart_btn.setToolTip("بروزرسانی پیشنهادات")
        self.refresh_smart_btn.setStyleSheet(glass_btn_style)
        self.refresh_smart_btn.clicked.connect(self.load_smart_suggestions)
        toolbar.addWidget(self.refresh_smart_btn)
        
        self.settings_btn = QtWidgets.QToolButton()
        self.settings_btn.setIcon(qta.icon('fa5s.cog', color='#C8C8C8'))
        self.settings_btn.setIconSize(QtCore.QSize(18, 18))
        self.settings_btn.setToolTip("تنظیمات قوانین هوشمند")
        self.settings_btn.setStyleSheet(glass_btn_style)
        self.settings_btn.clicked.connect(self.open_smart_rules_settings)
        toolbar.addWidget(self.settings_btn)
        
        toolbar.addStretch()
        layout.addLayout(toolbar)

        self.smart_table = QtWidgets.QTableWidget()
        self.smart_table.setColumnCount(7)
        self.smart_table.setHorizontalHeaderLabels(["نوع", "عنوان", "توضیحات", "اولویت", "تاریخ پیشنهادی", "دلیل", "عملیات"])
        self.smart_table.horizontalHeader().setStretchLastSection(True)
        self.smart_table.setColumnWidth(0, 80)
        self.smart_table.setColumnWidth(1, 150)
        self.smart_table.setColumnWidth(2, 200)
        self.smart_table.setColumnWidth(3, 60)
        self.smart_table.setColumnWidth(4, 100)
        self.smart_table.setColumnWidth(5, 200)
        self.smart_table.setStyleSheet("""
            QTableWidget {
                border: 1px solid #3E3E42;
                border-radius: 4px;
                background-color: #2D2D30;
                alternate-background-color: #252526;
                gridline-color: #3E3E42;
            }
            QTableWidget::item {
                padding: 8px 5px;
                color: #C8C8C8;
            }
            QHeaderView::section {
                background-color: #252526;
                color: #569CD6;
                border: none;
                border-bottom: 1px solid #3E3E42;
                padding: 8px;
                font-weight: bold;
            }
        """)
        layout.addWidget(self.smart_table)

        self.load_smart_suggestions()
        return tab

    def create_gantt_tab(self):
        """ایجاد تب گانت چارت"""
        tab = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout(tab)
        
        refresh_btn = QtWidgets.QPushButton("🔄 بروزرسانی")
        refresh_btn.setStyleSheet("""
            QPushButton {
                background-color: #0E639C;
                color: white;
                border-radius: 4px;
                padding: 5px 12px;
            }
        """)
        refresh_btn.clicked.connect(self.refresh_gantt_chart)
        layout.addWidget(refresh_btn)
        
        self.gantt_widget = EditableGanttWidget()
        layout.addWidget(self.gantt_widget)
        
        self.refresh_gantt_chart()
        
        return tab

    def refresh_gantt_chart(self):
        """بارگذاری داده‌های واقعی از دیتابیس در گانت چارت"""
        try:
            tasks_data = self.db.fetch_all("""
                SELECT 
                    pt.id, 
                    pt.task_title as title, 
                    pt.category as type,
                    pt.scheduled_date,
                    pt.estimated_duration_minutes as duration,
                    pp.cage_id as cage,
                    pp.plan_title as plan_title
                FROM plan_tasks pt
                JOIN production_plans pp ON pt.plan_id = pp.id
                ORDER BY pt.scheduled_date
            """)
            
            if not tasks_data:
                self.show_sample_data()
                return
            
            gantt_tasks = []
            for task in tasks_data:
                start_day = self.date_to_day_number(task['scheduled_date'])
                if start_day > 0:
                    gantt_tasks.append({
                        'id': task['id'],
                        'title': task['title'][:20],
                        'cage': task['cage'],
                        'plan': task['plan_title'],
                        'type': task['type'] or 'other',
                        'start_day': start_day,
                        'duration': max(1, task['duration'] / (24 * 60)),
                        'amount': None
                    })
            
            if gantt_tasks:
                self.gantt_widget.load_tasks(gantt_tasks)
            else:
                self.show_sample_data()
                
        except Exception as e:
            print(f"خطا در بارگذاری گانت: {e}")
            self.show_sample_data()
    
    def show_sample_data(self):
        """نمایش داده‌های نمونه در صورت نبودن داده واقعی"""
        sample_tasks = [
            {'id': 1, 'title': 'تغذیه قفس 1', 'cage': 'Cage-001', 'type': 'feeding', 'start_day': 5, 'duration': 2, 'amount': 250},
            {'id': 2, 'title': 'زیست توده', 'cage': 'Cage-001', 'type': 'biomass', 'start_day': 10, 'duration': 1, 'amount': None},
            {'id': 3, 'title': 'برداشت', 'cage': 'Cage-002', 'type': 'harvest', 'start_day': 8, 'duration': 3, 'amount': 5000},
            {'id': 4, 'title': 'تعمیرات تور', 'cage': 'Cage-002', 'type': 'maintenance', 'start_day': 15, 'duration': 2, 'amount': None},
            {'id': 5, 'title': 'بازرسی', 'cage': 'Cage-003', 'type': 'inspection', 'start_day': 12, 'duration': 1, 'amount': None},
        ]
        self.gantt_widget.load_tasks(sample_tasks)

    def date_to_day_number(self, date_str):
        """تبدیل تاریخ شمسی به شماره روز از شروع سال"""
        if not date_str:
            return 0
        try:
            parts = date_str.split('/')
            if len(parts) == 3:
                month = int(parts[1])
                day = int(parts[2])
                days_per_month = [31, 31, 31, 31, 31, 31, 30, 30, 30, 30, 30, 29]
                return sum(days_per_month[:month-1]) + day
        except:
            pass
        return 0

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

    def load_data(self):
        """بارگذاری دادهها"""
        self.load_cages()
        self.load_production_plans()
        self.load_maintenance_plans()

    def load_cages(self):
        """بارگذاری لیست قفس‌ها"""
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

    # ==================== توابع برنامه پرورش ====================

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

    def create_production_tab(self, glass_btn_style):
        """ایجاد تب برنامه پرورش (برنامه‌ها بالا، وظایف پایین)"""
        tab = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout(tab)
        layout.setSpacing(10)
        layout.setContentsMargins(10, 10, 10, 10)

        # ========== نوار ابزار ==========
        toolbar = QtWidgets.QHBoxLayout()
        toolbar.setSpacing(8)

        cage_label = QtWidgets.QLabel("قفس:")
        cage_label.setStyleSheet("color: #4EC9B0; font-weight: bold;")
        toolbar.addWidget(cage_label)

        self.cage_combo = QtWidgets.QComboBox()
        self.cage_combo.setMinimumWidth(150)
        self.cage_combo.setFixedHeight(28)
        self.cage_combo.setStyleSheet("""
            QComboBox {
                background-color: #3C3C3C;
                color: #C8C8C8;
                border: 1px solid #3E3E42;
                border-radius: 4px;
                padding: 4px;
            }
        """)
        self.cage_combo.currentIndexChanged.connect(self.on_cage_changed)
        toolbar.addWidget(self.cage_combo)

        toolbar.addSpacing(10)

        self.new_production_btn = QtWidgets.QToolButton()
        self.new_production_btn.setIcon(qta.icon('fa5s.plus', color='#C8C8C8'))
        self.new_production_btn.setIconSize(QtCore.QSize(14, 14))
        self.new_production_btn.setFixedSize(28, 28)
        self.new_production_btn.setToolTip("برنامه پرورش جدید")
        self.new_production_btn.setStyleSheet("""
            QToolButton {
                background-color: rgba(60, 60, 65, 180);
                border: 1px solid rgba(86, 156, 214, 80);
                border-radius: 4px;
                padding: 0px;
                min-width: 28px;
                min-height: 28px;
            }
            QToolButton:hover {
                background-color: rgba(86, 156, 214, 80);
                border-color: rgba(86, 156, 214, 150);
            }
        """)
        self.new_production_btn.clicked.connect(self.create_new_production_plan)
        toolbar.addWidget(self.new_production_btn)

        self.submit_production_btn = QtWidgets.QToolButton()
        self.submit_production_btn.setIcon(qta.icon('fa5s.paper-plane', color='#C8C8C8'))
        self.submit_production_btn.setIconSize(QtCore.QSize(14, 14))
        self.submit_production_btn.setFixedSize(28, 28)
        self.submit_production_btn.setToolTip("ارسال برنامه")
        self.submit_production_btn.setStyleSheet("""
            QToolButton {
                background-color: rgba(60, 60, 65, 180);
                border: 1px solid rgba(86, 156, 214, 80);
                border-radius: 4px;
                padding: 0px;
                min-width: 28px;
                min-height: 28px;
            }
            QToolButton:hover {
                background-color: rgba(86, 156, 214, 80);
                border-color: rgba(86, 156, 214, 150);
            }
        """)
        self.submit_production_btn.clicked.connect(self.submit_production_plan)
        self.submit_production_btn.setEnabled(False)
        toolbar.addWidget(self.submit_production_btn)

        refresh_btn = QtWidgets.QToolButton()
        refresh_btn.setIcon(qta.icon('fa5s.sync-alt', color='#C8C8C8'))
        refresh_btn.setIconSize(QtCore.QSize(14, 14))
        refresh_btn.setFixedSize(28, 28)
        refresh_btn.setToolTip("به‌روزرسانی")
        refresh_btn.setStyleSheet("""
            QToolButton {
                background-color: rgba(60, 60, 65, 180);
                border: 1px solid rgba(86, 156, 214, 80);
                border-radius: 4px;
                padding: 0px;
                min-width: 28px;
                min-height: 28px;
            }
            QToolButton:hover {
                background-color: rgba(86, 156, 214, 80);
                border-color: rgba(86, 156, 214, 150);
            }
        """)
        refresh_btn.clicked.connect(self.refresh_production_data)
        toolbar.addWidget(refresh_btn)

        toolbar.addStretch()
        layout.addLayout(toolbar)

        # ========== بخش برنامه‌های پرورش ==========
        plans_label = QtWidgets.QLabel("📌 برنامه‌های پرورش")
        plans_label.setStyleSheet("color: #C8C8C8; font-weight: bold; padding: 5px 0 2px 0;")
        layout.addWidget(plans_label)

        self.production_plans_list = QtWidgets.QListWidget()
        self.production_plans_list.setFixedHeight(180)
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
        self.production_plans_list.itemClicked.connect(self.on_production_plan_selected)
        layout.addWidget(self.production_plans_list)

        # دکمه‌های ویرایش و حذف
        plan_btn_layout = QtWidgets.QHBoxLayout()
        plan_btn_layout.setSpacing(10)
        plan_btn_layout.addStretch()

        self.edit_production_btn = QtWidgets.QToolButton()
        self.edit_production_btn.setIcon(qta.icon('fa5s.edit', color='#C8C8C8'))
        self.edit_production_btn.setIconSize(QtCore.QSize(14, 14))
        self.edit_production_btn.setFixedSize(28, 28)
        self.edit_production_btn.setToolTip("ویرایش برنامه")
        self.edit_production_btn.setStyleSheet("""
            QToolButton {
                background-color: rgba(60, 60, 65, 180);
                border: 1px solid rgba(86, 156, 214, 80);
                border-radius: 4px;
                padding: 0px;
                min-width: 28px;
                min-height: 28px;
            }
            QToolButton:hover {
                background-color: rgba(86, 156, 214, 80);
                border-color: rgba(86, 156, 214, 150);
            }
        """)
        self.edit_production_btn.clicked.connect(self.edit_production_plan)
        self.edit_production_btn.setEnabled(False)

        self.delete_production_btn = QtWidgets.QToolButton()
        self.delete_production_btn.setIcon(qta.icon('fa5s.trash-alt', color='#C8C8C8'))
        self.delete_production_btn.setIconSize(QtCore.QSize(14, 14))
        self.delete_production_btn.setFixedSize(28, 28)
        self.delete_production_btn.setToolTip("حذف برنامه")
        self.delete_production_btn.setStyleSheet("""
            QToolButton {
                background-color: rgba(60, 60, 65, 180);
                border: 1px solid rgba(86, 156, 214, 80);
                border-radius: 4px;
                padding: 0px;
                min-width: 28px;
                min-height: 28px;
            }
            QToolButton:hover {
                background-color: rgba(86, 156, 214, 80);
                border-color: rgba(86, 156, 214, 150);
            }
        """)
        self.delete_production_btn.clicked.connect(self.delete_production_plan)
        self.delete_production_btn.setEnabled(False)

        plan_btn_layout.addWidget(self.edit_production_btn)
        plan_btn_layout.addWidget(self.delete_production_btn)
        layout.addLayout(plan_btn_layout)

        # ========== بخش وظایف ==========
        # لیبل وظایف
        self.tasks_label = QtWidgets.QLabel("📋 وظایف برنامه")
        self.tasks_label.setStyleSheet("color: #C8C8C8; font-weight: bold; padding: 10px 0 2px 0;")
        layout.addWidget(self.tasks_label)

        # دکمه افزودن وظیفه
        task_toolbar = QtWidgets.QHBoxLayout()
        task_toolbar.addStretch()
        self.add_production_task_btn = QtWidgets.QToolButton()
        self.add_production_task_btn.setIcon(qta.icon('fa5s.plus', color='#C8C8C8'))
        self.add_production_task_btn.setIconSize(QtCore.QSize(14, 14))
        self.add_production_task_btn.setFixedSize(28, 28)
        self.add_production_task_btn.setToolTip("افزودن وظیفه")
        self.add_production_task_btn.setStyleSheet("""
            QToolButton {
                background-color: rgba(60, 60, 65, 180);
                border: 1px solid rgba(86, 156, 214, 80);
                border-radius: 4px;
                padding: 0px;
                min-width: 28px;
                min-height: 28px;
            }
            QToolButton:hover {
                background-color: rgba(86, 156, 214, 80);
                border-color: rgba(86, 156, 214, 150);
            }
        """)
        self.add_production_task_btn.clicked.connect(self.add_production_task)
        self.add_production_task_btn.setEnabled(False)
        task_toolbar.addWidget(self.add_production_task_btn)
        layout.addLayout(task_toolbar)

        # جدول وظایف
        self.production_tasks_table = QtWidgets.QTableWidget()
        self.production_tasks_table.setAlternatingRowColors(True)
        self.production_tasks_table.setMinimumHeight(250)
        self.production_tasks_table.setColumnCount(8)
        self.production_tasks_table.setHorizontalHeaderLabels(["شناسه", "وظیفه", "تاریخ", "زمان", "مدت", "مسئول", "اولویت", "وضعیت"])
        self.production_tasks_table.horizontalHeader().setStretchLastSection(True)
        self.production_tasks_table.setColumnWidth(0, 50)
        self.production_tasks_table.setColumnWidth(1, 160)
        self.production_tasks_table.setColumnWidth(2, 90)
        self.production_tasks_table.setColumnWidth(3, 60)
        self.production_tasks_table.setColumnWidth(4, 50)
        self.production_tasks_table.setColumnWidth(5, 100)
        self.production_tasks_table.setColumnWidth(6, 50)
        self.production_tasks_table.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAsNeeded)
        self.production_tasks_table.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAsNeeded)
        self.production_tasks_table.setStyleSheet("""
            QTableWidget {
                border: 1px solid #3E3E42;
                border-radius: 4px;
                background-color: #2D2D30;
                alternate-background-color: #252526;
                gridline-color: #3E3E42;
            }
            QTableWidget::item {
                padding: 6px 4px;
                color: #C8C8C8;
            }
            QHeaderView::section {
                background-color: #252526;
                color: #569CD6;
                border: none;
                border-bottom: 1px solid #3E3E42;
                padding: 6px;
                font-weight: bold;
            }
        """)
        layout.addWidget(self.production_tasks_table)

        return tab

    def load_production_plan_info(self):
        """بارگذاری اطلاعات برنامه پرورش"""
        if not self.current_plan_id:
            self.production_plan_info.setText("برنامه‌ای انتخاب نشده است")
            return
        
        plan = self.db.get_production_plan_by_id(self.current_plan_id)
        if plan:
            status_names = {'draft': 'پیش‌نویس', 'submitted': 'ارسال شده', 'approved': 'تایید شده', 
                           'in_progress': 'در حال اجرا', 'completed': 'تکمیل شده', 'cancelled': 'لغو شده'}
            self.production_plan_info.setText(f"📋 {plan['plan_title']} | {plan['start_date']} تا {plan['end_date']} | وضعیت: {status_names.get(plan['plan_status'], plan['plan_status'])}")

    def load_production_tasks(self):
        """بارگذاری وظایف برنامه پرورش"""
        if not self.current_plan_id:
            self.production_tasks_table.setRowCount(0)
            return
        
        tasks = self.db.fetch_all("""
            SELECT * FROM plan_tasks 
            WHERE plan_id = %s 
            ORDER BY id
        """, (self.current_plan_id,))
        
        self.production_tasks_table.setRowCount(len(tasks))
        
        if len(tasks) == 0:
            self.production_tasks_table.setRowCount(1)
            self.production_tasks_table.setSpan(0, 0, 1, 8)
            empty_item = QtWidgets.QTableWidgetItem("هیچ وظیفه‌ای برای این برنامه ثبت نشده است")
            empty_item.setTextAlignment(QtCore.Qt.AlignCenter)
            self.production_tasks_table.setItem(0, 0, empty_item)
            return
        
        status_icons = {'pending': '⏳ در انتظار', 'in_progress': '🔄 در حال انجام', 
                        'completed': '✅ انجام شده', 'delayed': '⚠️ تاخیر', 'cancelled': '❌ لغو شده'}
        priority_colors = {1: '#F48771', 2: '#DCDCAA', 3: '#C8C8C8'}
        priority_text = {1: 'بالا', 2: 'متوسط', 3: 'پایین'}

        for i, task in enumerate(tasks):
            self.production_tasks_table.setItem(i, 0, QtWidgets.QTableWidgetItem(str(task['id'])))
            self.production_tasks_table.setItem(i, 1, QtWidgets.QTableWidgetItem(task['task_title']))
            self.production_tasks_table.setItem(i, 2, QtWidgets.QTableWidgetItem(str(task['scheduled_date']) if task['scheduled_date'] else "-"))
            self.production_tasks_table.setItem(i, 3, QtWidgets.QTableWidgetItem(str(task['scheduled_start_time'])[:5] if task['scheduled_start_time'] else "-"))
            self.production_tasks_table.setItem(i, 4, QtWidgets.QTableWidgetItem(str(task['estimated_duration_minutes']) if task['estimated_duration_minutes'] else "-"))
            self.production_tasks_table.setItem(i, 5, QtWidgets.QTableWidgetItem(task['assigned_to_unit'] or "-"))
            
            priority_item = QtWidgets.QTableWidgetItem(priority_text.get(task['priority_level'], 'متوسط'))
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
            QtWidgets.QMessageBox.warning(self, "خطا", "هیچ برنامه‌ای انتخاب نشده است")
            return
        
        # دریافت اطلاعات برنامه از دیتابیس
        plan = self.db.fetch_one("SELECT * FROM production_plans WHERE id = %s", (self.current_plan_id,))
        if not plan:
            QtWidgets.QMessageBox.warning(self, "خطا", "برنامه یافت نشد")
            return
        
        # بررسی وضعیت برنامه (فقط پیش‌نویس یا لغو شده قابل ویرایش)
        if plan['plan_status'] not in ['draft', 'cancelled']:
            QtWidgets.QMessageBox.warning(self, "خطا", "فقط برنامه‌های در وضعیت پیش‌نویس یا لغو شده قابل ویرایش هستند")
            return
        
        # باز کردن دیالوگ ویرایش
        dialog = PlanDialog(self, plan['cage_id'], plan)
        if dialog.exec_():
            self.load_production_plans()
            self.load_production_plan_info()
            self.load_production_tasks()
            QtWidgets.QMessageBox.information(self, "موفق", "برنامه با موفقیت ویرایش شد")

    def delete_production_plan(self):
        """حذف برنامه پرورش"""
        if not self.current_plan_id:
            QtWidgets.QMessageBox.warning(self, "خطا", "هیچ برنامه‌ای انتخاب نشده است")
            return
        
        reply = QtWidgets.QMessageBox.question(
            self, 
            "تأیید حذف", 
            "آیا از حذف این برنامه و تمام وظایف آن مطمئن هستید؟",
            QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No
        )
        
        if reply == QtWidgets.QMessageBox.Yes:
            # حذف برنامه (وظایف به صورت آبشاری حذف می‌شوند)
            self.db.execute_query("DELETE FROM production_plans WHERE id = %s", (self.current_plan_id,))
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
        reply = QtWidgets.QMessageBox.question(self, "تأیید ارسال", "آیا از ارسال این برنامه به واحدها مطمئن هستید?", QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)
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
            self.maintenance_tasks_table.setItem(i, 2, QtWidgets.QTableWidgetItem(str(task['scheduled_date']) if task['scheduled_date'] else "-"))
            self.maintenance_tasks_table.setItem(i, 3, QtWidgets.QTableWidgetItem(str(task['scheduled_start_time'])[:5] if task['scheduled_start_time'] else "-"))
            self.maintenance_tasks_table.setItem(i, 4, QtWidgets.QTableWidgetItem(str(task['estimated_duration_minutes']) if task['estimated_duration_minutes'] else "-"))
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
        reply = QtWidgets.QMessageBox.question(self, "تأیید حذف", "آیا از حذف این برنامه نت و تمام وظایف آن مطمئن هستید?", QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)
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

    # ==================== توابع پیشنهادات هوشمند ====================

    def load_smart_suggestions(self):
        """بارگذاری پیشنهادات هوشمند از دیتابیس"""
        suggestions = self.db.get_ai_suggestions()
        self.smart_table.setRowCount(len(suggestions))
        
        type_names = {
            'alert': '⚠️ هشدار',
            'feeding': '🍽️ تغذیه',
            'maintenance': '🛠️ نت',
            'harvest': '💰 برداشت',
            'inspection': '🔍 بازرسی',
            'strategic': '📊 استراتژیک'
        }
        
        priority_colors = {1: '#F48771', 2: '#DCDCAA', 3: '#C8C8C8'}
        priority_text = {1: 'فوری', 2: 'متوسط', 3: 'کم'}
        
        for i, sug in enumerate(suggestions):
            self.smart_table.setItem(i, 0, QtWidgets.QTableWidgetItem(type_names.get(sug['suggestion_type'], sug['suggestion_type'])))
            self.smart_table.setItem(i, 1, QtWidgets.QTableWidgetItem(sug['title'][:50]))
            self.smart_table.setItem(i, 2, QtWidgets.QTableWidgetItem(sug['description'][:80]))
            priority_item = QtWidgets.QTableWidgetItem(priority_text.get(sug['priority'], 'متوسط'))
            priority_item.setForeground(QtGui.QColor(priority_colors.get(sug['priority'], '#C8C8C8')))
            self.smart_table.setItem(i, 3, priority_item)
            self.smart_table.setItem(i, 4, QtWidgets.QTableWidgetItem(str(sug['suggested_date'] or '-')))
            self.smart_table.setItem(i, 5, QtWidgets.QTableWidgetItem(sug['reasoning'][:100] if sug['reasoning'] else '-'))
            
            btn_widget = QtWidgets.QWidget()
            btn_layout = QtWidgets.QHBoxLayout(btn_widget)
            btn_layout.setContentsMargins(0, 0, 0, 0)
            btn_layout.setSpacing(5)
            
            if sug['status'] == 'pending':
                accept_btn = QtWidgets.QPushButton("✓ قبول")
                accept_btn.setFixedSize(70, 28)
                accept_btn.setStyleSheet("background-color: #2E8B57; color: white; border-radius: 3px; font-weight: bold;")
                accept_btn.clicked.connect(lambda checked, sid=sug['id']: self.accept_smart_suggestion(sid))
                
                reject_btn = QtWidgets.QPushButton("✗ رد")
                reject_btn.setFixedSize(70, 28)
                reject_btn.setStyleSheet("background-color: #8B2C2C; color: white; border-radius: 3px; font-weight: bold;")
                reject_btn.clicked.connect(lambda checked, sid=sug['id']: self.reject_smart_suggestion(sid))
                
                btn_layout.addWidget(accept_btn)
                btn_layout.addWidget(reject_btn)
            else:
                status_text = "✅ پذیرفته شده" if sug['status'] == 'accepted' else "❌ رد شده"
                status_label = QtWidgets.QLabel(status_text)
                status_label.setStyleSheet("color: #808080; font-size: 11px;")
                btn_layout.addWidget(status_label)
            
            btn_layout.addStretch()
            self.smart_table.setCellWidget(i, 6, btn_widget)
        
        self.smart_table.verticalHeader().setDefaultSectionSize(45)

    def accept_smart_suggestion(self, suggestion_id):
        """پذیرش یک پیشنهاد هوشمند"""
        suggestion = self.db.fetch_one("SELECT * FROM ai_suggestions WHERE id = %s", (suggestion_id,))
        if not suggestion:
            QtWidgets.QMessageBox.warning(self, "خطا", "پیشنهاد یافت نشد")
            return
        
        if suggestion['suggestion_type'] == 'maintenance':
            if self.current_maintenance_plan_id:
                self.db.add_maintenance_task(
                    self.current_maintenance_plan_id, None,
                    suggestion['title'], suggestion['description'], 'inspection',
                    suggestion['suggested_date'] or datetime.now().date(), '08:00:00', 60,
                    'تیم خودکار', 2
                )
                msg = "وظیفه به برنامه نت اضافه شد"
            else:
                msg = "لطفاً ابتدا یک برنامه نت انتخاب کنید"
                QtWidgets.QMessageBox.warning(self, "خطا", msg)
                return
        elif suggestion['suggestion_type'] == 'harvest':
            if self.current_plan_id:
                self.db.add_plan_task(
                    self.current_plan_id, None,
                    suggestion['title'], suggestion['description'], 'harvest',
                    suggestion['suggested_date'] or datetime.now().date(), '08:00:00', 480,
                    None, 'واحد برداشت', 1
                )
                msg = "وظیفه برداشت به برنامه پرورش اضافه شد"
            else:
                msg = "لطفاً ابتدا یک برنامه پرورش انتخاب کنید"
                QtWidgets.QMessageBox.warning(self, "خطا", msg)
                return
        else:
            msg = "هشدار ثبت شد"
        
        self.db.accept_suggestion(suggestion_id)
        self.load_smart_suggestions()
        QtWidgets.QMessageBox.information(self, "موفق", msg)

    def reject_smart_suggestion(self, suggestion_id):
        """رد یک پیشنهاد هوشمند"""
        self.db.reject_suggestion(suggestion_id)
        self.load_smart_suggestions()
        QtWidgets.QMessageBox.information(self, "اطلاع", "پیشنهاد رد شد.")

    def open_smart_rules_settings(self):
        """باز کردن دیالوگ تنظیمات قوانین هوشمند"""
        import traceback
        try:
            from .dialogs.smart_rules_settings_dialog import SmartRulesSettingsDialog
            dialog = SmartRulesSettingsDialog(self)
            dialog.exec_()
        except ImportError as e:
            QtWidgets.QMessageBox.warning(self, "خطا", f"فایل دیالوگ یافت نشد:\n{str(e)}")
        except Exception as e:
            QtWidgets.QMessageBox.warning(self, "خطا", f"خطا در باز کردن دیالوگ تنظیمات:\n{str(e)}")


class PlanDialog(QtWidgets.QDialog):
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
        cancel_btn = QtWidgets.QPushButton("انصراف")
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
        cancel_btn = QtWidgets.QPushButton("انصراف")
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

        # الگوهای تکراری - حذف شده
        line = QtWidgets.QFrame()
        line.setFrameShape(QtWidgets.QFrame.HLine)
        line.setStyleSheet("background-color: #3E3E42; margin: 5px 0;")
        layout.addRow(line)

        self.title_edit = QtWidgets.QLineEdit()
        self.title_edit.setPlaceholderText("مثال: شستشوی تور قفس")
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

        self.responsible_combo = QtWidgets.QComboBox()
        self.responsible_combo.setEditable(True)
        self.responsible_combo.addItems(["واحد بهره برداری", "واحد فنی", "واحد تغذیه", "واحد تعمیرات", "واحد زیست‌توده"])
        layout.addRow("مسئول:", self.responsible_combo)

        self.priority = QtWidgets.QComboBox()
        self.priority.addItems(["1 - بالا", "2 - متوسط", "3 - پایین"])
        layout.addRow("اولویت:", self.priority)

        btn_layout = QtWidgets.QHBoxLayout()
        ok_btn = QtWidgets.QPushButton("ذخیره")
        cancel_btn = QtWidgets.QPushButton("انصراف")
        cancel_btn.clicked.connect(self.reject)
        ok_btn.clicked.connect(self.accept)
        btn_layout.addWidget(ok_btn)
        btn_layout.addWidget(cancel_btn)
        layout.addRow(btn_layout)

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
                    None,
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
                    None,
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

        # الگوهای تکراری - حذف شده
        line = QtWidgets.QFrame()
        line.setFrameShape(QtWidgets.QFrame.HLine)
        line.setStyleSheet("background-color: #3E3E42; margin: 5px 0;")
        layout.addRow(line)

        self.title_edit = QtWidgets.QLineEdit()
        self.title_edit.setPlaceholderText("مثال: شستشوی تور قفس")
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
        cancel_btn = QtWidgets.QPushButton("انصراف")
        cancel_btn.clicked.connect(self.reject)
        ok_btn.clicked.connect(self.accept)
        btn_layout.addWidget(ok_btn)
        btn_layout.addWidget(cancel_btn)
        layout.addRow(btn_layout)

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
                None,
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