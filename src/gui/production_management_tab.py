"""
تب شاخصهای پرورش - نمایش شاخصهای عملکردی و تحلیل دادهها
نسخه با قابلیت انتخاب قفس (تک قفسی یا همه)
"""

from PyQt5 import QtWidgets, QtCore

class ProductionManagementTab(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_farm = None
        self.current_mooring = None
        self.current_cage = None
        self.all_cages = []
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

        # ذخیره همه قفسها
        if self.current_mooring:
            self.all_cages = [c.id for c in self.current_mooring.cages]

        self.update_cage_combo()
        self.update_all()

    def update_cage_combo(self):
        """به‌روزرسانی لیست قفسها در کامبوباکس"""
        if hasattr(self, 'cage_filter_combo'):
            self.cage_filter_combo.clear()
            self.cage_filter_combo.addItem("🌊 همه قفسها", None)
            for cage_id in self.all_cages:
                self.cage_filter_combo.addItem(f"📦 قفس {cage_id}", cage_id)

    def setup_ui(self):
        layout = QtWidgets.QVBoxLayout(self)
        layout.setSpacing(8)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setAlignment(QtCore.Qt.AlignTop)

        title = QtWidgets.QLabel("📊 شاخصهای کلیدی عملکرد پرورش")
        title.setAlignment(QtCore.Qt.AlignCenter)
        title.setStyleSheet("font-size: 15px; font-weight: bold; color: #569CD6; padding: 5px;")
        layout.addWidget(title)

        # ========== انتخاب قفس ==========
        filter_layout = QtWidgets.QHBoxLayout()
        filter_layout.setSpacing(8)

        filter_label = QtWidgets.QLabel("نمایش شاخصها برای:")
        filter_label.setStyleSheet("color: #C8C8C8; font-size: 12px;")
        filter_layout.addWidget(filter_label)

        self.cage_filter_combo = QtWidgets.QComboBox()
        self.cage_filter_combo.setMinimumWidth(150)
        self.cage_filter_combo.setStyleSheet("""
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
        self.cage_filter_combo.currentIndexChanged.connect(self.on_cage_filter_changed)
        filter_layout.addWidget(self.cage_filter_combo)

        filter_layout.addStretch()
        layout.addLayout(filter_layout)

        # ========== شش کارت در یک ردیف ==========
        cards_layout = QtWidgets.QHBoxLayout()
        cards_layout.setSpacing(8)
        cards_layout.setContentsMargins(0, 0, 0, 0)

        self.fcr_card = self.create_kpi_card("FCR", "--", "ضریب تبدیل", "#569CD6")
        cards_layout.addWidget(self.fcr_card)

        self.sgr_card = self.create_kpi_card("SGR", "-- %/روز", "نرخ رشد ویژه", "#4EC9B0")
        cards_layout.addWidget(self.sgr_card)

        self.survival_card = self.create_kpi_card("نرخ بقا", "-- %", "تعداد باقیمانده / اولیه", "#DCDCAA")
        cards_layout.addWidget(self.survival_card)

        self.biomass_card = self.create_kpi_card("زیستتوده", "-- kg", "وزن تخمینی کل", "#CE9178")
        cards_layout.addWidget(self.biomass_card)

        self.fcr_target_card = self.create_kpi_card("هدف FCR", "--", "هدف تعیین شده", "#808080")
        cards_layout.addWidget(self.fcr_target_card)

        self.weight_target_card = self.create_kpi_card("وزن هدف", "-- گرم", "هدف تعیین شده", "#808080")
        cards_layout.addWidget(self.weight_target_card)

        layout.addLayout(cards_layout)

        # ========== جدول عملکرد ==========
        period_label = QtWidgets.QLabel("📊 روند عملکرد دوره پرورش")
        period_label.setStyleSheet("font-size: 13px; font-weight: bold; color: #569CD6; margin-top: 5px;")
        layout.addWidget(period_label)

        self.performance_table = QtWidgets.QTableWidget()
        self.performance_table.setMinimumHeight(180)
        self.performance_table.setMaximumHeight(250)
        self.performance_table.setColumnCount(6)
        self.performance_table.setHorizontalHeaderLabels(["تاریخ", "وزن", "تعداد", "خوراک", "FCR", "تلفات"])
        self.performance_table.horizontalHeader().setStretchLastSection(True)
        self.performance_table.setColumnWidth(0, 90)
        self.performance_table.setColumnWidth(1, 60)
        self.performance_table.setColumnWidth(2, 80)
        self.performance_table.setColumnWidth(3, 80)
        self.performance_table.setColumnWidth(4, 60)
        self.performance_table.setColumnWidth(5, 60)
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

        # ========== هشدارها ==========
        alerts_label = QtWidgets.QLabel("⚠️ هشدارها و توصیهها")
        alerts_label.setStyleSheet("font-size: 13px; font-weight: bold; color: #F48771; margin-top: 5px;")
        layout.addWidget(alerts_label)

        self.alerts_text = QtWidgets.QTextEdit()
        self.alerts_text.setReadOnly(True)
        self.alerts_text.setMinimumHeight(60)
        self.alerts_text.setMaximumHeight(80)
        self.alerts_text.setStyleSheet("""
            QTextEdit {
                background-color: #2D2D30;
                border: 2px solid #F48771;
                border-radius: 6px;
                color: #F48771;
                font-size: 11px;
                padding: 6px;
            }
        """)
        layout.addWidget(self.alerts_text)

        layout.addStretch()

    def on_cage_filter_changed(self):
        """تغییر قفس انتخاب شده - به‌روزرسانی شاخصها"""
        self.update_all()

    def get_filtered_data(self):
        """دریافت دادههای فیلتر شده بر اساس قفس انتخاب شده"""
        selected_cage = self.cage_filter_combo.currentData()

        if selected_cage is None:  # همه قفسها
            return self.feeds, self.mortalities, self.biomasses, self.harvests, self.production_cycle

        # فیلتر بر اساس قفس انتخاب شده
        filtered_feeds = [f for f in self.feeds if str(f.cage_id) == str(selected_cage)]
        filtered_mortalities = [m for m in self.mortalities if str(m.cage_id) == str(selected_cage)]
        filtered_biomasses = [b for b in self.biomasses if str(b.cage_id) == str(selected_cage)]
        filtered_harvests = [h for h in self.harvests if str(h.cage_id) == str(selected_cage)]

        # برای cycle باید بررسی کنیم که آیا برای این قفس دوره فعال وجود دارد
        filtered_cycle = self.production_cycle if self.production_cycle and str(self.production_cycle.cage_id) == str(selected_cage) else None

        return filtered_feeds, filtered_mortalities, filtered_biomasses, filtered_harvests, filtered_cycle

    def create_kpi_card(self, title, default_value, subtitle, color):
        card = QtWidgets.QFrame()
        card.setFixedSize(130, 85)
        card.setStyleSheet(f"""
            QFrame {{
                background-color: #1E1E1E;
                border: 1px solid #3E3E42;
                border-radius: 6px;
            }}
        """)

        layout = QtWidgets.QVBoxLayout(card)
        layout.setContentsMargins(4, 4, 4, 4)
        layout.setSpacing(2)

        title_lbl = QtWidgets.QLabel(title)
        title_lbl.setStyleSheet(f"font-size: 9px; color: {color}; font-weight: bold;")
        title_lbl.setAlignment(QtCore.Qt.AlignCenter)
        layout.addWidget(title_lbl)

        value_lbl = QtWidgets.QLabel(default_value)
        value_lbl.setStyleSheet("""
            font-size: 14px; 
            font-weight: bold; 
            color: white;
            background-color: #2D2D30;
            border-radius: 4px;
            padding: 3px;
        """)
        value_lbl.setAlignment(QtCore.Qt.AlignCenter)
        value_lbl.setFixedHeight(32)
        layout.addWidget(value_lbl)

        subtitle_lbl = QtWidgets.QLabel(subtitle)
        subtitle_lbl.setStyleSheet("font-size: 8px; color: #808080;")
        subtitle_lbl.setAlignment(QtCore.Qt.AlignCenter)
        layout.addWidget(subtitle_lbl)

        card.value_label = value_lbl
        return card

    def update_all(self):
        feeds, mortalities, biomasses, harvests, cycle = self.get_filtered_data()

        if not cycle:
            self.show_empty_state()
            return

        self.calculate_and_update_kpis(feeds, mortalities, biomasses, harvests, cycle)
        self.update_performance_table(biomasses, feeds, mortalities, cycle)
        self.update_alerts(biomasses, feeds, mortalities, cycle)

    def show_empty_state(self):
        for card in [self.fcr_card, self.sgr_card, self.survival_card, 
                     self.biomass_card, self.fcr_target_card, self.weight_target_card]:
            if hasattr(card, 'value_label'):
                card.value_label.setText("--")
        self.performance_table.setRowCount(0)
        self.alerts_text.setPlainText("⚠️ لطفاً یک قفس با دوره فعال انتخاب کنید.")

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

    def calculate_and_update_kpis(self, feeds, mortalities, biomasses, harvests, cycle):
        if not cycle:
            return

        # تبدیل به float برای جلوگیری از خطای Decimal
        initial_weight = float(cycle.initial_weight) if hasattr(cycle.initial_weight, '__float__') else float(cycle.initial_weight)
        initial_count = float(cycle.initial_count) if hasattr(cycle.initial_count, '__float__') else float(cycle.initial_count)
        target_weight = float(cycle.target_weight) if hasattr(cycle.target_weight, '__float__') else float(cycle.target_weight)

        # زیستتوده فعلی
        if biomasses:
            last_biomass = biomasses[-1]
            current_weight = float(last_biomass.estimated_weight) if hasattr(last_biomass.estimated_weight, '__float__') else float(last_biomass.estimated_weight)
            current_count = float(last_biomass.estimated_count) if hasattr(last_biomass.estimated_count, '__float__') else float(last_biomass.estimated_count)
            current_biomass_kg = (current_weight * current_count) / 1000
            self.biomass_card.value_label.setText(f"{current_biomass_kg:,.0f}")
        else:
            current_biomass_kg = (initial_weight * initial_count) / 1000
            self.biomass_card.value_label.setText(f"{current_biomass_kg:,.0f}*")

        # نرخ بقا
        remaining_count = initial_count
        if biomasses:
            remaining_count = float(biomasses[-1].estimated_count) if hasattr(biomasses[-1].estimated_count, '__float__') else float(biomasses[-1].estimated_count)
        elif harvests:
            total_harvested = sum(float(h.harvest_count) for h in harvests)
            remaining_count = initial_count - total_harvested

        if initial_count > 0:
            survival_rate = (remaining_count / initial_count) * 100
            self.survival_card.value_label.setText(f"{survival_rate:.1f}")

        # کل خوراک مصرفی
        total_feed = sum(float(f.feed_amount) for f in feeds) if feeds else 0

        # FCR
        if biomasses and len(biomasses) >= 1:
            last_biomass = biomasses[-1]
            current_weight = float(last_biomass.estimated_weight) if hasattr(last_biomass.estimated_weight, '__float__') else float(last_biomass.estimated_weight)
            current_count = float(last_biomass.estimated_count) if hasattr(last_biomass.estimated_count, '__float__') else float(last_biomass.estimated_count)
            current_total_weight_kg = (current_weight * current_count) / 1000
            initial_total_weight_kg = (initial_weight * initial_count) / 1000
            weight_gain = current_total_weight_kg - initial_total_weight_kg

            if weight_gain > 0 and total_feed > 0:
                fcr = total_feed / weight_gain
                self.fcr_card.value_label.setText(f"{fcr:.2f}")

        # SGR
        if len(biomasses) >= 2:
            first_biomass = biomasses[0]
            last_biomass = biomasses[-1]
            first_weight = float(first_biomass.estimated_weight) if hasattr(first_biomass.estimated_weight, '__float__') else float(first_biomass.estimated_weight)
            last_weight = float(last_biomass.estimated_weight) if hasattr(last_biomass.estimated_weight, '__float__') else float(last_biomass.estimated_weight)

            days = self.calculate_days_between(first_biomass.date, last_biomass.date)
            if days > 0 and first_weight > 0:
                sgr = ((last_weight / first_weight) ** (1/days) - 1) * 100
                self.sgr_card.value_label.setText(f"{sgr:.2f}")

        # اهداف
        self.fcr_target_card.value_label.setText(f"{getattr(cycle, 'target_fcr', 1.5)}")
        self.weight_target_card.value_label.setText(f"{target_weight:.0f}")

    def update_performance_table(self, biomasses, feeds, mortalities, cycle):
        combined_data = []

        for b in biomasses:
            combined_data.append({
                'date': b.date,
                'weight': float(b.estimated_weight) if hasattr(b.estimated_weight, '__float__') else float(b.estimated_weight),
                'count': float(b.estimated_count) if hasattr(b.estimated_count, '__float__') else float(b.estimated_count),
            })

        combined_data.sort(key=lambda x: x.get('date', ''))

        self.performance_table.setRowCount(len(combined_data))

        if not cycle:
            return

        initial_weight = float(cycle.initial_weight) if hasattr(cycle.initial_weight, '__float__') else float(cycle.initial_weight)
        initial_count = float(cycle.initial_count) if hasattr(cycle.initial_count, '__float__') else float(cycle.initial_count)

        for i, data in enumerate(combined_data):
            feed_up_to_date = sum(float(f.feed_amount) for f in feeds if f.date <= data['date']) if feeds else 0
            mortality_up_to_date = sum(float(m.count) for m in mortalities if m.date <= data['date']) if mortalities else 0

            fcr_current = "--"
            initial_total_weight_kg = (initial_weight * initial_count) / 1000
            current_total_weight_kg = (data['weight'] * data['count']) / 1000
            weight_gain = current_total_weight_kg - initial_total_weight_kg
            if weight_gain > 0 and feed_up_to_date > 0:
                fcr_current = f"{feed_up_to_date / weight_gain:.2f}"

            self.performance_table.setItem(i, 0, QtWidgets.QTableWidgetItem(data['date']))
            self.performance_table.setItem(i, 1, QtWidgets.QTableWidgetItem(f"{data['weight']:.0f}"))
            self.performance_table.setItem(i, 2, QtWidgets.QTableWidgetItem(f"{data['count']:,.0f}"))
            self.performance_table.setItem(i, 3, QtWidgets.QTableWidgetItem(f"{feed_up_to_date:,.0f}"))
            self.performance_table.setItem(i, 4, QtWidgets.QTableWidgetItem(fcr_current))
            self.performance_table.setItem(i, 5, QtWidgets.QTableWidgetItem(f"{mortality_up_to_date:,.0f}"))

    def update_alerts(self, biomasses, feeds, mortalities, cycle):
        alerts = []

        if biomasses:
            last_biomass = biomasses[-1]
            current_weight = float(last_biomass.estimated_weight) if hasattr(last_biomass.estimated_weight, '__float__') else float(last_biomass.estimated_weight)
            target_weight = float(cycle.target_weight) if cycle and hasattr(cycle.target_weight, '__float__') else float(cycle.target_weight) if cycle else 0

            if target_weight > 0 and current_weight >= target_weight:
                alerts.append("✅ وزن ماهی به هدف تعیین شده رسیده است. زمان برداشت فرا رسیده!")

        total_feed = sum(float(f.feed_amount) for f in feeds) if feeds else 0
        if biomasses and len(biomasses) >= 1 and cycle:
            last_biomass = biomasses[-1]
            current_weight = float(last_biomass.estimated_weight) if hasattr(last_biomass.estimated_weight, '__float__') else float(last_biomass.estimated_weight)
            current_count = float(last_biomass.estimated_count) if hasattr(last_biomass.estimated_count, '__float__') else float(last_biomass.estimated_count)
            current_total_weight_kg = (current_weight * current_count) / 1000
            initial_weight = float(cycle.initial_weight) if hasattr(cycle.initial_weight, '__float__') else float(cycle.initial_weight)
            initial_count = float(cycle.initial_count) if hasattr(cycle.initial_count, '__float__') else float(cycle.initial_count)
            initial_total_weight_kg = (initial_weight * initial_count) / 1000
            weight_gain = current_total_weight_kg - initial_total_weight_kg
            if weight_gain > 0 and total_feed > 0:
                fcr = total_feed / weight_gain
                if fcr > 2.0:
                    alerts.append("⚠️ هشدار: FCR بالاتر از حد مطلوب است. بررسی راندمان خوراک ضروری است.")
                else:
                    alerts.append(f"✅ FCR در محدوده مناسب: {fcr:.2f}")

        if not alerts:
            alerts.append("✅ وضعیت مطلوب است. ادامه برنامه ریزی فعلی توصیه میشود.")

        self.alerts_text.setPlainText("\n".join(alerts))