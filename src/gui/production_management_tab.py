"""
تب شاخصهای پرورش - نمایش شاخصهای عملکردی و تحلیل دادهها
نسخه با استایل بهبود یافته
"""

from PyQt5 import QtWidgets, QtCore


class ProductionManagementTab(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_farm = None
        self.current_mooring = None
        self.current_cage = None
        self.feeds = []
        self.mortalities = []
        self.biomasses = []
        self.harvests = []
        self.production_cycle = None

        self.setup_ui()

    def set_data(self, farm, mooring, cage, feeds, mortalities, biomasses, harvests, cycle):
        self.current_farm = farm
        self.current_mooring = mooring
        self.current_cage = cage
        self.feeds = feeds
        self.mortalities = mortalities
        self.biomasses = biomasses
        self.harvests = harvests
        self.production_cycle = cycle

        self.update_all()

    def setup_ui(self):
        layout = QtWidgets.QVBoxLayout(self)
        layout.setSpacing(15)

        title = QtWidgets.QLabel("📊 شاخصهای کلیدی عملکرد پرورش")
        title.setAlignment(QtCore.Qt.AlignCenter)
        title.setStyleSheet("font-size: 16px; font-weight: bold; color: #569CD6; padding: 10px;")
        layout.addWidget(title)

        # کارتهای شاخصهای کلیدی (KPI)
        kpi_layout = QtWidgets.QGridLayout()
        kpi_layout.setSpacing(15)
        kpi_layout.setContentsMargins(5, 5, 5, 5)

        # سطر اول
        self.fcr_card = self.create_kpi_card("FCR (ضریب تبدیل)", "--", "کل خوراک / افزایش وزن", "#569CD6")
        kpi_layout.addWidget(self.fcr_card, 0, 0)
        
        self.sgr_card = self.create_kpi_card("SGR (نرخ رشد ویژه)", "-- %/روز", "نرخ رشد ویژه", "#4EC9B0")
        kpi_layout.addWidget(self.sgr_card, 0, 1)
        
        self.survival_card = self.create_kpi_card("نرخ بقا", "-- %", "تعداد باقیمانده / تعداد اولیه", "#DCDCAA")
        kpi_layout.addWidget(self.survival_card, 0, 2)

        # سطر دوم
        self.biomass_card = self.create_kpi_card("زیستتوده فعلی", "-- kg", "وزن تخمینی کل", "#CE9178")
        kpi_layout.addWidget(self.biomass_card, 1, 0)
        
        self.fcr_target_card = self.create_kpi_card("هدف FCR", "--", "هدف تعیین شده", "#808080")
        kpi_layout.addWidget(self.fcr_target_card, 1, 1)
        
        self.weight_target_card = self.create_kpi_card("وزن هدف", "-- گرم", "هدف تعیین شده", "#808080")
        kpi_layout.addWidget(self.weight_target_card, 1, 2)

        layout.addLayout(kpi_layout)

        # جدول عملکرد
        period_label = QtWidgets.QLabel("📊 روند عملکرد دوره پرورش")
        period_label.setStyleSheet("font-size: 14px; font-weight: bold; color: #569CD6; margin-top: 10px;")
        layout.addWidget(period_label)

        self.performance_table = QtWidgets.QTableWidget()
        self.performance_table.setColumnCount(6)
        self.performance_table.setHorizontalHeaderLabels(["تاریخ", "وزن (گرم)", "تعداد", "خوراک تجمعی (kg)", "FCR جاری", "تلفات تجمعی"])
        self.performance_table.horizontalHeader().setStretchLastSection(True)
        self.performance_table.setColumnWidth(0, 100)
        self.performance_table.setColumnWidth(1, 80)
        self.performance_table.setColumnWidth(2, 100)
        self.performance_table.setColumnWidth(3, 120)
        self.performance_table.setColumnWidth(4, 80)
        self.performance_table.setColumnWidth(5, 100)
        self.performance_table.setStyleSheet("""
            QTableWidget {
                border: 1px solid #3E3E42;
                border-radius: 4px;
                background-color: #2D2D30;
                alternate-background-color: #252526;
            }
            QTableWidget::item:selected {
                background-color: #0E639C;
            }
        """)
        layout.addWidget(self.performance_table)

        # هشدارها
        alerts_label = QtWidgets.QLabel("⚠️ هشدارها و توصیهها")
        alerts_label.setStyleSheet("font-size: 14px; font-weight: bold; color: #F48771; margin-top: 10px;")
        layout.addWidget(alerts_label)

        self.alerts_text = QtWidgets.QTextEdit()
        self.alerts_text.setReadOnly(True)
        self.alerts_text.setMaximumHeight(100)
        self.alerts_text.setStyleSheet("""
            QTextEdit {
                background-color: #252526;
                border: 1px solid #3E3E42;
                border-radius: 4px;
                color: #C8C8C8;
            }
        """)
        layout.addWidget(self.alerts_text)

    def create_kpi_card(self, title, default_value, subtitle, color):
        """ایجاد کارت KPI خواناتر"""
        card = QtWidgets.QFrame()
        card.setFixedSize(200, 110)
        card.setStyleSheet(f"""
            QFrame {{
                background-color: #1E1E1E;
                border: 1px solid #3E3E42;
                border-radius: 10px;
            }}
        """)
        
        layout = QtWidgets.QVBoxLayout(card)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(5)

        # عنوان
        title_lbl = QtWidgets.QLabel(title)
        title_lbl.setStyleSheet(f"font-size: 11px; color: {color}; font-weight: bold;")
        title_lbl.setAlignment(QtCore.Qt.AlignCenter)
        layout.addWidget(title_lbl)

        # مقدار (با QLabel ساده)
        value_lbl = QtWidgets.QLabel(default_value)
        value_lbl.setStyleSheet("""
            font-size: 18px; 
            font-weight: bold; 
            color: white;
            background-color: #2D2D30;
            border-radius: 6px;
            padding: 6px;
        """)
        value_lbl.setAlignment(QtCore.Qt.AlignCenter)
        value_lbl.setFixedHeight(45)
        layout.addWidget(value_lbl)

        # زیرنویس
        subtitle_lbl = QtWidgets.QLabel(subtitle)
        subtitle_lbl.setStyleSheet("font-size: 9px; color: #808080;")
        subtitle_lbl.setAlignment(QtCore.Qt.AlignCenter)
        subtitle_lbl.setWordWrap(True)
        layout.addWidget(subtitle_lbl)

        # ذخیره برچسب مقدار برای به‌روزرسانی بعدی
        card.value_label = value_lbl

        return card

    def update_all(self):
        if not self.production_cycle:
            self.show_empty_state()
            return

        self.calculate_and_update_kpis()
        self.update_performance_table()
        self.update_alerts()

    def show_empty_state(self):
        for card in [self.fcr_card, self.sgr_card, self.survival_card, 
                     self.biomass_card, self.fcr_target_card, self.weight_target_card]:
            if hasattr(card, 'value_label'):
                card.value_label.setText("--")
        self.performance_table.setRowCount(0)
        self.alerts_text.setPlainText("لطفاً یک قفس با دوره فعال انتخاب کنید.")

    def calculate_days_between(self, date1_str, date2_str):
        try:
            parts1 = date1_str.split('/')
            parts2 = date2_str.split('/')
            if len(parts1) == 3 and len(parts2) == 3:
                year1, month1, day1 = int(parts1[0]), int(parts1[1]), int(parts1[2])
                year2, month2, day2 = int(parts2[0]), int(parts2[1]), int(parts2[2])
                days1 = year1 * 365 + month1 * 30 + day1
                days2 = year2 * 365 + month2 * 30 + day2
                return days2 - days1
        except:
            pass
        return 0

    def calculate_and_update_kpis(self):
        cycle = self.production_cycle

        if not cycle:
            return

        # زیستتوده فعلی
        if self.biomasses:
            last_biomass = self.biomasses[-1]
            current_biomass_kg = (last_biomass.estimated_weight * last_biomass.estimated_count) / 1000
            self.biomass_card.value_label.setText(f"{current_biomass_kg:,.0f}")
        else:
            current_biomass_kg = (cycle.initial_weight * cycle.initial_count) / 1000
            self.biomass_card.value_label.setText(f"{current_biomass_kg:,.0f}*")

        # نرخ بقا
        remaining_count = cycle.initial_count
        if self.biomasses:
            remaining_count = self.biomasses[-1].estimated_count
        elif self.harvests:
            total_harvested = sum(h.harvest_count for h in self.harvests)
            remaining_count = cycle.initial_count - total_harvested
        
        if cycle.initial_count > 0:
            survival_rate = (remaining_count / cycle.initial_count) * 100
            self.survival_card.value_label.setText(f"{survival_rate:.1f}")

        # کل خوراک مصرفی
        total_feed = sum(f.feed_amount for f in self.feeds)

        # FCR
        if self.biomasses and len(self.biomasses) >= 1:
            last_biomass = self.biomasses[-1]
            current_weight = last_biomass.estimated_weight
            current_count = last_biomass.estimated_count
            current_total_weight_kg = (current_weight * current_count) / 1000
            initial_total_weight_kg = (cycle.initial_weight * cycle.initial_count) / 1000
            weight_gain = current_total_weight_kg - initial_total_weight_kg

            if weight_gain > 0 and total_feed > 0:
                fcr = total_feed / weight_gain
                self.fcr_card.value_label.setText(f"{fcr:.2f}")

        # SGR
        if len(self.biomasses) >= 2:
            first_biomass = self.biomasses[0]
            last_biomass = self.biomasses[-1]
            first_weight = first_biomass.estimated_weight
            last_weight = last_biomass.estimated_weight

            days = self.calculate_days_between(first_biomass.date, last_biomass.date)
            if days > 0 and first_weight > 0:
                sgr = ((last_weight / first_weight) ** (1/days) - 1) * 100
                self.sgr_card.value_label.setText(f"{sgr:.2f}")

        # اهداف
        self.fcr_target_card.value_label.setText(f"{getattr(cycle, 'target_fcr', 1.5)}")
        self.weight_target_card.value_label.setText(f"{cycle.target_weight:.0f}")

    def update_performance_table(self):
        combined_data = []

        for b in self.biomasses:
            combined_data.append({
                'date': b.date,
                'weight': b.estimated_weight,
                'count': b.estimated_count,
            })

        combined_data.sort(key=lambda x: x.get('date', ''))

        self.performance_table.setRowCount(len(combined_data))

        for i, data in enumerate(combined_data):
            feed_up_to_date = sum(f.feed_amount for f in self.feeds if f.date <= data['date'])
            mortality_up_to_date = sum(m.count for m in self.mortalities if m.date <= data['date'])

            fcr_current = "--"
            if self.production_cycle:
                initial_total_weight_kg = (self.production_cycle.initial_weight * self.production_cycle.initial_count) / 1000
                current_total_weight_kg = (data['weight'] * data['count']) / 1000
                weight_gain = current_total_weight_kg - initial_total_weight_kg
                if weight_gain > 0 and feed_up_to_date > 0:
                    fcr_current = f"{feed_up_to_date / weight_gain:.2f}"

            self.performance_table.setItem(i, 0, QtWidgets.QTableWidgetItem(data['date']))
            self.performance_table.setItem(i, 1, QtWidgets.QTableWidgetItem(f"{data['weight']:.0f}"))
            self.performance_table.setItem(i, 2, QtWidgets.QTableWidgetItem(f"{data['count']:,}"))
            self.performance_table.setItem(i, 3, QtWidgets.QTableWidgetItem(f"{feed_up_to_date:,.0f}"))
            self.performance_table.setItem(i, 4, QtWidgets.QTableWidgetItem(fcr_current))
            self.performance_table.setItem(i, 5, QtWidgets.QTableWidgetItem(f"{mortality_up_to_date:,}"))

    def update_alerts(self):
        alerts = []

        if self.biomasses:
            last_biomass = self.biomasses[-1]
            current_weight = last_biomass.estimated_weight
            target_weight = self.production_cycle.target_weight if self.production_cycle else 0

            if target_weight > 0 and current_weight >= target_weight:
                alerts.append("✅ وزن ماهی به هدف تعیین شده رسیده است. زمان برداشت فرا رسیده!")

        total_feed = sum(f.feed_amount for f in self.feeds)
        if self.biomasses and len(self.biomasses) >= 1 and self.production_cycle:
            last_biomass = self.biomasses[-1]
            current_total_weight_kg = (last_biomass.estimated_weight * last_biomass.estimated_count) / 1000
            initial_total_weight_kg = (self.production_cycle.initial_weight * self.production_cycle.initial_count) / 1000
            weight_gain = current_total_weight_kg - initial_total_weight_kg
            if weight_gain > 0 and total_feed > 0:
                fcr = total_feed / weight_gain
                if fcr > 2.0:
                    alerts.append("⚠️ هشدار: FCR بالاتر از حد مطلوب است. بررسی راندمان خوراک ضروری است.")

        if not alerts:
            alerts.append("✅ وضعیت مطلوب است. ادامه برنامه ریزی فعلی توصیه میشود.")

        self.alerts_text.setPlainText("\n".join(alerts))