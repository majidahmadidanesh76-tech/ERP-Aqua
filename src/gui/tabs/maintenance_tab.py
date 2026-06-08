"""
تب برنامه نت - ساده و مستقل
"""

from PyQt5 import QtWidgets, QtCore, QtGui
import qtawesome as qta

from ...database.db_handler import DatabaseHandler
from ..dialogs.maintenance_plan_dialog import MaintenancePlanDialog
from ..dialogs.task_dialog import TaskDialog


class MaintenanceTab(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.db = DatabaseHandler()
        self.current_maintenance_plan_id = None
        self.setup_ui()
        self.load_plans()

    def setup_ui(self):
        layout = QtWidgets.QVBoxLayout(self)
        layout.setSpacing(8)
        layout.setContentsMargins(8, 8, 8, 8)

        glass_btn_style = """
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

        glass_icon_style = """
            QToolButton {
                background-color: rgba(60, 60, 65, 180);
                border: 1px solid rgba(86, 156, 214, 80);
                border-radius: 3px;
            }
            QToolButton:hover { background-color: rgba(86, 156, 214, 100); }
        """

        # ========== نوار ابزار ==========
        toolbar = QtWidgets.QHBoxLayout()
        toolbar.setSpacing(10)

        asset_label = QtWidgets.QLabel("نوع تجهیز:")
        asset_label.setStyleSheet("color: #4EC9B0; font-weight: bold;")
        toolbar.addWidget(asset_label)

        self.asset_type_combo = QtWidgets.QComboBox()
        self.asset_type_combo.setMinimumWidth(200)
        self.asset_type_combo.setFixedHeight(32)
        self.asset_type_combo.addItems(["همه تجهیزات", "مورینگ", "بویه", "لنگر", "تور", "قفس", "کلکتور"])
        self.asset_type_combo.currentIndexChanged.connect(self.on_asset_type_changed)
        toolbar.addWidget(self.asset_type_combo, 1)

        self.new_maintenance_btn = QtWidgets.QToolButton()
        self.new_maintenance_btn.setIcon(qta.icon('fa5s.plus', color='#C8C8C8'))
        self.new_maintenance_btn.setFixedSize(30, 30)
        self.new_maintenance_btn.setStyleSheet(glass_icon_style)
        self.new_maintenance_btn.clicked.connect(self.create_new_plan)
        toolbar.addWidget(self.new_maintenance_btn)

        self.refresh_maintenance_btn = QtWidgets.QToolButton()
        self.refresh_maintenance_btn.setIcon(qta.icon('fa5s.sync-alt', color='#C8C8C8'))
        self.refresh_maintenance_btn.setFixedSize(30, 30)
        self.refresh_maintenance_btn.setStyleSheet(glass_icon_style)
        self.refresh_maintenance_btn.clicked.connect(self.load_plans)
        toolbar.addWidget(self.refresh_maintenance_btn)

        toolbar.addStretch()
        layout.addLayout(toolbar)

        # ========== برنامه‌های نت ==========
        plans_label = QtWidgets.QLabel("📌 برنامههای تعمیرات و نگهداری")
        plans_label.setStyleSheet("color: #C8C8C8; font-weight: bold;")
        layout.addWidget(plans_label)

        self.maintenance_plans_list = QtWidgets.QListWidget()
        self.maintenance_plans_list.setFixedHeight(120)
        self.maintenance_plans_list.itemClicked.connect(self.on_plan_selected)
        layout.addWidget(self.maintenance_plans_list)

        plan_btn_layout = QtWidgets.QHBoxLayout()
        plan_btn_layout.addStretch()

        self.edit_plan_btn = QtWidgets.QPushButton("✏️ ویرایش برنامه")
        self.edit_plan_btn.setFixedSize(100, 28)
        self.edit_plan_btn.setStyleSheet(glass_btn_style)
        self.edit_plan_btn.setEnabled(False)
        self.edit_plan_btn.clicked.connect(self.edit_plan)

        self.delete_plan_btn = QtWidgets.QPushButton("🗑️ حذف برنامه")
        self.delete_plan_btn.setFixedSize(100, 28)
        self.delete_plan_btn.setStyleSheet(glass_btn_style)
        self.delete_plan_btn.setEnabled(False)
        self.delete_plan_btn.clicked.connect(self.delete_plan)

        plan_btn_layout.addWidget(self.edit_plan_btn)
        plan_btn_layout.addWidget(self.delete_plan_btn)
        layout.addLayout(plan_btn_layout)

        # ========== وظایف نت ==========
        task_toolbar = QtWidgets.QHBoxLayout()
        self.add_task_btn = QtWidgets.QPushButton("➕ افزودن وظیفه")
        self.add_task_btn.setFixedSize(110, 28)
        self.add_task_btn.setStyleSheet(glass_btn_style)
        self.add_task_btn.setEnabled(False)
        self.add_task_btn.clicked.connect(self.add_task)
        task_toolbar.addWidget(self.add_task_btn)

        self.plan_info = QtWidgets.QLabel("برنامهای انتخاب نشده است")
        self.plan_info.setStyleSheet("color: #569CD6; font-size: 11px;")
        task_toolbar.addWidget(self.plan_info)
        task_toolbar.addStretch()
        layout.addLayout(task_toolbar)

        self.tasks_table = QtWidgets.QTableWidget()
        self.tasks_table.setColumnCount(7)
        self.tasks_table.setHorizontalHeaderLabels(["شناسه", "وظیفه", "تاریخ", "زمان", "مدت", "تیم مسئول", "وضعیت"])
        self.tasks_table.setColumnWidth(0, 40)
        self.tasks_table.setColumnWidth(1, 200)
        self.tasks_table.setColumnWidth(2, 85)
        self.tasks_table.setColumnWidth(3, 60)
        self.tasks_table.setColumnWidth(4, 50)
        self.tasks_table.setColumnWidth(5, 110)
        self.tasks_table.horizontalHeader().setStretchLastSection(True)
        self.tasks_table.verticalHeader().setDefaultSectionSize(28)
        layout.addWidget(self.tasks_table)

    def load_plans(self):
        """بارگذاری لیست برنامه‌های نت از دیتابیس"""
        self.maintenance_plans_list.clear()
        
        asset_type = self.asset_type_combo.currentText()
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

        for plan in plans:
            item_text = f"{plan['plan_title']} ({plan['asset_type']}) - {plan['start_date']} تا {plan['end_date']}"
            item = QtWidgets.QListWidgetItem(item_text)
            item.setData(QtCore.Qt.UserRole, plan['id'])
            self.maintenance_plans_list.addItem(item)

        if len(plans) == 0:
            self.maintenance_plans_list.addItem("--- هیچ برنامه‌ای وجود ندارد ---")

    def on_asset_type_changed(self):
        self.load_plans()
        self.current_maintenance_plan_id = None
        self.plan_info.setText("برنامهای انتخاب نشده است")
        self.tasks_table.setRowCount(0)
        self.add_task_btn.setEnabled(False)
        self.edit_plan_btn.setEnabled(False)
        self.delete_plan_btn.setEnabled(False)

    def on_plan_selected(self, item):
        if item.text() == "--- هیچ برنامه‌ای وجود ندارد ---":
            return
        self.current_maintenance_plan_id = item.data(QtCore.Qt.UserRole)
        self.load_tasks()
        self.add_task_btn.setEnabled(True)
        self.edit_plan_btn.setEnabled(True)
        self.delete_plan_btn.setEnabled(True)

    def load_tasks(self):
        if not self.current_maintenance_plan_id:
            return
        tasks = self.db.get_maintenance_tasks(self.current_maintenance_plan_id)
        self.tasks_table.setRowCount(len(tasks))
        
        if len(tasks) == 0:
            self.tasks_table.setRowCount(1)
            self.tasks_table.setSpan(0, 0, 1, 7)
            empty_item = QtWidgets.QTableWidgetItem("هیچ وظیفهای ثبت نشده است")
            empty_item.setTextAlignment(QtCore.Qt.AlignCenter)
            self.tasks_table.setItem(0, 0, empty_item)
            return

        status_icons = {'pending': '⏳ در انتظار', 'in_progress': '🔄 در حال انجام', 
                        'completed': '✅ انجام شده', 'delayed': '⚠️ تاخیر', 'cancelled': '❌ لغو شده'}

        for i, task in enumerate(tasks):
            self.tasks_table.setItem(i, 0, QtWidgets.QTableWidgetItem(str(task.get('id', ''))))
            self.tasks_table.setItem(i, 1, QtWidgets.QTableWidgetItem(str(task.get('task_title', ''))))
            self.tasks_table.setItem(i, 2, QtWidgets.QTableWidgetItem(str(task.get('scheduled_date', '')) or "-"))
            self.tasks_table.setItem(i, 3, QtWidgets.QTableWidgetItem(str(task.get('scheduled_start_time', ''))[:5] if task.get('scheduled_start_time') else "-"))
            self.tasks_table.setItem(i, 4, QtWidgets.QTableWidgetItem(str(task.get('estimated_duration_minutes', '')) or "-"))
            self.tasks_table.setItem(i, 5, QtWidgets.QTableWidgetItem(str(task.get('assigned_to_team', '')) or "-"))
            status_item = QtWidgets.QTableWidgetItem(status_icons.get(task.get('execution_status', 'pending'), '⏳ در انتظار'))
            if task.get('execution_status') == 'completed':
                status_item.setForeground(QtGui.QColor('#4EC9B0'))
            self.tasks_table.setItem(i, 6, status_item)

    def create_new_plan(self):
        dialog = MaintenancePlanDialog(self)
        if dialog.exec_():
            self.load_plans()
            QtWidgets.QMessageBox.information(self, "موفق", "برنامه نت جدید با موفقیت ایجاد شد")

    def edit_plan(self):
        QtWidgets.QMessageBox.information(self, "اطلاع", "ویرایش برنامه نت در حال توسعه...")

    def delete_plan(self):
        if not self.current_maintenance_plan_id:
            return
        reply = QtWidgets.QMessageBox.question(self, "تأیید", "آیا از حذف این برنامه مطمئن هستید؟",
                                               QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)
        if reply == QtWidgets.QMessageBox.Yes:
            self.db.delete_maintenance_plan(self.current_maintenance_plan_id)
            self.load_plans()
            self.tasks_table.setRowCount(0)
            self.plan_info.setText("برنامهای انتخاب نشده است")
            self.add_task_btn.setEnabled(False)
            self.edit_plan_btn.setEnabled(False)
            self.delete_plan_btn.setEnabled(False)

    def add_task(self):
        if not self.current_maintenance_plan_id:
            QtWidgets.QMessageBox.warning(self, "خطا", "لطفاً برنامه را انتخاب کنید")
            return
        dialog = TaskDialog(self, self.current_maintenance_plan_id, is_maintenance=True)
        if dialog.exec_():
            self.load_tasks()