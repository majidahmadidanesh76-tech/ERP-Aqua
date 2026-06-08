"""
تب گانت چارت - نمایش برنامه زمانی وظایف
"""

from PyQt5 import QtWidgets, QtCore, QtGui
import qtawesome as qta

from ...database.db_handler import DatabaseHandler
from ...widgets.gantt_chart_widget import EditableGanttWidget


class GanttTab(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.db = DatabaseHandler()
        self.setup_ui()
        self.load_data()

    def setup_ui(self):
        layout = QtWidgets.QVBoxLayout(self)
        layout.setSpacing(10)
        layout.setContentsMargins(10, 10, 10, 10)

        title = QtWidgets.QLabel("📊 نمای گانت - برنامه زمانی وظایف")
        title.setAlignment(QtCore.Qt.AlignCenter)
        title.setStyleSheet("font-size: 14px; font-weight: bold; color: #569CD6; padding: 5px;")
        layout.addWidget(title)

        # نوار ابزار
        toolbar = QtWidgets.QHBoxLayout()
        
        glass_icon_style = """
            QToolButton {
                background-color: rgba(60, 60, 65, 180);
                border: 1px solid rgba(86, 156, 214, 80);
                border-radius: 3px;
            }
            QToolButton:hover { background-color: rgba(86, 156, 214, 100); }
        """

        self.refresh_btn = QtWidgets.QToolButton()
        self.refresh_btn.setIcon(qta.icon('fa5s.sync-alt', color='#C8C8C8'))
        self.refresh_btn.setFixedSize(30, 30)
        self.refresh_btn.setStyleSheet(glass_icon_style)
        self.refresh_btn.setToolTip("بروزرسانی گانت چارت")
        self.refresh_btn.clicked.connect(self.load_data)
        toolbar.addWidget(self.refresh_btn)

        # فیلتر بر اساس قفس
        toolbar.addWidget(QtWidgets.QLabel("فیلتر قفس:"))
        self.cage_filter = QtWidgets.QComboBox()
        self.cage_filter.setMinimumWidth(120)
        self.cage_filter.addItem("همه قفس‌ها", None)
        self.cage_filter.currentIndexChanged.connect(self.on_filter_changed)
        toolbar.addWidget(self.cage_filter)

        toolbar.addStretch()
        layout.addLayout(toolbar)

        # ویجت گانت
        self.gantt_widget = EditableGanttWidget()
        layout.addWidget(self.gantt_widget)

        # بارگذاری لیست قفس‌ها
        self.load_cages()

    def load_cages(self):
        """بارگذاری لیست قفس‌ها برای فیلتر"""
        cages = self.db.fetch_all("SELECT id FROM cages ORDER BY id")
        for cage in cages:
            self.cage_filter.addItem(cage['id'], cage['id'])

    def on_filter_changed(self):
        """تغییر فیلتر قفس"""
        self.load_data()

    def load_data(self):
        """بارگذاری داده‌های واقعی از دیتابیس در گانت چارت"""
        try:
            cage_filter = self.cage_filter.currentData()
            
            if cage_filter:
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
                    WHERE pp.cage_id = %s
                    ORDER BY pt.scheduled_date
                """, (cage_filter,))
            else:
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
                        'title': task['title'][:25],
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
            {'id': 2, 'title': 'زیست توده قفس 1', 'cage': 'Cage-001', 'type': 'biomass', 'start_day': 10, 'duration': 1, 'amount': None},
            {'id': 3, 'title': 'برداشت قفس 2', 'cage': 'Cage-002', 'type': 'harvest', 'start_day': 8, 'duration': 3, 'amount': 5000},
            {'id': 4, 'title': 'تعمیرات تور قفس 2', 'cage': 'Cage-002', 'type': 'maintenance', 'start_day': 15, 'duration': 2, 'amount': None},
            {'id': 5, 'title': 'بازرسی قفس 3', 'cage': 'Cage-003', 'type': 'inspection', 'start_day': 12, 'duration': 1, 'amount': None},
        ]
        
        cage_filter = self.cage_filter.currentData()
        if cage_filter:
            sample_tasks = [t for t in sample_tasks if t['cage'] == cage_filter]
            
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