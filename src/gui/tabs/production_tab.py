"""
تب برنامه پرورش
"""

from PyQt5 import QtWidgets, QtCore, QtGui
import qtawesome as qta
from datetime import datetime

from ...database.db_handler import DatabaseHandler
from ...widgets.jalali_date_edit import JalaliDateEdit
from ..dialogs.plan_dialog import PlanDialog
from ..dialogs.task_dialog import TaskDialog


class ProductionTab(QtWidgets.QWidget):
    def __init__(self, parent=None, farm=None, mooring=None):
        super().__init__(parent)
        self.db = DatabaseHandler()
        self.current_farm = farm
        self.current_mooring = mooring
        self.current_plan_id = None
        self.current_plan = None
        self.setup_ui()
        self.load_data()

    def setup_ui(self):
        layout = QtWidgets.QVBoxLayout(self)
        layout.setSpacing(8)
        layout.setContentsMargins(8, 8, 8, 8)

        # ========== نوار ابزار بالایی ==========
        toolbar = QtWidgets.QHBoxLayout()
        toolbar.setSpacing(8)

        cage_label = QtWidgets.QLabel("قفس:")
        cage_label.setStyleSheet("color: #4EC9B0; font-weight: bold;")
        toolbar.addWidget(cage_label)

        self.cage_combo = QtWidgets.QComboBox()
        self.cage_combo.setMinimumWidth(150)
        self.cage_combo.setFixedHeight(30)
        self.cage_combo.setStyleSheet("""
            QComboBox {
                background-color: #3C3C3C;
                color: #C8C8C8;
                border: 1px solid #3E3E42;
                border-radius: 4px;
                padding: 4px 8px;
            }
            QComboBox:hover { border-color: #569CD6; }
        """)
        self.cage_combo.currentIndexChanged.connect(self.on_cage_changed)
        toolbar.addWidget(self.cage_combo)

        toolbar.addSpacing(15)

        glass_icon_style = """
            QToolButton {
                background-color: rgba(60, 60, 65, 180);
                border: 1px solid rgba(86, 156, 214, 80);
                border-radius: 3px;
            }
            QToolButton:hover {
                background-color: rgba(86, 156, 214, 100);
                border-color: rgba(86, 156, 214, 150);
            }
        """

        self.new_production_btn = QtWidgets.QToolButton()
        self.new_production_btn.setIcon(qta.icon('fa5s.plus', color='#C8C8C8'))
        self.new_production_btn.setIconSize(QtCore.QSize(16, 16))
        self.new_production_btn.setFixedSize(30, 30)
        self.new_production_btn.setToolTip("برنامه پرورش جدید")
        self.new_production_btn.setStyleSheet(glass_icon_style)
        self.new_production_btn.clicked.connect(self.create_new_production_plan)
        toolbar.addWidget(self.new_production_btn)

        self.submit_production_btn = QtWidgets.QToolButton()
        self.submit_production_btn.setIcon(qta.icon('fa5s.paper-plane', color='#C8C8C8'))
        self.submit_production_btn.setIconSize(QtCore.QSize(16, 16))
        self.submit_production_btn.setFixedSize(30, 30)
        self.submit_production_btn.setToolTip("ارسال برنامه")
        self.submit_production_btn.setStyleSheet(glass_icon_style)
        self.submit_production_btn.clicked.connect(self.submit_production_plan)
        self.submit_production_btn.setEnabled(False)
        toolbar.addWidget(self.submit_production_btn)

        refresh_btn = QtWidgets.QToolButton()
        refresh_btn.setIcon(qta.icon('fa5s.sync-alt', color='#C8C8C8'))
        refresh_btn.setIconSize(QtCore.QSize(16, 16))
        refresh_btn.setFixedSize(30, 30)
        refresh_btn.setToolTip("بهروزرسانی")
        refresh_btn.setStyleSheet(glass_icon_style)
        refresh_btn.clicked.connect(self.refresh_production_data)
        toolbar.addWidget(refresh_btn)

        toolbar.addStretch()
        layout.addLayout(toolbar)

        # ========== بخش برنامه‌های پرورش ==========
        plans_label = QtWidgets.QLabel("📌 برنامه‌های پرورش")
        plans_label.setStyleSheet("color: #C8C8C8; font-weight: bold; padding: 5px 0 2px 0;")
        layout.addWidget(plans_label)

        plans_frame = QtWidgets.QFrame()
        plans_frame.setStyleSheet("""
            QFrame {
                background-color: #2D2D30;
                border: 1px solid #3E3E42;
                border-radius: 4px;
            }
        """)
        plans_layout = QtWidgets.QVBoxLayout(plans_frame)
        plans_layout.setContentsMargins(5, 5, 5, 5)
        plans_layout.setSpacing(3)

        self.production_plans_list = QtWidgets.QListWidget()
        self.production_plans_list.setFixedHeight(120)
        self.production_plans_list.setStyleSheet("""
            QListWidget {
                background-color: #252526;
                border: none;
                color: #C8C8C8;
                outline: none;
            }
            QListWidget::item {
                padding: 4px 6px;
                border-bottom: 1px solid #3E3E42;
            }
            QListWidget::item:selected {
                background-color: #0E639C;
                color: white;
            }
            QListWidget::item:hover {
                background-color: #3A3A3A;
            }
        """)
        self.production_plans_list.itemClicked.connect(self.on_production_plan_selected)
        plans_layout.addWidget(self.production_plans_list)

        # دکمه‌های ویرایش/حذف برنامه
        plan_btn_layout = QtWidgets.QHBoxLayout()
        plan_btn_layout.setSpacing(8)
        plan_btn_layout.addStretch()

        glass_btn_style = """
            QPushButton {
                background-color: rgba(60, 60, 65, 200);
                color: #C8C8C8;
                border: 1px solid rgba(86, 156, 214, 80);
                border-radius: 4px;
                font-weight: bold;
                padding: 5px 10px;
            }
            QPushButton:hover {
                background-color: rgba(86, 156, 214, 100);
                color: white;
            }
        """

        self.edit_production_btn = QtWidgets.QPushButton("✏️ ویرایش برنامه")
        self.edit_production_btn.setFixedSize(100, 28)
        self.edit_production_btn.setStyleSheet(glass_btn_style)
        self.edit_production_btn.clicked.connect(self.edit_production_plan)
        self.edit_production_btn.setEnabled(False)

        self.delete_production_btn = QtWidgets.QPushButton("🗑️ حذف برنامه")
        self.delete_production_btn.setFixedSize(100, 28)
        self.delete_production_btn.setStyleSheet(glass_btn_style)
        self.delete_production_btn.clicked.connect(self.delete_production_plan)
        self.delete_production_btn.setEnabled(False)

        plan_btn_layout.addWidget(self.edit_production_btn)
        plan_btn_layout.addWidget(self.delete_production_btn)
        plans_layout.addLayout(plan_btn_layout)

        layout.addWidget(plans_frame)

        # ========== بخش وظایف برنامه ==========
        task_toolbar = QtWidgets.QHBoxLayout()
        task_toolbar.setSpacing(8)

        self.add_production_task_btn = QtWidgets.QPushButton("➕ افزودن وظیفه")
        self.add_production_task_btn.setFixedSize(110, 28)
        self.add_production_task_btn.setStyleSheet(glass_btn_style)
        self.add_production_task_btn.clicked.connect(self.add_production_task)
        self.add_production_task_btn.setEnabled(False)

        task_toolbar.addWidget(self.add_production_task_btn)

        self.production_plan_info = QtWidgets.QLabel("برنامهای انتخاب نشده است")
        self.production_plan_info.setStyleSheet("color: #569CD6; font-size: 11px; padding: 5px;")
        task_toolbar.addWidget(self.production_plan_info)

        task_toolbar.addStretch()
        layout.addLayout(task_toolbar)

        # ========== جدول وظایف ==========
        self.production_tasks_table = QtWidgets.QTableWidget()
        self.production_tasks_table.setAlternatingRowColors(True)
        self.production_tasks_table.setMinimumHeight(250)
        self.production_tasks_table.setColumnCount(8)
        self.production_tasks_table.setHorizontalHeaderLabels([
            "شناسه", "وظیفه", "تاریخ", "زمان", "مدت", "مسئول", "وضعیت", "عملیات"
        ])
        self.production_tasks_table.setColumnWidth(0, 40)
        self.production_tasks_table.setColumnWidth(1, 200)
        self.production_tasks_table.setColumnWidth(2, 85)
        self.production_tasks_table.setColumnWidth(3, 60)
        self.production_tasks_table.setColumnWidth(4, 50)
        self.production_tasks_table.setColumnWidth(5, 110)
        self.production_tasks_table.setColumnWidth(6, 85)
        self.production_tasks_table.setColumnWidth(7, 90)
        self.production_tasks_table.horizontalHeader().setStretchLastSection(False)
        self.production_tasks_table.verticalHeader().setDefaultSectionSize(32)
        self.production_tasks_table.setStyleSheet("""
            QTableWidget {
                border: 1px solid #3E3E42;
                border-radius: 4px;
                background-color: #2D2D30;
                alternate-background-color: #252526;
                gridline-color: #3E3E42;
            }
            QTableWidget::item {
                padding: 3px 3px;
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
                padding: 4px;
                font-weight: bold;
            }
        """)
        layout.addWidget(self.production_tasks_table)

        # ========== نوار وضعیت پایینی ==========
        self.setup_status_bar(layout)

    def setup_status_bar(self, parent_layout):
        """تنظیم نوار وضعیت پایینی"""
        status_frame = QtWidgets.QFrame()
        status_frame.setStyleSheet("""
            QFrame {
                background-color: #252526;
                border-radius: 8px;
                padding: 6px;
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
            label.setStyleSheet("color: #C8C8C8; font-size: 11px; padding: 3px;")
            status_layout.addWidget(label)

        status_layout.addStretch()
        parent_layout.addWidget(status_frame)

    # ==================== توابع بارگذاری داده ====================

    def load_data(self):
        self.load_cages()
        self.load_production_plans()

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

    def load_production_tasks(self):
        """بارگذاری وظایف برنامه پرورش - با پاک کردن کامل جدول قبل از بارگذاری"""
        if not self.current_plan_id:
            self.production_tasks_table.setRowCount(0)
            self.production_tasks_table.clearContents()
            self.update_task_stats([])
            return

        print(f"DEBUG: بارگذاری وظایف برای plan_id = {self.current_plan_id}")
        
        # دریافت وظایف از دیتابیس
        tasks = self.db.fetch_all("""
            SELECT * FROM plan_tasks 
            WHERE plan_id = %s 
            ORDER BY scheduled_date, scheduled_start_time
        """, (self.current_plan_id,))

        print(f"DEBUG: تعداد وظایف یافت شده: {len(tasks)}")
        for task in tasks:
            print(f"DEBUG: task id={task.get('id')}, title={task.get('task_title')}, plan_id={task.get('plan_id')}")

        # پاک کردن کامل جدول قبل از پر کردن مجدد
        self.production_tasks_table.clearContents()
        self.production_tasks_table.setRowCount(0)

        if len(tasks) == 0:
            self.production_tasks_table.setRowCount(1)
            self.production_tasks_table.setSpan(0, 0, 1, 8)
            empty_item = QtWidgets.QTableWidgetItem("هیچ وظیفهای برای این برنامه ثبت نشده است")
            empty_item.setTextAlignment(QtCore.Qt.AlignCenter)
            self.production_tasks_table.setItem(0, 0, empty_item)
            self.update_task_stats([])
            return

        # تنظیم تعداد ردیف‌ها
        self.production_tasks_table.setRowCount(len(tasks))

        status_icons = {
            'pending': '⏳ در انتظار',
            'in_progress': '🔄 در حال انجام', 
            'completed': '✅ انجام شده',
            'delayed': '⚠️ تاخیر',
            'cancelled': '❌ لغو شده'
        }

        glass_icon_style_small = """
            QToolButton {
                background-color: rgba(60, 60, 65, 180);
                border: 1px solid rgba(86, 156, 214, 80);
                border-radius: 3px;
            }
            QToolButton:hover {
                background-color: rgba(86, 156, 214, 100);
                border-color: rgba(86, 156, 214, 150);
            }
        """

        for i, task in enumerate(tasks):
            # ستون 0: شناسه
            self.production_tasks_table.setItem(i, 0, QtWidgets.QTableWidgetItem(str(task.get('id', ''))))
            # ستون 1: عنوان وظیفه
            self.production_tasks_table.setItem(i, 1, QtWidgets.QTableWidgetItem(str(task.get('task_title', ''))))
            # ستون 2: تاریخ
            self.production_tasks_table.setItem(i, 2, QtWidgets.QTableWidgetItem(str(task.get('scheduled_date', '')) if task.get('scheduled_date') else "-"))
            # ستون 3: ساعت شروع
            self.production_tasks_table.setItem(i, 3, QtWidgets.QTableWidgetItem(str(task.get('scheduled_start_time', ''))[:5] if task.get('scheduled_start_time') else "-"))
            # ستون 4: مدت زمان
            self.production_tasks_table.setItem(i, 4, QtWidgets.QTableWidgetItem(str(task.get('estimated_duration_minutes', '')) if task.get('estimated_duration_minutes') else "-"))
            # ستون 5: مسئول
            self.production_tasks_table.setItem(i, 5, QtWidgets.QTableWidgetItem(str(task.get('assigned_to_unit', '')) or "-"))
            
            # ستون 6: وضعیت
            status_item = QtWidgets.QTableWidgetItem(status_icons.get(task.get('execution_status', 'pending'), '⏳ در انتظار'))
            if task.get('execution_status') == 'completed':
                status_item.setForeground(QtGui.QColor('#4EC9B0'))
            elif task.get('execution_status') == 'delayed':
                status_item.setForeground(QtGui.QColor('#F48771'))
            self.production_tasks_table.setItem(i, 6, status_item)

            # ستون 7: دکمه‌های عملیات
            btn_widget = QtWidgets.QWidget()
            btn_layout = QtWidgets.QHBoxLayout(btn_widget)
            btn_layout.setContentsMargins(2, 2, 2, 2)
            btn_layout.setSpacing(2)

            # دکمه تکمیل
            complete_btn = QtWidgets.QToolButton()
            complete_btn.setIcon(qta.icon('fa5s.check-circle', color='#4EC9B0'))
            complete_btn.setIconSize(QtCore.QSize(14, 14))
            complete_btn.setToolTip("تکمیل وظیفه")
            complete_btn.setFixedSize(24, 24)
            complete_btn.setStyleSheet(glass_icon_style_small)
            complete_btn.clicked.connect(lambda checked, tid=task['id']: self.complete_production_task(tid))

            # دکمه ویرایش
            edit_btn = QtWidgets.QToolButton()
            edit_btn.setIcon(qta.icon('fa5s.edit', color='#569CD6'))
            edit_btn.setIconSize(QtCore.QSize(14, 14))
            edit_btn.setToolTip("ویرایش وظیفه")
            edit_btn.setFixedSize(24, 24)
            edit_btn.setStyleSheet(glass_icon_style_small)
            edit_btn.clicked.connect(lambda checked, tid=task['id']: self.edit_production_task(tid))

            # دکمه حذف
            delete_btn = QtWidgets.QToolButton()
            delete_btn.setIcon(qta.icon('fa5s.trash-alt', color='#F48771'))
            delete_btn.setIconSize(QtCore.QSize(14, 14))
            delete_btn.setToolTip("حذف وظیفه")
            delete_btn.setFixedSize(24, 24)
            delete_btn.setStyleSheet(glass_icon_style_small)
            delete_btn.clicked.connect(lambda checked, tid=task['id']: self.delete_production_task(tid))

            btn_layout.addWidget(complete_btn)
            btn_layout.addWidget(edit_btn)
            btn_layout.addWidget(delete_btn)
            btn_layout.addStretch()
            self.production_tasks_table.setCellWidget(i, 7, btn_widget)

        self.update_task_stats(tasks)

    def update_task_stats(self, tasks):
        """بهروزرسانی آمار وظایف"""
        total = len(tasks)
        completed = sum(1 for t in tasks if t.get('execution_status') == 'completed')
        pending = sum(1 for t in tasks if t.get('execution_status') == 'pending')
        delayed = sum(1 for t in tasks if t.get('execution_status') == 'delayed')
        self.total_tasks_label.setText(f"📋 کل وظایف: {total}")
        self.completed_tasks_label.setText(f"✅ انجام شده: {completed}")
        self.pending_tasks_label.setText(f"⏳ در انتظار: {pending}")
        self.delayed_tasks_label.setText(f"⚠️ تاخیر: {delayed}")

    # ==================== رویدادها ====================

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

    def refresh_production_data(self):
        self.load_production_plans()
        if self.current_plan_id:
            self.load_production_tasks()
        QtWidgets.QMessageBox.information(self, "بهروزرسانی", "دادههای برنامه پرورش بهروزرسانی شد")

    # ==================== عملیات روی برنامه‌ها ====================

    def create_new_production_plan(self):
        cage_id = self.cage_combo.currentData()
        if not cage_id:
            QtWidgets.QMessageBox.warning(self, "خطا", "لطفاً قفس را انتخاب کنید")
            return
        dialog = PlanDialog(self, cage_id)
        if dialog.exec_():
            self.load_production_plans()

    def edit_production_plan(self):
        if not self.current_plan_id:
            QtWidgets.QMessageBox.warning(self, "خطا", "هیچ برنامهای انتخاب نشده است")
            return
        if not self.current_plan:
            self.current_plan = self.db.fetch_one("SELECT * FROM production_plans WHERE id = %s", (self.current_plan_id,))
        if self.current_plan and self.current_plan.get('plan_status') in ['draft', 'cancelled']:
            dialog = PlanDialog(self, self.current_plan['cage_id'], self.current_plan)
            if dialog.exec_():
                self.load_production_plans()
                self.load_production_tasks()
        else:
            QtWidgets.QMessageBox.warning(self, "خطا", "فقط برنامههای در وضعیت پیشنویس یا لغو شده قابل ویرایش هستند")

    def delete_production_plan(self):
        if not self.current_plan_id:
            return
        reply = QtWidgets.QMessageBox.question(self, "تأیید", "آیا از حذف این برنامه مطمئن هستید؟",
                                               QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)
        if reply == QtWidgets.QMessageBox.Yes:
            self.db.execute_query("DELETE FROM production_plans WHERE id = %s", (self.current_plan_id,))
            self.load_production_plans()
            self.production_tasks_table.setRowCount(0)
            self.production_plan_info.setText("برنامهای انتخاب نشده است")
            self.submit_production_btn.setEnabled(False)
            self.add_production_task_btn.setEnabled(False)
            self.edit_production_btn.setEnabled(False)
            self.delete_production_btn.setEnabled(False)

    def submit_production_plan(self):
        QtWidgets.QMessageBox.information(self, "اطلاع", "ارسال برنامه در حال توسعه...")

    # ==================== عملیات روی وظایف ====================

    def add_production_task(self):
        """افزودن وظیفه به برنامه پرورش - با دیباگ کامل"""
        if not self.current_plan_id:
            QtWidgets.QMessageBox.warning(self, "خطا", "لطفاً برنامه را انتخاب کنید")
            return
        
        print(f"DEBUG: current_plan_id = {self.current_plan_id}")
        
        dialog = TaskDialog(self, self.current_plan_id)
        if dialog.exec_():
            data = dialog.result_data
            print(f"DEBUG: داده‌های وظیفه: {data}")
            
            try:
                result = self.db.execute_query("""
                    INSERT INTO plan_tasks 
                    (plan_id, task_title, task_description, category, scheduled_date, 
                     scheduled_start_time, estimated_duration_minutes, assigned_to_unit, priority_level, execution_status)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, 'pending')
                """, (self.current_plan_id, data['task_title'], data['task_description'], data['category'],
                      data['scheduled_date'], data['scheduled_start_time'], data['estimated_duration_minutes'],
                      data['assigned_to_unit'], data['priority_level']))
                
                print(f"DEBUG: نتیجه درج: {result}")
                
                if result:
                    self.load_production_tasks()
                    QtWidgets.QMessageBox.information(self, "موفق", "وظیفه با موفقیت اضافه شد")
                else:
                    QtWidgets.QMessageBox.warning(self, "خطا", "خطا در ذخیره وظیفه در دیتابیس")
                    
            except Exception as e:
                print(f"ERROR: {e}")
                import traceback
                traceback.print_exc()
                QtWidgets.QMessageBox.warning(self, "خطا", f"خطا: {str(e)}")

    def complete_production_task(self, task_id):
        self.db.execute_query("UPDATE plan_tasks SET execution_status = 'completed' WHERE id = %s", (task_id,))
        self.load_production_tasks()
        QtWidgets.QMessageBox.information(self, "موفق", "وظیفه با موفقیت تکمیل شد")

    def edit_production_task(self, task_id):
        task = self.db.fetch_one("SELECT * FROM plan_tasks WHERE id = %s", (task_id,))
        if task:
            dialog = TaskDialog(self, self.current_plan_id, is_maintenance=False, task=task)
            if dialog.exec_():
                data = dialog.result_data
                self.db.execute_query("""
                    UPDATE plan_tasks 
                    SET task_title = %s, task_description = %s, category = %s,
                        scheduled_date = %s, scheduled_start_time = %s,
                        estimated_duration_minutes = %s, assigned_to_unit = %s,
                        priority_level = %s
                    WHERE id = %s
                """, (data['task_title'], data['task_description'], data['category'],
                      data['scheduled_date'], data['scheduled_start_time'],
                      data['estimated_duration_minutes'], data['assigned_to_unit'],
                      data['priority_level'], task_id))
                self.load_production_tasks()
                QtWidgets.QMessageBox.information(self, "موفق", "وظیفه با موفقیت ویرایش شد")

    def delete_production_task(self, task_id):
        reply = QtWidgets.QMessageBox.question(self, "تأیید حذف", "آیا از حذف این وظیفه مطمئن هستید?", 
                                               QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)
        if reply == QtWidgets.QMessageBox.Yes:
            self.db.execute_query("DELETE FROM plan_tasks WHERE id = %s", (task_id,))
            self.load_production_tasks()
            QtWidgets.QMessageBox.information(self, "موفق", "وظیفه با موفقیت حذف شد")