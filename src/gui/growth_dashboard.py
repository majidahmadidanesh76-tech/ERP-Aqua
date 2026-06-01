"""
داشبورد تحلیلی پرورش - نمایش نمودارهای رشد، FCR، تلفات و پارامترهای آب
"""

import json
import os

from PyQt5 import QtWidgets, QtCore
import qtawesome as qta

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.pyplot as plt


class GrowthDashboard(QtWidgets.QWidget):
    def __init__(self, parent=None, farm=None, mooring=None):
        super().__init__(parent)
        self.current_farm = farm
        self.current_mooring = mooring
        self.feeds = []
        self.mortalities = []
        self.water_parameters = []
        self.biomasses = []
        self.data_file = "aquaculture_data.json"
        self.load_data()
        self.setup_ui()
    
    def set_farm_and_mooring(self, farm, mooring):
        self.current_farm = farm
        self.current_mooring = mooring
        self.load_data()
        self.update_charts()
    
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
                    
                    # بارگذاری تغذیه
                    for item in data.get('feeds', []):
                        if item.get('key') == key:
                            self.feeds = item.get('feeds', [])
                            break
                    
                    # بارگذاری تلفات
                    for item in data.get('mortalities', []):
                        if item.get('key') == key:
                            self.mortalities = item.get('mortalities', [])
                            break
                    
                    # بارگذاری پارامترهای آب
                    for item in data.get('water_parameters', []):
                        if item.get('key') == key:
                            self.water_parameters = item.get('parameters', [])
                            break
                    
                    # بارگذاری زیست‌توده
                    for item in data.get('biomasses', []):
                        if item.get('key') == key:
                            self.biomasses = item.get('biomasses', [])
                            break
            except Exception as e:
                print(f"خطا در بارگذاری داده‌ها: {e}")
    
    def setup_ui(self):
        layout = QtWidgets.QVBoxLayout(self)
        
        # عنوان
        title = QtWidgets.QLabel("📊 داشبورد تحلیلی پرورش")
        title.setAlignment(QtCore.Qt.AlignCenter)
        title.setStyleSheet("font-size: 16px; font-weight: bold; color: #569CD6; padding: 10px;")
        layout.addWidget(title)
        
        # انتخاب قفس
        select_layout = QtWidgets.QHBoxLayout()
        select_layout.addWidget(QtWidgets.QLabel("انتخاب قفس:"))
        self.cage_combo = QtWidgets.QComboBox()
        self.cage_combo.setMinimumWidth(150)
        select_layout.addWidget(self.cage_combo)
        
        # دکمه به‌روزرسانی
        self.refresh_btn = QtWidgets.QPushButton("🔄 به‌روزرسانی")
        self.refresh_btn.setStyleSheet("""
            QPushButton {
                background-color: #3A3A4A;
                color: #C8C8C8;
                border: 1px solid #4A4A5A;
                border-radius: 4px;
                padding: 4px 12px;
            }
            QPushButton:hover {
                background-color: #4A4A5A;
            }
        """)
        self.refresh_btn.clicked.connect(self.update_charts)
        select_layout.addWidget(self.refresh_btn)
        select_layout.addStretch()
        layout.addLayout(select_layout)
        
        # تب‌های مختلف نمودارها
        self.tabs = QtWidgets.QTabWidget()
        self.tabs.setTabPosition(QtWidgets.QTabWidget.North)
        self.tabs.setStyleSheet("""
            QTabWidget::pane {
                border: 1px solid #3E3E42;
                border-radius: 4px;
                background: #1E1E1E;
            }
            QTabBar::tab {
                background-color: #2D2D30;
                color: #C8C8C8;
                padding: 6px 12px;
                margin: 2px;
                border-radius: 4px;
            }
            QTabBar::tab:selected {
                background-color: #0E639C;
                color: white;
            }
        """)
        
        # تب رشد
        self.growth_tab = self.create_growth_tab()
        self.tabs.addTab(self.growth_tab, "📈 رشد و زیست‌توده")
        
        # تب خوراک و FCR
        self.feed_tab = self.create_feed_tab()
        self.tabs.addTab(self.feed_tab, "🍽️ خوراک و FCR")
        
        # تب تلفات
        self.mortality_tab = self.create_mortality_tab()
        self.tabs.addTab(self.mortality_tab, "⚠️ تلفات")
        
        # تب پارامترهای آب
        self.water_tab = self.create_water_tab()
        self.tabs.addTab(self.water_tab, "💧 پارامترهای آب")
        
        layout.addWidget(self.tabs)
        
        # پر کردن قفس‌ها
        self.update_cage_list()
    
    def create_growth_tab(self):
        tab = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout(tab)
        
        # نمودار رشد
        self.growth_canvas = FigureCanvas(Figure(figsize=(8, 4), facecolor='#2D2D30'))
        layout.addWidget(self.growth_canvas)
        
        # اطلاعات آماری
        stats_frame = QtWidgets.QFrame()
        stats_frame.setStyleSheet("""
            QFrame {
                background-color: #252526;
                border: 1px solid #3E3E42;
                border-radius: 4px;
                padding: 10px;
            }
            QLabel {
                color: #C8C8C8;
            }
        """)
        stats_layout = QtWidgets.QGridLayout(stats_frame)
        
        self.avg_weight_label = QtWidgets.QLabel("میانگین وزن: -- گرم")
        self.max_weight_label = QtWidgets.QLabel("حداکثر وزن: -- گرم")
        self.avg_daily_gain_label = QtWidgets.QLabel("میانگین رشد روزانه: -- گرم")
        
        stats_layout.addWidget(self.avg_weight_label, 0, 0)
        stats_layout.addWidget(self.max_weight_label, 0, 1)
        stats_layout.addWidget(self.avg_daily_gain_label, 1, 0, 1, 2)
        
        layout.addWidget(stats_frame)
        
        return tab
    
    def create_feed_tab(self):
        tab = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout(tab)
        
        # نمودار FCR
        self.fcr_canvas = FigureCanvas(Figure(figsize=(8, 4), facecolor='#2D2D30'))
        layout.addWidget(self.fcr_canvas)
        
        # آمار خوراک
        feed_stats_frame = QtWidgets.QFrame()
        feed_stats_frame.setStyleSheet("""
            QFrame {
                background-color: #252526;
                border: 1px solid #3E3E42;
                border-radius: 4px;
                padding: 10px;
            }
        """)
        feed_stats_layout = QtWidgets.QGridLayout(feed_stats_frame)
        
        self.total_feed_label = QtWidgets.QLabel("کل خوراک مصرفی: -- kg")
        self.avg_fcr_label = QtWidgets.QLabel("میانگین FCR: --")
        
        feed_stats_layout.addWidget(self.total_feed_label, 0, 0)
        feed_stats_layout.addWidget(self.avg_fcr_label, 0, 1)
        
        layout.addWidget(feed_stats_frame)
        
        return tab
    
    def create_mortality_tab(self):
        tab = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout(tab)
        
        # نمودار تلفات
        self.mortality_canvas = FigureCanvas(Figure(figsize=(8, 4), facecolor='#2D2D30'))
        layout.addWidget(self.mortality_canvas)
        
        # آمار تلفات
        mortality_stats_frame = QtWidgets.QFrame()
        mortality_stats_frame.setStyleSheet("""
            QFrame {
                background-color: #252526;
                border: 1px solid #3E3E42;
                border-radius: 4px;
                padding: 10px;
            }
        """)
        mortality_stats_layout = QtWidgets.QGridLayout(mortality_stats_frame)
        
        self.total_mortality_label = QtWidgets.QLabel("کل تلفات: -- عدد")
        self.mortality_rate_label = QtWidgets.QLabel("نرخ تلفات: --%")
        
        mortality_stats_layout.addWidget(self.total_mortality_label, 0, 0)
        mortality_stats_layout.addWidget(self.mortality_rate_label, 0, 1)
        
        layout.addWidget(mortality_stats_frame)
        
        return tab
    
    def create_water_tab(self):
        tab = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout(tab)
        
        # نمودارهای پارامترهای آب
        self.water_canvas = FigureCanvas(Figure(figsize=(8, 6), facecolor='#2D2D30'))
        layout.addWidget(self.water_canvas)
        
        return tab
    
    def update_cage_list(self):
        self.cage_combo.clear()
        if self.current_mooring:
            for cage in self.current_mooring.cages:
                self.cage_combo.addItem(cage.id, cage.id)
            if self.cage_combo.count() > 0:
                self.cage_combo.setCurrentIndex(0)
                self.update_charts()
    
    def update_charts(self):
        if not self.current_farm or not self.current_mooring:
            return
        
        selected_cage = self.cage_combo.currentData()
        
        # فیلتر داده‌ها بر اساس قفس انتخاب شده
        cage_biomasses = [b for b in self.biomasses if b.get('cage_id') == selected_cage]
        cage_feeds = [f for f in self.feeds if f.get('cage_id') == selected_cage]
        cage_mortalities = [m for m in self.mortalities if m.get('cage_id') == selected_cage]
        cage_water = [w for w in self.water_parameters if w.get('cage_id') == selected_cage]
        
        # مرتب‌سازی بر اساس تاریخ
        cage_biomasses.sort(key=lambda x: x.get('date', ''))
        cage_feeds.sort(key=lambda x: x.get('date', ''))
        cage_mortalities.sort(key=lambda x: x.get('date', ''))
        cage_water.sort(key=lambda x: x.get('date', ''))
        
        # به‌روزرسانی نمودار رشد
        self.update_growth_chart(cage_biomasses)
        
        # به‌روزرسانی نمودار FCR
        self.update_fcr_chart(cage_feeds, cage_biomasses)
        
        # به‌روزرسانی نمودار تلفات
        self.update_mortality_chart(cage_mortalities)
        
        # به‌روزرسانی نمودار پارامترهای آب
        self.update_water_chart(cage_water)
        
        # به‌روزرسانی آمار
        self.update_stats(cage_biomasses, cage_feeds, cage_mortalities)
    
    def update_growth_chart(self, biomasses):
        self.growth_canvas.figure.clear()
        ax = self.growth_canvas.figure.add_subplot(111)
        
        if biomasses:
            dates = [b.get('date', '') for b in biomasses]
            weights = [b.get('estimated_weight', 0) for b in biomasses]
            
            ax.plot(dates, weights, marker='o', color='#569CD6', linewidth=2)
            ax.set_title('روند رشد ماهی', color='#C8C8C8', fontsize=12)
            ax.set_xlabel('تاریخ', color='#C8C8C8')
            ax.set_ylabel('وزن (گرم)', color='#C8C8C8')
            ax.tick_params(colors='#C8C8C8')
            ax.grid(True, color='#3E3E42')
            
            # چرخش تاریخ‌ها برای خوانایی بهتر
            ax.set_xticklabels(dates, rotation=45, ha='right')
        else:
            ax.text(0.5, 0.5, 'داده‌ای برای نمایش وجود ندارد', 
                   ha='center', va='center', color='#C8C8C8', fontsize=12)
            ax.set_title('روند رشد ماهی', color='#C8C8C8', fontsize=12)
        
        self.growth_canvas.figure.tight_layout()
        self.growth_canvas.draw()
    
    def update_fcr_chart(self, feeds, biomasses):
        self.fcr_canvas.figure.clear()
        ax = self.fcr_canvas.figure.add_subplot(111)
        
        # محاسبه FCR بر اساس تاریخ‌های تغذیه
        if feeds and biomasses:
            feed_dates = [f.get('date', '') for f in feeds]
            feed_amounts = [f.get('feed_amount', 0) for f in feeds]
            total_feed = sum(feed_amounts)
            
            # محاسبه افزایش وزن (ساده)
            weights = [b.get('estimated_weight', 0) for b in biomasses]
            if len(weights) > 1:
                weight_gain = weights[-1] - weights[0]
                if weight_gain > 0 and total_feed > 0:
                    fcr = total_feed / weight_gain
                    self.avg_fcr_label.setText(f"میانگین FCR: {fcr:.2f}")
            
            ax.bar(feed_dates, feed_amounts, color='#4CAF50', alpha=0.7)
            ax.set_title('مصرف خوراک روزانه', color='#C8C8C8', fontsize=12)
            ax.set_xlabel('تاریخ', color='#C8C8C8')
            ax.set_ylabel('مقدار خوراک (kg)', color='#C8C8C8')
            ax.tick_params(colors='#C8C8C8')
            ax.grid(True, color='#3E3E42')
            ax.set_xticklabels(feed_dates, rotation=45, ha='right')
        else:
            ax.text(0.5, 0.5, 'داده‌ای برای نمایش وجود ندارد', 
                   ha='center', va='center', color='#C8C8C8', fontsize=12)
            ax.set_title('مصرف خوراک روزانه', color='#C8C8C8', fontsize=12)
        
        self.fcr_canvas.figure.tight_layout()
        self.fcr_canvas.draw()
    
    def update_mortality_chart(self, mortalities):
        self.mortality_canvas.figure.clear()
        ax = self.mortality_canvas.figure.add_subplot(111)
        
        if mortalities:
            dates = [m.get('date', '') for m in mortalities]
            counts = [m.get('count', 0) for m in mortalities]
            
            ax.bar(dates, counts, color='#D32F2F', alpha=0.7)
            ax.set_title('تلفات روزانه', color='#C8C8C8', fontsize=12)
            ax.set_xlabel('تاریخ', color='#C8C8C8')
            ax.set_ylabel('تعداد تلفات', color='#C8C8C8')
            ax.tick_params(colors='#C8C8C8')
            ax.grid(True, color='#3E3E42')
            ax.set_xticklabels(dates, rotation=45, ha='right')
        else:
            ax.text(0.5, 0.5, 'داده‌ای برای نمایش وجود ندارد', 
                   ha='center', va='center', color='#C8C8C8', fontsize=12)
            ax.set_title('تلفات روزانه', color='#C8C8C8', fontsize=12)
        
        self.mortality_canvas.figure.tight_layout()
        self.mortality_canvas.draw()
    
    def update_water_chart(self, water_params):
        self.water_canvas.figure.clear()
        
        if water_params:
            dates = [w.get('date', '') for w in water_params]
            temps = [w.get('temperature', 0) for w in water_params]
            oxygen = [w.get('dissolved_oxygen', 0) for w in water_params]
            ph = [w.get('ph', 0) for w in water_params]
            
            # ایجاد دو زیرنمودار
            ax1 = self.water_canvas.figure.add_subplot(211)
            ax1.plot(dates, temps, marker='o', color='#FF5722', linewidth=2, label='دما')
            ax1.plot(dates, oxygen, marker='s', color='#4CAF50', linewidth=2, label='اکسیژن')
            ax1.set_title('دما و اکسیژن محلول', color='#C8C8C8', fontsize=12)
            ax1.set_ylabel('مقدار', color='#C8C8C8')
            ax1.tick_params(colors='#C8C8C8')
            ax1.grid(True, color='#3E3E42')
            ax1.legend()
            
            ax2 = self.water_canvas.figure.add_subplot(212)
            ax2.plot(dates, ph, marker='^', color='#2196F3', linewidth=2, label='pH')
            ax2.set_title('pH', color='#C8C8C8', fontsize=12)
            ax2.set_xlabel('تاریخ', color='#C8C8C8')
            ax2.set_ylabel('pH', color='#C8C8C8')
            ax2.tick_params(colors='#C8C8C8')
            ax2.grid(True, color='#3E3E42')
            ax2.legend()
            
            for ax in [ax1, ax2]:
                ax.set_xticklabels(dates, rotation=45, ha='right')
        else:
            ax = self.water_canvas.figure.add_subplot(111)
            ax.text(0.5, 0.5, 'داده‌ای برای نمایش وجود ندارد', 
                   ha='center', va='center', color='#C8C8C8', fontsize=12)
            ax.set_title('پارامترهای آب', color='#C8C8C8', fontsize=12)
        
        self.water_canvas.figure.tight_layout()
        self.water_canvas.draw()
    
    def update_stats(self, biomasses, feeds, mortalities):
        if biomasses:
            weights = [b.get('estimated_weight', 0) for b in biomasses]
            self.avg_weight_label.setText(f"میانگین وزن: {sum(weights)/len(weights):.1f} گرم")
            self.max_weight_label.setText(f"حداکثر وزن: {max(weights):.1f} گرم")
            
            # محاسبه رشد روزانه
            if len(weights) > 1:
                first_weight = weights[0]
                last_weight = weights[-1]
                days = len(weights)
                daily_gain = (last_weight - first_weight) / days if days > 0 else 0
                self.avg_daily_gain_label.setText(f"میانگین رشد روزانه: {daily_gain:.1f} گرم")
        
        if feeds:
            total_feed = sum(f.get('feed_amount', 0) for f in feeds)
            self.total_feed_label.setText(f"کل خوراک مصرفی: {total_feed:.1f} kg")
        
        if mortalities:
            total_mortality = sum(m.get('count', 0) for m in mortalities)
            self.total_mortality_label.setText(f"کل تلفات: {total_mortality} عدد")
            
            # محاسبه نرخ تلفات (درصد از کل جمعیت اولیه - ساده شده)
            if biomasses and len(biomasses) > 0:
                first_biomass = biomasses[0]
                initial_count = first_biomass.get('estimated_count', 1)
                if initial_count > 0:
                    mortality_rate = (total_mortality / initial_count) * 100
                    self.mortality_rate_label.setText(f"نرخ تلفات: {mortality_rate:.1f}%")