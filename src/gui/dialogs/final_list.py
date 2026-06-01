"""
دیالوگ نمایش لیست کامل اجزای مورینگ برای ERP-Aqua
نسخه نهایی - بدون حاشیه دور جدول‌ها
"""

from PyQt5 import QtWidgets, QtCore
import qtawesome as qta

from .base_dialog import BaseDialog


class FinalConfirmDialog(BaseDialog):
    
    def __init__(self, parent=None, farms=None, current_farm=None, current_mooring=None):
        self.farms = farms if farms else []
        self.current_farm = current_farm
        self.current_mooring = current_mooring
        super().__init__(parent, title="📋 لیست اجزای مورینگ", width=1200, height=700)
        self.setup_ui()
    
    def setup_ui(self):
        layout = QtWidgets.QVBoxLayout(self)
        
        title = QtWidgets.QLabel("✅ گزارش کامل اجزای سیستم")
        title.setAlignment(QtCore.Qt.AlignCenter)
        title.setStyleSheet("font-size: 16px; font-weight: bold; color: #569CD6; padding: 10px;")
        layout.addWidget(title)
        
        # انتخاب مزرعه و مورینگ
        select_layout = QtWidgets.QHBoxLayout()
        select_layout.addWidget(QtWidgets.QLabel("مزرعه:"))
        self.farm_combo = QtWidgets.QComboBox()
        self.farm_combo.setMinimumWidth(150)
        select_layout.addWidget(self.farm_combo)
        
        select_layout.addSpacing(20)
        select_layout.addWidget(QtWidgets.QLabel("مورینگ:"))
        self.mooring_combo = QtWidgets.QComboBox()
        self.mooring_combo.setMinimumWidth(150)
        select_layout.addWidget(self.mooring_combo)
        select_layout.addStretch()
        layout.addLayout(select_layout)
        
        # تب‌ها
        self.tab_widget = QtWidgets.QTabWidget()
        self.tab_widget.setTabPosition(QtWidgets.QTabWidget.North)
        self.tab_widget.setIconSize(QtCore.QSize(18, 18))
        layout.addWidget(self.tab_widget)
        
        # دکمه بستن
        btn_layout = QtWidgets.QHBoxLayout()
        close_btn = QtWidgets.QPushButton("بستن")
        close_btn.setFixedWidth(100)
        close_btn.setStyleSheet("""
            QPushButton {
                background-color: #0E639C;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 6px 15px;
            }
            QPushButton:hover {
                background-color: #1177BB;
            }
        """)
        close_btn.clicked.connect(self.accept)
        btn_layout.addStretch()
        btn_layout.addWidget(close_btn)
        btn_layout.addStretch()
        layout.addLayout(btn_layout)
        
        # پر کردن مزارع
        for farm in self.farms:
            self.farm_combo.addItem(farm.name, farm.id)
        
        self.farm_combo.currentIndexChanged.connect(self.on_farm_changed)
        self.mooring_combo.currentIndexChanged.connect(self.on_mooring_changed)
        
        if self.farm_combo.count() > 0:
            self.on_farm_changed()
    
    def on_farm_changed(self):
        farm_id = self.farm_combo.currentData()
        farm = None
        for f in self.farms:
            if f.id == farm_id:
                farm = f
                break
        
        self.mooring_combo.clear()
        if farm:
            for mooring in farm.moorings:
                self.mooring_combo.addItem(mooring.id, mooring.id)
        
        if self.mooring_combo.count() > 0:
            self.on_mooring_changed()
    
    def on_mooring_changed(self):
        farm_id = self.farm_combo.currentData()
        mooring_id = self.mooring_combo.currentData()
        
        farm = None
        for f in self.farms:
            if f.id == farm_id:
                farm = f
                break
        
        mooring = None
        if farm:
            for m in farm.moorings:
                if m.id == mooring_id:
                    mooring = m
                    break
        
        self.update_tables(mooring)
    
    def update_tables(self, mooring):
        self.tab_widget.clear()
        
        if not mooring:
            lbl = QtWidgets.QLabel("مورینگ انتخاب نشده است")
            lbl.setAlignment(QtCore.Qt.AlignCenter)
            lbl.setStyleSheet("color: #F48771; font-size: 14px;")
            self.tab_widget.addTab(lbl, "خطا")
            return
        
        # استایل بدون حاشیه برای همه جداول
        no_border_style = """
            QTableWidget {
                border: none;
                outline: none;
                background-color: #2D2D30;
            }
            QTableWidget::item {
                border: none;
                padding: 4px;
            }
            QHeaderView::section {
                border: none;
                border-bottom: 1px solid #3E3E42;
                background-color: #252526;
                color: #C8C8C8;
                padding: 4px;
            }
        """
        
        # ==================== بویه‌ها ====================
        buoy_table = QtWidgets.QTableWidget()
        buoy_table.setStyleSheet(no_border_style)
        buoy_table.setFrameShape(QtWidgets.QFrame.NoFrame)
        buoy_table.setColumnCount(12)
        buoy_table.setHorizontalHeaderLabels([
            "شناسه", "نوع", "UTM X", "UTM Y", "جنس", "حجم (لیتر)",
            "تاریخ نصب", "وضعیت", "چراغ", "رنگ بدنه", "رنگ نقشه", "یادداشت"
        ])
        buoy_table.setRowCount(len(mooring.buoys))
        for i, b in enumerate(mooring.buoys):
            buoy_table.setItem(i, 0, QtWidgets.QTableWidgetItem(b.id))
            buoy_table.setItem(i, 1, QtWidgets.QTableWidgetItem("اصلی" if b.buoy_type == "main" else "نشانه‌گر"))
            buoy_table.setItem(i, 2, QtWidgets.QTableWidgetItem(f"{b.utm_x:.2f}"))
            buoy_table.setItem(i, 3, QtWidgets.QTableWidgetItem(f"{b.utm_y:.2f}"))
            buoy_table.setItem(i, 4, QtWidgets.QTableWidgetItem(b.material))
            buoy_table.setItem(i, 5, QtWidgets.QTableWidgetItem(f"{b.volume}"))
            buoy_table.setItem(i, 6, QtWidgets.QTableWidgetItem(b.install_date))
            buoy_table.setItem(i, 7, QtWidgets.QTableWidgetItem(b.status))
            buoy_table.setItem(i, 8, QtWidgets.QTableWidgetItem("دارد" if b.has_light else "ندارد"))
            buoy_table.setItem(i, 9, QtWidgets.QTableWidgetItem(b.body_color))
            buoy_table.setItem(i, 10, QtWidgets.QTableWidgetItem(b.color))
            buoy_table.setItem(i, 11, QtWidgets.QTableWidgetItem(b.note))
        buoy_table.horizontalHeader().setStretchLastSection(True)
        self.tab_widget.addTab(buoy_table, qta.icon('fa5s.square', color='#A0A0A0'), "بویه‌ها")
        
        # ==================== لنگرها ====================
        anchor_table = QtWidgets.QTableWidget()
        anchor_table.setStyleSheet(no_border_style)
        anchor_table.setFrameShape(QtWidgets.QFrame.NoFrame)
        anchor_table.setColumnCount(10)
        anchor_table.setHorizontalHeaderLabels([
            "شناسه", "نوع", "UTM X", "UTM Y", "وزن (kg)", "جنس",
            "عمق نصب (m)", "تاریخ نصب", "وضعیت", "یادداشت"
        ])
        anchor_table.setRowCount(len(mooring.anchors))
        for i, a in enumerate(mooring.anchors):
            anchor_table.setItem(i, 0, QtWidgets.QTableWidgetItem(a.id))
            anchor_table.setItem(i, 1, QtWidgets.QTableWidgetItem("فلزی" if a.anchor_type == "steel" else "بتنی"))
            anchor_table.setItem(i, 2, QtWidgets.QTableWidgetItem(f"{a.utm_x:.2f}"))
            anchor_table.setItem(i, 3, QtWidgets.QTableWidgetItem(f"{a.utm_y:.2f}"))
            anchor_table.setItem(i, 4, QtWidgets.QTableWidgetItem(f"{a.weight}"))
            anchor_table.setItem(i, 5, QtWidgets.QTableWidgetItem(a.material))
            anchor_table.setItem(i, 6, QtWidgets.QTableWidgetItem(f"{a.install_depth}"))
            anchor_table.setItem(i, 7, QtWidgets.QTableWidgetItem(a.install_date))
            anchor_table.setItem(i, 8, QtWidgets.QTableWidgetItem(a.status))
            anchor_table.setItem(i, 9, QtWidgets.QTableWidgetItem(a.note))
        anchor_table.horizontalHeader().setStretchLastSection(True)
        self.tab_widget.addTab(anchor_table, qta.icon('fa5s.anchor', color='#569CD6'), "لنگرها")
        
        # ==================== زنجیرها ====================
        chain_table = QtWidgets.QTableWidget()
        chain_table.setStyleSheet(no_border_style)
        chain_table.setFrameShape(QtWidgets.QFrame.NoFrame)
        chain_table.setColumnCount(9)
        chain_table.setHorizontalHeaderLabels([
            "شناسه", "شروع", "پایان", "قطر (mm)", "نوع", "جنس",
            "تاریخ نصب", "وضعیت", "یادداشت"
        ])
        chain_table.setRowCount(len(mooring.anchor_chains))
        for i, c in enumerate(mooring.anchor_chains):
            start_text = f"دستی ({c.start_x:.0f},{c.start_y:.0f})" if c.use_manual_start else (c.start_id or "-")
            end_text = f"دستی ({c.end_x:.0f},{c.end_y:.0f})" if c.use_manual_end else (c.end_id or "-")
            chain_table.setItem(i, 0, QtWidgets.QTableWidgetItem(c.id))
            chain_table.setItem(i, 1, QtWidgets.QTableWidgetItem(start_text))
            chain_table.setItem(i, 2, QtWidgets.QTableWidgetItem(end_text))
            chain_table.setItem(i, 3, QtWidgets.QTableWidgetItem(f"{c.diameter}"))
            chain_table.setItem(i, 4, QtWidgets.QTableWidgetItem(c.chain_type))
            chain_table.setItem(i, 5, QtWidgets.QTableWidgetItem(c.material))
            chain_table.setItem(i, 6, QtWidgets.QTableWidgetItem(c.install_date))
            chain_table.setItem(i, 7, QtWidgets.QTableWidgetItem(c.status))
            chain_table.setItem(i, 8, QtWidgets.QTableWidgetItem(c.note))
        chain_table.horizontalHeader().setStretchLastSection(True)
        self.tab_widget.addTab(chain_table, qta.icon('fa5s.link', color='#C8C8C8'), "زنجیرها")
        
        # ==================== طناب اصلی ====================
        rope_table = QtWidgets.QTableWidget()
        rope_table.setStyleSheet(no_border_style)
        rope_table.setFrameShape(QtWidgets.QFrame.NoFrame)
        rope_table.setColumnCount(10)
        rope_table.setHorizontalHeaderLabels([
            "شناسه", "شروع", "پایان", "قطر (mm)", "طول (m)", "تعداد رشته",
            "جنس", "تاریخ نصب", "وضعیت", "یادداشت"
        ])
        rope_table.setRowCount(len(mooring.anchor_ropes))
        for i, r in enumerate(mooring.anchor_ropes):
            start_text = f"دستی ({r.start_x:.0f},{r.start_y:.0f})" if r.use_manual_start else (r.start_id or "-")
            end_text = f"دستی ({r.end_x:.0f},{r.end_y:.0f})" if r.use_manual_end else (r.end_id or "-")
            rope_table.setItem(i, 0, QtWidgets.QTableWidgetItem(r.id))
            rope_table.setItem(i, 1, QtWidgets.QTableWidgetItem(start_text))
            rope_table.setItem(i, 2, QtWidgets.QTableWidgetItem(end_text))
            rope_table.setItem(i, 3, QtWidgets.QTableWidgetItem(f"{r.diameter}"))
            rope_table.setItem(i, 4, QtWidgets.QTableWidgetItem(f"{r.length}"))
            rope_table.setItem(i, 5, QtWidgets.QTableWidgetItem(f"{r.strand_count}"))
            rope_table.setItem(i, 6, QtWidgets.QTableWidgetItem(r.material))
            rope_table.setItem(i, 7, QtWidgets.QTableWidgetItem(r.install_date))
            rope_table.setItem(i, 8, QtWidgets.QTableWidgetItem(r.status))
            rope_table.setItem(i, 9, QtWidgets.QTableWidgetItem(r.note))
        rope_table.horizontalHeader().setStretchLastSection(True)
        self.tab_widget.addTab(rope_table, qta.icon('fa5s.grip-lines', color='#C8C8C8'), "طناب اصلی")
        
        # ==================== زنجیر بویه ====================
        buoy_chain_table = QtWidgets.QTableWidget()
        buoy_chain_table.setStyleSheet(no_border_style)
        buoy_chain_table.setFrameShape(QtWidgets.QFrame.NoFrame)
        buoy_chain_table.setColumnCount(9)
        buoy_chain_table.setHorizontalHeaderLabels([
            "شناسه", "بویه", "کلکتور", "قطر (mm)", "طول (m)", 
            "جنس", "نوع", "وضعیت", "یادداشت"
        ])
        buoy_chain_table.setRowCount(len(mooring.buoy_chains))
        for i, bc in enumerate(mooring.buoy_chains):
            buoy_chain_table.setItem(i, 0, QtWidgets.QTableWidgetItem(bc.id))
            buoy_chain_table.setItem(i, 1, QtWidgets.QTableWidgetItem(bc.buoy_id or "-"))
            buoy_chain_table.setItem(i, 2, QtWidgets.QTableWidgetItem(bc.collector_id or "-"))
            buoy_chain_table.setItem(i, 3, QtWidgets.QTableWidgetItem(f"{bc.diameter}"))
            buoy_chain_table.setItem(i, 4, QtWidgets.QTableWidgetItem(f"{bc.length}"))
            buoy_chain_table.setItem(i, 5, QtWidgets.QTableWidgetItem(bc.material))
            buoy_chain_table.setItem(i, 6, QtWidgets.QTableWidgetItem(bc.chain_type))
            buoy_chain_table.setItem(i, 7, QtWidgets.QTableWidgetItem(bc.status))
            buoy_chain_table.setItem(i, 8, QtWidgets.QTableWidgetItem(bc.note))
        buoy_chain_table.horizontalHeader().setStretchLastSection(True)
        self.tab_widget.addTab(buoy_chain_table, qta.icon('fa5s.link', color='#A0A0A0'), "زنجیر بویه")
        
        # ==================== شاکل‌ها ====================
        shackle_table = QtWidgets.QTableWidget()
        shackle_table.setStyleSheet(no_border_style)
        shackle_table.setFrameShape(QtWidgets.QFrame.NoFrame)
        shackle_table.setColumnCount(9)
        shackle_table.setHorizontalHeaderLabels([
            "شناسه", "نوع", "تعداد", "سایز (mm)", "تناژ (تن)", 
            "جنس", "قطعه متصل", "وضعیت", "یادداشت"
        ])
        shackle_table.setRowCount(len(mooring.shackles))
        for i, sh in enumerate(mooring.shackles):
            shackle_table.setItem(i, 0, QtWidgets.QTableWidgetItem(sh.id))
            shackle_table.setItem(i, 1, QtWidgets.QTableWidgetItem(sh.shackle_type))
            shackle_table.setItem(i, 2, QtWidgets.QTableWidgetItem(f"{sh.quantity}"))
            shackle_table.setItem(i, 3, QtWidgets.QTableWidgetItem(f"{sh.size}"))
            shackle_table.setItem(i, 4, QtWidgets.QTableWidgetItem(f"{sh.capacity}"))
            shackle_table.setItem(i, 5, QtWidgets.QTableWidgetItem(sh.material))
            shackle_table.setItem(i, 6, QtWidgets.QTableWidgetItem(sh.connected_id))
            shackle_table.setItem(i, 7, QtWidgets.QTableWidgetItem(sh.status))
            shackle_table.setItem(i, 8, QtWidgets.QTableWidgetItem(sh.note))
        shackle_table.horizontalHeader().setStretchLastSection(True)
        self.tab_widget.addTab(shackle_table, qta.icon('fa5s.shield-alt', color='#D4A574'), "شاکل‌ها")
        
        # ==================== طناب برایدل ====================
        bridle_table = QtWidgets.QTableWidget()
        bridle_table.setStyleSheet(no_border_style)
        bridle_table.setFrameShape(QtWidgets.QFrame.NoFrame)
        bridle_table.setColumnCount(9)
        bridle_table.setHorizontalHeaderLabels([
            "شناسه", "بویه متصل", "مختصات قفس", "قطر (mm)", "طول (m)",
            "تعداد رشته", "جنس", "وضعیت", "یادداشت"
        ])
        bridle_table.setRowCount(len(mooring.bridle_ropes))
        for i, br in enumerate(mooring.bridle_ropes):
            bridle_table.setItem(i, 0, QtWidgets.QTableWidgetItem(br.id))
            bridle_table.setItem(i, 1, QtWidgets.QTableWidgetItem(br.buoy_id or "-"))
            bridle_table.setItem(i, 2, QtWidgets.QTableWidgetItem(f"({br.cage_x:.0f},{br.cage_y:.0f})"))
            bridle_table.setItem(i, 3, QtWidgets.QTableWidgetItem(f"{br.diameter}"))
            bridle_table.setItem(i, 4, QtWidgets.QTableWidgetItem(f"{br.length}"))
            bridle_table.setItem(i, 5, QtWidgets.QTableWidgetItem(f"{br.strand_count}"))
            bridle_table.setItem(i, 6, QtWidgets.QTableWidgetItem(br.material))
            bridle_table.setItem(i, 7, QtWidgets.QTableWidgetItem(br.status))
            bridle_table.setItem(i, 8, QtWidgets.QTableWidgetItem(br.note))
        bridle_table.horizontalHeader().setStretchLastSection(True)
        self.tab_widget.addTab(bridle_table, qta.icon('fa5s.code-branch', color='#D4A574'), "طناب برایدل")
        
        # ==================== قفس‌ها ====================
        cage_table = QtWidgets.QTableWidget()
        cage_table.setStyleSheet(no_border_style)
        cage_table.setFrameShape(QtWidgets.QFrame.NoFrame)
        cage_table.setColumnCount(8)
        cage_table.setHorizontalHeaderLabels([
            "شناسه", "قطر (m)", "جنس", "تاریخ نصب", 
            "وضعیت", "مختصات", "رنگ نقشه", "یادداشت"
        ])
        cage_table.setRowCount(len(mooring.cages))
        for i, cg in enumerate(mooring.cages):
            cage_table.setItem(i, 0, QtWidgets.QTableWidgetItem(cg.id))
            cage_table.setItem(i, 1, QtWidgets.QTableWidgetItem(f"{cg.diameter}"))
            cage_table.setItem(i, 2, QtWidgets.QTableWidgetItem(cg.material))
            cage_table.setItem(i, 3, QtWidgets.QTableWidgetItem(cg.install_date))
            cage_table.setItem(i, 4, QtWidgets.QTableWidgetItem(cg.status))
            cage_table.setItem(i, 5, QtWidgets.QTableWidgetItem(f"({cg.utm_x:.0f},{cg.utm_y:.0f})"))
            cage_table.setItem(i, 6, QtWidgets.QTableWidgetItem(cg.color))
            cage_table.setItem(i, 7, QtWidgets.QTableWidgetItem(cg.note))
        cage_table.horizontalHeader().setStretchLastSection(True)
        self.tab_widget.addTab(cage_table, qta.icon('fa5s.circle', color='#A0A0A0'), "قفس‌ها")
        
        # ==================== تورها ====================
        net_table = QtWidgets.QTableWidget()
        net_table.setStyleSheet(no_border_style)
        net_table.setFrameShape(QtWidgets.QFrame.NoFrame)
        net_table.setColumnCount(8)
        net_table.setHorizontalHeaderLabels([
            "شناسه", "قفس متصل", "قطر طناب (mm)", "اندازه چشمه (mm)", 
            "جنس", "عمق (m)", "وضعیت", "یادداشت"
        ])
        net_table.setRowCount(len(mooring.nets))
        for i, nt in enumerate(mooring.nets):
            net_table.setItem(i, 0, QtWidgets.QTableWidgetItem(nt.id))
            net_table.setItem(i, 1, QtWidgets.QTableWidgetItem(nt.cage_id or "-"))
            net_table.setItem(i, 2, QtWidgets.QTableWidgetItem(f"{nt.diameter}"))
            net_table.setItem(i, 3, QtWidgets.QTableWidgetItem(f"{nt.mesh_size}"))
            net_table.setItem(i, 4, QtWidgets.QTableWidgetItem(nt.material))
            net_table.setItem(i, 5, QtWidgets.QTableWidgetItem(f"{nt.depth}"))
            net_table.setItem(i, 6, QtWidgets.QTableWidgetItem(nt.status))
            net_table.setItem(i, 7, QtWidgets.QTableWidgetItem(nt.note))
        net_table.horizontalHeader().setStretchLastSection(True)
        self.tab_widget.addTab(net_table, qta.icon('fa5s.th', color='#C8C8C8'), "تورها")
        
        # ==================== کلکتورها ====================
        collector_table = QtWidgets.QTableWidget()
        collector_table.setStyleSheet(no_border_style)
        collector_table.setFrameShape(QtWidgets.QFrame.NoFrame)
        collector_table.setColumnCount(9)
        collector_table.setHorizontalHeaderLabels([
            "شناسه", "بویه متصل", "قطر (m)", "ضخامت (mm)", "عمق (m)",
            "جنس", "تاریخ نصب", "وضعیت", "یادداشت"
        ])
        collector_table.setRowCount(len(mooring.collectors))
        for i, col in enumerate(mooring.collectors):
            collector_table.setItem(i, 0, QtWidgets.QTableWidgetItem(col.id))
            collector_table.setItem(i, 1, QtWidgets.QTableWidgetItem(col.buoy_id or "-"))
            collector_table.setItem(i, 2, QtWidgets.QTableWidgetItem(f"{col.diameter}"))
            collector_table.setItem(i, 3, QtWidgets.QTableWidgetItem(f"{col.thickness}"))
            collector_table.setItem(i, 4, QtWidgets.QTableWidgetItem(f"{col.depth}"))
            collector_table.setItem(i, 5, QtWidgets.QTableWidgetItem(col.material))
            collector_table.setItem(i, 6, QtWidgets.QTableWidgetItem(col.install_date))
            collector_table.setItem(i, 7, QtWidgets.QTableWidgetItem(col.status))
            collector_table.setItem(i, 8, QtWidgets.QTableWidgetItem(col.note))
        collector_table.horizontalHeader().setStretchLastSection(True)
        self.tab_widget.addTab(collector_table, qta.icon('fa5s.circle', color='#569CD6'), "کلکتورها")
        
        # استایل نهایی برای حذف هرگونه حاشیه باقیمانده
        self.tab_widget.setStyleSheet("""
            QTabWidget::pane {
                border: none;
                background: transparent;
            }
        """)