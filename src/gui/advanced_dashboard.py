"""
داشبورد تحلیلی پیشرفته پرورش - با نمودارهای حرفه‌ای و تاریخ عددی
"""

import json
import os
import numpy as np
from datetime import datetime

from PyQt5 import QtWidgets, QtCore
import qtawesome as qta

try:
    import matplotlib.pyplot as plt
    import matplotlib as mpl
    from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
    from matplotlib.figure import Figure
    import seaborn as sns
    MATPLOTLIB_AVAILABLE = True
    
    # تنظیم استایل حرفه‌ای
    plt.style.use('seaborn-v0_8-darkgrid')
    sns.set_palette("husl")
    mpl.rcParams['axes.unicode_minus'] = False
    mpl.rcParams['figure.facecolor'] = '#2D2D30'
    mpl.rcParams['axes.facecolor'] = '#1E1E1E'
    mpl.rcParams['savefig.facecolor'] = '#2D2D30'
    
except ImportError:
    MATPLOTLIB_AVAILABLE = False
    print("Warning: matplotlib/seaborn not installed.")


def convert_persian_date_to_number(date_str):
    """تبدیل تاریخ شمسی به عدد (روز از شروع)"""
    if not date_str:
        return 0
    try:
        # تاریخ شمسی به فرمت YYYY/MM/DD
        parts = date_str.split('/')
        if len(parts) == 3:
            year = int(parts[0])
            month = int(parts[1])
            day = int(parts[2])
            # تبدیل به روز از شروع سال (ساده شده)
            return (month - 1) * 30 + day
    except:
        pass
    return 0


