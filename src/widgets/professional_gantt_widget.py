# src/widgets/professional_gantt_widget.py

"""
Gantt chart view widget for visualizing project timeline and task dependencies.
Adapted for ERP-Aqua with Persian language support - RTL Version.
"""

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QGraphicsView,
                             QGraphicsScene, QGraphicsRectItem, QGraphicsTextItem,
                             QGraphicsLineItem, QPushButton, QLabel, QGraphicsWidget,
                             QScrollArea, QGraphicsPathItem)
from PyQt5.QtCore import Qt, pyqtSignal, QRectF, QPointF, QLineF
from PyQt5.QtGui import QColor, QPen, QBrush, QFont, QPainter, QPainterPath
from datetime import datetime, timedelta
import jdatetime


class GanttBar(QGraphicsRectItem):
    """Gantt chart bar representing a task."""
    
    def __init__(self, task, x, y, width, height, min_date, day_width):
        super().__init__(x, y, width, height)
        self.task = task
        self.min_date = min_date
        self.day_width = day_width
        
        # تبدیل تاریخ به شمسی برای تولتیپ
        start_shamsi = self._to_shamsi(task['start_date'])
        end_shamsi = self._to_shamsi(task['end_date'])
        
        # تشخیص تاخیر
        is_delayed = task.get('status') == 'delayed'
        progress = task.get('progress', 0)
        
        # تنظیم رنگ بر اساس نوع وظیفه
        colors = {
            'feeding': QColor(78, 201, 176),     # سبز - تغذیه
            'biomass': QColor(86, 156, 214),     # آبی - زیست توده
            'harvest': QColor(206, 145, 120),    # قهوه‌ای - برداشت
            'maintenance': QColor(244, 135, 113), # قرمز - تعمیرات
            'inspection': QColor(218, 165, 32),   # زرد - بازرسی
            'other': QColor(150, 150, 150)        # خاکستری - سایر
        }
        color = colors.get(task.get('type', 'other'), QColor(100, 100, 100))
        
        # اگر وظیفه تاخیر داشته باشد، رنگ قرمزتر می‌شود
        if is_delayed:
            color = QColor(220, 50, 50)
        
        # تنظیم شفافیت بر اساس پیشرفت
        if progress >= 100:
            color.setAlpha(150)
        
        self.setBrush(QBrush(color))
        self.setPen(QPen(color.darker(120), 1.5))
        self.setFlag(QGraphicsRectItem.ItemIsSelectable, True)
        
        # تولتیپ با اطلاعات کامل
        tooltip = f"""
        <div style="direction:rtl; padding:5px;">
            <b>{task['title']}</b><br>
            قفس: {task['cage']}<br>
            نوع: {self._get_type_name(task.get('type', 'other'))}<br>
            شروع: {start_shamsi}<br>
            پایان: {end_shamsi}<br>
            مدت: {task['duration']} روز<br>
            پیشرفت: {progress}%<br>
            {self._get_delay_text(task) if is_delayed else ''}
        </div>
        """
        self.setToolTip(tooltip)
    
    def _to_shamsi(self, dt):
        try:
            jd = jdatetime.date.fromgregorian(date=dt.date())
            return f"{jd.year}/{jd.month:02d}/{jd.day:02d}"
        except:
            return dt.strftime("%Y/%m/%d")
    
    def _get_type_name(self, type_key):
        types = {
            'feeding': 'تغذیه',
            'biomass': 'زیست توده',
            'harvest': 'برداشت',
            'maintenance': 'تعمیرات',
            'inspection': 'بازرسی',
            'other': 'سایر'
        }
        return types.get(type_key, type_key)
    
    def _get_delay_text(self, task):
        if task.get('status') == 'delayed':
            return f"<span style='color:#F48771;'>⚠️ تاخیر: {task.get('delay_days', 0)} روز</span>"
        return ""


