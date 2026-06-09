"""
تب گانت چارت – نسخه حرفه‌ای با QGraphicsView
"""

from PyQt5 import QtWidgets, QtCore
from datetime import datetime, timedelta
import jdatetime

from ...database.db_handler import DatabaseHandler
from ...widgets.professional_gantt_widget import ProfessionalGanttWidget


class GanttTab(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.db = DatabaseHandler()
        self.setup_ui()
        QtCore.QTimer.singleShot(500, self.load_data)

    def setup_ui(self):
        layout = QtWidgets.QVBoxLayout(self)
        layout.setSpacing(10)
        layout.setContentsMargins(10, 10, 10, 10)

        # عنوان
        title = QtWidgets.QLabel("📊 نمودار گانت حرفه‌ای - برنامه زمانی وظایف")
        title.setAlignment(QtCore.Qt.AlignCenter)
        title.setStyleSheet("font-size: 14px; font-weight: bold; color: #569CD6; padding: 5px;")
        layout.addWidget(title)

        # فیلترها
        filter_layout = QtWidgets.QHBoxLayout()
        filter_layout.setSpacing(10)

        filter_layout.addWidget(QtWidgets.QLabel("قفس:"))
        self.cage_combo = QtWidgets.QComboBox()
        self.cage_combo.addItem("همه", None)
        self.cage_combo.currentIndexChanged.connect(self.load_data)
        filter_layout.addWidget(self.cage_combo)

        filter_layout.addStretch()

        self.refresh_btn = QtWidgets.QPushButton("🔄 بروزرسانی")
        self.refresh_btn.clicked.connect(self.load_data)
        filter_layout.addWidget(self.refresh_btn)

        layout.addLayout(filter_layout)

        # ویجت گانت حرفه‌ای
        self.gantt_widget = ProfessionalGanttWidget()
        layout.addWidget(self.gantt_widget)

        self.load_cages()

    def load_cages(self):
        try:
            cages = self.db.fetch_all("SELECT id FROM cages ORDER BY id")
            for cage in cages:
                self.cage_combo.addItem(cage['id'], cage['id'])
        except Exception as e:
            print(f"خطا: {e}")

    def load_data(self):
        cage_filter = self.cage_combo.currentData()

        query = """
            SELECT pt.id, pt.task_title as title, pt.category as type,
                   pt.scheduled_date, pt.estimated_duration_minutes as duration,
                   pp.cage_id as cage, pt.execution_status
            FROM plan_tasks pt
            LEFT JOIN production_plans pp ON pt.plan_id = pp.id
            WHERE 1=1
        """
        params = []
        if cage_filter:
            query += " AND pp.cage_id = %s"
            params.append(cage_filter)

        tasks_data = self.db.fetch_all(query, params)
        if not tasks_data:
            self.gantt_widget.load_tasks([])
            return

        tasks = []
        for t in tasks_data:
            start_date_raw = t['scheduled_date']
            if start_date_raw and hasattr(start_date_raw, 'year'):
                start_date = datetime(start_date_raw.year, start_date_raw.month, start_date_raw.day)
            else:
                continue

            duration_days = max(1, t['duration'] / (24 * 60))
            end_date = start_date + timedelta(days=duration_days)
            
            # تشخیص وضعیت تاخیر (اگر تاریخ پایان از امروز گذشته و کامل نشده)
            today = datetime.now().date()
            status = t['execution_status']
            delay_days = 0
            
            if status != 'completed' and end_date.date() < today:
                status = 'delayed'
                delay_days = (today - end_date.date()).days
            
            progress = 100 if status == 'completed' else 0
            cage = t.get('cage') if t.get('cage') else "نامشخص"

            task_type = t['type'] or 'other'
            
            tasks.append({
                'id': t['id'],
                'title': t['title'],
                'cage': cage,
                'type': task_type,
                'status': status,
                'delay_days': delay_days,
                'start_date': start_date,
                'end_date': end_date,
                'duration': duration_days,
                'progress': progress,
                'dependencies': []  # برای اضافه کردن وابستگی‌ها در آینده
            })

        self.gantt_widget.load_tasks(tasks)