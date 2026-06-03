"""
داشبورد تحلیلی پرورش با استفاده از PyQtGraph
نسخه متصل به دیتابیس - با تبدیل تاریخ شمسی به عدد و نمایش برچسب شمسی
"""

from PyQt5 import QtWidgets, QtCore
import pyqtgraph as pg
import jdatetime

from ..database.db_handler import DatabaseHandler


class PyQtDashboard(QtWidgets.QWidget):
    def __init__(self, parent=None, farm=None, mooring=None):
        super().__init__(parent)
        self.db = DatabaseHandler()
        self.current_farm = farm
        self.current_mooring = mooring
        self.current_cycle = None
        self.feeds = []
        self.mortalities = []
        self.water_parameters = []
        self.biomasses = []

        pg.setConfigOptions(antialias=True)
        pg.setConfigOption('background', '#2D2D30')
        pg.setConfigOption('foreground', '#C8C8C8')

        self.setup_ui()

    def persian_date_to_number(self, date_str):
        """تبدیل تاریخ شمسی به عدد (روز از شروع سال 1400)"""
        if not date_str:
            return 0
        try:
            parts = date_str.split('/')
            if len(parts) == 3:
                year = int(parts[0])
                month = int(parts[1])
                day = int(parts[2])
                base_date = jdatetime.date(1400, 1, 1)
                target_date = jdatetime.date(year, month, day)
                return (target_date - base_date).days
        except:
            pass
        return 0

    def set_farm_and_mooring(self, farm, mooring):
        self.current_farm = farm
        self.current_mooring = mooring
        self.update_cage_list()

    def load_data(self):
        """بارگذاری داده‌ها از دیتابیس"""
        self.feeds = []
        self.mortalities = []
        self.water_parameters = []
        self.biomasses = []

        if not self.current_farm or not self.current_mooring:
            return

        cage_id = self.cage_combo.currentData() if self.cage_combo.count() > 0 else None
        if not cage_id:
            return

        self.current_cycle = self.db.get_active_cycle(cage_id)
        if self.current_cycle:
            self.feeds = self.db.get_feeds_by_cycle(self.current_cycle.id)
            self.mortalities = self.db.get_mortalities_by_cycle(self.current_cycle.id)
            self.biomasses = self.db.get_biomasses_by_cycle(self.current_cycle.id)
            if hasattr(self.db, 'get_water_parameters_by_cycle'):
                self.water_parameters = self.db.get_water_parameters_by_cycle(self.current_cycle.id)

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

        self.refresh_btn = QtWidgets.QPushButton("🔄 بهروزرسانی")
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
        self.tabs.addTab(self.growth_tab, "📈 رشد و زیستتوده")

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
        self.update_all_charts()
        QtWidgets.QMessageBox.information(self, "بهروزرسانی", "داده‌ها با موفقیت به‌روزرسانی شدند")

    def on_cage_changed(self):
        self.load_data()
        self.update_all_charts()

    def update_cage_list(self):
        self.cage_combo.clear()
        if self.current_mooring and hasattr(self.current_mooring, 'cages'):
            for cage in self.current_mooring.cages:
                self.cage_combo.addItem(cage.id, cage.id)
            if self.cage_combo.count() > 0:
                self.cage_combo.setCurrentIndex(0)
                self.load_data()
                self.update_all_charts()

    def get_cage_data(self):
        return self.biomasses, self.feeds, self.mortalities, self.water_parameters

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
        self.biomass_label = QtWidgets.QLabel("زیستتوده: -- kg")

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
            self.growth_plot.setTitle('📊 داده‌ای برای نمایش وجود ندارد\nلطفاً ابتدا زیست توده ثبت کنید')
            return

        # تبدیل تاریخ به عدد و ذخیره تاریخ اصلی برای برچسب
        dates_num = []
        dates_str = []
        for b in biomasses:
            dates_num.append(self.persian_date_to_number(b.date))
            dates_str.append(b.date)
        
        weights = [b.estimated_weight for b in biomasses]
        counts = [b.estimated_count for b in biomasses]

        # رسم نمودار
        self.growth_plot.plot(dates_num, weights, pen=pg.mkPen(color='#569CD6', width=3), symbol='o', symbolBrush='#569CD6')
        
        # تنظیم برچسب‌های محور X به صورت تاریخ شمسی
        if len(dates_num) > 0:
            axis = self.growth_plot.getAxis('bottom')
            axis.setTicks([[(dates_num[i], dates_str[i]) for i in range(len(dates_num))]])

        if weights:
            self.avg_weight_label.setText(f"میانگین وزن: {sum(weights)/len(weights):.0f} گرم")
            self.max_weight_label.setText(f"حداکثر وزن: {max(weights):.0f} گرم")

        if len(weights) > 1 and dates_num[-1] > dates_num[0]:
            days = dates_num[-1] - dates_num[0]
            if days > 0:
                daily_gain = (weights[-1] - weights[0]) / days
                self.daily_gain_label.setText(f"رشد روزانه: {daily_gain:.1f} گرم")

        if counts and weights:
            total_biomass = (weights[-1] * counts[-1]) / 1000 if counts and weights else 0
            self.biomass_label.setText(f"زیستتوده: {total_biomass:.0f} kg")

    def update_feed_chart(self, feeds, biomasses):
        self.feed_plot.clear()

        if not feeds:
            self.feed_plot.setTitle('🍽️ داده‌ای برای نمایش وجود ندارد\nلطفاً ابتدا تغذیه ثبت کنید')
            return

        dates_num = []
        dates_str = []
        for f in feeds:
            dates_num.append(self.persian_date_to_number(f.date))
            dates_str.append(f.date)
        
        amounts = [f.feed_amount for f in feeds]

        bg = pg.BarGraphItem(x=dates_num, height=amounts, width=1.0, brush='#4CAF50')
        self.feed_plot.addItem(bg)
        
        # تنظیم برچسب‌های محور X
        if len(dates_num) > 0:
            axis = self.feed_plot.getAxis('bottom')
            axis.setTicks([[(dates_num[i], dates_str[i]) for i in range(len(dates_num))]])

        total_feed = sum(amounts)
        self.total_feed_label.setText(f"کل خوراک: {total_feed:.0f} kg")

        if biomasses and len(biomasses) >= 2:
            weights = [b.estimated_weight for b in biomasses]
            weight_gain = weights[-1] - weights[0] if len(weights) > 0 else 0
            if weight_gain > 0 and total_feed > 0:
                fcr = total_feed / weight_gain
                self.avg_fcr_label.setText(f"میانگین FCR: {fcr:.2f}")

    def update_mortality_chart(self, mortalities, biomasses):
        self.mortality_plot.clear()

        if not mortalities:
            self.mortality_plot.setTitle('⚠️ داده‌ای برای نمایش وجود ندارد\nلطفاً ابتدا تلفات ثبت کنید')
            return

        dates_num = []
        dates_str = []
        for m in mortalities:
            dates_num.append(self.persian_date_to_number(m.date))
            dates_str.append(m.date)
        
        counts = [m.count for m in mortalities]

        self.mortality_plot.plot(dates_num, counts, pen=pg.mkPen(color='#F48771', width=3), symbol='o', symbolBrush='#F48771')
        
        # تنظیم برچسب‌های محور X
        if len(dates_num) > 0:
            axis = self.mortality_plot.getAxis('bottom')
            axis.setTicks([[(dates_num[i], dates_str[i]) for i in range(len(dates_num))]])

        total_mortality = sum(counts)
        self.total_mortality_label.setText(f"کل تلفات: {total_mortality} عدد")

        if biomasses:
            initial_count = biomasses[0].estimated_count if biomasses else 1
            if initial_count > 0:
                mortality_rate = (total_mortality / initial_count) * 100
                self.mortality_rate_label.setText(f"نرخ تلفات: {mortality_rate:.1f}%")

    def update_water_chart(self, water_params):
        self.water_plot.clear()

        if not water_params:
            self.water_plot.setTitle('💧 داده‌ای برای نمایش وجود ندارد\nلطفاً ابتدا پارامترهای آب ثبت کنید')
            return

        dates_num = []
        dates_str = []
        for w in water_params:
            dates_num.append(self.persian_date_to_number(w.date))
            dates_str.append(w.date)
        
        temps = [w.temperature for w in water_params]
        oxygen = [w.dissolved_oxygen for w in water_params]

        self.water_plot.plot(dates_num, temps, pen=pg.mkPen(color='#FF5722', width=3), symbol='o', name='دما')
        self.water_plot.plot(dates_num, oxygen, pen=pg.mkPen(color='#4CAF50', width=3), symbol='s', name='اکسیژن')
        
        # تنظیم برچسب‌های محور X
        if len(dates_num) > 0:
            axis = self.water_plot.getAxis('bottom')
            axis.setTicks([[(dates_num[i], dates_str[i]) for i in range(len(dates_num))]])

        self.water_plot.addLegend()