class DependencyArrow(QGraphicsPathItem):
    """خط اتصال بین وظایف با فلش"""
    
    def __init__(self, start_point, end_point):
        super().__init__()
        self.start_point = start_point
        self.end_point = end_point
        self.setup_path()
        self.setPen(QPen(QColor(150, 150, 150), 1.5, Qt.DashLine))
        self.setBrush(QBrush(QColor(150, 150, 150)))
        self.setZValue(0)
    
    def setup_path(self):
        path = QPainterPath()
        path.moveTo(self.start_point)
        
        # محاسبه نقطه کنترلی برای منحنی
        cp1 = QPointF(self.start_point.x() + (self.end_point.x() - self.start_point.x()) * 0.5,
                      self.start_point.y())
        cp2 = QPointF(self.start_point.x() + (self.end_point.x() - self.start_point.x()) * 0.5,
                      self.end_point.y())
        
        path.cubicTo(cp1, cp2, self.end_point)
        
        # اضافه کردن فلش در انتها
        angle = 0
        if self.end_point.x() > self.start_point.x():
            angle = -45
        else:
            angle = -135
        
        import math
        arrow_size = 8
        arrow_angle = math.radians(angle + 160)
        arrow_point1 = QPointF(self.end_point.x() - arrow_size * math.cos(arrow_angle),
                               self.end_point.y() - arrow_size * math.sin(arrow_angle))
        arrow_angle2 = math.radians(angle - 160)
        arrow_point2 = QPointF(self.end_point.x() - arrow_size * math.cos(arrow_angle2),
                               self.end_point.y() - arrow_size * math.sin(arrow_angle2))
        
        self.setPath(path)


