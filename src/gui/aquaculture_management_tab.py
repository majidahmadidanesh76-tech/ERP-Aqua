"""
صفحه مدیریت آبزی‌پروری - شامل هچری، نرسری و پرورش در دریا
نسخه دیتابیس - با ذخیره و بارگذاری صحیح داده‌ها
"""

from functools import partial

from PyQt5 import QtWidgets, QtCore
import qtawesome as qta

from .dialogs.feed_dialog import FeedDialog
from .dialogs.mortality_dialog import MortalityDialog
from .dialogs.water_parameter_dialog import WaterParameterDialog
from .dialogs.biomass_dialog import BiomassDialog
from .dialogs.harvest_dialog import HarvestDialog
from .dialogs.cycle_dialog import CycleDialog
from .pyqt_dashboard import PyQtDashboard as GrowthDashboard
from .production_management_tab import ProductionManagementTab
from ..database.db_handler import DatabaseHandler


class AquacultureManagementTab(QtWidgets.QWidget):
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
        self.harvest_records = []
        
        self.setup_ui()
        
        if self.current_farm and self.current_mooring:
            self.load_current_data()
    
    def set_farm_and_mooring(self, farm, mooring):
        self.current_farm = farm
        self.current_mooring = mooring
        self.update_cage_list()
        self.load_current_data()
        if hasattr(self, 'growth_dashboard'):
            self.growth_dashboard.set_farm_and_mooring(farm, mooring)
    
    def load_current_data(self):
        """بارگذاری داده‌های دوره فعال از دیتابیس"""
        if not self.current_farm or not self.current_mooring:
            return
        
        cage_id = self.cage_combo.currentData() if self.cage_combo.count() > 0 else None
        
        if cage_id:
            self.current_cycle = self.db.get_active_cycle(cage_id)
            
            if self.current_cycle:
                self.feeds = self.db.get_feeds_by_cycle(self.current_cycle.id)
                self.mortalities = self.db.get_mortalities_by_cycle(self.current_cycle.id)
                self.biomasses = self.db.get_biomasses_by_cycle(self.current_cycle.id)
                self.harvest_records = self.db.get_harvests_by_cycle(self.current_cycle.id)
                
                self.current_cycle.total_harvested_count = sum(h.harvest_count for h in self.harvest_records)
                self.current_cycle.total_harvested_kg = sum(h.total_weight_kg for h in self.harvest_records)
                self.current_cycle.remaining_count = self.current_cycle.initial_count - self.current_cycle.total_harvested_count
            else:
                self.feeds = []
                self.mortalities = []
                self.biomasses = []
                self.harvest_records = []
        
        self.update_feed_table()
        self.update_mortality_table()
        self.update_water_table()
        self.update_biomass_table()
        self.update_harvest_table()
        self.update_cycle_display()
        self.update_production_management_data()
        
        if hasattr(self, 'growth_dashboard'):
            self.growth_dashboard.set_farm_and_mooring(self.current_farm, self.current_mooring)
    
    # ==================== مدیریت قفس و دوره پرورش ====================
    
    def update_cage_list(self):
        """پر کردن لیست قفس‌ها در کامبوباکس"""
        self.cage_combo.clear()
        if self.current_mooring and hasattr(self.current_mooring, 'cages'):
            for cage in self.current_mooring.cages:
                self.cage_combo.addItem(cage.id, cage.id)
        if self.cage_combo.count() > 0:
            self.cage_combo.setCurrentIndex(0)
            self.load_current_data()
    
    def on_cage_changed(self):
        """تغییر قفس - به‌روزرسانی همه جداول و نمایش‌ها"""
        self.load_current_data()
        if hasattr(self, 'growth_dashboard'):
            self.growth_dashboard.update_all_charts()
    
    def update_cycle_display(self):
        """به‌روزرسانی نمایش اطلاعات دوره فعال"""
        if self.current_cycle:
            text = (f"📋 دوره فعال: {self.current_cycle.start_date} | "
                   f"گونه: {self.current_cycle.species} | "
                   f"تعداد اولیه: {self.current_cycle.initial_count:,} | "
                   f"تعداد باقیمانده: {self.current_cycle.remaining_count:,} | "
                   f"برداشت شده: {self.current_cycle.total_harvested_kg:,.0f} kg")
            self.cycle_info_label.setText(text)
            self.cycle_info_label.setStyleSheet("color: #4EC9B0; font-size: 12px; padding: 5px; background-color: #252526; border-radius: 4px;")
        else:
            self.cycle_info_label.setText("📋 هیچ دوره فعالی برای این قفس وجود ندارد")
            self.cycle_info_label.setStyleSheet("color: #F48771; font-size: 12px; padding: 5px; background-color: #252526; border-radius: 4px;")
    
    def update_production_management_data(self):
        """به‌روزرسانی داده‌های تب مدیریت پرورش"""
        if hasattr(self, 'production_management_tab'):
            self.production_management_tab.set_data(
                self.current_farm,
                self.current_mooring,
                self.cage_combo.currentData() if self.cage_combo.count() > 0 else None,
                self.feeds,
                self.mortalities,
                self.biomasses,
                self.harvest_records,
                self.current_cycle
            )
    
    def start_production_cycle(self):
        """شروع دوره پرورش برای قفس انتخاب شده"""
        if not self.current_farm or not self.current_mooring:
            QtWidgets.QMessageBox.warning(self, "خطا", "لطفاً ابتدا مزرعه و مورینگ را انتخاب کنید")
            return
        
        cage_id = self.cage_combo.currentData() if self.cage_combo.count() > 0 else None
        
        if not cage_id:
            QtWidgets.QMessageBox.warning(self, "خطا", "لطفاً یک قفس را انتخاب کنید")
            return
        
        if self.current_cycle:
            QtWidgets.QMessageBox.warning(self, "خطا", 
                f"این قفس در حال حاضر یک دوره فعال دارد (شروع: {self.current_cycle.start_date})\n"
                f"برای شروع دوره جدید، ابتدا دوره فعلی را با برداشت نهایی کامل کنید.")
            return
        
        dialog = CycleDialog(self, mode="start")
        if dialog.exec_():
            result = dialog.result_data
            cycle_id = self.db.start_production_cycle(
                cage_id,
                result.get("date"),
                result.get("species"),
                result.get("initial_count"),
                result.get("initial_weight"),
                result.get("target_weight"),
                1.5,
                result.get("note")
            )
            if cycle_id:
                self.load_current_data()
                self.update_cycle_display()
                self.update_production_management_data()
                QtWidgets.QMessageBox.information(self, "موفق", f"دوره پرورش با موفقیت شروع شد\nتعداد اولیه: {result.get('initial_count'):,} عدد")
            else:
                QtWidgets.QMessageBox.warning(self, "خطا", "خطا در شروع دوره پرورش")
    
    def add_harvest(self):
        """ثبت برداشت مرحله‌ای"""
        if not self.current_farm or not self.current_mooring:
            QtWidgets.QMessageBox.warning(self, "خطا", "لطفاً ابتدا مزرعه و مورینگ را انتخاب کنید")
            return
        
        if not self.current_cycle:
            QtWidgets.QMessageBox.warning(self, "خطا", "هیچ دوره فعالی برای این قفس وجود ندارد. لطفاً ابتدا دوره پرورش را شروع کنید.")
            return
        
        dialog = HarvestDialog(self, current_farm=self.current_farm, current_mooring=self.current_mooring, cycle=self.current_cycle)
        if dialog.exec_():
            result = dialog.result_data
            
            if self.db.save_harvest(
                self.current_cycle.cage_id,
                self.current_cycle.id,
                result.get("harvest_date"),
                result.get("harvest_count"),
                result.get("average_weight"),
                result.get("total_weight_kg"),
                result.get("customer"),
                result.get("price_per_kg"),
                result.get("total_amount"),
                result.get("is_final"),
                result.get("note")
            ):
                self.load_current_data()
                self.update_harvest_table()
                self.update_cycle_display()
                self.update_production_management_data()
                
                QtWidgets.QMessageBox.information(self, "موفق", 
                    f"برداشت با موفقیت ثبت شد\n"
                    f"تعداد: {result.get('harvest_count'):,} عدد\n"
                    f"کل مبلغ: {result.get('total_amount'):,.0f} تومان")
            else:
                QtWidgets.QMessageBox.warning(self, "خطا", "خطا در ثبت برداشت")
    
    # ==================== عملیات زیست‌توده ====================
    
    def add_biomass(self):
        if not self.current_farm or not self.current_mooring:
            QtWidgets.QMessageBox.warning(self, "خطا", "لطفاً مزرعه و مورینگ را انتخاب کنید")
            return
        
        if not self.current_cycle:
            QtWidgets.QMessageBox.warning(self, "خطا", "هیچ دوره فعالی برای این قفس وجود ندارد. لطفاً ابتدا دوره پرورش را شروع کنید.")
            return
        
        default_initial_count = self.current_cycle.initial_count if self.current_cycle else 0
        
        dialog = BiomassDialog(self, current_farm=self.current_farm, current_mooring=self.current_mooring,
                              harvests=self.harvest_records, default_initial_count=default_initial_count)
        if dialog.exec_():
            if self.db.save_biomass(
                self.current_cycle.cage_id,
                self.current_cycle.id,
                dialog.biomass.date,
                dialog.biomass.estimated_weight,
                dialog.biomass.estimated_count,
                dialog.biomass.sample_size,
                dialog.biomass.note
            ):
                self.load_current_data()
                self.update_biomass_table()
                self.update_production_management_data()
                if hasattr(self, 'growth_dashboard'):
                    self.growth_dashboard.load_data()
                    self.growth_dashboard.update_all_charts()
                QtWidgets.QMessageBox.information(self, "موفق", "زیست‌توده ثبت شد")
            else:
                QtWidgets.QMessageBox.warning(self, "خطا", "خطا در ثبت زیست‌توده")
    
    def edit_biomass(self, index):
        if not self.current_cycle:
            return
        biomass = self.biomasses[index]
        default_initial_count = self.current_cycle.initial_count if self.current_cycle else 0
        
        dialog = BiomassDialog(self, current_farm=self.current_farm, current_mooring=self.current_mooring,
                              biomass=biomass, harvests=self.harvest_records, default_initial_count=default_initial_count)
        if dialog.exec_():
            self.load_current_data()
            self.update_biomass_table()
            self.update_production_management_data()
            if hasattr(self, 'growth_dashboard'):
                self.growth_dashboard.load_data()
                self.growth_dashboard.update_all_charts()
            QtWidgets.QMessageBox.information(self, "موفق", "زیست‌توده ویرایش شد")
    
    def delete_biomass(self, index):
        if QtWidgets.QMessageBox.question(self, "تأیید", "حذف شود؟") == QtWidgets.QMessageBox.Yes:
            self.biomasses.pop(index)
            self.update_biomass_table()
            self.update_production_management_data()
            if hasattr(self, 'growth_dashboard'):
                self.growth_dashboard.load_data()
                self.growth_dashboard.update_all_charts()
    
    def clear_all_biomasses(self):
        if QtWidgets.QMessageBox.question(self, "تأیید", "همه زیست‌توده حذف شوند؟") == QtWidgets.QMessageBox.Yes:
            self.biomasses.clear()
            self.update_biomass_table()
            self.update_production_management_data()
            if hasattr(self, 'growth_dashboard'):
                self.growth_dashboard.load_data()
                self.growth_dashboard.update_all_charts()
    
    def update_biomass_table(self):
        current_cage = self.cage_combo.currentData() if self.cage_combo.count() > 0 else None
        filtered_biomasses = [b for b in self.biomasses if b.cage_id == current_cage] if current_cage else self.biomasses
        
        self.biomass_table.setRowCount(len(filtered_biomasses))
        self.biomass_table.setColumnCount(7)
        self.biomass_table.setHorizontalHeaderLabels(["تاریخ", "قفس", "وزن", "تعداد تخمینی", "تعداد نمونه", "یادداشت", ""])
        self.biomass_table.setColumnWidth(0, 100)
        self.biomass_table.setColumnWidth(1, 100)
        self.biomass_table.setColumnWidth(2, 80)
        self.biomass_table.setColumnWidth(3, 100)
        self.biomass_table.setColumnWidth(4, 100)
        self.biomass_table.setColumnWidth(6, 60)
        self.biomass_table.horizontalHeader().setStretchLastSection(False)
        self.biomass_table.horizontalHeader().setSectionResizeMode(5, QtWidgets.QHeaderView.Stretch)
        
        for i, b in enumerate(filtered_biomasses):
            self.biomass_table.setItem(i, 0, QtWidgets.QTableWidgetItem(b.date))
            self.biomass_table.setItem(i, 1, QtWidgets.QTableWidgetItem(b.cage_id))
            self.biomass_table.setItem(i, 2, QtWidgets.QTableWidgetItem(f"{b.estimated_weight:.1f}"))
            self.biomass_table.setItem(i, 3, QtWidgets.QTableWidgetItem(str(b.estimated_count)))
            self.biomass_table.setItem(i, 4, QtWidgets.QTableWidgetItem(str(b.sample_size)))
            self.biomass_table.setItem(i, 5, QtWidgets.QTableWidgetItem(b.note))
            
            btn_widget = QtWidgets.QWidget()
            btn_layout = QtWidgets.QHBoxLayout(btn_widget)
            btn_layout.setContentsMargins(0, 0, 0, 0)
            btn_layout.setSpacing(2)
            edit_btn = QtWidgets.QToolButton()
            edit_btn.setIcon(qta.icon('fa5s.edit', color='#569CD6'))
            edit_btn.setIconSize(QtCore.QSize(16, 16))
            edit_btn.setFixedSize(24, 24)
            edit_btn.clicked.connect(partial(self.edit_biomass, i))
            delete_btn = QtWidgets.QToolButton()
            delete_btn.setIcon(qta.icon('fa5s.trash-alt', color='#F48771'))
            delete_btn.setIconSize(QtCore.QSize(16, 16))
            delete_btn.setFixedSize(24, 24)
            delete_btn.clicked.connect(partial(self.delete_biomass, i))
            btn_layout.addWidget(edit_btn)
            btn_layout.addWidget(delete_btn)
            btn_layout.addStretch()
            self.biomass_table.setCellWidget(i, 6, btn_widget)
    
    # ==================== عملیات تغذیه ====================
    
    def add_feed(self):
        if not self.current_farm or not self.current_mooring:
            QtWidgets.QMessageBox.warning(self, "خطا", "لطفاً مزرعه و مورینگ را انتخاب کنید")
            return
        
        if not self.current_cycle:
            QtWidgets.QMessageBox.warning(self, "خطا", "هیچ دوره فعالی برای این قفس وجود ندارد. لطفاً ابتدا دوره پرورش را شروع کنید.")
            return
        
        dialog = FeedDialog(self, current_farm=self.current_farm, current_mooring=self.current_mooring)
        if dialog.exec_():
            if self.db.save_feed(
                self.current_cycle.cage_id,
                self.current_cycle.id,
                dialog.feed.date,
                dialog.feed.feed_type,
                dialog.feed.feed_amount,
                dialog.feed.feed_time,
                dialog.feed.note
            ):
                self.load_current_data()
                self.update_feed_table()
                self.update_production_management_data()
                if hasattr(self, 'growth_dashboard'):
                    self.growth_dashboard.load_data()
                    self.growth_dashboard.update_all_charts()
            else:
                QtWidgets.QMessageBox.warning(self, "خطا", "خطا در ثبت تغذیه")
    
    def edit_feed(self, index):
        QtWidgets.QMessageBox.information(self, "اطلاع", "برای ویرایش، ابتدا رکورد را حذف و دوباره ثبت کنید")
    
    def delete_feed(self, index):
        if QtWidgets.QMessageBox.question(self, "تأیید", "حذف شود؟") == QtWidgets.QMessageBox.Yes:
            self.feeds.pop(index)
            self.update_feed_table()
            self.update_production_management_data()
            if hasattr(self, 'growth_dashboard'):
                self.growth_dashboard.load_data()
                self.growth_dashboard.update_all_charts()
    
    def clear_all_feeds(self):
        if QtWidgets.QMessageBox.question(self, "تأیید", "همه تغذیه‌ها حذف شوند؟") == QtWidgets.QMessageBox.Yes:
            self.feeds.clear()
            self.update_feed_table()
            self.update_production_management_data()
            if hasattr(self, 'growth_dashboard'):
                self.growth_dashboard.load_data()
                self.growth_dashboard.update_all_charts()
    
    def update_feed_table(self):
        current_cage = self.cage_combo.currentData() if self.cage_combo.count() > 0 else None
        filtered_feeds = [f for f in self.feeds if f.cage_id == current_cage] if current_cage else self.feeds
        
        self.feed_table.setRowCount(len(filtered_feeds))
        self.feed_table.setColumnCount(7)
        self.feed_table.setHorizontalHeaderLabels(["تاریخ", "قفس", "نوع غذا", "مقدار", "زمان", "یادداشت", ""])
        self.feed_table.setColumnWidth(0, 100)
        self.feed_table.setColumnWidth(1, 100)
        self.feed_table.setColumnWidth(2, 130)
        self.feed_table.setColumnWidth(3, 70)
        self.feed_table.setColumnWidth(4, 100)
        self.feed_table.setColumnWidth(6, 60)
        self.feed_table.horizontalHeader().setStretchLastSection(False)
        self.feed_table.horizontalHeader().setSectionResizeMode(5, QtWidgets.QHeaderView.Stretch)
        
        for i, feed in enumerate(filtered_feeds):
            self.feed_table.setItem(i, 0, QtWidgets.QTableWidgetItem(feed.date))
            self.feed_table.setItem(i, 1, QtWidgets.QTableWidgetItem(feed.cage_id))
            self.feed_table.setItem(i, 2, QtWidgets.QTableWidgetItem(feed.feed_type))
            self.feed_table.setItem(i, 3, QtWidgets.QTableWidgetItem(str(feed.feed_amount)))
            self.feed_table.setItem(i, 4, QtWidgets.QTableWidgetItem(feed.feed_time))
            self.feed_table.setItem(i, 5, QtWidgets.QTableWidgetItem(feed.note))
            
            btn_widget = QtWidgets.QWidget()
            btn_layout = QtWidgets.QHBoxLayout(btn_widget)
            btn_layout.setContentsMargins(0, 0, 0, 0)
            btn_layout.setSpacing(2)
            edit_btn = QtWidgets.QToolButton()
            edit_btn.setIcon(qta.icon('fa5s.edit', color='#569CD6'))
            edit_btn.setIconSize(QtCore.QSize(16, 16))
            edit_btn.setFixedSize(24, 24)
            edit_btn.clicked.connect(partial(self.edit_feed, i))
            delete_btn = QtWidgets.QToolButton()
            delete_btn.setIcon(qta.icon('fa5s.trash-alt', color='#F48771'))
            delete_btn.setIconSize(QtCore.QSize(16, 16))
            delete_btn.setFixedSize(24, 24)
            delete_btn.clicked.connect(partial(self.delete_feed, i))
            btn_layout.addWidget(edit_btn)
            btn_layout.addWidget(delete_btn)
            btn_layout.addStretch()
            self.feed_table.setCellWidget(i, 6, btn_widget)
    
    # ==================== عملیات تلفات ====================
    
    def add_mortality(self):
        if not self.current_farm or not self.current_mooring:
            QtWidgets.QMessageBox.warning(self, "خطا", "لطفاً مزرعه و مورینگ را انتخاب کنید")
            return
        
        if not self.current_cycle:
            QtWidgets.QMessageBox.warning(self, "خطا", "هیچ دوره فعالی برای این قفس وجود ندارد. لطفاً ابتدا دوره پرورش را شروع کنید.")
            return
        
        dialog = MortalityDialog(self, current_farm=self.current_farm, current_mooring=self.current_mooring)
        if dialog.exec_():
            if self.db.save_mortality(
                self.current_cycle.cage_id,
                self.current_cycle.id,
                dialog.mortality.date,
                dialog.mortality.count,
                dialog.mortality.cause,
                dialog.mortality.note
            ):
                self.load_current_data()
                self.update_mortality_table()
                self.update_production_management_data()
                if hasattr(self, 'growth_dashboard'):
                    self.growth_dashboard.load_data()
                    self.growth_dashboard.update_all_charts()
            else:
                QtWidgets.QMessageBox.warning(self, "خطا", "خطا در ثبت تلفات")
    
    def edit_mortality(self, index):
        QtWidgets.QMessageBox.information(self, "اطلاع", "برای ویرایش، ابتدا رکورد را حذف و دوباره ثبت کنید")
    
    def delete_mortality(self, index):
        if QtWidgets.QMessageBox.question(self, "تأیید", "حذف شود؟") == QtWidgets.QMessageBox.Yes:
            self.mortalities.pop(index)
            self.update_mortality_table()
            self.update_production_management_data()
            if hasattr(self, 'growth_dashboard'):
                self.growth_dashboard.load_data()
                self.growth_dashboard.update_all_charts()
    
    def clear_all_mortalities(self):
        if QtWidgets.QMessageBox.question(self, "تأیید", "همه تلفات حذف شوند؟") == QtWidgets.QMessageBox.Yes:
            self.mortalities.clear()
            self.update_mortality_table()
            self.update_production_management_data()
            if hasattr(self, 'growth_dashboard'):
                self.growth_dashboard.load_data()
                self.growth_dashboard.update_all_charts()
    
    def update_mortality_table(self):
        current_cage = self.cage_combo.currentData() if self.cage_combo.count() > 0 else None
        filtered_mortalities = [m for m in self.mortalities if m.cage_id == current_cage] if current_cage else self.mortalities
        
        self.mortality_table.setRowCount(len(filtered_mortalities))
        self.mortality_table.setColumnCount(6)
        self.mortality_table.setHorizontalHeaderLabels(["تاریخ", "قفس", "تعداد", "علت", "یادداشت", ""])
        self.mortality_table.setColumnWidth(0, 100)
        self.mortality_table.setColumnWidth(1, 100)
        self.mortality_table.setColumnWidth(2, 70)
        self.mortality_table.setColumnWidth(3, 130)
        self.mortality_table.setColumnWidth(5, 60)
        self.mortality_table.horizontalHeader().setStretchLastSection(False)
        self.mortality_table.horizontalHeader().setSectionResizeMode(4, QtWidgets.QHeaderView.Stretch)
        
        for i, m in enumerate(filtered_mortalities):
            self.mortality_table.setItem(i, 0, QtWidgets.QTableWidgetItem(m.date))
            self.mortality_table.setItem(i, 1, QtWidgets.QTableWidgetItem(m.cage_id))
            self.mortality_table.setItem(i, 2, QtWidgets.QTableWidgetItem(str(m.count)))
            self.mortality_table.setItem(i, 3, QtWidgets.QTableWidgetItem(m.cause))
            self.mortality_table.setItem(i, 4, QtWidgets.QTableWidgetItem(m.note))
            
            btn_widget = QtWidgets.QWidget()
            btn_layout = QtWidgets.QHBoxLayout(btn_widget)
            btn_layout.setContentsMargins(0, 0, 0, 0)
            btn_layout.setSpacing(2)
            edit_btn = QtWidgets.QToolButton()
            edit_btn.setIcon(qta.icon('fa5s.edit', color='#569CD6'))
            edit_btn.setIconSize(QtCore.QSize(16, 16))
            edit_btn.setFixedSize(24, 24)
            edit_btn.clicked.connect(partial(self.edit_mortality, i))
            delete_btn = QtWidgets.QToolButton()
            delete_btn.setIcon(qta.icon('fa5s.trash-alt', color='#F48771'))
            delete_btn.setIconSize(QtCore.QSize(16, 16))
            delete_btn.setFixedSize(24, 24)
            delete_btn.clicked.connect(partial(self.delete_mortality, i))
            btn_layout.addWidget(edit_btn)
            btn_layout.addWidget(delete_btn)
            btn_layout.addStretch()
            self.mortality_table.setCellWidget(i, 5, btn_widget)
    
    # ==================== عملیات پارامترهای آب ====================
    
    def add_water_parameter(self):
        if not self.current_farm or not self.current_mooring:
            QtWidgets.QMessageBox.warning(self, "خطا", "لطفاً مزرعه و مورینگ را انتخاب کنید")
            return
        
        if not self.current_cycle:
            QtWidgets.QMessageBox.warning(self, "خطا", "هیچ دوره فعالی برای این قفس وجود ندارد. لطفاً ابتدا دوره پرورش را شروع کنید.")
            return
        
        dialog = WaterParameterDialog(self, current_farm=self.current_farm, current_mooring=self.current_mooring)
        if dialog.exec_():
            if self.db.save_water_parameter(
                self.current_cycle.cage_id,
                self.current_cycle.id,
                dialog.parameter.date,
                dialog.parameter.time,
                dialog.parameter.temperature,
                dialog.parameter.dissolved_oxygen,
                dialog.parameter.salinity,
                dialog.parameter.ph,
                dialog.parameter.note
            ):
                self.load_current_data()
                self.update_water_table()
                self.update_production_management_data()
                if hasattr(self, 'growth_dashboard'):
                    self.growth_dashboard.load_data()
                    self.growth_dashboard.update_all_charts()
            else:
                QtWidgets.QMessageBox.warning(self, "خطا", "خطا در ثبت پارامترهای آب")
    
    def edit_water_parameter(self, index):
        QtWidgets.QMessageBox.information(self, "اطلاع", "برای ویرایش، ابتدا رکورد را حذف و دوباره ثبت کنید")
    
    def delete_water_parameter(self, index):
        if QtWidgets.QMessageBox.question(self, "تأیید", "حذف شود؟") == QtWidgets.QMessageBox.Yes:
            self.water_parameters.pop(index)
            self.update_water_table()
            self.update_production_management_data()
            if hasattr(self, 'growth_dashboard'):
                self.growth_dashboard.load_data()
                self.growth_dashboard.update_all_charts()
    
    def clear_all_water_parameters(self):
        if QtWidgets.QMessageBox.question(self, "تأیید", "همه پارامترها حذف شوند؟") == QtWidgets.QMessageBox.Yes:
            self.water_parameters.clear()
            self.update_water_table()
            self.update_production_management_data()
            if hasattr(self, 'growth_dashboard'):
                self.growth_dashboard.load_data()
                self.growth_dashboard.update_all_charts()
    
    def update_water_table(self):
        current_cage = self.cage_combo.currentData() if self.cage_combo.count() > 0 else None
        filtered_water = [w for w in self.water_parameters if w.cage_id == current_cage] if current_cage else self.water_parameters
        
        self.water_table.setRowCount(len(filtered_water))
        self.water_table.setColumnCount(9)
        self.water_table.setHorizontalHeaderLabels(["تاریخ", "قفس", "زمان", "دما", "اکسیژن", "شوری", "pH", "یادداشت", ""])
        self.water_table.setColumnWidth(0, 100)
        self.water_table.setColumnWidth(1, 100)
        self.water_table.setColumnWidth(2, 90)
        self.water_table.setColumnWidth(3, 60)
        self.water_table.setColumnWidth(4, 70)
        self.water_table.setColumnWidth(5, 60)
        self.water_table.setColumnWidth(6, 50)
        self.water_table.setColumnWidth(8, 60)
        self.water_table.horizontalHeader().setStretchLastSection(False)
        self.water_table.horizontalHeader().setSectionResizeMode(7, QtWidgets.QHeaderView.Stretch)
        
        for i, p in enumerate(filtered_water):
            self.water_table.setItem(i, 0, QtWidgets.QTableWidgetItem(p.date))
            self.water_table.setItem(i, 1, QtWidgets.QTableWidgetItem(p.cage_id))
            self.water_table.setItem(i, 2, QtWidgets.QTableWidgetItem(p.time))
            self.water_table.setItem(i, 3, QtWidgets.QTableWidgetItem(f"{p.temperature:.1f}"))
            self.water_table.setItem(i, 4, QtWidgets.QTableWidgetItem(f"{p.dissolved_oxygen:.1f}"))
            self.water_table.setItem(i, 5, QtWidgets.QTableWidgetItem(f"{p.salinity:.1f}"))
            self.water_table.setItem(i, 6, QtWidgets.QTableWidgetItem(f"{p.ph:.1f}"))
            self.water_table.setItem(i, 7, QtWidgets.QTableWidgetItem(p.note))
            
            btn_widget = QtWidgets.QWidget()
            btn_layout = QtWidgets.QHBoxLayout(btn_widget)
            btn_layout.setContentsMargins(0, 0, 0, 0)
            btn_layout.setSpacing(2)
            edit_btn = QtWidgets.QToolButton()
            edit_btn.setIcon(qta.icon('fa5s.edit', color='#569CD6'))
            edit_btn.setIconSize(QtCore.QSize(16, 16))
            edit_btn.setFixedSize(24, 24)
            edit_btn.clicked.connect(partial(self.edit_water_parameter, i))
            delete_btn = QtWidgets.QToolButton()
            delete_btn.setIcon(qta.icon('fa5s.trash-alt', color='#F48771'))
            delete_btn.setIconSize(QtCore.QSize(16, 16))
            delete_btn.setFixedSize(24, 24)
            delete_btn.clicked.connect(partial(self.delete_water_parameter, i))
            btn_layout.addWidget(edit_btn)
            btn_layout.addWidget(delete_btn)
            btn_layout.addStretch()
            self.water_table.setCellWidget(i, 8, btn_widget)
    
    def update_harvest_table(self):
        current_cage = self.cage_combo.currentData() if self.cage_combo.count() > 0 else None
        filtered_harvests = [h for h in self.harvest_records if h.cage_id == current_cage] if current_cage else self.harvest_records
        
        self.harvest_table.setRowCount(len(filtered_harvests))
        for i, h in enumerate(filtered_harvests):
            self.harvest_table.setItem(i, 0, QtWidgets.QTableWidgetItem(h.harvest_date))
            self.harvest_table.setItem(i, 1, QtWidgets.QTableWidgetItem(str(h.harvest_count)))
            self.harvest_table.setItem(i, 2, QtWidgets.QTableWidgetItem(f"{h.average_weight:.0f}"))
            self.harvest_table.setItem(i, 3, QtWidgets.QTableWidgetItem(f"{h.total_weight_kg:,.0f}"))
            self.harvest_table.setItem(i, 4, QtWidgets.QTableWidgetItem(h.customer))
            self.harvest_table.setItem(i, 5, QtWidgets.QTableWidgetItem(f"{h.price_per_kg:,.0f}"))
            self.harvest_table.setItem(i, 6, QtWidgets.QTableWidgetItem(f"{h.total_amount:,.0f}"))
            self.harvest_table.setItem(i, 7, QtWidgets.QTableWidgetItem(h.note))
    
    # ==================== رابط کاربری ====================
    
    def setup_ui(self):
        layout = QtWidgets.QVBoxLayout(self)
        
        self.setStyleSheet("""
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
            QTabBar::tab:hover:!selected {
                background-color: #3E3E42;
            }
            QTableWidget {
                border: 1px solid #3E3E42;
                border-radius: 4px;
                background-color: #2D2D30;
                alternate-background-color: #252526;
                gridline-color: #3E3E42;
            }
            QTableWidget::item:selected {
                background-color: #0E639C;
            }
            QHeaderView::section {
                background-color: #252526;
                color: #569CD6;
                border: none;
                border-bottom: 1px solid #3E3E42;
                padding: 4px;
            }
            QPushButton {
                font-weight: bold;
                border: none;
                border-radius: 4px;
                padding: 6px 12px;
            }
        """)
        
        self.tabs = QtWidgets.QTabWidget()
        self.tabs.setTabPosition(QtWidgets.QTabWidget.North)
        
        self.hatchery_tab = self.create_hatchery_tab()
        self.tabs.addTab(self.hatchery_tab, "🐟 هچری")
        
        self.nursery_tab = self.create_nursery_tab()
        self.tabs.addTab(self.nursery_tab, "🌱 نرسری")
        
        self.growout_tab = self.create_growout_tab()
        self.tabs.addTab(self.growout_tab, "🌊 پرورش در دریا")
        
        layout.addWidget(self.tabs)
    
    def create_hatchery_tab(self):
        tab = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout(tab)
        title = QtWidgets.QLabel("مدیریت هچری (تخم‌گشایی و لارو)")
        title.setStyleSheet("font-size: 14px; font-weight: bold; color: #569CD6; padding: 10px;")
        layout.addWidget(title)
        info = QtWidgets.QLabel("بخش هچری در حال توسعه...")
        info.setAlignment(QtCore.Qt.AlignCenter)
        info.setStyleSheet("color: #C8C8C8; font-size: 12px; padding: 50px;")
        layout.addWidget(info)
        return tab
    
    def create_nursery_tab(self):
        tab = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout(tab)
        title = QtWidgets.QLabel("مدیریت نرسری (رشد اولیه)")
        title.setStyleSheet("font-size: 14px; font-weight: bold; color: #569CD6; padding: 10px;")
        layout.addWidget(title)
        info = QtWidgets.QLabel("بخش نرسری در حال توسعه...")
        info.setAlignment(QtCore.Qt.AlignCenter)
        info.setStyleSheet("color: #C8C8C8; font-size: 12px; padding: 50px;")
        layout.addWidget(info)
        return tab
    
    def create_growout_tab(self):
        tab = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout(tab)
        layout.setSpacing(8)
        
        # نوار ابزار بالایی
        toolbar = QtWidgets.QHBoxLayout()
        toolbar.setSpacing(8)
        
        # انتخاب قفس
        cage_label = QtWidgets.QLabel("قفس:")
        cage_label.setStyleSheet("color: #569CD6; font-weight: bold;")
        toolbar.addWidget(cage_label)
        
        self.cage_combo = QtWidgets.QComboBox()
        self.cage_combo.setMinimumWidth(120)
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
        toolbar.addWidget(self.cage_combo)
        
        toolbar.addSpacing(20)
        
        # دکمه شروع دوره
        self.start_cycle_btn = QtWidgets.QPushButton("🚀 شروع دوره")
        self.start_cycle_btn.setStyleSheet("""
            QPushButton {
                background-color: #0E639C;
                color: white;
                font-weight: bold;
                font-size: 12px;
                border: none;
                border-radius: 4px;
                padding: 6px 12px;
            }
            QPushButton:hover {
                background-color: #1177BB;
            }
        """)
        self.start_cycle_btn.clicked.connect(self.start_production_cycle)
        toolbar.addWidget(self.start_cycle_btn)
        
        # دکمه ثبت برداشت
        self.harvest_btn = QtWidgets.QPushButton("💰 ثبت برداشت")
        self.harvest_btn.setStyleSheet("""
            QPushButton {
                background-color: #2E8B57;
                color: white;
                font-weight: bold;
                font-size: 12px;
                border: none;
                border-radius: 4px;
                padding: 6px 12px;
            }
            QPushButton:hover {
                background-color: #3CB371;
            }
        """)
        self.harvest_btn.clicked.connect(self.add_harvest)
        toolbar.addWidget(self.harvest_btn)
        
        # جداکننده
        separator = QtWidgets.QLabel("  |  ")
        separator.setStyleSheet("color: #3E3E42;")
        toolbar.addWidget(separator)
        
        # زیست‌توده
        self.add_biomass_btn = QtWidgets.QPushButton("📊 زیست‌توده")
        self.add_biomass_btn.setStyleSheet("QPushButton { background-color: #4A4A3A; color: #C8C8C8; border: 1px solid #5A5A4A; border-radius: 4px; padding: 6px 12px; } QPushButton:hover { background-color: #5A5A4A; color: white; }")
        self.add_biomass_btn.clicked.connect(self.add_biomass)
        toolbar.addWidget(self.add_biomass_btn)
        
        # تغذیه
        self.add_feed_btn = QtWidgets.QPushButton("➕ تغذیه")
        self.add_feed_btn.setStyleSheet("QPushButton { background-color: #3A3A4A; color: #C8C8C8; border: 1px solid #4A4A5A; border-radius: 4px; padding: 6px 12px; } QPushButton:hover { background-color: #4A4A5A; color: white; }")
        self.add_feed_btn.clicked.connect(self.add_feed)
        toolbar.addWidget(self.add_feed_btn)
        
        # تلفات
        self.add_mortality_btn = QtWidgets.QPushButton("⚠️ تلفات")
        self.add_mortality_btn.setStyleSheet("QPushButton { background-color: #4A3A3A; color: #C8C8C8; border: 1px solid #5A4A4A; border-radius: 4px; padding: 6px 12px; } QPushButton:hover { background-color: #5A4A4A; color: white; }")
        self.add_mortality_btn.clicked.connect(self.add_mortality)
        toolbar.addWidget(self.add_mortality_btn)
        
        # پارامترهای آب
        self.add_water_btn = QtWidgets.QPushButton("💧 پارامترهای آب")
        self.add_water_btn.setStyleSheet("QPushButton { background-color: #3A4A4A; color: #C8C8C8; border: 1px solid #4A5A5A; border-radius: 4px; padding: 6px 12px; } QPushButton:hover { background-color: #4A5A5A; color: white; }")
        self.add_water_btn.clicked.connect(self.add_water_parameter)
        toolbar.addWidget(self.add_water_btn)
        
        toolbar.addStretch()
        layout.addLayout(toolbar)
        
        # اطلاعات دوره فعال
        self.cycle_info_label = QtWidgets.QLabel("📋 هیچ دوره فعالی برای این قفس وجود ندارد")
        self.cycle_info_label.setStyleSheet("color: #C8C8C8; font-size: 12px; padding: 5px; background-color: #252526; border-radius: 4px;")
        layout.addWidget(self.cycle_info_label)
        
        # تب‌های داخلی
        self.inner_tabs = QtWidgets.QTabWidget()
        self.inner_tabs.setStyleSheet("QTabWidget::pane { border: 1px solid #3E3E42; border-radius: 4px; background: #1E1E1E; } QTabBar::tab { background-color: #2D2D30; color: #C8C8C8; padding: 4px 10px; margin: 1px; border-radius: 3px; } QTabBar::tab:selected { background-color: #0E639C; color: white; }")
        
        # زیست‌توده
        biomass_tab = QtWidgets.QWidget()
        biomass_layout = QtWidgets.QVBoxLayout(biomass_tab)
        biomass_toolbar = QtWidgets.QHBoxLayout()
        biomass_toolbar.addStretch()
        self.clear_biomass_btn = QtWidgets.QPushButton("🗑️ حذف همه زیست‌توده‌ها")
        self.clear_biomass_btn.setStyleSheet("QPushButton { background-color: #5A4A3A; color: #C8C8C8; border: 1px solid #6A5A4A; border-radius: 4px; padding: 4px 10px; }")
        self.clear_biomass_btn.clicked.connect(self.clear_all_biomasses)
        biomass_toolbar.addWidget(self.clear_biomass_btn)
        biomass_layout.addLayout(biomass_toolbar)
        self.biomass_table = QtWidgets.QTableWidget()
        biomass_layout.addWidget(self.biomass_table)
        self.inner_tabs.addTab(biomass_tab, "📊 زیست‌توده")
        
        # تغذیه
        feed_tab = QtWidgets.QWidget()
        feed_layout = QtWidgets.QVBoxLayout(feed_tab)
        feed_toolbar = QtWidgets.QHBoxLayout()
        feed_toolbar.addStretch()
        self.clear_feed_btn = QtWidgets.QPushButton("🗑️ حذف همه تغذیه‌ها")
        self.clear_feed_btn.setStyleSheet("QPushButton { background-color: #5A4A3A; color: #C8C8C8; border: 1px solid #6A5A4A; border-radius: 4px; padding: 4px 10px; }")
        self.clear_feed_btn.clicked.connect(self.clear_all_feeds)
        feed_toolbar.addWidget(self.clear_feed_btn)
        feed_layout.addLayout(feed_toolbar)
        self.feed_table = QtWidgets.QTableWidget()
        feed_layout.addWidget(self.feed_table)
        self.inner_tabs.addTab(feed_tab, "🍽️ تغذیه")
        
        # تلفات
        mortality_tab = QtWidgets.QWidget()
        mortality_layout = QtWidgets.QVBoxLayout(mortality_tab)
        mortality_toolbar = QtWidgets.QHBoxLayout()
        mortality_toolbar.addStretch()
        self.clear_mortality_btn = QtWidgets.QPushButton("🗑️ حذف همه تلفات‌ها")
        self.clear_mortality_btn.setStyleSheet("QPushButton { background-color: #5A4A3A; color: #C8C8C8; border: 1px solid #6A5A4A; border-radius: 4px; padding: 4px 10px; }")
        self.clear_mortality_btn.clicked.connect(self.clear_all_mortalities)
        mortality_toolbar.addWidget(self.clear_mortality_btn)
        mortality_layout.addLayout(mortality_toolbar)
        self.mortality_table = QtWidgets.QTableWidget()
        mortality_layout.addWidget(self.mortality_table)
        self.inner_tabs.addTab(mortality_tab, "⚠️ تلفات")
        
        # پارامترهای آب
        water_tab = QtWidgets.QWidget()
        water_layout = QtWidgets.QVBoxLayout(water_tab)
        water_toolbar = QtWidgets.QHBoxLayout()
        water_toolbar.addStretch()
        self.clear_water_btn = QtWidgets.QPushButton("🗑️ حذف همه پارامترهای آب")
        self.clear_water_btn.setStyleSheet("QPushButton { background-color: #5A4A3A; color: #C8C8C8; border: 1px solid #6A5A4A; border-radius: 4px; padding: 4px 10px; }")
        self.clear_water_btn.clicked.connect(self.clear_all_water_parameters)
        water_toolbar.addWidget(self.clear_water_btn)
        water_layout.addLayout(water_toolbar)
        self.water_table = QtWidgets.QTableWidget()
        water_layout.addWidget(self.water_table)
        self.inner_tabs.addTab(water_tab, "💧 پارامترهای آب")
        
        # برداشت‌ها
        harvest_tab = QtWidgets.QWidget()
        harvest_layout = QtWidgets.QVBoxLayout(harvest_tab)
        self.harvest_table = QtWidgets.QTableWidget()
        self.harvest_table.setColumnCount(8)
        self.harvest_table.setHorizontalHeaderLabels(["تاریخ", "تعداد", "وزن متوسط", "کل وزن(kg)", "مشتری", "قیمت(kg)", "کل مبلغ", "یادداشت"])
        self.harvest_table.horizontalHeader().setStretchLastSection(True)
        harvest_layout.addWidget(self.harvest_table)
        self.inner_tabs.addTab(harvest_tab, "💰 برداشت‌ها")
        
        # مدیریت پرورش
        self.production_management_tab = ProductionManagementTab()
        self.inner_tabs.addTab(self.production_management_tab, "📊 شاخص‌های پرورش")
        
        # داشبورد
        dashboard_tab = QtWidgets.QWidget()
        dashboard_layout = QtWidgets.QVBoxLayout(dashboard_tab)
        self.growth_dashboard = GrowthDashboard(self, self.current_farm, self.current_mooring)
        dashboard_layout.addWidget(self.growth_dashboard)
        self.inner_tabs.addTab(dashboard_tab, "📊 داشبورد تحلیل پرورش")
        
        layout.addWidget(self.inner_tabs)
        
        # پر کردن لیست قفس‌ها
        self.update_cage_list()
        
        return tab