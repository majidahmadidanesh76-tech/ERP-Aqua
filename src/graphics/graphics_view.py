"""
نمایش گرافیکی نقشه برای ERP-Aqua
"""

import math
from PyQt5 import QtCore, QtGui, QtWidgets
import qtawesome as qta

from ..core.constants import (
    DEFAULT_ZOOM_FACTOR, DEFAULT_BUOY_SIZE, 
    DEFAULT_ANCHOR_WIDTH, DEFAULT_ANCHOR_HEIGHT
)
from .north_arrow import FixedNorthArrow


class MooringGraphicsView(QtWidgets.QGraphicsView):
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setScene(QtWidgets.QGraphicsScene(self))
        self.setRenderHint(QtGui.QPainter.Antialiasing)
        self.setMinimumHeight(400)
        self.setDragMode(QtWidgets.QGraphicsView.ScrollHandDrag)
        self.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAsNeeded)
        self.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAsNeeded)
        self.setTransformationAnchor(QtWidgets.QGraphicsView.AnchorUnderMouse)
        
        self.zoom_factor = DEFAULT_ZOOM_FACTOR
        self.farm = None
        self.visible_mooring_ids = set()
        self.first_draw = True
        
        self.min_x = float('inf')
        self.max_x = float('-inf')
        self.min_y = float('inf')
        self.max_y = float('-inf')
        
        self.buoy_size = DEFAULT_BUOY_SIZE
        self.anchor_w = DEFAULT_ANCHOR_WIDTH
        self.anchor_h = DEFAULT_ANCHOR_HEIGHT
        
        self.draw_background()
        self.fixed_north_arrow = FixedNorthArrow(self)
        self.setup_zoom_buttons()
    
    def setup_zoom_buttons(self):
        self.zoom_widget = QtWidgets.QWidget(self)
        self.zoom_widget.setStyleSheet("background: transparent;")
        zoom_layout = QtWidgets.QVBoxLayout(self.zoom_widget)
        zoom_layout.setContentsMargins(0, 0, 8, 8)
        zoom_layout.setSpacing(5)
        
        self.zoom_in_btn = QtWidgets.QToolButton()
        self.zoom_in_btn.setIcon(qta.icon('fa5s.search-plus', color='#C8C8C8'))
        self.zoom_in_btn.setIconSize(QtCore.QSize(18, 18))
        self.zoom_in_btn.setFixedSize(32, 32)
        self.zoom_in_btn.setProperty("class", "glass-btn")
        self.zoom_in_btn.setToolTip("زوم +")
        self.zoom_in_btn.clicked.connect(self.zoom_in)
        
        self.zoom_out_btn = QtWidgets.QToolButton()
        self.zoom_out_btn.setIcon(qta.icon('fa5s.search-minus', color='#C8C8C8'))
        self.zoom_out_btn.setIconSize(QtCore.QSize(18, 18))
        self.zoom_out_btn.setFixedSize(32, 32)
        self.zoom_out_btn.setProperty("class", "glass-btn")
        self.zoom_out_btn.setToolTip("زوم -")
        self.zoom_out_btn.clicked.connect(self.zoom_out)
        
        self.reset_btn = QtWidgets.QToolButton()
        self.reset_btn.setIcon(qta.icon('fa5s.sync-alt', color='#C8C8C8'))
        self.reset_btn.setIconSize(QtCore.QSize(16, 16))
        self.reset_btn.setFixedSize(32, 32)
        self.reset_btn.setProperty("class", "glass-btn")
        self.reset_btn.setToolTip("بازنشانی")
        self.reset_btn.clicked.connect(self.reset_view)
        
        zoom_layout.addWidget(self.zoom_in_btn)
        zoom_layout.addWidget(self.zoom_out_btn)
        zoom_layout.addWidget(self.reset_btn)
        zoom_layout.addStretch()
    
    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.zoom_widget.setGeometry(self.width() - 50, 10, 40, 120)
        if hasattr(self, 'fixed_north_arrow'):
            self.fixed_north_arrow.setGeometry(8, 8, 70, 70)
    
    def draw_background(self):
        bg = self.scene().addRect(-10000, -10000, 20000, 20000, 
                                   QtGui.QPen(QtCore.Qt.NoPen), 
                                   QtGui.QBrush(QtGui.QColor(45, 45, 48)))
        bg.setZValue(-100)
        pen = QtGui.QPen(QtGui.QColor(70, 70, 75, 100), 1)
        for i in range(-20, 21):
            self.scene().addLine(-10000, i * 500, 10000, i * 500, pen)
            self.scene().addLine(i * 500, -10000, i * 500, 10000, pen)
    
    def set_farm(self, farm):
        self.farm = farm
        self.first_draw = True
        self.draw_system()
    
    def set_visible_moorings(self, mooring_ids):
        self.visible_mooring_ids = set(mooring_ids)
        self.draw_system()
    
    def get_all_items(self):
        if not self.farm:
            return [], [], [], [], [], [], [], [], [], []
        
        all_buoys = []
        all_anchors = []
        all_chains = []
        all_ropes = []
        all_buoy_chains = []
        all_shackles = []
        all_bridles = []
        all_cages = []
        all_nets = []
        all_collectors = []
        
        for mooring in self.farm.moorings:
            if mooring.id in self.visible_mooring_ids:
                all_buoys.extend(mooring.buoys)
                all_anchors.extend(mooring.anchors)
                all_chains.extend(mooring.anchor_chains)
                all_ropes.extend(mooring.anchor_ropes)
                all_buoy_chains.extend(mooring.buoy_chains)
                all_shackles.extend(mooring.shackles)
                all_bridles.extend(mooring.bridle_ropes)
                all_cages.extend(mooring.cages)
                all_nets.extend(mooring.nets)
                all_collectors.extend(mooring.collectors)
        
        return (all_buoys, all_anchors, all_chains, all_ropes, 
                all_buoy_chains, all_shackles, all_bridles, 
                all_cages, all_nets, all_collectors)
    
    def update_bounds_simple(self, buoys, anchors):
        """فقط از بویه‌ها و لنگرها برای محاسبه محدوده استفاده کن"""
        self.min_x = float('inf')
        self.max_x = float('-inf')
        self.min_y = float('inf')
        self.max_y = float('-inf')
        
        for b in buoys:
            self.min_x = min(self.min_x, b.utm_x)
            self.max_x = max(self.max_x, b.utm_x)
            self.min_y = min(self.min_y, b.utm_y)
            self.max_y = max(self.max_y, b.utm_y)
        
        for a in anchors:
            self.min_x = min(self.min_x, a.utm_x)
            self.max_x = max(self.max_x, a.utm_x)
            self.min_y = min(self.min_y, a.utm_y)
            self.max_y = max(self.max_y, a.utm_y)
        
        if self.min_x == float('inf'):
            if self.farm:
                self.min_x = self.farm.center_x - 500
                self.max_x = self.farm.center_x + 500
                self.min_y = self.farm.center_y - 500
                self.max_y = self.farm.center_y + 500
            else:
                self.min_x, self.max_x, self.min_y, self.max_y = 0, 1000, 0, 1000
        
        margin_x = max((self.max_x - self.min_x) * 0.2, 100)
        margin_y = max((self.max_y - self.min_y) * 0.2, 100)
        self.min_x -= margin_x
        self.max_x += margin_x
        self.min_y -= margin_y
        self.max_y += margin_y
    
    def to_screen_x(self, x):
        w = self.width() if self.width() > 0 else 800
        if self.max_x == self.min_x:
            return w / 2
        return (x - self.min_x) / (self.max_x - self.min_x) * w
    
    def to_screen_y(self, y):
        h = self.height() if self.height() > 0 else 600
        if self.max_y == self.min_y:
            return h / 2
        return h - (y - self.min_y) / (self.max_y - self.min_y) * h
    
    def draw_system(self):
        self.scene().clear()
        self.draw_background()
        
        if not self.farm:
            self.show_message("لطفاً ابتدا یک مزرعه انتخاب کنید")
            return
        
        (buoys, anchors, chains, ropes, buoy_chains, shackles, 
         bridles, cages, nets, collectors) = self.get_all_items()
        
        if len(buoys) == 0 and len(anchors) == 0:
            self.show_message("هیچ جزئی برای مورینگ انتخاب شده وجود ندارد")
            return
        
        self.update_line_coordinates(buoys, anchors, chains, ropes)
        self.update_bounds_simple(buoys, anchors)
        
        # رسم خطوط اتصال
        for chain in chains:
            self.draw_anchor_chain(chain)
        for rope in ropes:
            self.draw_anchor_rope(rope)
        for buoy_chain in buoy_chains:
            self.draw_buoy_chain_line(buoy_chain, buoys)
        for bridle in bridles:
            self.draw_bridle_line(bridle, buoys)
        
        # رسم اشکال
        for anchor in anchors:
            self.draw_anchor(anchor)
        for buoy in buoys:
            self.draw_buoy(buoy)
        for cage in cages:
            self.draw_cage(cage)
        for net in nets:
            self.draw_net(net, cages)
        
        if self.first_draw:
            self.first_draw = False
            if self.min_x != float('inf'):
                self.reset_view()
    
    def update_line_coordinates(self, buoys, anchors, chains, ropes):
        positions = {}
        for b in buoys:
            positions[b.id] = (b.utm_x, b.utm_y)
        for a in anchors:
            positions[a.id] = (a.utm_x, a.utm_y)
        
        for chain in chains:
            if not chain.use_manual_start and chain.start_id in positions:
                chain.start_x, chain.start_y = positions[chain.start_id]
            if not chain.use_manual_end and chain.end_id in positions:
                chain.end_x, chain.end_y = positions[chain.end_id]
        
        for rope in ropes:
            if not rope.use_manual_start and rope.start_id in positions:
                rope.start_x, rope.start_y = positions[rope.start_id]
            if not rope.use_manual_end and rope.end_id in positions:
                rope.end_x, rope.end_y = positions[rope.end_id]
    
    def show_message(self, text):
        msg = self.scene().addText(text)
        msg.setDefaultTextColor(QtGui.QColor(200, 200, 200))
        msg.setPos(200, 250)
        font = QtGui.QFont()
        font.setPointSize(12)
        font.setBold(True)
        msg.setFont(font)
        
        bg = self.scene().addRect(190, 240, msg.boundingRect().width() + 20, 
                                   msg.boundingRect().height() + 20,
                                   QtGui.QPen(QtCore.Qt.NoPen), 
                                   QtGui.QBrush(QtGui.QColor(30, 30, 30, 200)))
        bg.setZValue(-1)
    
    def reset_view(self):
        if self.min_x == float('inf'):
            return
        self.resetTransform()
        center_x = (self.min_x + self.max_x) / 2
        center_y = (self.min_y + self.max_y) / 2
        width = self.max_x - self.min_x
        height = self.max_y - self.min_y
        margin = max(width * 0.2, 100)
        view_w = self.width() if self.width() > 0 else 800
        view_h = self.height() if self.height() > 0 else 600
        scale_x = (view_w - 100) / (width + 2 * margin)
        scale_y = (view_h - 100) / (height + 2 * margin)
        scale = min(scale_x, scale_y, 1.5)
        self.scale(scale, scale)
        self.centerOn(self.to_screen_x(center_x), self.to_screen_y(center_y))
    
    def draw_buoy(self, buoy):
        x = self.to_screen_x(buoy.utm_x)
        y = self.to_screen_y(buoy.utm_y)
        half = self.buoy_size / 2
        rect = self.scene().addRect(x - half, y - half, self.buoy_size, self.buoy_size,
                                     QtGui.QPen(QtGui.QColor(buoy.color), 2),
                                     QtGui.QBrush(QtGui.QColor(buoy.color + "80")))
        rect.setZValue(10)
        text = self.scene().addText(f"■ {buoy.id}")
        text.setDefaultTextColor(QtGui.QColor(buoy.color))
        font = QtGui.QFont()
        font.setBold(True)
        font.setPointSize(7)
        text.setFont(font)
        text.setPos(x + half + 3, y - 8)
        text.setZValue(11)
    
    def draw_anchor(self, anchor):
        x = self.to_screen_x(anchor.utm_x)
        y = self.to_screen_y(anchor.utm_y)
        
        if anchor.anchor_type == "steel":
            size = 18
            half = size / 2
            points = [
                QtCore.QPointF(x, y - half),
                QtCore.QPointF(x - half, y + half),
                QtCore.QPointF(x + half, y + half)
            ]
            polygon = QtGui.QPolygonF(points)
            brush = QtGui.QBrush(QtGui.QColor(anchor.color))
            pen = QtGui.QPen(QtGui.QColor(anchor.color), 2)
            self.scene().addPolygon(polygon, pen, brush)
            
            text = self.scene().addText(f"▲ {anchor.id}")
            text.setDefaultTextColor(QtGui.QColor(anchor.color))
            font = QtGui.QFont()
            font.setBold(True)
            font.setPointSize(7)
            text.setFont(font)
            text.setPos(x + half + 5, y - 6)
            text.setZValue(11)
        else:
            size = 16
            half = size / 2
            pen = QtGui.QPen(QtGui.QColor(anchor.color), 3)
            rect = self.scene().addRect(x - half, y - half, size, size, pen)
            rect.setBrush(QtGui.QBrush(QtCore.Qt.NoBrush))
            rect.setZValue(10)
            
            text = self.scene().addText(f"□ {anchor.id}")
            text.setDefaultTextColor(QtGui.QColor(anchor.color))
            font = QtGui.QFont()
            font.setBold(True)
            font.setPointSize(7)
            text.setFont(font)
            text.setPos(x + half + 5, y - 6)
            text.setZValue(11)
    
    def draw_anchor_chain(self, chain):
        if chain.start_x == 0 and chain.start_y == 0 and chain.end_x == 0 and chain.end_y == 0:
            return
        x1, y1 = self.to_screen_x(chain.start_x), self.to_screen_y(chain.start_y)
        x2, y2 = self.to_screen_x(chain.end_x), self.to_screen_y(chain.end_y)
        pen = QtGui.QPen(QtGui.QColor(chain.color), 3)
        line = self.scene().addLine(x1, y1, x2, y2, pen)
        line.setZValue(5)
        if chain.id:
            mx, my = (x1 + x2) / 2, (y1 + y2) / 2
            text = self.scene().addText(f"🔗 {chain.id}")
            text.setDefaultTextColor(QtGui.QColor(chain.color))
            font = QtGui.QFont()
            font.setPointSize(6)
            text.setFont(font)
            text.setPos(mx - 12, my - 8)
            text.setZValue(6)
    
    def draw_anchor_rope(self, rope):
        if rope.start_x == 0 and rope.start_y == 0 and rope.end_x == 0 and rope.end_y == 0:
            return
        x1, y1 = self.to_screen_x(rope.start_x), self.to_screen_y(rope.start_y)
        x2, y2 = self.to_screen_x(rope.end_x), self.to_screen_y(rope.end_y)
        pen = QtGui.QPen(QtGui.QColor(rope.color), 2)
        pen.setStyle(QtCore.Qt.DashLine)
        line = self.scene().addLine(x1, y1, x2, y2, pen)
        line.setZValue(5)
        if rope.id:
            mx, my = (x1 + x2) / 2, (y1 + y2) / 2
            text = self.scene().addText(f"≈ {rope.id}")
            text.setDefaultTextColor(QtGui.QColor(rope.color))
            font = QtGui.QFont()
            font.setPointSize(6)
            text.setFont(font)
            text.setPos(mx - 12, my - 8)
            text.setZValue(6)
    
    def draw_buoy_chain_line(self, buoy_chain, buoys):
        try:
            if hasattr(buoy_chain, 'buoy_id') and buoy_chain.buoy_id:
                return
            
            buoy_positions = {b.id: (b.utm_x, b.utm_y) for b in buoys}
            
            start_id = getattr(buoy_chain, 'start_buoy_id', None)
            end_id = getattr(buoy_chain, 'end_buoy_id', None)
            
            if start_id and end_id:
                if start_id in buoy_positions and end_id in buoy_positions:
                    x1, y1 = buoy_positions[start_id]
                    x2, y2 = buoy_positions[end_id]
                    sx1, sy1 = self.to_screen_x(x1), self.to_screen_y(y1)
                    sx2, sy2 = self.to_screen_x(x2), self.to_screen_y(y2)
                    pen = QtGui.QPen(QtGui.QColor(buoy_chain.color), 2)
                    line = self.scene().addLine(sx1, sy1, sx2, sy2, pen)
                    line.setZValue(5)
        except Exception as e:
            print(f"خطا در رسم زنجیر بویه: {e}")
    
    def draw_bridle_line(self, bridle, buoys):
        try:
            cage_x = bridle.cage_x
            cage_y = bridle.cage_y
            buoy_positions = {b.id: (b.utm_x, b.utm_y) for b in buoys}
            
            if bridle.buoy_id in buoy_positions:
                buoy_x, buoy_y = buoy_positions[bridle.buoy_id]
                sx1, sy1 = self.to_screen_x(cage_x), self.to_screen_y(cage_y)
                sx2, sy2 = self.to_screen_x(buoy_x), self.to_screen_y(buoy_y)
                
                pen = QtGui.QPen(QtGui.QColor(bridle.color), 2)
                pen.setStyle(QtCore.Qt.DashLine)
                line = self.scene().addLine(sx1, sy1, sx2, sy2, pen)
                line.setZValue(5)
                
                mx, my = (sx1 + sx2) / 2, (sy1 + sy2) / 2
                text = self.scene().addText(f"≈ {bridle.id}")
                text.setDefaultTextColor(QtGui.QColor(bridle.color))
                font = QtGui.QFont()
                font.setPointSize(6)
                text.setFont(font)
                text.setPos(mx - 12, my - 8)
                text.setZValue(6)
        except Exception as e:
            print(f"خطا در رسم برایدل: {e}")
    
    def draw_cage(self, cage):
        """رسم قفس - نسخه ساده و تست شده"""
        try:
            # اگر مختصات نداشت، رسم نکن
            if cage.utm_x == 0 and cage.utm_y == 0:
                print(f"قفس {cage.id} مختصات ندارد")
                return
            
            x = self.to_screen_x(cage.utm_x)
            y = self.to_screen_y(cage.utm_y)
            
            # محاسبه شعاع بر اساس قطر واقعی
            # هر متر = 2 پیکسل (قابل تنظیم)
            radius = int(cage.diameter * 2)
            radius = max(8, min(radius, 80))  # محدوده حداقل 8 و حداکثر 80 پیکسل
            
            # رسم دایره
            ellipse = self.scene().addEllipse(x - radius, y - radius, radius * 2, radius * 2,
                                              QtGui.QPen(QtGui.QColor(cage.color), 2),
                                              QtGui.QBrush(QtGui.QColor(cage.color + "40")))
            ellipse.setZValue(10)
            
            # متن شناسه
            text = self.scene().addText(f"○ {cage.id}")
            text.setDefaultTextColor(QtGui.QColor(cage.color))
            font = QtGui.QFont()
            font.setBold(True)
            font.setPointSize(7)
            text.setFont(font)
            text.setPos(x + radius + 3, y - 6)
            text.setZValue(11)
            
            print(f"قفس {cage.id} با قطر {cage.diameter} متر در مختصات ({cage.utm_x},{cage.utm_y}) رسم شد")
        except Exception as e:
            print(f"خطا در رسم قفس: {e}")
    
    def draw_net(self, net, cages):
        cage_positions = {c.id: (c.utm_x, c.utm_y) for c in cages}
        if net.cage_id in cage_positions:
            x, y = cage_positions[net.cage_id]
            sx, sy = self.to_screen_x(x), self.to_screen_y(y)
            size = 20
            rect = self.scene().addRect(sx - size/2, sy - size/2, size, size,
                                        QtGui.QPen(QtGui.QColor(net.color), 2),
                                        QtGui.QBrush(QtGui.QColor(net.color + "40")))
            rect.setZValue(9)
    
    def zoom_in(self):
        self.scale(self.zoom_factor, self.zoom_factor)
    
    def zoom_out(self):
        self.scale(1/self.zoom_factor, 1/self.zoom_factor)
    
    def wheelEvent(self, event):
        if event.angleDelta().y() > 0:
            self.scale(self.zoom_factor, self.zoom_factor)
        else:
            self.scale(1/self.zoom_factor, 1/self.zoom_factor)