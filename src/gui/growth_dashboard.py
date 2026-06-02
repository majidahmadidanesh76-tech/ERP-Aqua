"""
داشبورد تحلیلی پرورش - نمایش نمودارهای رشد، FCR، تلفات و پارامترهای آب
"""

import json
import os
from pathlib import Path

from PyQt5 import QtWidgets, QtCore
import qtawesome as qta

try:
    from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
    from matplotlib.figure import Figure
    import matplotlib.pyplot as plt
    import matplotlib as mpl
    from matplotlib.font_manager import FontProperties
    MATPLOTLIB_AVAILABLE = True
    
    # تنظیم فونت فارسی برای matplotlib
    # مسیر فونت Tahoma در ویندوز
    font_paths = [
        "C:/Windows/Fonts/Tahoma.ttf",
        "C:/Windows/Fonts/BNazanin.ttf",
        "C:/Windows/Fonts/B Nazanin.ttf",
        "C:/Windows/Fonts/IRANSans.ttf",
    ]
    
    font_loaded = False
    for font_path in font_paths:
        if os.path.exists(font_path):
            try:
                mpl.rcParams['font.family'] = 'sans-serif'
                mpl.rcParams['font.sans-serif'] = [FontProperties(fname=font_path).get_name()]
                mpl.rcParams['axes.unicode_minus'] = False
                font_loaded = True
                print(f"فونت {font_path} بارگذاری شد")
                break
            except:
                pass
    
    if not font_loaded:
        print("هیچ فونت فارسی یافت نشد. از فونت پیش‌فرض استفاده می‌شود.")
        
