"""
ویجت گانت چارت حرفه‌ای برای ERP-Aqua
"""

from PyQt5 import QtWidgets, QtCore, QtGui
import pyqtgraph as pg

class EditableGanttWidget(pg.GraphicsLayoutWidget):
    """ویجت گانت چارت حرفه‌ای"""
    
    taskChanged = QtCore.pyqtSignal(dict)
    taskAdded = QtCore.pyqtSignal(dict)
    taskDeleted = QtCore.pyqtSignal(int)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setBackground('#1E1E1E')
        
        self.plot = self.addPlot()
        self.plot.setLabel('bottom', 'زمان', units='روز از سال')
        self.plot.setLabel('left', 'وظایف')
        self.plot.showGrid(x=True, y=True, alpha=0.2)
        self.plot.setMouseEnabled(x=True, y=False)
        self.plot.setXRange(0, 365, padding=0.05)
        
        self.colors = {
            'feeding': (78, 201, 176),      # سبز
            'biomass': (86, 156, 214),      # آبی
            'harvest': (206, 145, 120),     # قهوه‌ای
            'maintenance': (244, 135, 113), # قرمز
            'inspection': (218, 165, 32),   # نارنجی
            'other': (150, 150, 150),       # خاکستری
        }

    def load_tasks(self, tasks):
        """بارگذاری وظایف در گانت"""
        self.plot.clear()
        
        if not tasks:
            text = pg.TextItem("هیچ وظیفه‌ای وجود ندارد\nبرای افزودن، از بخش برنامه پرورش استفاده کنید", 
                               color='#808080', anchor=(0.5, 0.5))
            text.setPos(180, 5)
            self.plot.addItem(text)
            return
        
        # یافتن حداکثر روز
        max_day = 0
        for task in tasks:
            end = task.get('start_day', 0) + task.get('duration', 1)
            if end > max_day:
                max_day = end
        self.plot.setXRange(0, max_day + 10, padding=0.05)
        
        for i, task in enumerate(tasks):
            row = i
            start = task.get('start_day', 0)
            duration = task.get('duration', 1)
            color = self.colors.get(task.get('type', 'other'), self.colors['other'])
            
            # میله اصلی
            rect = QtWidgets.QGraphicsRectItem(start, row - 0.35, duration, 0.7)
            rect.setBrush(QtGui.QBrush(QtGui.QColor(*color)))
            rect.setPen(QtGui.QPen(QtGui.QColor(255, 255, 255), 1))
            
            # Tooltip با اطلاعات کامل
            tooltip = f"""<b>{task.get('title', 'بدون عنوان')}</b><br/>
            قفس: {task.get('cage', '-')}<br/>
            شروع: روز {start}<br/>
            مدت: {duration} روز<br/>
            نوع: {task.get('type', 'other')}"""
            if task.get('amount'):
                tooltip += f"<br/>مقدار: {task['amount']:,.0f} kg"
            rect.setToolTip(tooltip)
            
            self.plot.addItem(rect)
            
            # عنوان روی میله
            text = pg.TextItem(task.get('title', '')[:12], color='#FFFFFF', anchor=(0, 0.5))
            text.setPos(start + 0.1, row - 0.1)
            self.plot.addItem(text)
            
            # مقدار روی میله (در صورت وجود)
            if task.get('amount'):
                amount_text = pg.TextItem(f"{task['amount']:.0f}", color='#FFD700', anchor=(1, 0.5))
                amount_text.setPos(start + duration - 0.2, row - 0.1)
                self.plot.addItem(amount_text)
        
        # تنظیم محور Y
        ticks = []
        for i, task in enumerate(tasks):
            display = f"{task.get('cage', '')} | {task.get('title', '')[:15]}"
            ticks.append((i, display))
        self.plot.getAxis('left').setTicks([ticks])