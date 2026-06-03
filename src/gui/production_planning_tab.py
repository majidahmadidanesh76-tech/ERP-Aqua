"""
صفحه برنامهریزی تولید - شامل تقویم رشد و برنامه شیفتی و بودجهبندی سالانه
نسخه با تاریخ میلادی و تبدیل شمسی برای نمایش
"""

from PyQt5 import QtWidgets, QtCore, QtGui
import qtawesome as qta
from ..database.db_handler import DatabaseHandler
from functools import partial
from datetime import date, timedelta
import math
import jdatetime

class ProductionPlanningTab(QtWidgets.QWidget):
    def __init__(self, parent=None, farm=None, mooring=None):
        super().__init__(parent)
        self.db = DatabaseHandler()
        self.current_farm = farm
        self.current_mooring = mooring
        self.setup_ui()
        self.load_data()

    def setup_ui(self):
        layout = QtWidgets.QVBoxLayout(self)
        layout.setSpacing(10)

        title = QtWidgets.QLabel("📋 برنامهریزی تولید")
        title.setAlignment(QtCore.Qt.AlignCenter)
        title.setStyleSheet("font-size: 18px; font-weight: bold; color: #569CD6; padding: 10px;")
        layout.addWidget(title)

        self.tabs = QtWidgets.QTabWidget()
        self.tabs.setStyleSheet("""
            QTabWidget::pane {
                border: 1px solid #2D2D30;
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

        self.growth_calendar_tab = self.create_growth_calendar_tab()
        self.tabs.addTab(self.growth_calendar_tab, "📅 تقویم رشد")

        self.shift_planning_tab = self.create_shift_planning_tab()
        self.tabs.addTab(self.shift_planning_tab, "🧑🌾 برنامه شیفتی")

        self.budget_tab = self.create_budget_tab()
        self.tabs.addTab(self.budget_tab, "📊 بودجهبندی سالانه")

        layout.addWidget(self.tabs)

    def load_data(self):
        self.load_cages()
        self.load_species()
        self.load_saved_plans()
        self.update_budget_preview()

    def load_cages(self):
        self.cage_combo.clear()
        self.budget_cage_combo.clear()
        if self.current_mooring and hasattr(self.current_mooring, 'cages'):
            for cage in self.current_mooring.cages:
                self.cage_combo.addItem(cage.id, cage.id)
                self.budget_cage_combo.addItem(cage.id, cage.id)
            if self.cage_combo.count() > 0:
                self.cage_combo.setCurrentIndex(0)
            if self.budget_cage_combo.count() > 0:
                self.budget_cage_combo.setCurrentIndex(0)

    def load_species(self):
        species = self.db.get_all_species()
        self.species_combo.clear()
        for s in species:
            self.species_combo.addItem(s['name'], s['id'])

    def load_saved_plans(self):
        if hasattr(self, 'plans_list'):
            cage_id = self.cage_combo.currentData() if self.cage_combo.count() > 0 else None
            self.plans_list.clear()
            if cage_id:
                plans = self.db.get_production_plans_by_cage(cage_id)
                for plan in plans:
                    item_text = f"{plan['planned_stocking_date']} → {plan['planned_harvest_date']} (خوراک: {plan['estimated_feed_required']:.0f}kg)"
                    item = QtWidgets.QListWidgetItem(item_text)
                    item.setData(QtCore.Qt.UserRole, plan['id'])
                    self.plans_list.addItem(item)

    def convert_miladi_to_shamsi(self, miladi_date):
        """تبدیل تاریخ میلادی به شمسی برای نمایش"""
        if not miladi_date:
            return ""
        try:
            if isinstance(miladi_date, str):
                parts = miladi_date.split('-')
                if len(parts) == 3:
                    d = date(int(parts[0]), int(parts[1]), int(parts[2]))
                    shamsi = jdatetime.date.fromgregorian(date=d)
                    return f"{shamsi.year}/{shamsi.month:02d}/{shamsi.day:02d}"
            elif hasattr(miladi_date, 'year'):
                shamsi = jdatetime.date.fromgregorian(date=miladi_date)
                return f"{shamsi.year}/{shamsi.month:02d}/{shamsi.day:02d}"
        except:
            pass
        return str(miladi_date)

    # ==================== توزیع هوشمند خوراک ====================
    
    def distribute_feed_over_months(self, total_feed_kg, start_year, start_month, end_year, end_month):
        duration_months = (end_year - start_year) * 12 + (end_month - start_month) + 1
        if duration_months <= 0 or total_feed_kg <= 0:
            return [0] * 12
        weights = []
        for i in range(duration_months):
            weight = (i + 1) ** 1.5
            weights.append(weight)
        total_weight = sum(weights)
        weights = [w / total_weight for w in weights]
        monthly_feeds_period = [total_feed_kg * w for w in weights]
        result = [0] * 12
        for i in range(duration_months):
            month_idx = (start_month + i) % 12
            result[month_idx] += monthly_feeds_period[i]
        return result

    # ==================== تب تقویم رشد ====================

    def create_growth_calendar_tab(self):
        tab = QtWidgets.QWidget()
        main_layout = QtWidgets.QVBoxLayout(tab)
        main_layout.setSpacing(10)

        saved_group = QtWidgets.QGroupBox("📋 برنامههای ذخیره شده")
        saved_group.setStyleSheet("""
            QGroupBox {
                border: 1px solid #2D2D30;
                border-radius: 5px;
                margin-top: 10px;
                padding-top: 10px;
                color: #C8C8C8;
                font-weight: bold;
            }
            QGroupBox::title {
                color: #569CD6;
            }
        """)
        saved_layout = QtWidgets.QVBoxLayout(saved_group)

        self.plans_list = QtWidgets.QListWidget()
        self.plans_list.setMaximumHeight(120)
        self.plans_list.setStyleSheet("""
            QListWidget {
                background-color: #252526;
                border: 1px solid #2D2D30;
                border-radius: 4px;
                color: #C8C8C8;
                padding: 5px;
            }
            QListWidget::item {
                padding: 6px;
                border-bottom: 1px solid #2D2D30;
            }
            QListWidget::item:selected {
                background-color: #0E639C;
            }
        """)

        list_btn_layout = QtWidgets.QHBoxLayout()
        list_btn_layout.setSpacing(5)

        glass_btn_style = """
            QToolButton {
                background-color: rgba(60, 60, 65, 180);
                border: none;
                border-radius: 4px;
                padding: 4px;
                min-width: 32px;
                min-height: 32px;
            }
            QToolButton:hover {
                background-color: rgba(86, 156, 214, 100);
            }
        """

        self.edit_plan_btn = QtWidgets.QToolButton()
        self.edit_plan_btn.setIcon(qta.icon('fa5s.edit', color='#569CD6'))
        self.edit_plan_btn.setIconSize(QtCore.QSize(18, 18))
        self.edit_plan_btn.setToolTip("ویرایش برنامه")
        self.edit_plan_btn.setStyleSheet(glass_btn_style)
        self.edit_plan_btn.clicked.connect(self.edit_selected_plan)
        self.edit_plan_btn.setEnabled(False)

        self.delete_plan_btn = QtWidgets.QToolButton()
        self.delete_plan_btn.setIcon(qta.icon('fa5s.trash-alt', color='#F48771'))
        self.delete_plan_btn.setIconSize(QtCore.QSize(18, 18))
        self.delete_plan_btn.setToolTip("حذف برنامه")
        self.delete_plan_btn.setStyleSheet(glass_btn_style)
        self.delete_plan_btn.clicked.connect(self.delete_selected_plan)
        self.delete_plan_btn.setEnabled(False)

        list_btn_layout.addWidget(self.edit_plan_btn)
        list_btn_layout.addWidget(self.delete_plan_btn)
        list_btn_layout.addStretch()

        saved_layout.addWidget(self.plans_list)
        saved_layout.addLayout(list_btn_layout)

        self.plans_list.itemSelectionChanged.connect(self.on_plan_selected)

        main_layout.addWidget(saved_group)

        input_group = QtWidgets.QGroupBox("📝 اطلاعات اولیه")
        input_group.setStyleSheet("""
            QGroupBox {
                border: 1px solid #2D2D30;
                border-radius: 5px;
                margin-top: 10px;
                padding-top: 10px;
                color: #C8C8C8;
                font-weight: bold;
            }
            QGroupBox::title {
                color: #569CD6;
            }
        """)
        form_layout = QtWidgets.QFormLayout(input_group)
        form_layout.setSpacing(12)
        form_layout.setLabelAlignment(QtCore.Qt.AlignRight)

        label_style = "color: #C8C8C8; font-weight: normal; min-width: 100px;"

        self.cage_combo = QtWidgets.QComboBox()
        self.cage_combo.setMinimumWidth(220)
        self.cage_combo.setStyleSheet("padding: 5px; background-color: #3C3C3C; border: 1px solid #2D2D30; border-radius: 4px; color: #C8C8C8;")
        self.cage_combo.currentIndexChanged.connect(self.load_saved_plans)
        cage_label = QtWidgets.QLabel("انتخاب قفس:")
        cage_label.setStyleSheet(label_style)
        form_layout.addRow(cage_label, self.cage_combo)

        self.species_combo = QtWidgets.QComboBox()
        self.species_combo.setStyleSheet("padding: 5px; background-color: #3C3C3C; border: 1px solid #2D2D30; border-radius: 4px; color: #C8C8C8;")
        species_label = QtWidgets.QLabel("گونه ماهی:")
        species_label.setStyleSheet(label_style)
        form_layout.addRow(species_label, self.species_combo)

        # تاریخ رهاسازی (میلادی)
        self.stocking_date = QtWidgets.QDateEdit()
        self.stocking_date.setCalendarPopup(True)
        self.stocking_date.setDate(QtCore.QDate.currentDate())
        self.stocking_date.setStyleSheet("padding: 5px; background-color: #3C3C3C; border: 1px solid #2D2D30; border-radius: 4px; color: #C8C8C8;")
        date_label = QtWidgets.QLabel("تاریخ رهاسازی (میلادی):")
        date_label.setStyleSheet(label_style)
        form_layout.addRow(date_label, self.stocking_date)

        self.initial_weight = QtWidgets.QDoubleSpinBox()
        self.initial_weight.setRange(1, 5000)
        self.initial_weight.setValue(50)
        self.initial_weight.setSuffix(" گرم")
        self.initial_weight.setStyleSheet("padding: 5px; background-color: #3C3C3C; border: 1px solid #2D2D30; border-radius: 4px; color: #C8C8C8;")
        weight_label = QtWidgets.QLabel("وزن اولیه:")
        weight_label.setStyleSheet(label_style)
        form_layout.addRow(weight_label, self.initial_weight)

        main_layout.addWidget(input_group)

        self.calc_btn = QtWidgets.QPushButton("🔮 محاسبه پیشبینی رشد")
        self.calc_btn.setMinimumHeight(40)
        self.calc_btn.setStyleSheet("""
            QPushButton {
                background-color: rgba(86, 156, 214, 80);
                color: white;
                font-weight: bold;
                border-radius: 4px;
                padding: 8px 16px;
                border: none;
            }
            QPushButton:hover {
                background-color: rgba(86, 156, 214, 120);
            }
        """)
        self.calc_btn.clicked.connect(self.calculate_growth_forecast)
        main_layout.addWidget(self.calc_btn)

        self.result_group = QtWidgets.QGroupBox("📊 نتایج پیشبینی")
        self.result_group.setStyleSheet("""
            QGroupBox {
                border: 1px solid #2D2D30;
                border-radius: 5px;
                margin-top: 10px;
                padding-top: 10px;
                color: #C8C8C8;
                font-weight: bold;
            }
            QGroupBox::title {
                color: #569CD6;
            }
        """)
        result_layout = QtWidgets.QGridLayout(self.result_group)
        result_layout.setSpacing(12)
        result_layout.setHorizontalSpacing(20)

        result_label_style = "color: #C8C8C8; font-weight: normal;"
        result_value_style = "color: #4EC9B0; font-weight: bold; font-size: 13px;"

        harvest_lbl = QtWidgets.QLabel("⏳ تاریخ تخمینی برداشت (میلادی):")
        harvest_lbl.setStyleSheet(result_label_style)
        self.harvest_date_label = QtWidgets.QLabel("--")
        self.harvest_date_label.setStyleSheet(result_value_style)
        self.harvest_date_label.setAlignment(QtCore.Qt.AlignRight)
        result_layout.addWidget(harvest_lbl, 0, 0)
        result_layout.addWidget(self.harvest_date_label, 0, 1)

        harvest_shamsi_lbl = QtWidgets.QLabel("📅 تاریخ تخمینی برداشت (شمسی):")
        harvest_shamsi_lbl.setStyleSheet(result_label_style)
        self.harvest_date_shamsi_label = QtWidgets.QLabel("--")
        self.harvest_date_shamsi_label.setStyleSheet(result_value_style)
        self.harvest_date_shamsi_label.setAlignment(QtCore.Qt.AlignRight)
        result_layout.addWidget(harvest_shamsi_lbl, 0, 2)
        result_layout.addWidget(self.harvest_date_shamsi_label, 0, 3)

        feed_lbl = QtWidgets.QLabel("🍽️ خوراک مورد نیاز (کل):")
        feed_lbl.setStyleSheet(result_label_style)
        self.feed_needed_label = QtWidgets.QLabel("--")
        self.feed_needed_label.setStyleSheet(result_value_style)
        self.feed_needed_label.setAlignment(QtCore.Qt.AlignRight)
        result_layout.addWidget(feed_lbl, 1, 0)
        result_layout.addWidget(self.feed_needed_label, 1, 1)

        fcr_lbl = QtWidgets.QLabel("📊 ضریب تبدیل پیشبینی:")
        fcr_lbl.setStyleSheet(result_label_style)
        self.fcr_label = QtWidgets.QLabel("--")
        self.fcr_label.setStyleSheet(result_value_style)
        self.fcr_label.setAlignment(QtCore.Qt.AlignRight)
        result_layout.addWidget(fcr_lbl, 1, 2)
        result_layout.addWidget(self.fcr_label, 1, 3)

        growth_lbl = QtWidgets.QLabel("📈 نرخ رشد روزانه:")
        growth_lbl.setStyleSheet(result_label_style)
        self.growth_rate_label = QtWidgets.QLabel("--")
        self.growth_rate_label.setStyleSheet(result_value_style)
        self.growth_rate_label.setAlignment(QtCore.Qt.AlignRight)
        result_layout.addWidget(growth_lbl, 2, 0)
        result_layout.addWidget(self.growth_rate_label, 2, 1)

        result_layout.setColumnStretch(1, 1)
        result_layout.setColumnStretch(3, 1)

        main_layout.addWidget(self.result_group)

        self.save_plan_btn = QtWidgets.QPushButton("💾 ذخیره این برنامه")
        self.save_plan_btn.setMinimumHeight(40)
        self.save_plan_btn.setStyleSheet("""
            QPushButton {
                background-color: rgba(46, 139, 87, 80);
                color: white;
                font-weight: bold;
                border-radius: 4px;
                padding: 8px 16px;
                border: none;
            }
            QPushButton:hover {
                background-color: rgba(46, 139, 87, 120);
            }
        """)
        self.save_plan_btn.clicked.connect(self.save_current_plan)
        self.save_plan_btn.setEnabled(False)
        main_layout.addWidget(self.save_plan_btn)

        main_layout.addStretch()
        return tab

    def on_plan_selected(self):
        has_selection = len(self.plans_list.selectedItems()) > 0
        self.edit_plan_btn.setEnabled(has_selection)
        self.delete_plan_btn.setEnabled(has_selection)

    def edit_selected_plan(self):
        selected = self.plans_list.selectedItems()
        if not selected:
            QtWidgets.QMessageBox.warning(self, "خطا", "لطفاً یک برنامه را انتخاب کنید")
            return
        plan_id = selected[0].data(QtCore.Qt.UserRole)
        try:
            cursor = self.db.db.connection.cursor(dictionary=True)
            cursor.execute("SELECT * FROM production_plans WHERE id = %s", (plan_id,))
            plan = cursor.fetchone()
            cursor.close()
            if plan:
                self.cage_combo.setCurrentText(plan['cage_id'])
                species_id = plan['species_id']
                for i in range(self.species_combo.count()):
                    if self.species_combo.itemData(i) == species_id:
                        self.species_combo.setCurrentIndex(i)
                        break
                
                stocking_date = plan['planned_stocking_date']
                if hasattr(stocking_date, 'strftime'):
                    date_str = stocking_date.strftime("%Y-%m-%d")
                else:
                    date_str = str(stocking_date)
                
                date_parts = date_str.split('-')
                self.stocking_date.setDate(QtCore.QDate(int(date_parts[0]), int(date_parts[1]), int(date_parts[2])))
                self.initial_weight.setValue(50)
                self.calculate_growth_forecast()
                cursor2 = self.db.db.connection.cursor()
                cursor2.execute("DELETE FROM production_plans WHERE id = %s", (plan_id,))
                self.db.db.connection.commit()
                cursor2.close()
                self.load_saved_plans()
                QtWidgets.QMessageBox.information(self, "اطلاع", "برنامه برای ویرایش بارگذاری شد. پس از ویرایش، دوباره ذخیره کنید.")
            else:
                QtWidgets.QMessageBox.warning(self, "خطا", "برنامه یافت نشد")
        except Exception as e:
            QtWidgets.QMessageBox.warning(self, "خطا", f"خطا در ویرایش: {e}")

    def delete_selected_plan(self):
        selected = self.plans_list.selectedItems()
        if not selected:
            QtWidgets.QMessageBox.warning(self, "خطا", "لطفاً یک برنامه را انتخاب کنید")
            return
        plan_id = selected[0].data(QtCore.Qt.UserRole)
        reply = QtWidgets.QMessageBox.question(self, "تأیید حذف", "آیا از حذف این برنامه مطمئن هستید؟", QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)
        if reply == QtWidgets.QMessageBox.Yes:
            try:
                cursor = self.db.db.connection.cursor()
                cursor.execute("DELETE FROM production_plans WHERE id = %s", (plan_id,))
                self.db.db.connection.commit()
                cursor.close()
                self.load_saved_plans()
                QtWidgets.QMessageBox.information(self, "موفق", "برنامه با موفقیت حذف شد")
            except Exception as e:
                QtWidgets.QMessageBox.warning(self, "خطا", f"خطا در حذف: {e}")

    def calculate_growth_forecast(self):
        species_id = self.species_combo.currentData()
        if not species_id:
            QtWidgets.QMessageBox.warning(self, "خطا", "لطفاً گونه ماهی را انتخاب کنید")
            return
        species = self.db.get_species_by_id(species_id)
        if not species:
            QtWidgets.QMessageBox.warning(self, "خطا", "اطلاعات گونه یافت نشد")
            return
        initial_weight = self.initial_weight.value()
        target_weight = float(species.get('typical_harvest_weight', 0))
        daily_gain = float(species.get('avg_daily_gain', 0))
        target_fcr = float(species.get('target_fcr', 1.5))
        if daily_gain <= 0:
            self.harvest_date_label.setText("محاسبه ناممکن")
            QtWidgets.QMessageBox.warning(self, "خطا", "نرخ رشد روزانه معتبر نیست")
            return
        days_needed = (target_weight - initial_weight) / daily_gain
        harvest_date = self.stocking_date.date().addDays(int(days_needed))
        
        weight_gain_kg = (target_weight - initial_weight) / 1000
        feed_needed = weight_gain_kg * target_fcr
        
        self.harvest_date_label.setText(harvest_date.toString("yyyy-MM-dd"))
        
        # تبدیل تاریخ برداشت به شمسی
        try:
            harvest_gregorian = date(harvest_date.year(), harvest_date.month(), harvest_date.day())
            harvest_jalali = jdatetime.date.fromgregorian(date=harvest_gregorian)
            self.harvest_date_shamsi_label.setText(f"{harvest_jalali.year}/{harvest_jalali.month:02d}/{harvest_jalali.day:02d}")
        except:
            self.harvest_date_shamsi_label.setText("خطا در تبدیل")
        
        self.feed_needed_label.setText(f"{feed_needed:,.0f}")
        self.fcr_label.setText(f"{target_fcr}")
        self.growth_rate_label.setText(f"{daily_gain:.1f}")
        
        self.current_forecast = {
            'species_id': species_id,
            'stocking_date': self.stocking_date.date().toString("yyyy-MM-dd"),
            'harvest_date': harvest_date.toString("yyyy-MM-dd"),
            'feed_needed': feed_needed,
            'target_weight': target_weight
        }
        self.save_plan_btn.setEnabled(True)

    def clear_input_fields(self):
        self.stocking_date.setDate(QtCore.QDate.currentDate())
        self.initial_weight.setValue(50)
        self.harvest_date_label.setText("--")
        self.harvest_date_shamsi_label.setText("--")
        self.feed_needed_label.setText("--")
        self.fcr_label.setText("--")
        self.growth_rate_label.setText("--")
        self.save_plan_btn.setEnabled(False)
        if hasattr(self, 'current_forecast'):
            delattr(self, 'current_forecast')

    def save_current_plan(self):
        cage_id = self.cage_combo.currentData()
        if not cage_id:
            QtWidgets.QMessageBox.warning(self, "خطا", "لطفاً قفس را انتخاب کنید")
            return
        if not hasattr(self, 'current_forecast'):
            QtWidgets.QMessageBox.warning(self, "خطا", "لطفاً ابتدا پیشبینی را محاسبه کنید")
            return
        result = self.db.save_production_plan(
            cage_id,
            self.current_forecast['species_id'],
            self.current_forecast['stocking_date'],
            self.current_forecast['harvest_date'],
            self.current_forecast['feed_needed']
        )
        if result:
            QtWidgets.QMessageBox.information(self, "موفق", "برنامه تولید با موفقیت ذخیره شد")
            self.clear_input_fields()
            self.load_saved_plans()
        else:
            QtWidgets.QMessageBox.warning(self, "خطا", "خطا در ذخیره برنامه تولید")

    # ==================== تب برنامه شیفتی ====================

    def create_shift_planning_tab(self):
        tab = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout(tab)
        layout.setSpacing(10)

        toolbar = QtWidgets.QHBoxLayout()
        toolbar.setSpacing(8)

        date_label = QtWidgets.QLabel("تاریخ:")
        date_label.setStyleSheet("color: #C8C8C8; font-weight: bold;")
        toolbar.addWidget(date_label)

        self.shift_date = QtWidgets.QDateEdit()
        self.shift_date.setCalendarPopup(True)
        self.shift_date.setDate(QtCore.QDate.currentDate())
        self.shift_date.setMinimumWidth(120)
        self.shift_date.setStyleSheet("padding: 5px; background-color: #3C3C3C; border: 1px solid #2D2D30; border-radius: 4px; color: #C8C8C8;")
        self.shift_date.dateChanged.connect(self.load_daily_tasks)
        toolbar.addWidget(self.shift_date)

        toolbar.addSpacing(20)

        self.add_task_btn = QtWidgets.QPushButton("➕ افزودن وظیفه")
        self.add_task_btn.setStyleSheet("""
            QPushButton {
                background-color: rgba(46, 139, 87, 80);
                color: white;
                font-weight: bold;
                border-radius: 4px;
                padding: 6px 12px;
                border: none;
            }
            QPushButton:hover {
                background-color: rgba(46, 139, 87, 120);
            }
        """)
        self.add_task_btn.clicked.connect(self.add_new_task)
        toolbar.addWidget(self.add_task_btn)

        toolbar.addSpacing(10)

        self.refresh_tasks_btn = QtWidgets.QPushButton("🔄 بهروزرسانی")
        self.refresh_tasks_btn.setStyleSheet("""
            QPushButton {
                background-color: rgba(86, 156, 214, 80);
                color: white;
                font-weight: bold;
                border-radius: 4px;
                padding: 6px 12px;
                border: none;
            }
            QPushButton:hover {
                background-color: rgba(86, 156, 214, 120);
            }
        """)
        self.refresh_tasks_btn.clicked.connect(self.load_daily_tasks)
        toolbar.addWidget(self.refresh_tasks_btn)

        toolbar.addStretch()
        layout.addLayout(toolbar)

        self.tasks_table = QtWidgets.QTableWidget()
        self.tasks_table.setColumnCount(6)
        self.tasks_table.setHorizontalHeaderLabels(["شناسه", "زمان", "وظیفه", "مسئول", "وضعیت", "عملیات"])
        self.tasks_table.horizontalHeader().setStretchLastSection(True)
        self.tasks_table.setColumnWidth(0, 60)
        self.tasks_table.setColumnWidth(1, 100)
        self.tasks_table.setColumnWidth(2, 130)
        self.tasks_table.setColumnWidth(3, 120)
        self.tasks_table.setColumnWidth(4, 100)
        self.tasks_table.setColumnWidth(5, 80)
        self.tasks_table.setStyleSheet("""
            QTableWidget {
                border: 1px solid #2D2D30;
                border-radius: 4px;
                background-color: #2D2D30;
                alternate-background-color: #252526;
                gridline-color: #2D2D30;
            }
            QTableWidget::item:selected {
                background-color: #0E639C;
            }
            QHeaderView::section {
                background-color: #252526;
                color: #569CD6;
                border: none;
                border-bottom: 1px solid #2D2D30;
            }
        """)
        layout.addWidget(self.tasks_table)

        stats_frame = QtWidgets.QFrame()
        stats_frame.setStyleSheet("background-color: #252526; border-radius: 5px; padding: 5px; border: 1px solid #2D2D30;")
        stats_layout = QtWidgets.QHBoxLayout(stats_frame)

        self.total_tasks_label = QtWidgets.QLabel("📋 کل وظایف: 0")
        self.pending_tasks_label = QtWidgets.QLabel("⏳ در انتظار: 0")
        self.done_tasks_label = QtWidgets.QLabel("✅ انجام شده: 0")

        for label in [self.total_tasks_label, self.pending_tasks_label, self.done_tasks_label]:
            label.setStyleSheet("color: #C8C8C8; font-size: 11px;")
            stats_layout.addWidget(label)

        stats_layout.addStretch()
        layout.addWidget(stats_frame)

        self.load_daily_tasks()

        return tab

    def load_daily_tasks(self):
        task_date = self.shift_date.date().toString("yyyy-MM-dd")
        tasks = self.db.get_daily_tasks_by_date(task_date)
        self.tasks_table.setRowCount(len(tasks))

        pending = 0
        done = 0

        glass_btn_style = """
            QToolButton {
                background-color: rgba(60, 60, 65, 180);
                border: none;
                border-radius: 3px;
                padding: 2px;
                min-width: 20px;
                min-height: 20px;
            }
            QToolButton:hover {
                background-color: rgba(86, 156, 214, 100);
            }
        """

        for i, task in enumerate(tasks):
            self.tasks_table.setItem(i, 0, QtWidgets.QTableWidgetItem(str(task['id'])))
            self.tasks_table.setItem(i, 1, QtWidgets.QTableWidgetItem(task['shift_time']))
            self.tasks_table.setItem(i, 2, QtWidgets.QTableWidgetItem(task['task_type']))
            self.tasks_table.setItem(i, 3, QtWidgets.QTableWidgetItem(task['assigned_to'] if task['assigned_to'] else "تعیین نشده"))

            if task['status'] == 'done':
                status_text = "✅ انجام شده"
                done += 1
            else:
                status_text = "⏳ در انتظار"
                pending += 1
            self.tasks_table.setItem(i, 4, QtWidgets.QTableWidgetItem(status_text))

            btn_widget = QtWidgets.QWidget()
            btn_layout = QtWidgets.QHBoxLayout(btn_widget)
            btn_layout.setContentsMargins(2, 2, 2, 2)
            btn_layout.setSpacing(2)

            if task['status'] != 'done':
                complete_btn = QtWidgets.QToolButton()
                complete_btn.setIcon(qta.icon('fa5s.check-circle', color='#4EC9B0'))
                complete_btn.setIconSize(QtCore.QSize(12, 12))
                complete_btn.setToolTip("تکمیل وظیفه")
                complete_btn.setStyleSheet(glass_btn_style)
                complete_btn.setFixedSize(20, 20)
                complete_btn.clicked.connect(partial(self.complete_task, task['id']))
                btn_layout.addWidget(complete_btn)
                
                edit_btn = QtWidgets.QToolButton()
                edit_btn.setIcon(qta.icon('fa5s.edit', color='#569CD6'))
                edit_btn.setIconSize(QtCore.QSize(12, 12))
                edit_btn.setToolTip("ویرایش وظیفه")
                edit_btn.setStyleSheet(glass_btn_style)
                edit_btn.setFixedSize(20, 20)
                edit_btn.clicked.connect(partial(self.edit_task, task['id']))
                btn_layout.addWidget(edit_btn)
                
                delete_btn = QtWidgets.QToolButton()
                delete_btn.setIcon(qta.icon('fa5s.trash-alt', color='#F48771'))
                delete_btn.setIconSize(QtCore.QSize(12, 12))
                delete_btn.setToolTip("حذف وظیفه")
                delete_btn.setStyleSheet(glass_btn_style)
                delete_btn.setFixedSize(20, 20)
                delete_btn.clicked.connect(partial(self.delete_task, task['id']))
                btn_layout.addWidget(delete_btn)
            else:
                completed_label = QtWidgets.QLabel("🔒")
                completed_label.setToolTip("این وظیفه قبلاً تکمیل شده و قابل ویرایش یا حذف نیست")
                completed_label.setStyleSheet("color: #808080; font-size: 12px;")
                btn_layout.addWidget(completed_label)

            btn_layout.addStretch()
            self.tasks_table.setCellWidget(i, 5, btn_widget)

        self.total_tasks_label.setText(f"📋 کل وظایف: {len(tasks)}")
        self.pending_tasks_label.setText(f"⏳ در انتظار: {pending}")
        self.done_tasks_label.setText(f"✅ انجام شده: {done}")

    def add_new_task(self):
        dialog = TaskDialog(self, self.shift_date.date().toString("yyyy-MM-dd"))
        if dialog.exec_():
            result = dialog.get_data()
            self.db.save_daily_task(
                plan_id=0,
                task_date=result['date'],
                task_type=result['task_type'],
                assigned_to=result['assigned_to'],
                shift_time=result['shift_time'],
                notes=result['notes']
            )
            self.load_daily_tasks()
            QtWidgets.QMessageBox.information(self, "موفق", "وظیفه با موفقیت اضافه شد")

    def edit_task(self, task_id):
        task_date = self.shift_date.date().toString("yyyy-MM-dd")
        tasks = self.db.get_daily_tasks_by_date(task_date)
        
        task = None
        for t in tasks:
            if t['id'] == task_id:
                task = t
                break

        if not task:
            QtWidgets.QMessageBox.warning(self, "خطا", "وظیفه یافت نشد")
            return
        
        if hasattr(task['task_date'], 'strftime'):
            task_date_str = task['task_date'].strftime("%Y-%m-%d")
        else:
            task_date_str = str(task['task_date'])
        
        task_for_dialog = task.copy()
        task_for_dialog['task_date'] = task_date_str

        dialog = TaskDialog(self, task_date_str, task_for_dialog)
        if dialog.exec_():
            result = dialog.get_data()
            self.db.delete_task(task_id)
            self.db.save_daily_task(
                plan_id=0,
                task_date=result['date'],
                task_type=result['task_type'],
                assigned_to=result['assigned_to'],
                shift_time=result['shift_time'],
                notes=result['notes']
            )
            self.load_daily_tasks()
            QtWidgets.QMessageBox.information(self, "موفق", "وظیفه با موفقیت ویرایش شد")

    def complete_task(self, task_id):
        self.db.update_task_status(task_id, 'done')
        self.load_daily_tasks()

    def delete_task(self, task_id):
        reply = QtWidgets.QMessageBox.question(self, "تأیید", "آیا از حذف این وظیفه مطمئن هستید؟", QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)
        if reply == QtWidgets.QMessageBox.Yes:
            self.db.delete_task(task_id)
            self.load_daily_tasks()
            QtWidgets.QMessageBox.information(self, "موفق", "وظیفه با موفقیت حذف شد")

    # ==================== تب بودجهبندی سالانه ====================

    def create_budget_tab(self):
        tab = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout(tab)
        layout.setSpacing(15)

        title = QtWidgets.QLabel("📊 بودجهبندی سالانه مزرعه")
        title.setAlignment(QtCore.Qt.AlignCenter)
        title.setStyleSheet("font-size: 16px; font-weight: bold; color: #569CD6; padding: 10px;")
        layout.addWidget(title)

        # انتخاب قفس و سال
        filter_layout = QtWidgets.QHBoxLayout()
        filter_layout.setSpacing(15)

        filter_layout.addWidget(QtWidgets.QLabel("قفس:"))
        self.budget_cage_combo = QtWidgets.QComboBox()
        self.budget_cage_combo.setMinimumWidth(120)
        self.budget_cage_combo.setStyleSheet("background-color: #3C3C3C; color: #C8C8C8; border: 1px solid #3E3E42; border-radius: 4px; padding: 5px;")
        self.budget_cage_combo.currentIndexChanged.connect(self.update_budget_preview)
        filter_layout.addWidget(self.budget_cage_combo)

        filter_layout.addWidget(QtWidgets.QLabel("سال:"))
        self.budget_year_combo = QtWidgets.QComboBox()
        current_miladi_year = date.today().year
        current_shamsi_year = current_miladi_year - 621
        for y in range(current_shamsi_year - 1, current_shamsi_year + 3):
            self.budget_year_combo.addItem(str(y), y)
        self.budget_year_combo.setCurrentIndex(1)
        self.budget_year_combo.currentIndexChanged.connect(self.update_budget_preview)
        self.budget_year_combo.setStyleSheet("background-color: #3C3C3C; color: #C8C8C8; border: 1px solid #3E3E42; border-radius: 4px; padding: 5px;")
        filter_layout.addWidget(self.budget_year_combo)

        filter_layout.addStretch()
        layout.addLayout(filter_layout)

        # کارت‌های خلاصه مالی
        cards_layout = QtWidgets.QHBoxLayout()
        cards_layout.setSpacing(10)

        self.total_revenue_card = self.create_budget_card("💰 درآمد کل", "0 تومان", "#4EC9B0")
        self.total_cost_card = self.create_budget_card("💸 هزینه کل", "0 تومان", "#F48771")
        self.net_profit_card = self.create_budget_card("📈 سود خالص", "0 تومان", "#DCDCAA")
        self.profit_margin_card = self.create_budget_card("🎯 حاشیه سود", "0%", "#569CD6")

        cards_layout.addWidget(self.total_revenue_card)
        cards_layout.addWidget(self.total_cost_card)
        cards_layout.addWidget(self.net_profit_card)
        cards_layout.addWidget(self.profit_margin_card)
        layout.addLayout(cards_layout)

        # جدول بودجه ماهانه
        monthly_label = QtWidgets.QLabel("📅 بودجه ماهانه")
        monthly_label.setStyleSheet("font-size: 14px; font-weight: bold; color: #569CD6; margin-top: 10px;")
        layout.addWidget(monthly_label)

        self.budget_table = QtWidgets.QTableWidget()
        self.budget_table.setColumnCount(5)
        self.budget_table.setHorizontalHeaderLabels(["ماه", "درآمد (تومان)", "هزینه خوراک (تومان)", "سایر هزینه‌ها (تومان)", "سود ماهانه (تومان)"])
        self.budget_table.horizontalHeader().setStretchLastSection(True)
        self.budget_table.setColumnWidth(0, 100)
        self.budget_table.setColumnWidth(1, 200)
        self.budget_table.setColumnWidth(2, 200)
        self.budget_table.setColumnWidth(3, 180)
        self.budget_table.setColumnWidth(4, 200)
        self.budget_table.setStyleSheet("""
            QTableWidget {
                border: 1px solid #2D2D30;
                border-radius: 4px;
                background-color: #2D2D30;
                alternate-background-color: #252526;
            }
            QTableWidget::item:selected {
                background-color: #0E639C;
            }
            QHeaderView::section {
                background-color: #252526;
                color: #569CD6;
                border: none;
                border-bottom: 1px solid #2D2D30;
                padding: 6px;
            }
        """)
        layout.addWidget(self.budget_table)

        # ورودی‌های تنظیمات بودجه
        settings_group = QtWidgets.QGroupBox("⚙️ تنظیمات بودجه (اعداد به تومان)")
        settings_group.setStyleSheet("""
            QGroupBox {
                border: 1px solid #2D2D30;
                border-radius: 5px;
                margin-top: 10px;
                padding-top: 10px;
                color: #C8C8C8;
            }
            QGroupBox::title {
                color: #569CD6;
            }
        """)
        settings_layout = QtWidgets.QHBoxLayout(settings_group)
        settings_layout.setSpacing(15)

        settings_layout.addWidget(QtWidgets.QLabel("قیمت خوراک (هر کیلوگرم):"))
        self.feed_price = QtWidgets.QDoubleSpinBox()
        self.feed_price.setRange(1000, 10000000)
        self.feed_price.setValue(25000)
        self.feed_price.setSuffix(" تومان")
        self.feed_price.setStyleSheet("background-color: #3C3C3C; color: #C8C8C8; border: 1px solid #3E3E42; border-radius: 4px; padding: 5px;")
        self.feed_price.valueChanged.connect(self.update_budget_preview)
        settings_layout.addWidget(self.feed_price)

        settings_layout.addWidget(QtWidgets.QLabel("قیمت فروش (هر کیلوگرم ماهی):"))
        self.fish_price = QtWidgets.QDoubleSpinBox()
        self.fish_price.setRange(10000, 10000000)
        self.fish_price.setValue(120000)
        self.fish_price.setSuffix(" تومان")
        self.fish_price.setStyleSheet("background-color: #3C3C3C; color: #C8C8C8; border: 1px solid #3E3E42; border-radius: 4px; padding: 5px;")
        self.fish_price.valueChanged.connect(self.update_budget_preview)
        settings_layout.addWidget(self.fish_price)

        settings_layout.addWidget(QtWidgets.QLabel("سایر هزینه‌های ماهانه:"))
        self.other_cost = QtWidgets.QDoubleSpinBox()
        self.other_cost.setRange(0, 5000000000)
        self.other_cost.setValue(5000000)
        self.other_cost.setSuffix(" تومان")
        self.other_cost.setStyleSheet("background-color: #3C3C3C; color: #C8C8C8; border: 1px solid #3E3E42; border-radius: 4px; padding: 5px;")
        self.other_cost.valueChanged.connect(self.update_budget_preview)
        settings_layout.addWidget(self.other_cost)

        settings_layout.addStretch()
        layout.addWidget(settings_group)

        return tab

    def create_budget_card(self, title, default_value, color):
        card = QtWidgets.QFrame()
        card.setFixedHeight(85)
        card.setStyleSheet(f"""
            QFrame {{
                background-color: #1E1E1E;
                border: 1px solid #3E3E42;
                border-radius: 8px;
            }}
        """)
        layout = QtWidgets.QVBoxLayout(card)
        layout.setContentsMargins(10, 8, 10, 8)

        title_label = QtWidgets.QLabel(title)
        title_label.setStyleSheet(f"font-size: 11px; color: {color}; font-weight: bold;")
        title_label.setAlignment(QtCore.Qt.AlignCenter)
        layout.addWidget(title_label)

        value_label = QtWidgets.QLabel(default_value)
        value_label.setStyleSheet("font-size: 16px; font-weight: bold; color: #C8C8C8;")
        value_label.setAlignment(QtCore.Qt.AlignCenter)
        layout.addWidget(value_label)

        card.value_label = value_label
        return card

    def update_budget_preview(self):
        try:
            cage_id = self.budget_cage_combo.currentData() if self.budget_cage_combo.count() > 0 else None
            selected_year = self.budget_year_combo.currentData() if self.budget_year_combo.count() > 0 else 1405
            feed_price_kg = self.feed_price.value()
            fish_price_kg = self.fish_price.value()
            other_cost_monthly = self.other_cost.value()

            months_name = ["فروردین", "اردیبهشت", "خرداد", "تیر", "مرداد", "شهریور", 
                           "مهر", "آبان", "آذر", "دی", "بهمن", "اسفند"]
            
            monthly_revenues = [0] * 12
            monthly_feed_costs = [0] * 12
            
            plans = self.db.get_production_plans_by_cage(cage_id) if cage_id else []
            
            for plan in plans:
                try:
                    stocking_date = plan.get('planned_stocking_date')
                    harvest_date = plan.get('planned_harvest_date')
                    total_feed_kg = float(plan.get('estimated_feed_required', 0))
                    
                    if stocking_date and harvest_date and total_feed_kg > 0:
                        if hasattr(stocking_date, 'strftime'):
                            start_str = stocking_date.strftime("%Y-%m-%d")
                        else:
                            start_str = str(stocking_date)
                        
                        if hasattr(harvest_date, 'strftime'):
                            end_str = harvest_date.strftime("%Y-%m-%d")
                        else:
                            end_str = str(harvest_date)
                        
                        start_parts = start_str.split('-')
                        end_parts = end_str.split('-')
                        
                        if len(start_parts) >= 2 and len(end_parts) >= 2:
                            start_month = int(start_parts[1]) - 1
                            end_month = int(end_parts[1]) - 1
                            start_year = int(start_parts[0])
                            end_year = int(end_parts[0])
                            
                            monthly_feeds = self.distribute_feed_over_months(
                                total_feed_kg, start_year, start_month, end_year, end_month
                            )
                            
                            for i in range(12):
                                monthly_feed_costs[i] += monthly_feeds[i] * feed_price_kg
                except:
                    pass
            
            try:
                if cage_id:
                    query = "SELECT harvest_date, total_weight_kg FROM harvests WHERE cage_id = %s"
                    harvests = self.db.fetch_all(query, (cage_id,))
                    
                    for harvest in harvests:
                        harvest_date = harvest.get('harvest_date')
                        total_weight_kg = harvest.get('total_weight_kg', 0)
                        
                        if harvest_date and total_weight_kg > 0:
                            date_parts = str(harvest_date).split('/')
                            if len(date_parts) == 3:
                                year = int(date_parts[0])
                                month = int(date_parts[1]) - 1
                                
                                if year == selected_year:
                                    revenue = total_weight_kg * fish_price_kg
                                    monthly_revenues[month] += revenue
            except:
                pass
            
            total_revenue = sum(monthly_revenues)
            total_feed_cost = sum(monthly_feed_costs)
            total_other_cost = other_cost_monthly * 12
            total_cost = total_feed_cost + total_other_cost
            net_profit = total_revenue - total_cost
            profit_margin = (net_profit / total_revenue * 100) if total_revenue > 0 else 0

            self.total_revenue_card.value_label.setText(f"{total_revenue:,.0f} تومان")
            self.total_cost_card.value_label.setText(f"{total_cost:,.0f} تومان")
            self.net_profit_card.value_label.setText(f"{net_profit:,.0f} تومان")
            self.profit_margin_card.value_label.setText(f"{profit_margin:.1f}%")

            self.budget_table.setRowCount(12)
            for i, month_name in enumerate(months_name):
                revenue = monthly_revenues[i]
                feed_cost = monthly_feed_costs[i]
                profit = revenue - feed_cost - other_cost_monthly
                
                self.budget_table.setItem(i, 0, QtWidgets.QTableWidgetItem(month_name))
                
                revenue_item = QtWidgets.QTableWidgetItem(f"{revenue:,.0f}")
                revenue_item.setForeground(QtGui.QColor("#4EC9B0") if revenue > 0 else QtGui.QColor("#808080"))
                self.budget_table.setItem(i, 1, revenue_item)
                
                feed_item = QtWidgets.QTableWidgetItem(f"{feed_cost:,.0f}")
                feed_item.setForeground(QtGui.QColor("#F48771"))
                self.budget_table.setItem(i, 2, feed_item)
                
                other_item = QtWidgets.QTableWidgetItem(f"{other_cost_monthly:,.0f}")
                other_item.setForeground(QtGui.QColor("#DCDCAA"))
                self.budget_table.setItem(i, 3, other_item)
                
                profit_color = "#4EC9B0" if profit >= 0 else "#F48771"
                profit_item = QtWidgets.QTableWidgetItem(f"{profit:,.0f}")
                profit_item.setForeground(QtGui.QColor(profit_color))
                self.budget_table.setItem(i, 4, profit_item)

        except Exception as e:
            print(f"خطا در بروزرسانی بودجه: {e}")


class TaskDialog(QtWidgets.QDialog):
    def __init__(self, parent=None, default_date="", task=None):
        super().__init__(parent)
        self.setWindowTitle("➕ افزودن وظیفه جدید" if not task else "✏️ ویرایش وظیفه")
        self.setModal(True)
        self.resize(450, 480)
        self.default_date = default_date
        self.task = task
        self.setup_ui()
        if task:
            self.load_task_data()

    def setup_ui(self):
        layout = QtWidgets.QFormLayout(self)
        layout.setSpacing(12)
        layout.setLabelAlignment(QtCore.Qt.AlignRight)

        label_style = "color: #C8C8C8; min-width: 80px;"
        input_style = """
            background-color: #3C3C3C;
            color: #C8C8C8;
            border: 1px solid #2D2D30;
            border-radius: 4px;
            padding: 8px;
            min-height: 32px;
        """

        self.date_edit = QtWidgets.QDateEdit()
        self.date_edit.setCalendarPopup(True)
        if self.default_date:
            if isinstance(self.default_date, str):
                date_parts = self.default_date.split('-')
                self.date_edit.setDate(QtCore.QDate(int(date_parts[0]), int(date_parts[1]), int(date_parts[2])))
            else:
                self.date_edit.setDate(QtCore.QDate.currentDate())
        self.date_edit.setStyleSheet(input_style)
        date_lbl = QtWidgets.QLabel("تاریخ:")
        date_lbl.setStyleSheet(label_style)
        layout.addRow(date_lbl, self.date_edit)

        self.task_type = QtWidgets.QComboBox()
        self.task_type.addItems(["تغذیه", "نمونهبرداری", "بازرسی تور", "ثبت تلفات", "نگهداری", "تعمیرات", "برداشت", "سایر"])
        self.task_type.setStyleSheet(input_style)
        task_lbl = QtWidgets.QLabel("نوع وظیفه:")
        task_lbl.setStyleSheet(label_style)
        layout.addRow(task_lbl, self.task_type)

        self.shift_time = QtWidgets.QComboBox()
        self.shift_time.addItems(["صبح (6-9)", "قبل از ظهر (9-12)", "بعد از ظهر (12-15)", "عصر (15-18)", "شب (18-21)"])
        self.shift_time.setStyleSheet(input_style)
        shift_lbl = QtWidgets.QLabel("زمان:")
        shift_lbl.setStyleSheet(label_style)
        layout.addRow(shift_lbl, self.shift_time)

        self.assigned_to = QtWidgets.QLineEdit()
        self.assigned_to.setPlaceholderText("نام مسئول")
        self.assigned_to.setStyleSheet(input_style)
        assigned_lbl = QtWidgets.QLabel("مسئول:")
        assigned_lbl.setStyleSheet(label_style)
        layout.addRow(assigned_lbl, self.assigned_to)

        self.priority = QtWidgets.QComboBox()
        self.priority.addItems(["عادی", "بالا", "فوری"])
        self.priority.setStyleSheet(input_style)
        priority_lbl = QtWidgets.QLabel("اولویت:")
        priority_lbl.setStyleSheet(label_style)
        layout.addRow(priority_lbl, self.priority)

        self.notes = QtWidgets.QTextEdit()
        self.notes.setMaximumHeight(80)
        self.notes.setPlaceholderText("توضیحات اضافی...")
        self.notes.setStyleSheet(f"{input_style} max-height: 80px;")
        notes_lbl = QtWidgets.QLabel("یادداشت:")
        notes_lbl.setStyleSheet(label_style)
        layout.addRow(notes_lbl, self.notes)

        btn_layout = QtWidgets.QHBoxLayout()
        ok_btn = QtWidgets.QPushButton("ذخیره")
        ok_btn.setMinimumHeight(35)
        ok_btn.setStyleSheet("""
            QPushButton {
                background-color: rgba(86, 156, 214, 80);
                color: white;
                padding: 8px 16px;
                border-radius: 4px;
                border: none;
            }
            QPushButton:hover {
                background-color: rgba(86, 156, 214, 120);
            }
        """)
        ok_btn.clicked.connect(self.accept)
        cancel_btn = QtWidgets.QPushButton("انصراف")
        cancel_btn.setMinimumHeight(35)
        cancel_btn.setStyleSheet("""
            QPushButton {
                background-color: #3C3C3C;
                color: #C8C8C8;
                border: 1px solid #2D2D30;
                border-radius: 4px;
                padding: 8px 16px;
            }
        """)
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(ok_btn)
        btn_layout.addWidget(cancel_btn)
        layout.addRow(btn_layout)

    def load_task_data(self):
        if self.task:
            date_parts = self.task['task_date'].split('-')
            self.date_edit.setDate(QtCore.QDate(int(date_parts[0]), int(date_parts[1]), int(date_parts[2])))

            idx = self.task_type.findText(self.task['task_type'])
            if idx >= 0:
                self.task_type.setCurrentIndex(idx)

            idx = self.shift_time.findText(self.task['shift_time'])
            if idx >= 0:
                self.shift_time.setCurrentIndex(idx)

            self.assigned_to.setText(self.task['assigned_to'])
            self.notes.setText(self.task['notes'])

    def get_data(self):
        return {
            'date': self.date_edit.date().toString("yyyy-MM-dd"),
            'task_type': self.task_type.currentText(),
            'shift_time': self.shift_time.currentText(),
            'assigned_to': self.assigned_to.text(),
            'priority': self.priority.currentText(),
            'notes': self.notes.toPlainText()
        }