except ImportError:
    MATPLOTLIB_AVAILABLE = False
    print("Warning: matplotlib not installed. Charts will not be displayed.")


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
        self.update_cage_list()
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
        title.setStyleSheet("font-size: 16px; font-weight: bold; color: #569CD6; padding: 10px;")
        layout.addWidget(title)
        
        # انتخاب قفس
        select_layout = QtWidgets.QHBoxLayout()
        select_layout.addWidget(QtWidgets.QLabel("انتخاب قفس:"))
        self.cage_combo = QtWidgets.QComboBox()
        self.cage_combo.setMinimumWidth(150)
        self.cage_combo.currentIndexChanged.connect(self.on_cage_changed)
        select_layout.addWidget(self.cage_combo)
        
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
        
        if not MATPLOTLIB_AVAILABLE:
            error_label = QtWidgets.QLabel("⚠️ matplotlib نصب نیست. نمودارها نمایش داده نمی‌شوند.")
            error_label.setAlignment(QtCore.Qt.AlignCenter)
            error_label.setStyleSheet("color: #F48771; padding: 20px;")
            layout.addWidget(error_label)
            return
        
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
        
        self.growth_tab = self.create_growth_tab()
        self.tabs.addTab(self.growth_tab, "رشد و زیست‌توده")
        
        self.feed_tab = self.create_feed_tab()
        self.tabs.addTab(self.feed_tab, "خوراک و FCR")
        
        self.mortality_tab = self.create_mortality_tab()
        self.tabs.addTab(self.mortality_tab, "تلفات")
        
        self.water_tab = self.create_water_tab()
        self.tabs.addTab(self.water_tab, "پارامترهای آب")
        
        layout.addWidget(self.tabs)
        
        self.update_cage_list()
    
    def on_cage_changed(self):
        self.update_charts()
    
    def create_growth_tab(self):
        tab = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout(tab)
        
        self.growth_canvas = FigureCanvas(Figure(figsize=(8, 4), facecolor='#2D2D30'))
        layout.addWidget(self.growth_canvas)
        
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
        
        self.fcr_canvas = FigureCanvas(Figure(figsize=(8, 4), facecolor='#2D2D30'))
        layout.addWidget(self.fcr_canvas)
        
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
        
        self.mortality_canvas = FigureCanvas(Figure(figsize=(8, 4), facecolor='#2D2D30'))
        layout.addWidget(self.mortality_canvas)
        
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
        
        self.water_canvas = FigureCanvas(Figure(figsize=(8, 6), facecolor='#2D2D30'))
        layout.addWidget(self.water_canvas)
        return tab
    
    def update_cage_list(self):
        self.cage_combo.clear()
        if self.current_mooring and hasattr(self.current_mooring, 'cages'):
            for cage in self.current_mooring.cages:
                self.cage_combo.addItem(cage.id, cage.id)
            if self.cage_combo.count() > 0:
                self.cage_combo.setCurrentIndex(0)
                self.update_charts()
    
    def update_charts(self):
        if not MATPLOTLIB_AVAILABLE:
            return
        if not self.current_farm or not self.current_mooring:
            return
        
        selected_cage = self.cage_combo.currentData()
        
        cage_biomasses = [b for b in self.biomasses if b.get('cage_id') == selected_cage]
        cage_feeds = [f for f in self.feeds if f.get('cage_id') == selected_cage]
        cage_mortalities = [m for m in self.mortalities if m.get('cage_id') == selected_cage]
        cage_water = [w for w in self.water_parameters if w.get('cage_id') == selected_cage]
        
        cage_biomasses.sort(key=lambda x: x.get('date', ''))
        cage_feeds.sort(key=lambda x: x.get('date', ''))
        cage_mortalities.sort(key=lambda x: x.get('date', ''))
        cage_water.sort(key=lambda x: x.get('date', ''))
        
        self.update_growth_chart(cage_biomasses)
        self.update_fcr_chart(cage_feeds, cage_biomasses)
        self.update_mortality_chart(cage_mortalities)
        self.update_water_chart(cage_water)
        self.update_stats(cage_biomasses, cage_feeds, cage_mortalities)
    
    def update_growth_chart(self, biomasses):
        self.growth_canvas.figure.clear()
        ax = self.growth_canvas.figure.add_subplot(111)
        
        if biomasses:
            dates = [b.get('date', '') for b in biomasses]
            weights = [b.get('estimated_weight', 0) for b in biomasses]
            
            ax.plot(dates, weights, marker='o', color='#569CD6', linewidth=2)
            ax.set_title('روند رشد ماهی', color='#C8C8C8', fontsize=12)
            ax.set_xlabel('تاریخ', color='#C8C8C8', fontsize=10)
            ax.set_ylabel('وزن (گرم)', color='#C8C8C8', fontsize=10)
            ax.tick_params(colors='#C8C8C8')
            ax.grid(True, color='#3E3E42')
            plt.setp(ax.get_xticklabels(), rotation=45, ha='right')
        else:
            ax.text(0.5, 0.5, 'داده‌ای برای نمایش وجود ندارد\nلطفاً ابتدا در تب زیست‌توده اطلاعات ثبت کنید', 
                   ha='center', va='center', color='#C8C8C8', fontsize=12, transform=ax.transAxes)
            ax.set_title('روند رشد ماهی', color='#C8C8C8', fontsize=12)
        
        self.growth_canvas.figure.tight_layout()
        self.growth_canvas.draw()
    
    def update_fcr_chart(self, feeds, biomasses):
        self.fcr_canvas.figure.clear()
        ax = self.fcr_canvas.figure.add_subplot(111)
        
        if feeds:
            feed_dates = [f.get('date', '') for f in feeds]
            feed_amounts = [f.get('feed_amount', 0) for f in feeds]
            total_feed = sum(feed_amounts)
            self.total_feed_label.setText(f"کل خوراک مصرفی: {total_feed:.1f} kg")
            
            if biomasses and len(biomasses) >= 2:
                weights = [b.get('estimated_weight', 0) for b in biomasses]
                weight_gain = weights[-1] - weights[0]
                if weight_gain > 0 and total_feed > 0:
                    fcr = total_feed / weight_gain
                    self.avg_fcr_label.setText(f"میانگین FCR: {fcr:.2f}")
            
            ax.bar(feed_dates, feed_amounts, color='#4CAF50', alpha=0.7)
            ax.set_title('مصرف خوراک روزانه', color='#C8C8C8', fontsize=12)
            ax.set_xlabel('تاریخ', color='#C8C8C8', fontsize=10)
            ax.set_ylabel('مقدار خوراک (kg)', color='#C8C8C8', fontsize=10)
            ax.tick_params(colors='#C8C8C8')
            ax.grid(True, color='#3E3E42')
            plt.setp(ax.get_xticklabels(), rotation=45, ha='right')
        else:
            ax.text(0.5, 0.5, 'داده‌ای برای نمایش وجود ندارد\nلطفاً ابتدا در تب تغذیه اطلاعات ثبت کنید', 
                   ha='center', va='center', color='#C8C8C8', fontsize=12, transform=ax.transAxes)
            ax.set_title('مصرف خوراک روزانه', color='#C8C8C8', fontsize=12)
        
        self.fcr_canvas.figure.tight_layout()
        self.fcr_canvas.draw()
    
    def update_mortality_chart(self, mortalities):
        self.mortality_canvas.figure.clear()
        ax = self.mortality_canvas.figure.add_subplot(111)
        
        if mortalities:
            dates = [m.get('date', '') for m in mortalities]
            counts = [m.get('count', 0) for m in mortalities]
            total = sum(counts)
            self.total_mortality_label.setText(f"کل تلفات: {total} عدد")
            
            ax.bar(dates, counts, color='#D32F2F', alpha=0.7)
            ax.set_title('تلفات روزانه', color='#C8C8C8', fontsize=12)
            ax.set_xlabel('تاریخ', color='#C8C8C8', fontsize=10)
            ax.set_ylabel('تعداد تلفات', color='#C8C8C8', fontsize=10)
            ax.tick_params(colors='#C8C8C8')
            ax.grid(True, color='#3E3E42')
            plt.setp(ax.get_xticklabels(), rotation=45, ha='right')
        else:
            ax.text(0.5, 0.5, 'داده‌ای برای نمایش وجود ندارد\nلطفاً ابتدا در تب تلفات اطلاعات ثبت کنید', 
                   ha='center', va='center', color='#C8C8C8', fontsize=12, transform=ax.transAxes)
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
            
            ax1 = self.water_canvas.figure.add_subplot(211)
            ax1.plot(dates, temps, marker='o', color='#FF5722', linewidth=2, label='دما')
            ax1.plot(dates, oxygen, marker='s', color='#4CAF50', linewidth=2, label='اکسیژن')
            ax1.set_title('دما و اکسیژن محلول', color='#C8C8C8', fontsize=12)
            ax1.set_ylabel('مقدار', color='#C8C8C8', fontsize=10)
            ax1.tick_params(colors='#C8C8C8')
            ax1.grid(True, color='#3E3E42')
            ax1.legend()
            plt.setp(ax1.get_xticklabels(), rotation=45, ha='right')
            
            ax2 = self.water_canvas.figure.add_subplot(212)
            ax2.plot(dates, ph, marker='^', color='#2196F3', linewidth=2, label='pH')
            ax2.set_title('pH', color='#C8C8C8', fontsize=12)
            ax2.set_xlabel('تاریخ', color='#C8C8C8', fontsize=10)
            ax2.set_ylabel('pH', color='#C8C8C8', fontsize=10)
            ax2.tick_params(colors='#C8C8C8')
            ax2.grid(True, color='#3E3E42')
            ax2.legend()
            plt.setp(ax2.get_xticklabels(), rotation=45, ha='right')
        else:
            ax = self.water_canvas.figure.add_subplot(111)
            ax.text(0.5, 0.5, 'داده‌ای برای نمایش وجود ندارد\nلطفاً ابتدا در تب پارامترهای آب اطلاعات ثبت کنید', 
                   ha='center', va='center', color='#C8C8C8', fontsize=12, transform=ax.transAxes)
            ax.set_title('پارامترهای آب', color='#C8C8C8', fontsize=12)
        
        self.water_canvas.figure.tight_layout()
        self.water_canvas.draw()
    
    def update_stats(self, biomasses, feeds, mortalities):
        if biomasses:
            weights = [b.get('estimated_weight', 0) for b in biomasses]
            self.avg_weight_label.setText(f"میانگین وزن: {sum(weights)/len(weights):.1f} گرم")
            self.max_weight_label.setText(f"حداکثر وزن: {max(weights):.1f} گرم")
            
            if len(weights) > 1:
                days = len(weights)
                daily_gain = (weights[-1] - weights[0]) / days if days > 0 else 0
                self.avg_daily_gain_label.setText(f"میانگین رشد روزانه: {daily_gain:.1f} گرم")
        
        if mortalities and biomasses:
            total_mortality = sum(m.get('count', 0) for m in mortalities)
            first_biomass = biomasses[0] if biomasses else {}
            initial_count = first_biomass.get('estimated_count', 1)
            if initial_count > 0:
                mortality_rate = (total_mortality / initial_count) * 100
                self.mortality_rate_label.setText(f"نرخ تلفات: {mortality_rate:.1f}%")