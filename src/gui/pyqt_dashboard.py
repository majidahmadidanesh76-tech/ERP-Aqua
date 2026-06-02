"""
داشبورد تحلیلی پرورش با استفاده از PyQtGraph
نمایش تاریخ شمسی در محور x
"""

import json
import os

from PyQt5 import QtWidgets, QtCore, QtGui
import pyqtgraph as pg


class PyQtDashboard(QtWidgets.QWidget):
    def __init__(self, parent=None, farm=None, mooring=None):
        super().__init__(parent)
        self.current_farm = farm
        self.current_mooring = mooring
        self.feeds = []
        self.mortalities = []
        self.water_parameters = []
        self.biomasses = []
        self.data_file = "aquaculture_data.json"
        
        pg.setConfigOptions(antialias=True)
        pg.setConfigOption('background', '#2D2D30')
        pg.setConfigOption('foreground', '#C8C8C8')
        
        self.load_data()
        self.setup_ui()
    
    def set_farm_and_mooring(self, farm, mooring):
        self.current_farm = farm
        self.current_mooring = mooring
        self.load_data()
        self.update_cage_list()
        self.update_all_charts()
    
    def load_data(self):
        self.feeds = []
        self.mortalities = []
        self.water_parameters = []
        self.biomasses = []
        
        if not self.current_farm or not self.current_mooring:
            return
        
        key = f"{self.current_farm.id}_{self.current_mooring.id}"
        
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    
                    for item in data.get('feeds', []):
                        if item.get('key') == key:
                            self.feeds = item.get('feeds', [])
                            break
                    
                    for item in data.get('mortalities', []):
                        if item.get('key') == key:
                            self.mortalities = item.get('mortalities', [])
                            break
                    
                    for item in data.get('water_parameters', []):
                        if item.get('key') == key:
                            self.water_parameters = item.get('parameters', [])
                            break
                    
                    for item in data.get('biomasses', []):
                        if item.get('key') == key:
                            self.biomasses = item.get('biomasses', [])
                            break
            except Exception as e:
                print(f"خطا در بارگذاری داده‌ها: {e}")
    
    def setup_ui(self):
        layout = QtWidgets.QVBoxLayout(self)
        
        title = QtWidgets.QLabel("📊 داشبورد تحلیلی پرورش")
        title.setAlignment(QtCore.Qt.AlignCenter)
        title.setStyleSheet("font-size: 18px; font-weight: bold; color: #569CD6; padding: 10px;")
        layout.addWidget(title)
        
        controls_layout = QtWidgets.QHBoxLayout()
        
        cage_label = QtWidgets.QLabel("انتخاب قفس:")
        cage_label.setStyleSheet("color: #C8C8C8; font-weight: bold;")
        controls_layout.addWidget(cage_label)
        
        self.cage_combo = QtWidgets.QComboBox()
        self.cage_combo.setMinimumWidth(150)
        self.cage_combo.setStyleSheet("""
            QComboBox {
                background-color: #3C3C3C;
                color: #C8C8C8;
                border: 1px solid #3E3E42;
                border-radius: 4px;
                padding: 4px 8px;
            }
            QComboBox:hover {
                border-color: #569CD6;
            }
        """)
        self.cage_combo.currentIndexChanged.connect(self.on_cage_changed)
        controls_layout.addWidget(self.cage_combo)
        
        controls_layout.addSpacing(20)
        
        self.refresh_btn = QtWidgets.QPushButton("🔄 به‌روزرسانی")
        self.refresh_btn.setStyleSheet("""
            QPushButton {
                background-color: #0E639C;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 6px 12px;
            }
            QPushButton:hover {
                background-color: #1177BB;
            }
        """)
        self.refresh_btn.clicked.connect(self.on_refresh_clicked)
        controls_layout.addWidget(self.refresh_btn)
        
        controls_layout.addStretch()
        layout.addLayout(controls_layout)
        
        self.tabs = QtWidgets.QTabWidget()
        self.tabs.setStyleSheet("""
            QTabWidget::pane {
                border: 1px solid #3E3E42;
                border-radius: 4px;
                background: #1E1E1E;
            }
            QTabBar::tab {
                background-color: #2D2D30;
                color: #C8C8C8;
                padding: 8px 16px;
                margin: 2px;
                border-radius: 4px;
            }
            QTabBar::tab:selected {
                background-color: #0E639C;
                color: white;
            }
        """)
        
        self.growth_tab = self.create_growth_tab()
        self.tabs.addTab(self.growth_tab, "📈 رشد و زیست‌توده")
        
        self.feed_tab = self.create_feed_tab()
        self.tabs.addTab(self.feed_tab, "🍽️ خوراک و FCR")
        
        self.mortality_tab = self.create_mortality_tab()
        self.tabs.addTab(self.mortality_tab, "⚠️ تلفات")
        
        self.water_tab = self.create_water_tab()
        self.tabs.addTab(self.water_tab, "💧 پارامترهای آب")
        
        layout.addWidget(self.tabs)
        
        self.update_cage_list()
    
    def on_refresh_clicked(self):
        self.load_data()
        self.update_cage_list()
        self.update_all_charts()
        QtWidgets.QMessageBox.information(self, "به‌روزرسانی", "داده‌ها با موفقیت به‌روزرسانی شدند")
    
    def on_cage_changed(self):
        self.update_all_charts()
    
    def update_cage_list(self):
        self.cage_combo.clear()
        
        if self.current_mooring and hasattr(self.current_mooring, 'cages'):
            for cage in self.current_mooring.cages:
                self.cage_combo.addItem(cage.id, cage.id)
            if self.cage_combo.count() > 0:
                self.cage_combo.setCurrentIndex(0)
    
    def get_cage_data(self):
        selected_cage = self.cage_combo.currentData()
        
        cage_biomasses = [b for b in self.biomasses if b.get('cage_id') == selected_cage]
        cage_feeds = [f for f in self.feeds if f.get('cage_id') == selected_cage]
        cage_mortalities = [m for m in self.mortalities if m.get('cage_id') == selected_cage]
        cage_water = [w for w in self.water_parameters if w.get('cage_id') == selected_cage]
        
        cage_biomasses.sort(key=lambda x: x.get('date', ''))
        cage_feeds.sort(key=lambda x: x.get('date', ''))
        cage_mortalities.sort(key=lambda x: x.get('date', ''))
        cage_water.sort(key=lambda x: x.get('date', ''))
        
        return cage_biomasses, cage_feeds, cage_mortalities, cage_water
    
    def create_growth_tab(self):
        tab = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout(tab)
        
        self.growth_plot = pg.PlotWidget()
        self.growth_plot.setLabel('left', 'وزن (گرم)')
        self.growth_plot.setLabel('bottom', 'تاریخ')
        self.growth_plot.setTitle('روند رشد ماهی')
        self.growth_plot.showGrid(x=True, y=True, alpha=0.3)
        layout.addWidget(self.growth_plot)
        
        stats_frame = QtWidgets.QFrame()
        stats_frame.setStyleSheet("background-color: #252526; border-radius: 8px; padding: 10px;")
        stats_layout = QtWidgets.QHBoxLayout(stats_frame)
        
        self.avg_weight_label = QtWidgets.QLabel("میانگین وزن: -- گرم")
        self.max_weight_label = QtWidgets.QLabel("حداکثر وزن: -- گرم")
        self.daily_gain_label = QtWidgets.QLabel("رشد روزانه: -- گرم")
        self.biomass_label = QtWidgets.QLabel("زیست‌توده: -- kg")
        
        for label in [self.avg_weight_label, self.max_weight_label, self.daily_gain_label, self.biomass_label]:
            label.setStyleSheet("color: #C8C8C8; font-size: 12px;")
            stats_layout.addWidget(label)
        
        layout.addWidget(stats_frame)
        return tab
    
    def create_feed_tab(self):
        tab = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout(tab)
        
        self.feed_plot = pg.PlotWidget()
        self.feed_plot.setLabel('left', 'مقدار خوراک (kg)')
        self.feed_plot.setLabel('bottom', 'تاریخ')
        self.feed_plot.setTitle('مصرف خوراک روزانه')
        self.feed_plot.showGrid(x=True, y=True, alpha=0.3)
        layout.addWidget(self.feed_plot)
        
        stats_frame = QtWidgets.QFrame()
        stats_frame.setStyleSheet("background-color: #252526; border-radius: 8px; padding: 10px;")
        stats_layout = QtWidgets.QHBoxLayout(stats_frame)
        
        self.total_feed_label = QtWidgets.QLabel("کل خوراک: -- kg")
        self.avg_fcr_label = QtWidgets.QLabel("میانگین FCR: --")
        
        for label in [self.total_feed_label, self.avg_fcr_label]:
            label.setStyleSheet("color: #C8C8C8; font-size: 12px;")
            stats_layout.addWidget(label)
        
        layout.addWidget(stats_frame)
        return tab
    
    def create_mortality_tab(self):
        tab = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout(tab)
        
        self.mortality_plot = pg.PlotWidget()
        self.mortality_plot.setLabel('left', 'تعداد تلفات')
        self.mortality_plot.setLabel('bottom', 'تاریخ')
        self.mortality_plot.setTitle('تلفات روزانه')
        self.mortality_plot.showGrid(x=True, y=True, alpha=0.3)
        layout.addWidget(self.mortality_plot)
        
        stats_frame = QtWidgets.QFrame()
        stats_frame.setStyleSheet("background-color: #252526; border-radius: 8px; padding: 10px;")
        stats_layout = QtWidgets.QHBoxLayout(stats_frame)
        
        self.total_mortality_label = QtWidgets.QLabel("کل تلفات: -- عدد")
        self.mortality_rate_label = QtWidgets.QLabel("نرخ تلفات: --%")
        
        for label in [self.total_mortality_label, self.mortality_rate_label]:
            label.setStyleSheet("color: #C8C8C8; font-size: 12px;")
            stats_layout.addWidget(label)
        
        layout.addWidget(stats_frame)
        return tab
    
    def create_water_tab(self):
        tab = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout(tab)
        
        self.water_plot = pg.PlotWidget()
        self.water_plot.setLabel('left', 'مقدار')
        self.water_plot.setLabel('bottom', 'تاریخ')
        self.water_plot.setTitle('پارامترهای آب')
        self.water_plot.showGrid(x=True, y=True, alpha=0.3)
        layout.addWidget(self.water_plot)
        
        return tab
    
    def update_all_charts(self):
        if not self.current_farm or not self.current_mooring:
            return
        
        if self.cage_combo.count() == 0:
            return
        
        biomasses, feeds, mortalities, water_params = self.get_cage_data()
        
        self.update_growth_chart(biomasses)
        self.update_feed_chart(feeds, biomasses)
        self.update_mortality_chart(mortalities, biomasses)
        self.update_water_chart(water_params)
    
    def update_growth_chart(self, biomasses):
        self.growth_plot.clear()
        
        if not biomasses:
            self.growth_plot.setTitle('داده‌ای برای نمایش وجود ندارد')
            return
        
        dates = [b.get('date', '') for b in biomasses]
        weights = [b.get('estimated_weight', 0) for b in biomasses]
        counts = [b.get('estimated_count', 0) for b in biomasses]
        
        # رسم خط وزن
        self.growth_plot.plot(dates, weights, pen=pg.mkPen(color='#569CD6', width=3), symbol='o', symbolBrush='#569CD6')
        
        # آمار
        if weights:
            self.avg_weight_label.setText(f"میانگین وزن: {sum(weights)/len(weights):.0f} گرم")
            self.max_weight_label.setText(f"حداکثر وزن: {max(weights):.0f} گرم")
        
        if len(weights) > 1:
            daily_gain = (weights[-1] - weights[0]) / len(weights)
            self.daily_gain_label.setText(f"رشد روزانه: {daily_gain:.1f} گرم")
        
        if counts and weights:
            total_biomass = (weights[-1] * counts[-1]) / 1000 if counts and weights else 0
            self.biomass_label.setText(f"زیست‌توده: {total_biomass:.0f} kg")
    
    def update_feed_chart(self, feeds, biomasses):
        self.feed_plot.clear()
        
        if not feeds:
            self.feed_plot.setTitle('داده‌ای برای نمایش وجود ندارد')
            return
        
        dates = [f.get('date', '') for f in feeds]
        amounts = [f.get('feed_amount', 0) for f in feeds]
        
        # نمودار میله‌ای
        bg = pg.BarGraphItem(x=dates, height=amounts, width=0.5, brush='#4CAF50')
        self.feed_plot.addItem(bg)
        
        total_feed = sum(amounts)
        self.total_feed_label.setText(f"کل خوراک: {total_feed:.0f} kg")
        
        if biomasses and len(biomasses) >= 2:
            weights = [b.get('estimated_weight', 0) for b in biomasses]
            weight_gain = weights[-1] - weights[0] if len(weights) > 0 else 0
            if weight_gain > 0 and total_feed > 0:
                fcr = total_feed / weight_gain
                self.avg_fcr_label.setText(f"میانگین FCR: {fcr:.2f}")
    
    def update_mortality_chart(self, mortalities, biomasses):
        self.mortality_plot.clear()
        
        if not mortalities:
            self.mortality_plot.setTitle('داده‌ای برای نمایش وجود ندارد')
            return
        
        dates = [m.get('date', '') for m in mortalities]
        counts = [m.get('count', 0) for m in mortalities]
        
        self.mortality_plot.plot(dates, counts, pen=pg.mkPen(color='#F48771', width=3), symbol='o', symbolBrush='#F48771')
        
        total_mortality = sum(counts)
        self.total_mortality_label.setText(f"کل تلفات: {total_mortality} عدد")
        
        if biomasses:
            initial_count = biomasses[0].get('estimated_count', 1) if biomasses else 1
            if initial_count > 0:
                mortality_rate = (total_mortality / initial_count) * 100
                self.mortality_rate_label.setText(f"نرخ تلفات: {mortality_rate:.1f}%")
    
    def update_water_chart(self, water_params):
        self.water_plot.clear()
        
        if not water_params:
            self.water_plot.setTitle('داده‌ای برای نمایش وجود ندارد')
            return
        
        dates = [w.get('date', '') for w in water_params]
        temps = [w.get('temperature', 0) for w in water_params]
        oxygen = [w.get('dissolved_oxygen', 0) for w in water_params]
        
        self.water_plot.plot(dates, temps, pen=pg.mkPen(color='#FF5722', width=3), symbol='o', name='دما')
        self.water_plot.plot(dates, oxygen, pen=pg.mkPen(color='#4CAF50', width=3), symbol='s', name='اکسیژن')
        
        self.water_plot.addLegend()