class AdvancedGrowthDashboard(QtWidgets.QWidget):
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
        
        title = QtWidgets.QLabel("📊 داشبورد تحلیلی پیشرفته پرورش")
        title.setAlignment(QtCore.Qt.AlignCenter)
        title.setStyleSheet("font-size: 18px; font-weight: bold; color: #569CD6; padding: 10px;")
        layout.addWidget(title)
        
        # کنترل‌ها
        controls_layout = QtWidgets.QHBoxLayout()
        
        controls_layout.addWidget(QtWidgets.QLabel("انتخاب قفس:"))
        self.cage_combo = QtWidgets.QComboBox()
        self.cage_combo.setMinimumWidth(150)
        self.cage_combo.currentIndexChanged.connect(self.on_cage_changed)
        controls_layout.addWidget(self.cage_combo)
        
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
        self.refresh_btn.clicked.connect(self.on_cage_changed)
        controls_layout.addWidget(self.refresh_btn)
        controls_layout.addStretch()
        
        layout.addLayout(controls_layout)
        
        if not MATPLOTLIB_AVAILABLE:
            error_label = QtWidgets.QLabel("⚠️ matplotlib و seaborn نصب نیستند.\nلطفاً با دستور pip install seaborn matplotlib نصب کنید.")
            error_label.setAlignment(QtCore.Qt.AlignCenter)
            error_label.setStyleSheet("color: #F48771; padding: 20px; font-size: 14px;")
            layout.addWidget(error_label)
            return
        
        # تب‌های مختلف
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
        
        self.growth_tab = self.create_advanced_growth_tab()
        self.tabs.addTab(self.growth_tab, "📈 تحلیل رشد پیشرفته")
        
        self.feed_tab = self.create_advanced_feed_tab()
        self.tabs.addTab(self.feed_tab, "🍽️ تحلیل خوراک")
        
        self.mortality_tab = self.create_advanced_mortality_tab()
        self.tabs.addTab(self.mortality_tab, "⚠️ تحلیل تلفات")
        
        self.water_tab = self.create_advanced_water_tab()
        self.tabs.addTab(self.water_tab, "💧 تحلیل کیفی آب")
        
        layout.addWidget(self.tabs)
        
        self.update_cage_list()
    
    def on_cage_changed(self):
        self.update_all_charts()
    
    def update_cage_list(self):
        self.cage_combo.clear()
        if self.current_mooring and hasattr(self.current_mooring, 'cages'):
            for cage in self.current_mooring.cages:
                self.cage_combo.addItem(f"قفس {cage.id}", cage.id)
            if self.cage_combo.count() > 0:
                self.cage_combo.setCurrentIndex(0)
                self.update_all_charts()
    
    def get_cage_data(self):
        selected_cage = self.cage_combo.currentData()
        
        cage_biomasses = [b for b in self.biomasses if b.get('cage_id') == selected_cage]
        cage_feeds = [f for f in self.feeds if f.get('cage_id') == selected_cage]
        cage_mortalities = [m for m in self.mortalities if m.get('cage_id') == selected_cage]
        cage_water = [w for w in self.water_parameters if w.get('cage_id') == selected_cage]
        
        # مرتب‌سازی بر اساس تاریخ (تبدیل شده به عدد)
        for item in cage_biomasses:
            item['date_num'] = convert_persian_date_to_number(item.get('date', ''))
        for item in cage_feeds:
            item['date_num'] = convert_persian_date_to_number(item.get('date', ''))
        for item in cage_mortalities:
            item['date_num'] = convert_persian_date_to_number(item.get('date', ''))
        for item in cage_water:
            item['date_num'] = convert_persian_date_to_number(item.get('date', ''))
        
        cage_biomasses.sort(key=lambda x: x.get('date_num', 0))
        cage_feeds.sort(key=lambda x: x.get('date_num', 0))
        cage_mortalities.sort(key=lambda x: x.get('date_num', 0))
        cage_water.sort(key=lambda x: x.get('date_num', 0))
        
        return cage_biomasses, cage_feeds, cage_mortalities, cage_water
    
    def create_advanced_growth_tab(self):
        tab = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout(tab)
        
        self.growth_canvas = FigureCanvas(Figure(figsize=(10, 5), facecolor='#2D2D30'))
        layout.addWidget(self.growth_canvas)
        
        # کارت‌های آماری
        stats_widget = QtWidgets.QWidget()
        stats_widget.setStyleSheet("background-color: #252526; border-radius: 8px;")
        stats_layout = QtWidgets.QHBoxLayout(stats_widget)
        
        self.avg_weight_card = self.create_stat_card("میانگین وزن", "-- گرم", "#569CD6")
        self.max_weight_card = self.create_stat_card("حداکثر وزن", "-- گرم", "#4EC9B0")
        self.daily_gain_card = self.create_stat_card("رشد روزانه", "-- گرم/روز", "#DCDCAA")
        self.biomass_card = self.create_stat_card("زیست‌توده کل", "-- کیلوگرم", "#CE9178")
        
        stats_layout.addWidget(self.avg_weight_card)
        stats_layout.addWidget(self.max_weight_card)
        stats_layout.addWidget(self.daily_gain_card)
        stats_layout.addWidget(self.biomass_card)
        
        layout.addWidget(stats_widget)
        
        return tab
    
    def create_advanced_feed_tab(self):
        tab = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout(tab)
        
        self.feed_canvas = FigureCanvas(Figure(figsize=(10, 5), facecolor='#2D2D30'))
        layout.addWidget(self.feed_canvas)
        
        feed_stats_widget = QtWidgets.QWidget()
        feed_stats_widget.setStyleSheet("background-color: #252526; border-radius: 8px;")
        feed_stats_layout = QtWidgets.QHBoxLayout(feed_stats_widget)
        
        self.total_feed_card = self.create_stat_card("کل خوراک مصرفی", "-- kg", "#4EC9B0")
        self.avg_fcr_card = self.create_stat_card("میانگین FCR", "--", "#DCDCAA")
        
        feed_stats_layout.addWidget(self.total_feed_card)
        feed_stats_layout.addWidget(self.avg_fcr_card)
        
        layout.addWidget(feed_stats_widget)
        
        return tab
    
    def create_advanced_mortality_tab(self):
        tab = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout(tab)
        
        self.mortality_canvas = FigureCanvas(Figure(figsize=(10, 5), facecolor='#2D2D30'))
        layout.addWidget(self.mortality_canvas)
        
        mortality_stats_widget = QtWidgets.QWidget()
        mortality_stats_widget.setStyleSheet("background-color: #252526; border-radius: 8px;")
        mortality_stats_layout = QtWidgets.QHBoxLayout(mortality_stats_widget)
        
        self.total_mortality_card = self.create_stat_card("کل تلفات", "-- عدد", "#F48771")
        self.mortality_rate_card = self.create_stat_card("نرخ تلفات", "--%", "#DCDCAA")
        self.survival_rate_card = self.create_stat_card("نرخ بقا", "--%", "#4EC9B0")
        
        mortality_stats_layout.addWidget(self.total_mortality_card)
        mortality_stats_layout.addWidget(self.mortality_rate_card)
        mortality_stats_layout.addWidget(self.survival_rate_card)
        
        layout.addWidget(mortality_stats_widget)
        
        return tab
    
    def create_advanced_water_tab(self):
        tab = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout(tab)
        
        self.water_canvas = FigureCanvas(Figure(figsize=(10, 6), facecolor='#2D2D30'))
        layout.addWidget(self.water_canvas)
        
        return tab
    
    def create_stat_card(self, title, value, color):
        card = QtWidgets.QFrame()
        card.setStyleSheet(f"""
            QFrame {{
                background-color: #1E1E1E;
                border: 1px solid #3E3E42;
                border-radius: 8px;
                padding: 10px;
            }}
        """)
        layout = QtWidgets.QVBoxLayout(card)
        
        title_label = QtWidgets.QLabel(title)
        title_label.setStyleSheet(f"font-size: 11px; color: {color};")
        
        value_label = QtWidgets.QLabel(value)
        value_label.setObjectName("value")
        value_label.setStyleSheet("font-size: 18px; font-weight: bold; color: #C8C8C8;")
        
        layout.addWidget(title_label)
        layout.addWidget(value_label)
        
        return card
    
    def update_all_charts(self):
        if not MATPLOTLIB_AVAILABLE:
            return
        if not self.current_farm or not self.current_mooring:
            return
        
        biomasses, feeds, mortalities, water_params = self.get_cage_data()
        
        self.update_advanced_growth_chart(biomasses)
        self.update_advanced_feed_chart(feeds, biomasses)
        self.update_advanced_mortality_chart(mortalities, biomasses)
        self.update_advanced_water_chart(water_params)
    
    def update_advanced_growth_chart(self, biomasses):
        self.growth_canvas.figure.clear()
        
        if not biomasses:
            ax = self.growth_canvas.figure.add_subplot(111)
            ax.text(0.5, 0.5, '📊 داده‌ای برای نمایش وجود ندارد\nلطفاً ابتدا در تب زیست‌توده اطلاعات ثبت کنید', 
                   ha='center', va='center', color='#C8C8C8', fontsize=14, transform=ax.transAxes)
            ax.set_facecolor('#1E1E1E')
            self.growth_canvas.figure.tight_layout()
            self.growth_canvas.draw()
            return
        
        dates_num = [b.get('date_num', 0) for b in biomasses]
        dates_str = [b.get('date', '') for b in biomasses]
        weights = [b.get('estimated_weight', 0) for b in biomasses]
        counts = [b.get('estimated_count', 0) for b in biomasses]
        
        total_biomass = [(w * c) / 1000 for w, c in zip(weights, counts)]
        
        ax1 = self.growth_canvas.figure.add_subplot(111)
        ax2 = ax1.twinx()
        
        line1 = ax1.plot(dates_num, weights, 'o-', color='#569CD6', linewidth=2, markersize=8, label='وزن ماهی')
        ax1.fill_between(dates_num, weights, alpha=0.2, color='#569CD6')
        ax1.set_xlabel('تعداد روز از شروع (روز)', color='#C8C8C8', fontsize=11)
        ax1.set_ylabel('وزن (گرم)', color='#569CD6', fontsize=11)
        ax1.tick_params(colors='#C8C8C8')
        ax1.grid(True, color='#3E3E42', linestyle='--', alpha=0.5)
        
        bars = ax2.bar(dates_num, total_biomass, alpha=0.4, color='#4EC9B0', label='زیست‌توده کل', width=1.5)
        ax2.set_ylabel('زیست‌توده کل (کیلوگرم)', color='#4EC9B0', fontsize=11)
        ax2.tick_params(colors='#C8C8C8')
        
        final_weight = weights[-1] if weights else 0
        total_biomass_val = total_biomass[-1] if total_biomass else 0
        ax1.set_title(f'📈 روند رشد - وزن نهایی: {final_weight:.0f} گرم | زیست‌توده: {total_biomass_val:.0f} کیلوگرم', 
                     color='#C8C8C8', fontsize=12)
        
        # نمایش تاریخ شمسی به عنوان tooltip (در استاتوس بار)
        self.avg_weight_card.findChild(QtWidgets.QLabel, "value").setText(f"{sum(weights)/len(weights):.0f} گرم")
        self.max_weight_card.findChild(QtWidgets.QLabel, "value").setText(f"{max(weights):.0f} گرم")
        
        if len(weights) > 1:
            daily_gain = (weights[-1] - weights[0]) / len(weights)
            self.daily_gain_card.findChild(QtWidgets.QLabel, "value").setText(f"{daily_gain:.1f} گرم/روز")
        
        if total_biomass:
            self.biomass_card.findChild(QtWidgets.QLabel, "value").setText(f"{total_biomass[-1]:.0f} کیلوگرم")
        
        self.growth_canvas.figure.tight_layout()
        self.growth_canvas.draw()
    
    def update_advanced_feed_chart(self, feeds, biomasses):
        self.feed_canvas.figure.clear()
        
        if not feeds:
            ax = self.feed_canvas.figure.add_subplot(111)
            ax.text(0.5, 0.5, '🍽️ داده‌ای برای نمایش وجود ندارد\nلطفاً ابتدا در تب تغذیه اطلاعات ثبت کنید', 
                   ha='center', va='center', color='#C8C8C8', fontsize=14, transform=ax.transAxes)
            ax.set_facecolor('#1E1E1E')
            self.feed_canvas.figure.tight_layout()
            self.feed_canvas.draw()
            return
        
        dates_num = [f.get('date_num', 0) for f in feeds]
        amounts = [f.get('feed_amount', 0) for f in feeds]
        
        total_feed = sum(amounts)
        self.total_feed_card.findChild(QtWidgets.QLabel, "value").setText(f"{total_feed:.0f} kg")
        
        if biomasses and len(biomasses) >= 2:
            weights = [b.get('estimated_weight', 0) for b in biomasses]
            weight_gain = weights[-1] - weights[0]
            if weight_gain > 0 and total_feed > 0:
                fcr = total_feed / weight_gain
                self.avg_fcr_card.findChild(QtWidgets.QLabel, "value").setText(f"{fcr:.2f}")
        
        ax = self.feed_canvas.figure.add_subplot(111)
        colors = plt.cm.YlOrRd(np.linspace(0.3, 0.8, len(amounts)))
        bars = ax.bar(dates_num, amounts, color=colors, edgecolor='none', width=1.5)
        ax.set_xlabel('تعداد روز از شروع (روز)', color='#C8C8C8', fontsize=11)
        ax.set_ylabel('مقدار خوراک (کیلوگرم)', color='#C8C8C8', fontsize=11)
        ax.set_title(f'🍽️ مصرف خوراک روزانه - مجموع کل: {total_feed:.0f} کیلوگرم', color='#C8C8C8', fontsize=12)
        ax.tick_params(colors='#C8C8C8')
        ax.grid(True, color='#3E3E42', linestyle='--', alpha=0.3, axis='y')
        
        self.feed_canvas.figure.tight_layout()
        self.feed_canvas.draw()
    
    def update_advanced_mortality_chart(self, mortalities, biomasses):
        self.mortality_canvas.figure.clear()
        
        if not mortalities:
            ax = self.mortality_canvas.figure.add_subplot(111)
            ax.text(0.5, 0.5, '⚠️ داده‌ای برای نمایش وجود ندارد\nلطفاً ابتدا در تب تلفات اطلاعات ثبت کنید', 
                   ha='center', va='center', color='#C8C8C8', fontsize=14, transform=ax.transAxes)
            ax.set_facecolor('#1E1E1E')
            self.mortality_canvas.figure.tight_layout()
            self.mortality_canvas.draw()
            return
        
        dates_num = [m.get('date_num', 0) for m in mortalities]
        counts = [m.get('count', 0) for m in mortalities]
        
        total_mortality = sum(counts)
        self.total_mortality_card.findChild(QtWidgets.QLabel, "value").setText(f"{total_mortality} عدد")
        
        survival_rate = 100
        if biomasses:
            initial_count = biomasses[0].get('estimated_count', 1)
            if initial_count > 0:
                mortality_rate = (total_mortality / initial_count) * 100
                survival_rate = 100 - mortality_rate
                self.mortality_rate_card.findChild(QtWidgets.QLabel, "value").setText(f"{mortality_rate:.1f}%")
                self.survival_rate_card.findChild(QtWidgets.QLabel, "value").setText(f"{survival_rate:.1f}%")
        
        ax = self.mortality_canvas.figure.add_subplot(111)
        ax.plot(dates_num, counts, 'o-', color='#F48771', linewidth=2, markersize=8)
        ax.fill_between(dates_num, counts, alpha=0.2, color='#F48771')
        ax.set_xlabel('تعداد روز از شروع (روز)', color='#C8C8C8', fontsize=11)
        ax.set_ylabel('تعداد تلفات', color='#F48771', fontsize=11)
        ax.set_title(f'⚠️ روند تلفات روزانه - کل تلفات: {total_mortality} عدد | نرخ بقا: {survival_rate:.1f}%', 
                    color='#C8C8C8', fontsize=12)
        ax.tick_params(colors='#C8C8C8')
        ax.grid(True, color='#3E3E42', linestyle='--', alpha=0.5)
        
        self.mortality_canvas.figure.tight_layout()
        self.mortality_canvas.draw()
    
    def update_advanced_water_chart(self, water_params):
        self.water_canvas.figure.clear()
        
        if not water_params:
            ax = self.water_canvas.figure.add_subplot(111)
            ax.text(0.5, 0.5, '💧 داده‌ای برای نمایش وجود ندارد\nلطفاً ابتدا در تب پارامترهای آب اطلاعات ثبت کنید', 
                   ha='center', va='center', color='#C8C8C8', fontsize=14, transform=ax.transAxes)
            ax.set_facecolor('#1E1E1E')
            self.water_canvas.figure.tight_layout()
            self.water_canvas.draw()
            return
        
        dates_num = [w.get('date_num', 0) for w in water_params]
        temps = [w.get('temperature', 0) for w in water_params]
        oxygen = [w.get('dissolved_oxygen', 0) for w in water_params]
        ph = [w.get('ph', 0) for w in water_params]
        
        ax1 = self.water_canvas.figure.add_subplot(311)
        ax1.plot(dates_num, temps, 'o-', color='#FF5722', linewidth=2, markersize=6)
        ax1.fill_between(dates_num, temps, alpha=0.2, color='#FF5722')
        ax1.set_ylabel('دما (°C)', color='#FF5722', fontsize=10)
        ax1.tick_params(colors='#C8C8C8')
        ax1.grid(True, color='#3E3E42', linestyle='--', alpha=0.3)
        ax1.set_title('پارامترهای کیفی آب', color='#C8C8C8', fontsize=12)
        
        ax2 = self.water_canvas.figure.add_subplot(312)
        ax2.plot(dates_num, oxygen, 's-', color='#4CAF50', linewidth=2, markersize=6)
        ax2.fill_between(dates_num, oxygen, alpha=0.2, color='#4CAF50')
        ax2.set_ylabel('اکسیژن (mg/L)', color='#4CAF50', fontsize=10)
        ax2.tick_params(colors='#C8C8C8')
        ax2.grid(True, color='#3E3E42', linestyle='--', alpha=0.3)
        
        ax3 = self.water_canvas.figure.add_subplot(313)
        ax3.plot(dates_num, ph, '^-', color='#2196F3', linewidth=2, markersize=6)
        ax3.fill_between(dates_num, ph, alpha=0.2, color='#2196F3')
        ax3.set_xlabel('تعداد روز از شروع (روز)', color='#C8C8C8', fontsize=10)
        ax3.set_ylabel('pH', color='#2196F3', fontsize=10)
        ax3.tick_params(colors='#C8C8C8')
        ax3.grid(True, color='#3E3E42', linestyle='--', alpha=0.3)
        
        self.water_canvas.figure.tight_layout()
        self.water_canvas.draw()