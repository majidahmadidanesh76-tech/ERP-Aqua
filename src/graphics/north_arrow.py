"""
فلش شمال برای نمایش جهت در نقشه
این فلش به صورت ثابت در گوشه نقشه نمایش داده می‌شود
"""

from PyQt5 import QtCore, QtGui, QtWidgets


class NorthArrow(QtWidgets.QGraphicsItem):
    """
    فلش شمال به عنوان یک QGraphicsItem
    با قابلیت نادیده گرفتن تبدیلات (برای ثابت ماندن در گوشه)
    """
    
    def __init__(self):
        super().__init__()
        self.setZValue(1000)
        # نادیده گرفتن تبدیلات (زوم و جابجایی) برای ثابت ماندن در گوشه
        self.setFlag(QtWidgets.QGraphicsItem.ItemIgnoresTransformations, True)
    
    def boundingRect(self):
        """محدوده مستطیلی فلش"""
        return QtCore.QRectF(0, 0, 60, 60)
    
    def paint(self, painter, option, widget):
        """رسم فلش شمال"""
        painter.save()
        painter.setRenderHint(QtGui.QPainter.Antialiasing)
        
        # دایره پس‌زمینه
        painter.setBrush(QtGui.QBrush(QtGui.QColor(0, 0, 0, 150)))
        painter.setPen(QtGui.QPen(QtCore.Qt.NoPen))
        painter.drawEllipse(5, 5, 50, 50)
        
        # فلش قرمز رنگ
        painter.setBrush(QtGui.QBrush(QtGui.QColor(255, 80, 80)))
        painter.setPen(QtGui.QPen(QtGui.QColor(255, 100, 100), 2))
        
        path = QtGui.QPainterPath()
        path.moveTo(30, 10)      # نوک فلش
        path.lineTo(38, 45)      # پای راست
        path.lineTo(30, 40)      # وسط پایین
        path.lineTo(22, 45)      # پای چپ
        path.closeSubpath()
        painter.drawPath(path)
        
        # متن "شمال"
        painter.setPen(QtGui.QPen(QtGui.QColor(255, 255, 255)))
        font = QtGui.QFont()
        font.setBold(True)
        font.setPointSize(8)
        painter.setFont(font)
        painter.drawText(20, 58, "شمال")
        
        painter.restore()


class FixedNorthArrow(QtWidgets.QGraphicsView):
    """
    ویجت ثابت برای نمایش فلش شمال در گوشه نقشه
    این کلاس یک QGraphicsView جداگانه است که روی نقشه قرار می‌گیرد
    """
    
    def __init__(self, parent=None):
        super().__init__(parent)
        # تنظیمات برای شفافیت و عدم دریافت رویدادهای ماوس
        self.setStyleSheet("background: transparent; border: none;")
        self.setAttribute(QtCore.Qt.WA_TransparentForMouseEvents)
        
        # ایجاد صحنه و اضافه کردن فلش
        self.north_arrow = NorthArrow()
        scene = QtWidgets.QGraphicsScene(self)
        self.setScene(scene)
        scene.addItem(self.north_arrow)
        self.north_arrow.setPos(8, 8)
        
        # تنظیم اندازه و موقعیت
        self.setGeometry(8, 8, 70, 70)
    
    def resizeEvent(self, event):
        """تنظیم مجدد موقعیت هنگام تغییر اندازه"""
        super().resizeEvent(event)
        self.setGeometry(8, 8, 70, 70)