class ProfessionalGanttWidget(QWidget):
    """Gantt chart view widget for timeline visualization - RTL Version."""
    
    task_selected = pyqtSignal(object)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.tasks = []
        self.row_height = 45
        self.day_width = 35
        self.label_width = 220
        self.init_ui()
    
    def init_ui(self):
        """Initialize the Gantt view UI."""
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Header
        header = QHBoxLayout()
        self.title_label = QLabel("📊 نمودار گانت - برنامه زمانی وظایف")
        self.title_label.setStyleSheet("font-size: 14px; font-weight: bold; color: #569CD6;")
        
        self.zoom_in_button = QPushButton("🔍+ بزرگنمایی")
        self.zoom_out_button = QPushButton("🔍- کوچکنمایی")
        self.refresh_button = QPushButton("🔄 بروزرسانی")
        
        for btn in [self.zoom_in_button, self.zoom_out_button, self.refresh_button]:
            btn.setStyleSheet("""
                QPushButton {
                    background-color: #0E639C;
                    color: white;
                    border: none;
                    border-radius: 4px;
                    padding: 6px 12px;
                    font-weight: bold;
                }
                QPushButton:hover { background-color: #1177BB; }
            """)
        
        header.addWidget(self.title_label)
        header.addStretch()
        header.addWidget(self.zoom_in_button)
        header.addWidget(self.zoom_out_button)
        header.addWidget(self.refresh_button)
        
        layout.addLayout(header)
        
        # Scroll area for Gantt chart
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setStyleSheet("border: none; background: #1E1E1E;")
        
        # Graphics view
        self.scene = QGraphicsScene()
        self.view = QGraphicsView(self.scene)
        self.view.setRenderHint(QPainter.Antialiasing)
        self.view.setStyleSheet("border: 1px solid #3E3E42; border-radius: 4px; background: #1E1E1E;")
        self.view.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.view.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        
        self.scroll_area.setWidget(self.view)
        layout.addWidget(self.scroll_area)
        
        # Legend
        legend_layout = QHBoxLayout()
        legend_layout.addWidget(QLabel("راهنما:"))
        
        types = [
            ("تغذیه", QColor(78, 201, 176)),
            ("زیست توده", QColor(86, 156, 214)),
            ("برداشت", QColor(206, 145, 120)),
            ("تعمیرات", QColor(244, 135, 113)),
            ("بازرسی", QColor(218, 165, 32)),
            ("تاخیر", QColor(220, 50, 50)),
            ("سایر", QColor(150, 150, 150))
        ]
        
        for name, color in types:
            color_label = QLabel("■")
            color_label.setStyleSheet(f"color: rgb({color.red()}, {color.green()}, {color.blue()}); font-size: 16px;")
            legend_layout.addWidget(color_label)
            legend_layout.addWidget(QLabel(name))
        
        legend_layout.addStretch()
        layout.addLayout(legend_layout)
        
        self.setLayout(layout)
        
        # Connect signals
        self.zoom_in_button.clicked.connect(self.zoom_in)
        self.zoom_out_button.clicked.connect(self.zoom_out)
        self.refresh_button.clicked.connect(self.refresh)
    
    def load_tasks(self, tasks):
        """بارگذاری وظایف و رسم گانت چارت"""
        self.tasks = tasks
        self.draw_gantt_chart()
    
    def draw_gantt_chart(self):
        """Draw the Gantt chart."""
        self.scene.clear()
        
        if not self.tasks:
            text = self.scene.addText("هیچ وظیفه‌ای برای نمایش وجود ندارد.\nبرای افزودن وظیفه، از بخش برنامه‌ریزی استفاده کنید.")
            text.setPos(20, 20)
            text.setDefaultTextColor(QColor(200, 200, 200))
            return
        
        # Find date range
        min_date = min(task['start_date'] for task in self.tasks)
        max_date = max(task['end_date'] for task in self.tasks)
        
        # Add padding
        min_date = min_date - timedelta(days=2)
        max_date = max_date + timedelta(days=2)
        
        total_days = (max_date - min_date).days
        
        # Draw timeline header
        self.draw_timeline_header(min_date, total_days)
        
        # Draw tasks
        y_offset = 80
        self.task_bars = []
        
        for idx, task in enumerate(sorted(self.tasks, key=lambda x: x['start_date'])):
            # Draw task label (راست‌چین)
            label_text = f"{task['cage']} | {task['title'][:25]}"
            label = QGraphicsTextItem(label_text)
            # محاسبه موقعیت برای راست‌چین: از سمت راست شروع می‌شود
            label_width = label.boundingRect().width()
            label_x = self.label_width - label_width - 10
            label.setPos(label_x, y_offset + 12)
            label.setDefaultTextColor(QColor(200, 200, 200))
            label.setFont(QFont("Segoe UI", 9))
            self.scene.addItem(label)
            
            # Calculate bar position
            start_day = (task['start_date'] - min_date).days
            duration_days = (task['end_date'] - task['start_date']).days
            
            if duration_days < 1:
                duration_days = 1
            
            x = self.label_width + start_day * self.day_width
            y = y_offset
            width = duration_days * self.day_width
            height = self.row_height - 12
            
            # Draw task bar
            bar = GanttBar(task, x, y, width, height, min_date, self.day_width)
            self.scene.addItem(bar)
            self.task_bars.append(bar)
            
            # Draw progress indicator
            progress = task.get('progress', 0)
            if progress > 0:
                progress_width = width * (progress / 100.0)
                progress_bar = QGraphicsRectItem(x, y, progress_width, height)
                progress_bar.setBrush(QBrush(QColor(50, 205, 50, 150)))
                progress_bar.setPen(QPen(Qt.NoPen))
                self.scene.addItem(progress_bar)
            
            # Draw percentage text
            if progress > 0:
                percent_text = QGraphicsTextItem(f"{progress}%")
                percent_x = x + width - 35
                percent_y = y + height / 2 - 6
                percent_text.setPos(percent_x, percent_y)
                percent_text.setDefaultTextColor(QColor(255, 255, 255))
                percent_text.setFont(QFont("Segoe UI", 8, QFont.Bold))
                self.scene.addItem(percent_text)
            
            # Draw dependency arrows
            if task.get('dependencies'):
                for dep_id in task['dependencies']:
                    dep_task = next((t for t in self.tasks if t['id'] == dep_id), None)
                    if dep_task:
                        # پیدا کردن موقعیت وظیفه وابسته
                        dep_start_day = (dep_task['start_date'] - min_date).days
                        dep_duration = (dep_task['end_date'] - dep_task['start_date']).days
                        dep_x = self.label_width + (dep_start_day + dep_duration) * self.day_width
                        dep_y = 80 + (self.tasks.index(dep_task)) * self.row_height + self.row_height / 2
                        
                        task_x = x
                        task_y = y + height / 2
                        
                        # رسم فلش
                        arrow = DependencyArrow(QPointF(dep_x, dep_y), QPointF(task_x, task_y))
                        self.scene.addItem(arrow)
            
            y_offset += self.row_height
        
        # Set scene rect
        scene_width = self.label_width + total_days * self.day_width + 100
        scene_height = y_offset + 50
        self.scene.setSceneRect(0, 0, scene_width, scene_height)
        self.view.setSceneRect(0, 0, scene_width, scene_height)
    
    def draw_timeline_header(self, start_date, total_days):
        """Draw the timeline header with dates."""
        y = 15
        x = self.label_width
        
        # Draw background
        header_bg = QGraphicsRectItem(x, 0, total_days * self.day_width, 65)
        header_bg.setBrush(QBrush(QColor(37, 37, 38)))
        header_bg.setPen(QPen(Qt.NoPen))
        self.scene.addItem(header_bg)
        
        # Draw month labels (شمسی - راست‌چین)
        current_month = None
        month_start_x = x
        month_names = ['فروردین', 'اردیبهشت', 'خرداد', 'تیر', 'مرداد', 'شهریور',
                       'مهر', 'آبان', 'آذر', 'دی', 'بهمن', 'اسفند']
        
        # Draw day grid lines
        for day in range(total_days + 1):
            line_x = x + day * self.day_width
            date = start_date + timedelta(days=day)
            shamsi_date = jdatetime.date.fromgregorian(date=date)
            
            # Month label
            if shamsi_date.month != current_month:
                if current_month is not None:
                    month_width = line_x - month_start_x
                    if month_width > 30:
                        month_text = QGraphicsTextItem(
                            f"{month_names[shamsi_date.month - 1]} {shamsi_date.year}"
                        )
                        month_text.setPos(month_start_x + (month_width - month_text.boundingRect().width()) / 2, y)
                        month_text.setDefaultTextColor(QColor(86, 156, 214))
                        month_text.setFont(QFont("Segoe UI", 9, QFont.Bold))
                        self.scene.addItem(month_text)
                
                current_month = shamsi_date.month
                month_start_x = line_x
            
            # Day number
            if day % 7 == 0 or day == total_days:
                # Draw vertical line
                line = QGraphicsLineItem(line_x, 45, line_x, 65)
                line.setPen(QPen(QColor(62, 62, 66), 1))
                self.scene.addItem(line)
                
                # Day number text
                day_text = QGraphicsTextItem(f"{shamsi_date.day}")
                day_text.setPos(line_x + 5, 48)
                day_text.setDefaultTextColor(QColor(150, 150, 150))
                day_text.setFont(QFont("Segoe UI", 8))
                self.scene.addItem(day_text)
        
        # Draw final month label
        final_date = start_date + timedelta(days=total_days)
        final_shamsi = jdatetime.date.fromgregorian(date=final_date)
        final_x = x + total_days * self.day_width
        month_width = final_x - month_start_x
        if month_width > 30:
            month_text = QGraphicsTextItem(f"{month_names[final_shamsi.month - 1]} {final_shamsi.year}")
            month_text.setPos(month_start_x + (month_width - month_text.boundingRect().width()) / 2, y)
            month_text.setDefaultTextColor(QColor(86, 156, 214))
            month_text.setFont(QFont("Segoe UI", 9, QFont.Bold))
            self.scene.addItem(month_text)
        
        # Draw bottom line
        bottom_line = QGraphicsLineItem(self.label_width, 65, x + total_days * self.day_width, 65)
        bottom_line.setPen(QPen(QColor(86, 156, 214), 2))
        self.scene.addItem(bottom_line)
    
    def zoom_in(self):
        """Zoom in the Gantt chart."""
        self.day_width = min(self.day_width * 1.3, 80)
        self.draw_gantt_chart()
    
    def zoom_out(self):
        """Zoom out the Gantt chart."""
        self.day_width = max(self.day_width / 1.3, 20)
        self.draw_gantt_chart()
    
    def refresh(self):
        """Refresh the Gantt chart."""
        self.draw_gantt_chart()