"""
تب برنامه نت - نسخه نهایی با فیلتر صحیح نوع تجهیزات
"""

from PyQt5 import QtWidgets, QtCore, QtGui
import qtawesome as qta

from ...database.db_handler import DatabaseHandler
from ..dialogs.maintenance_plan_dialog import MaintenancePlanDialog
from ..dialogs.task_dialog import TaskDialog
from ..dialogs.dialog_style import BUTTON_STYLE, CANCEL_BUTTON_STYLE, TOOLBUTTON_STYLE

class MaintenanceTab(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.db = DatabaseHandler()
        self.current_maintenance_plan_id = None
        self.current_plan = None
        self.setup_ui()
        self.load_equipment_types()
        self.load_plans()

    def setup_ui(self):
        layout = QtWidgets.QVBoxLayout(self)
        layout.setSpacing(8)
        layout.setContentsMargins(8, 8, 8, 8)

        # ========== نوار ابزار ==========
        toolbar = QtWidgets.QHBoxLayout()
        toolbar.setSpacing(10)

        asset_label = QtWidgets.QLabel("نوع تجهیزات:")
        asset_label.setStyleSheet("color: #4EC9B0; font-weight: bold;")
        toolbar.addWidget(asset_label)

        self.asset_type_combo = QtWidgets.QComboBox()
        self.asset_type_combo.setMinimumWidth(150)
        self.asset_type_combo.setFixedHeight(32)
        self.asset_type_combo.addItem("همه تجهیزات", None)
        self.asset_type_combo.currentIndexChanged.connect(self.on_asset_type_changed)
        toolbar.addWidget(self.asset_type_combo, 1)

        self.new_maintenance_btn = QtWidgets.QToolButton()
        self.new_maintenance_btn.setIcon(qta.icon('fa5s.plus', color='#C8C8C8'))
        self.new_maintenance_btn.setFixedSize(30, 30)
        self.new_maintenance_btn.setStyleSheet(TOOLBUTTON_STYLE)
        self.new_maintenance_btn.setToolTip("برنامه نت جدید")
        self.new_maintenance_btn.clicked.connect(self.create_new_plan)
        toolbar.addWidget(self.new_maintenance_btn)

        self.submit_plan_btn = QtWidgets.QToolButton()
        self.submit_plan_btn.setIcon(qta.icon('fa5s.paper-plane', color='#C8C8C8'))
        self.submit_plan_btn.setIconSize(QtCore.QSize(16, 16))
        self.submit_plan_btn.setFixedSize(30, 30)
        self.submit_plan_btn.setToolTip("ارسال برنامه")
        self.submit_plan_btn.setStyleSheet(TOOLBUTTON_STYLE)
        self.submit_plan_btn.clicked.connect(self.submit_plan)
        self.submit_plan_btn.setEnabled(False)
        toolbar.addWidget(self.submit_plan_btn)

        self.refresh_maintenance_btn = QtWidgets.QToolButton()
        self.refresh_maintenance_btn.setIcon(qta.icon('fa5s.sync-alt', color='#C8C8C8'))
        self.refresh_maintenance_btn.setFixedSize(30, 30)
        self.refresh_maintenance_btn.setStyleSheet(TOOLBUTTON_STYLE)
        self.refresh_maintenance_btn.clicked.connect(self.load_plans)
        toolbar.addWidget(self.refresh_maintenance_btn)

        toolbar.addStretch()
        layout.addLayout(toolbar)

        # ========== برنامه‌های نت ==========
        plans_label = QtWidgets.QLabel("📌 برنامه‌های تعمیرات و نگهداری")
        plans_label.setStyleSheet("color: #C8C8C8; font-weight: bold;")
        layout.addWidget(plans_label)

        self.maintenance_plans_list = QtWidgets.QListWidget()
        self.maintenance_plans_list.setFixedHeight(120)
        self.maintenance_plans_list.itemClicked.connect(self.on_plan_selected)
        layout.addWidget(self.maintenance_plans_list)

        plan_btn_layout = QtWidgets.QHBoxLayout()
        plan_btn_layout.addStretch()

        self.edit_plan_btn = QtWidgets.QPushButton("✏️ ویرایش برنامه")
        self.edit_plan_btn.setFixedSize(120, 32)
        self.edit_plan_btn.setStyleSheet(BUTTON_STYLE)
        self.edit_plan_btn.setEnabled(False)
        self.edit_plan_btn.clicked.connect(self.edit_plan)

        self.delete_plan_btn = QtWidgets.QPushButton("🗑️ حذف برنامه")
        self.delete_plan_btn.setFixedSize(120, 32)
        self.delete_plan_btn.setStyleSheet(BUTTON_STYLE)
        self.delete_plan_btn.setEnabled(False)
        self.delete_plan_btn.clicked.connect(self.delete_plan)

        plan_btn_layout.addWidget(self.edit_plan_btn)
        plan_btn_layout.addWidget(self.delete_plan_btn)
        layout.addLayout(plan_btn_layout)

        # ========== وظایف نت ==========
        task_toolbar = QtWidgets.QHBoxLayout()
        self.add_task_btn = QtWidgets.QPushButton("➕ افزودن وظیفه")
        self.add_task_btn.setFixedSize(130, 32)
        self.add_task_btn.setStyleSheet(BUTTON_STYLE)
        self.add_task_btn.setEnabled(False)
        self.add_task_btn.clicked.connect(self.add_task)
        task_toolbar.addWidget(self.add_task_btn)

        self.plan_info = QtWidgets.QLabel("برنامهای انتخاب نشده است")
        self.plan_info.setStyleSheet("color: #569CD6; font-size: 11px;")
        task_toolbar.addWidget(self.plan_info)
        task_toolbar.addStretch()
        layout.addLayout(task_toolbar)

        # ========== جدول وظایف ==========
        self.tasks_table = QtWidgets.QTableWidget()
        self.tasks_table.setColumnCount(8)
        self.tasks_table.setHorizontalHeaderLabels(["شناسه", "وظیفه", "تاریخ", "زمان", "مدت", "تیم مسئول", "وضعیت", "عملیات"])
        self.tasks_table.setColumnWidth(0, 50)
        self.tasks_table.setColumnWidth(1, 220)
        self.tasks_table.setColumnWidth(2, 100)
        self.tasks_table.setColumnWidth(3, 70)
        self.tasks_table.setColumnWidth(4, 60)
        self.tasks_table.setColumnWidth(5, 120)
        self.tasks_table.setColumnWidth(6, 90)
        self.tasks_table.setColumnWidth(7, 100)
        self.tasks_table.horizontalHeader().setStretchLastSection(False)
        self.tasks_table.verticalHeader().setDefaultSectionSize(40)
        self.tasks_table.setAlternatingRowColors(True)
        self.tasks_table.setStyleSheet("""
            QTableWidget {
                border: 1px solid #3E3E42;
                border-radius: 4px;
                background-color: #2D2D30;
                alternate-background-color: #252526;
                gridline-color: #3E3E42;
            }
            QTableWidget::item {
                padding: 5px 4px;
                color: #C8C8C8;
            }
            QTableWidget::item:selected {
                background-color: #0E639C;
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
        layout.addWidget(self.tasks_table)

        # ========== نوار وضعیت پایین جدول ==========
        status_frame = QtWidgets.QFrame()
        status_frame.setStyleSheet("""
            QFrame {
                background-color: #252526;
                border-radius: 6px;
                margin-top: 5px;
                padding: 5px;
            }
        """)
        status_layout = QtWidgets.QHBoxLayout(status_frame)
        status_layout.setSpacing(15)

        self.total_tasks_label = QtWidgets.QLabel("📋 کل وظایف: 0")
        self.completed_tasks_label = QtWidgets.QLabel("✅ انجام شده: 0")
        self.pending_tasks_label = QtWidgets.QLabel("⏳ در انتظار: 0")
        self.in_progress_tasks_label = QtWidgets.QLabel("🔄 در حال انجام: 0")
        self.delayed_tasks_label = QtWidgets.QLabel("⚠️ تاخیر: 0")

        for label in [self.total_tasks_label, self.completed_tasks_label, 
                      self.pending_tasks_label, self.in_progress_tasks_label, 
                      self.delayed_tasks_label]:
            label.setStyleSheet("color: #C8C8C8; font-size: 11px; padding: 3px;")
            status_layout.addWidget(label)

        status_layout.addStretch()
        layout.addWidget(status_frame)

    def update_task_stats(self, tasks):
        total = len(tasks)
        completed = sum(1 for t in tasks if t.get('execution_status') == 'completed')
        pending = sum(1 for t in tasks if t.get('execution_status') == 'pending')
        in_progress = sum(1 for t in tasks if t.get('execution_status') == 'in_progress')
        delayed = sum(1 for t in tasks if t.get('execution_status') == 'delayed')
        
        self.total_tasks_label.setText(f"📋 کل وظایف: {total}")
        self.completed_tasks_label.setText(f"✅ انجام شده: {completed}")
        self.pending_tasks_label.setText(f"⏳ در انتظار: {pending}")
        self.in_progress_tasks_label.setText(f"🔄 در حال انجام: {in_progress}")
        self.delayed_tasks_label.setText(f"⚠️ تاخیر: {delayed}")

    def load_equipment_types(self):
        """بارگذاری انواع تجهیزات از دیتابیس برای فیلتر"""
        self.asset_type_combo.clear()
        self.asset_type_combo.addItem("همه تجهیزات", None)
        
        try:
            equipments = self.db.fetch_all("SELECT name, display_name FROM equipment_types ORDER BY name")
            for eq in equipments:
                display_text = eq.get('display_name') or eq.get('name')
                self.asset_type_combo.addItem(display_text, eq.get('name'))
        except Exception as e:
            print(f"خطا در بارگذاری انواع تجهیزات: {e}")

    def on_asset_type_changed(self):
        """تغییر فیلتر نوع تجهیزات"""
        self.load_plans()
        
        # غیرفعال کردن دکمه جدید برنامه اگر "همه تجهیزات" انتخاب شده باشد
        if self.asset_type_combo.currentData() is None:
            self.new_maintenance_btn.setEnabled(False)
            self.new_maintenance_btn.setToolTip("برای ایجاد برنامه جدید، ابتدا یک نوع تجهیزات را انتخاب کنید")
        else:
            self.new_maintenance_btn.setEnabled(True)
            self.new_maintenance_btn.setToolTip("برنامه نت جدید")

    def load_plans(self):
        """بارگذاری لیست برنامه‌های نت از دیتابیس با فیلتر نوع تجهیزات"""
        self.maintenance_plans_list.clear()

        asset_type = self.asset_type_combo.currentData()

        if asset_type:
            # فقط برنامه‌هایی که asset_type آنها برابر با انتخاب شده است
            plans = self.db.fetch_all("""
                SELECT id, plan_title, plan_type, start_date, end_date, plan_status
                FROM maintenance_plans 
                WHERE asset_type = %s
                ORDER BY id DESC
            """, (asset_type,))
        else:
            # "همه تجهیزات" - هیچ برنامه‌ای نمایش داده نشود
            plans = []

        type_fa_map = {"daily": "روزانه", "weekly": "هفتگی", "monthly": "ماهانه", "yearly": "سالانه"}
        status_icons = {'draft': '📝', 'submitted': '📤', 'approved': '✅', 'in_progress': '⚙️', 'completed': '✔️', 'cancelled': '❌'}

        for plan in plans:
            plan_type_fa = type_fa_map.get(plan['plan_type'], plan['plan_type'])
            icon = status_icons.get(plan['plan_status'], '📝')
            item_text = f"{icon} {plan['plan_title']} ({plan_type_fa}) - {plan['start_date']} تا {plan['end_date']}"
            item = QtWidgets.QListWidgetItem(item_text)
            item.setData(QtCore.Qt.UserRole, plan['id'])
            self.maintenance_plans_list.addItem(item)

        if len(plans) == 0:
            self.maintenance_plans_list.addItem("--- هیچ برنامهای وجود ندارد ---")

    def on_plan_selected(self, item):
        if item.text() == "--- هیچ برنامهای وجود ندارد ---":
            return
        self.current_maintenance_plan_id = item.data(QtCore.Qt.UserRole)
        self.current_plan = self.db.fetch_one("SELECT * FROM maintenance_plans WHERE id = %s", (self.current_maintenance_plan_id,))
        self.load_tasks()

        if self.current_plan:
            status_names = {'draft': 'پیشنویس', 'submitted': 'ارسال شده', 'approved': 'تایید شده', 
                           'in_progress': 'در حال اجرا', 'completed': 'تکمیل شده', 'cancelled': 'لغو شده'}
            
            plan_type_fa = {"daily": "روزانه", "weekly": "هفتگی", "monthly": "ماهانه", "yearly": "سالانه"}.get(self.current_plan['plan_type'], self.current_plan['plan_type'])
            self.plan_info.setText(f"📋 {self.current_plan['plan_title']} ({plan_type_fa}) - {self.current_plan['start_date']} تا {self.current_plan['end_date']} | وضعیت: {status_names.get(self.current_plan['plan_status'], self.current_plan['plan_status'])}")

            can_edit = self.current_plan['plan_status'] in ['draft', 'cancelled']
            self.edit_plan_btn.setEnabled(can_edit)
            self.submit_plan_btn.setEnabled(self.current_plan['plan_status'] == 'draft')
            self.delete_plan_btn.setEnabled(can_edit)
            self.add_task_btn.setEnabled(can_edit)
        else:
            self.plan_info.setText("برنامهای انتخاب نشده است")
            self.edit_plan_btn.setEnabled(False)
            self.submit_plan_btn.setEnabled(False)
            self.delete_plan_btn.setEnabled(False)
            self.add_task_btn.setEnabled(False)

    def load_tasks(self):
        if not self.current_maintenance_plan_id:
            self.tasks_table.setRowCount(0)
            self.update_task_stats([])
            return

        tasks = self.db.fetch_all("""
            SELECT * FROM maintenance_plan_tasks 
            WHERE plan_id = %s 
            ORDER BY id DESC
        """, (self.current_maintenance_plan_id,))
        
        self.tasks_table.clearContents()
        self.tasks_table.setRowCount(0)
        
        if len(tasks) == 0:
            self.tasks_table.setRowCount(1)
            self.tasks_table.setSpan(0, 0, 1, 8)
            empty_item = QtWidgets.QTableWidgetItem("هیچ وظیفهای ثبت نشده است")
            empty_item.setTextAlignment(QtCore.Qt.AlignCenter)
            self.tasks_table.setItem(0, 0, empty_item)
            self.update_task_stats([])
            return

        status_icons = {'pending': '⏳ در انتظار', 'in_progress': '🔄 در حال انجام', 
                        'completed': '✅ انجام شده', 'delayed': '⚠️ تاخیر', 'cancelled': '❌ لغو شده'}

        glass_icon_style_small = """
            QToolButton {
                background-color: rgba(60, 60, 65, 180);
                border: 1px solid rgba(86, 156, 214, 80);
                border-radius: 3px;
            }
            QToolButton:hover {
                background-color: rgba(86, 156, 214, 100);
            }
        """

        self.tasks_table.setRowCount(len(tasks))

        for i, task in enumerate(tasks):
            self.tasks_table.setItem(i, 0, QtWidgets.QTableWidgetItem(str(task.get('id', ''))))
            self.tasks_table.setItem(i, 1, QtWidgets.QTableWidgetItem(str(task.get('task_title', ''))))
            
            scheduled_date = task.get('scheduled_date', '')
            if scheduled_date and hasattr(scheduled_date, 'strftime'):
                scheduled_date = scheduled_date.strftime('%Y/%m/%d')
            elif scheduled_date and isinstance(scheduled_date, str) and '-' in scheduled_date:
                scheduled_date = scheduled_date.replace('-', '/')
            self.tasks_table.setItem(i, 2, QtWidgets.QTableWidgetItem(str(scheduled_date) or "-"))
            
            start_time = str(task.get('scheduled_start_time', ''))[:5] if task.get('scheduled_start_time') else "-"
            self.tasks_table.setItem(i, 3, QtWidgets.QTableWidgetItem(start_time))
            self.tasks_table.setItem(i, 4, QtWidgets.QTableWidgetItem(str(task.get('estimated_duration_minutes', '')) or "-"))
            self.tasks_table.setItem(i, 5, QtWidgets.QTableWidgetItem(str(task.get('assigned_to_team', '')) or "-"))

            status_item = QtWidgets.QTableWidgetItem(status_icons.get(task.get('execution_status', 'pending'), '⏳ در انتظار'))
            if task.get('execution_status') == 'completed':
                status_item.setForeground(QtGui.QColor('#4EC9B0'))
            elif task.get('execution_status') == 'delayed':
                status_item.setForeground(QtGui.QColor('#F48771'))
            self.tasks_table.setItem(i, 6, status_item)

            btn_widget = QtWidgets.QWidget()
            btn_layout = QtWidgets.QHBoxLayout(btn_widget)
            btn_layout.setContentsMargins(2, 2, 2, 2)
            btn_layout.setSpacing(2)

            complete_btn = QtWidgets.QToolButton()
            complete_btn.setIcon(qta.icon('fa5s.check-circle', color='#4EC9B0'))
            complete_btn.setIconSize(QtCore.QSize(14, 14))
            complete_btn.setToolTip("تکمیل وظیفه")
            complete_btn.setFixedSize(24, 24)
            complete_btn.setStyleSheet(glass_icon_style_small)
            complete_btn.clicked.connect(lambda checked, tid=task['id']: self.complete_maintenance_task(tid))

            edit_btn = QtWidgets.QToolButton()
            edit_btn.setIcon(qta.icon('fa5s.edit', color='#569CD6'))
            edit_btn.setIconSize(QtCore.QSize(14, 14))
            edit_btn.setToolTip("ویرایش وظیفه")
            edit_btn.setFixedSize(24, 24)
            edit_btn.setStyleSheet(glass_icon_style_small)
            edit_btn.clicked.connect(lambda checked, tid=task['id']: self.edit_maintenance_task(tid))

            delete_btn = QtWidgets.QToolButton()
            delete_btn.setIcon(qta.icon('fa5s.trash-alt', color='#F48771'))
            delete_btn.setIconSize(QtCore.QSize(14, 14))
            delete_btn.setToolTip("حذف وظیفه")
            delete_btn.setFixedSize(24, 24)
            delete_btn.setStyleSheet(glass_icon_style_small)
            delete_btn.clicked.connect(lambda checked, tid=task['id']: self.delete_maintenance_task(tid))

            btn_layout.addWidget(complete_btn)
            btn_layout.addWidget(edit_btn)
            btn_layout.addWidget(delete_btn)
            btn_layout.addStretch()
            
            self.tasks_table.setCellWidget(i, 7, btn_widget)
        
        self.update_task_stats(tasks)

    # ==================== عملیات روی برنامه‌ها ====================

    def create_new_plan(self):
        # بررسی اینکه نوع تجهیزات انتخاب شده باشد
        asset_type = self.asset_type_combo.currentData()
        if asset_type is None:
            QtWidgets.QMessageBox.warning(self, "خطا", 
                "لطفاً ابتدا یک نوع تجهیزات را از کامبوباکس انتخاب کنید.\n"
                "در حالت 'همه تجهیزات' نمی‌توانید برنامه جدید ایجاد کنید.")
            return
        
        dialog = MaintenancePlanDialog(self)
        if dialog.exec_():
            data = dialog.result_data
            try:
                start_date = data['start_date'].replace('/', '-')
                end_date = data['end_date'].replace('/', '-')
                
                result = self.db.execute_query("""
                    INSERT INTO maintenance_plans 
                    (plan_title, plan_type, start_date, end_date, asset_type, plan_status, notes)
                    VALUES (%s, %s, %s, %s, %s, 'draft', %s)
                """, (data['plan_title'], data['plan_type'], start_date, end_date, 
                      asset_type, data['notes']))
                
                if result:
                    self.load_plans()
                    QtWidgets.QMessageBox.information(self, "موفق", "برنامه نت جدید با موفقیت ایجاد شد")
                else:
                    QtWidgets.QMessageBox.warning(self, "خطا", "خطا در ذخیره برنامه نت")
            except Exception as e:
                QtWidgets.QMessageBox.warning(self, "خطا", f"خطا: {str(e)}")

    def edit_plan(self):
        if not self.current_maintenance_plan_id:
            QtWidgets.QMessageBox.warning(self, "خطا", "هیچ برنامهای انتخاب نشده است")
            return

        plan = self.db.fetch_one("SELECT * FROM maintenance_plans WHERE id = %s", (self.current_maintenance_plan_id,))
        
        if not plan:
            QtWidgets.QMessageBox.warning(self, "خطا", "برنامه یافت نشد")
            return
            
        if plan.get('plan_status') not in ['draft', 'cancelled']:
            QtWidgets.QMessageBox.warning(self, "خطا", "فقط برنامه‌های در وضعیت پیشنویس یا لغو شده قابل ویرایش هستند")
            return

        dialog = MaintenancePlanDialog(self, plan=plan)
        if dialog.exec_():
            data = dialog.result_data
            try:
                start_date = data['start_date'].replace('/', '-')
                end_date = data['end_date'].replace('/', '-')
                
                self.db.execute_query("""
                    UPDATE maintenance_plans 
                    SET plan_title = %s, plan_type = %s, start_date = %s, end_date = %s, notes = %s
                    WHERE id = %s
                """, (data['plan_title'], data['plan_type'], start_date, end_date, 
                      data['notes'], self.current_maintenance_plan_id))
                
                self.load_plans()
                self.current_plan = self.db.fetch_one("SELECT * FROM maintenance_plans WHERE id = %s", (self.current_maintenance_plan_id,))
                if self.current_plan:
                    status_names = {'draft': 'پیشنویس', 'submitted': 'ارسال شده', 'approved': 'تایید شده', 
                                   'in_progress': 'در حال اجرا', 'completed': 'تکمیل شده', 'cancelled': 'لغو شده'}
                    plan_type_fa = {"daily": "روزانه", "weekly": "هفتگی", "monthly": "ماهانه", "yearly": "سالانه"}.get(self.current_plan['plan_type'], self.current_plan['plan_type'])
                    self.plan_info.setText(f"📋 {self.current_plan['plan_title']} ({plan_type_fa}) - {self.current_plan['start_date']} تا {self.current_plan['end_date']} | وضعیت: {status_names.get(self.current_plan['plan_status'], self.current_plan['plan_status'])}")
                
                QtWidgets.QMessageBox.information(self, "موفق", "برنامه نت با موفقیت ویرایش شد")
            except Exception as e:
                QtWidgets.QMessageBox.warning(self, "خطا", f"خطا در ویرایش برنامه نت:\n{str(e)}")

    def submit_plan(self):
        if not self.current_maintenance_plan_id:
            QtWidgets.QMessageBox.warning(self, "خطا", "هیچ برنامهای انتخاب نشده است")
            return

        reply = QtWidgets.QMessageBox.question(
            self, "تأیید ارسال",
            "آیا از ارسال این برنامه برای تایید مطمئن هستید؟\nپس از ارسال، برنامه قابل ویرایش نخواهد بود.",
            QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No
        )
        if reply == QtWidgets.QMessageBox.Yes:
            self.db.execute_query("UPDATE maintenance_plans SET plan_status = 'submitted' WHERE id = %s", 
                                  (self.current_maintenance_plan_id,))
            self.load_plans()
            if self.current_maintenance_plan_id:
                self.current_plan = self.db.fetch_one("SELECT * FROM maintenance_plans WHERE id = %s", (self.current_maintenance_plan_id,))
                plan_type_fa = {"daily": "روزانه", "weekly": "هفتگی", "monthly": "ماهانه", "yearly": "سالانه"}.get(self.current_plan['plan_type'], self.current_plan['plan_type'])
                self.plan_info.setText(f"📋 {self.current_plan['plan_title']} ({plan_type_fa}) - {self.current_plan['start_date']} تا {self.current_plan['end_date']} | وضعیت: ارسال شده")
            self.submit_plan_btn.setEnabled(False)
            self.edit_plan_btn.setEnabled(False)
            self.add_task_btn.setEnabled(False)
            QtWidgets.QMessageBox.information(self, "موفق", "برنامه با موفقیت ارسال شد")

    def delete_plan(self):
        if not self.current_maintenance_plan_id:
            return
        reply = QtWidgets.QMessageBox.question(self, "تأیید", "آیا از حذف این برنامه مطمئن هستید؟",
                                               QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)
        if reply == QtWidgets.QMessageBox.Yes:
            self.db.execute_query("DELETE FROM maintenance_plans WHERE id = %s", (self.current_maintenance_plan_id,))
            self.load_plans()
            self.tasks_table.setRowCount(0)
            self.plan_info.setText("برنامهای انتخاب نشده است")
            self.current_maintenance_plan_id = None
            self.current_plan = None
            self.add_task_btn.setEnabled(False)
            self.edit_plan_btn.setEnabled(False)
            self.submit_plan_btn.setEnabled(False)
            self.delete_plan_btn.setEnabled(False)

    # ==================== عملیات روی وظایف ====================

    def add_task(self):
        if not self.current_maintenance_plan_id:
            QtWidgets.QMessageBox.warning(self, "خطا", "لطفاً برنامه را انتخاب کنید")
            return
        
        dialog = TaskDialog(self, self.current_maintenance_plan_id, is_maintenance=True)
        if dialog.exec_():
            data = dialog.result_data
            try:
                scheduled_date = data['scheduled_date'].replace('/', '-')
                
                self.db.execute_query("""
                    INSERT INTO maintenance_plan_tasks 
                    (plan_id, task_title, task_description, scheduled_date, 
                     scheduled_start_time, estimated_duration_minutes, assigned_to_team, 
                     priority_level, execution_status)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, 'pending')
                """, (self.current_maintenance_plan_id, 
                      data['task_title'], 
                      data['task_description'],
                      scheduled_date, 
                      data['scheduled_start_time'],
                      data['estimated_duration_minutes'], 
                      data['assigned_to_unit'],
                      data['priority_level']))
                
                self.load_tasks()
                QtWidgets.QMessageBox.information(self, "موفق", "وظیفه با موفقیت اضافه شد")
            except Exception as e:
                QtWidgets.QMessageBox.warning(self, "خطا", f"خطا: {str(e)}")

    def edit_maintenance_task(self, task_id):
        task = self.db.fetch_one("SELECT * FROM maintenance_plan_tasks WHERE id = %s", (task_id,))
        if task:
            dialog = TaskDialog(self, self.current_maintenance_plan_id, is_maintenance=True, task=task)
            if dialog.exec_():
                self.load_tasks()
                QtWidgets.QMessageBox.information(self, "موفق", "وظیفه با موفقیت ویرایش شد")

    def delete_maintenance_task(self, task_id):
        reply = QtWidgets.QMessageBox.question(self, "تأیید حذف", 
            "آیا از حذف این وظیفه مطمئن هستید؟",
            QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)
        if reply == QtWidgets.QMessageBox.Yes:
            self.db.execute_query("DELETE FROM maintenance_plan_tasks WHERE id = %s", (task_id,))
            self.load_tasks()
            QtWidgets.QMessageBox.information(self, "موفق", "وظیفه با موفقیت حذف شد")

    def complete_maintenance_task(self, task_id):
        self.db.execute_query("UPDATE maintenance_plan_tasks SET execution_status = 'completed' WHERE id = %s", (task_id,))
        self.load_tasks()
        QtWidgets.QMessageBox.information(self, "موفق", "وظیفه با موفقیت تکمیل شد")