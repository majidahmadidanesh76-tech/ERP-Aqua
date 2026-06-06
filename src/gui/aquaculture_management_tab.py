"""
صفحه مدیریت آبزی پروری - نسخه نهایی با دیتابیس
شامل: هچری، نرسری، پرورش در دریا، جیره‌بندی، بهداشت و درمان
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
from ..widgets.jalali_date_edit import JalaliDateEdit


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
        self.update_production_management_data()

    def load_current_data(self):
        if not self.current_farm or not self.current_mooring:
            return

        cage_id = self.cage_combo.currentData() if self.cage_combo.count() > 0 else None

        if cage_id:
            self.current_cycle = self.db.get_active_cycle(cage_id)

            if self.current_cycle:
                self.feeds = self.db.get_feeds_by_cycle(self.current_cycle.id)
                self.mortalities = self.db.get_mortalities_by_cycle(self.current_cycle.id)
                self.biomasses = self.db.get_biomasses_by_cycle(self.current_cycle.id)
                if hasattr(self.db, 'get_water_parameters_by_cycle'):
                    self.water_parameters = self.db.get_water_parameters_by_cycle(self.current_cycle.id)
                else:
                    self.water_parameters = []
                self.harvest_records = self.db.get_harvests_by_cycle(self.current_cycle.id)

                self.current_cycle.total_harvested_count = sum(h.harvest_count for h in self.harvest_records)
                self.current_cycle.total_harvested_kg = sum(h.total_weight_kg for h in self.harvest_records)
                self.current_cycle.remaining_count = self.current_cycle.initial_count - self.current_cycle.total_harvested_count
            else:
                self.feeds = []
                self.mortalities = []
                self.biomasses = []
                self.water_parameters = []
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

    def update_cage_list(self):
        self.cage_combo.clear()
        if self.current_mooring and hasattr(self.current_mooring, 'cages'):
            for cage in self.current_mooring.cages:
                self.cage_combo.addItem(cage.id, cage.id)
            if self.cage_combo.count() > 0:
                self.cage_combo.setEnabled(True)
                self.cage_combo.setCurrentIndex(0)
                self.load_current_data()
        else:
            self.cage_combo.setEnabled(False)
            self.cage_combo.addItem("--- هیچ قفسی موجود نیست ---")

    def on_cage_changed(self):
        self.load_current_data()
        if hasattr(self, 'growth_dashboard'):
            self.growth_dashboard.set_farm_and_mooring(self.current_farm, self.current_mooring)
        self.update_production_management_data()

    def update_cycle_display(self):
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
        if hasattr(self, 'production_management_tab'):
            cage = self.cage_combo.currentData() if self.cage_combo.count() > 0 else None
            self.production_management_tab.set_data(
                self.current_farm,
                self.current_mooring,
                cage,
                self.feeds,
                self.mortalities,
                self.biomasses,
                self.harvest_records,
                self.current_cycle
            )

    def start_production_cycle(self):
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

    def edit_production_cycle(self):
        QtWidgets.QMessageBox.information(self, "اطلاع", "ویرایش دوره در حال توسعه...")

    # ==================== برداشت ====================

    def add_harvest(self):
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
                QtWidgets.QMessageBox.information(self, "موفق", "برداشت با موفقیت ثبت شد")
            else:
                QtWidgets.QMessageBox.warning(self, "خطا", "خطا در ثبت برداشت")

    def edit_harvest(self, index):
        QtWidgets.QMessageBox.information(self, "اطلاع", "ویرایش برداشت در حال توسعه...")

    def delete_harvest(self, index):
        if QtWidgets.QMessageBox.question(self, "تأیید", "آیا از حذف این برداشت مطمئن هستید؟") == QtWidgets.QMessageBox.Yes:
            if index < len(self.harvest_records):
                to_delete = self.harvest_records[index]
                if hasattr(to_delete, 'id') and to_delete.id:
                    self.db.execute_query("DELETE FROM harvests WHERE id = %s", (to_delete.id,))
                self.load_current_data()

    # ==================== زیست توده ====================

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
            result = self.db.save_biomass(
                self.current_cycle.cage_id,
                self.current_cycle.id,
                dialog.biomass.date,
                dialog.biomass.estimated_weight,
                dialog.biomass.estimated_count,
                dialog.biomass.sample_size,
                dialog.biomass.note
            )
            if result:
                self.load_current_data()
                self.update_biomass_table()
                self.update_production_management_data()
                if hasattr(self, 'growth_dashboard'):
                    self.growth_dashboard.load_data()
                    self.growth_dashboard.update_all_charts()
                QtWidgets.QMessageBox.information(self, "موفق", "زیست توده ثبت شد")
            else:
                QtWidgets.QMessageBox.warning(self, "خطا", "خطا در ثبت زیست توده")

    def edit_biomass(self, index):
        if not self.current_cycle:
            return
        current_cage = self.cage_combo.currentData() if self.cage_combo.count() > 0 else None
        if current_cage:
            filtered = [b for b in self.biomasses if str(b.cage_id) == str(current_cage)]
        else:
            filtered = self.biomasses
        if index >= len(filtered):
            return
        biomass = filtered[index]
        default_initial_count = self.current_cycle.initial_count if self.current_cycle else 0

        dialog = BiomassDialog(self, current_farm=self.current_farm, current_mooring=self.current_mooring,
                              biomass=biomass, harvests=self.harvest_records, default_initial_count=default_initial_count)
        if dialog.exec_():
            old_id = biomass.id if hasattr(biomass, 'id') and biomass.id else None
            if old_id:
                self.db.delete_biomass(old_id)
            result = self.db.save_biomass(
                self.current_cycle.cage_id,
                self.current_cycle.id,
                dialog.biomass.date,
                dialog.biomass.estimated_weight,
                dialog.biomass.estimated_count,
                dialog.biomass.sample_size,
                dialog.biomass.note
            )
            if result:
                self.load_current_data()
                self.update_biomass_table()
                self.update_production_management_data()
                if hasattr(self, 'growth_dashboard'):
                    self.growth_dashboard.load_data()
                    self.growth_dashboard.update_all_charts()
                QtWidgets.QMessageBox.information(self, "موفق", "زیست توده ویرایش شد")
            else:
                QtWidgets.QMessageBox.warning(self, "خطا", "خطا در ویرایش زیست توده")

    def delete_biomass(self, index):
        if not self.current_cycle:
            QtWidgets.QMessageBox.warning(self, "خطا", "هیچ دوره فعالی وجود ندارد")
            return
        
        current_cage = self.cage_combo.currentData() if self.cage_combo.count() > 0 else None
        if current_cage:
            filtered = [b for b in self.biomasses if str(b.cage_id) == str(current_cage)]
        else:
            filtered = self.biomasses
        
        if index >= len(filtered):
            return
        
        to_delete = filtered[index]
        
        reply = QtWidgets.QMessageBox.question(
            self, "تأیید حذف",
            f"آیا از حذف زیست توده تاریخ {to_delete.date} مطمئن هستید؟",
            QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No
        )
        
        if reply == QtWidgets.QMessageBox.Yes:
            if hasattr(to_delete, 'id') and to_delete.id:
                self.db.delete_biomass(to_delete.id)
            
            for i, b in enumerate(self.biomasses):
                if hasattr(b, 'id') and b.id == to_delete.id:
                    self.biomasses.pop(i)
                    break
            
            self.update_biomass_table()
            self.update_production_management_data()
            if hasattr(self, 'growth_dashboard'):
                self.growth_dashboard.load_data()
                self.growth_dashboard.update_all_charts()
            
            QtWidgets.QMessageBox.information(self, "موفق", "زیست توده با موفقیت حذف شد")

    def clear_all_biomasses(self):
        if QtWidgets.QMessageBox.question(self, "تأیید", "آیا از حذف همه زیست تودهها مطمئن هستید؟") == QtWidgets.QMessageBox.Yes:
            self.db.execute_query("DELETE FROM biomasses WHERE cycle_id = %s", (self.current_cycle.id,))
            self.load_current_data()

    def update_biomass_table(self):
        current_cage = self.cage_combo.currentData() if self.cage_combo.count() > 0 else None

        if current_cage:
            filtered_biomasses = [b for b in self.biomasses if str(b.cage_id) == str(current_cage)]
        else:
            filtered_biomasses = self.biomasses

        self.biomass_table.setRowCount(len(filtered_biomasses))
        self.biomass_table.setColumnCount(7)
        self.biomass_table.setHorizontalHeaderLabels(["تاریخ", "قفس", "وزن (گرم)", "تعداد تخمینی", "تعداد نمونه", "یادداشت", "عملیات"])
        self.biomass_table.setColumnWidth(0, 100)
        self.biomass_table.setColumnWidth(1, 80)
        self.biomass_table.setColumnWidth(2, 100)
        self.biomass_table.setColumnWidth(3, 120)
        self.biomass_table.setColumnWidth(4, 100)
        self.biomass_table.setColumnWidth(6, 80)
        self.biomass_table.horizontalHeader().setStretchLastSection(False)
        self.biomass_table.horizontalHeader().setSectionResizeMode(5, QtWidgets.QHeaderView.Stretch)

        for i, b in enumerate(filtered_biomasses):
            self.biomass_table.setItem(i, 0, QtWidgets.QTableWidgetItem(b.date))
            self.biomass_table.setItem(i, 1, QtWidgets.QTableWidgetItem(b.cage_id))
            self.biomass_table.setItem(i, 2, QtWidgets.QTableWidgetItem(f"{b.estimated_weight:.1f}"))
            self.biomass_table.setItem(i, 3, QtWidgets.QTableWidgetItem(f"{b.estimated_count:,}"))
            self.biomass_table.setItem(i, 4, QtWidgets.QTableWidgetItem(str(b.sample_size)))
            self.biomass_table.setItem(i, 5, QtWidgets.QTableWidgetItem(b.note if b.note else ""))

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

    # ==================== تغذیه ====================

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
        QtWidgets.QMessageBox.information(self, "اطلاع", "ویرایش تغذیه در حال توسعه...")

    def delete_feed(self, index):
        if QtWidgets.QMessageBox.question(self, "تأیید", "حذف شود؟") == QtWidgets.QMessageBox.Yes:
            if index < len(self.feeds):
                to_delete = self.feeds[index]
                if hasattr(to_delete, 'id') and to_delete.id:
                    self.db.execute_query("DELETE FROM feeds WHERE id = %s", (to_delete.id,))
                self.load_current_data()

    def clear_all_feeds(self):
        if QtWidgets.QMessageBox.question(self, "تأیید", "همه تغذیهها حذف شوند؟") == QtWidgets.QMessageBox.Yes:
            self.db.execute_query("DELETE FROM feeds WHERE cycle_id = %s", (self.current_cycle.id,))
            self.load_current_data()

    def update_feed_table(self):
        current_cage = self.cage_combo.currentData() if self.cage_combo.count() > 0 else None
        filtered_feeds = [f for f in self.feeds if str(f.cage_id) == str(current_cage)] if current_cage else self.feeds

        self.feed_table.setRowCount(len(filtered_feeds))
        self.feed_table.setColumnCount(7)
        self.feed_table.setHorizontalHeaderLabels(["تاریخ", "قفس", "نوع غذا", "مقدار", "زمان", "یادداشت", "عملیات"])
        self.feed_table.setColumnWidth(0, 100)
        self.feed_table.setColumnWidth(1, 100)
        self.feed_table.setColumnWidth(2, 130)
        self.feed_table.setColumnWidth(3, 70)
        self.feed_table.setColumnWidth(4, 100)
        self.feed_table.setColumnWidth(6, 80)
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

    # ==================== تلفات ====================

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
        QtWidgets.QMessageBox.information(self, "اطلاع", "ویرایش تلفات در حال توسعه...")

    def delete_mortality(self, index):
        if QtWidgets.QMessageBox.question(self, "تأیید", "حذف شود؟") == QtWidgets.QMessageBox.Yes:
            if index < len(self.mortalities):
                to_delete = self.mortalities[index]
                if hasattr(to_delete, 'id') and to_delete.id:
                    self.db.execute_query("DELETE FROM mortalities WHERE id = %s", (to_delete.id,))
                self.load_current_data()

    def clear_all_mortalities(self):
        if QtWidgets.QMessageBox.question(self, "تأیید", "همه تلفات حذف شوند؟") == QtWidgets.QMessageBox.Yes:
            self.db.execute_query("DELETE FROM mortalities WHERE cycle_id = %s", (self.current_cycle.id,))
            self.load_current_data()

    def update_mortality_table(self):
        current_cage = self.cage_combo.currentData() if self.cage_combo.count() > 0 else None
        filtered_mortalities = [m for m in self.mortalities if str(m.cage_id) == str(current_cage)] if current_cage else self.mortalities

        self.mortality_table.setRowCount(len(filtered_mortalities))
        self.mortality_table.setColumnCount(6)
        self.mortality_table.setHorizontalHeaderLabels(["تاریخ", "قفس", "تعداد", "علت", "یادداشت", "عملیات"])
        self.mortality_table.setColumnWidth(0, 100)
        self.mortality_table.setColumnWidth(1, 100)
        self.mortality_table.setColumnWidth(2, 70)
        self.mortality_table.setColumnWidth(3, 130)
        self.mortality_table.setColumnWidth(5, 80)
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

    # ==================== پارامترهای آب ====================

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
        QtWidgets.QMessageBox.information(self, "اطلاع", "ویرایش پارامتر آب در حال توسعه...")

    def delete_water_parameter(self, index):
        if QtWidgets.QMessageBox.question(self, "تأیید", "آیا از حذف این پارامتر آب مطمئن هستید؟") == QtWidgets.QMessageBox.Yes:
            current_cage = self.cage_combo.currentData() if self.cage_combo.count() > 0 else None
            if current_cage:
                filtered = [w for w in self.water_parameters if str(w.cage_id) == str(current_cage)]
                if index < len(filtered):
                    to_delete = filtered[index]
                    if hasattr(to_delete, 'id') and to_delete.id:
                        if hasattr(self.db, 'delete_water_parameter'):
                            self.db.delete_water_parameter(to_delete.id)
                    for i, w in enumerate(self.water_parameters):
                        if w.id == to_delete.id and w.date == to_delete.date:
                            self.water_parameters.pop(i)
                            break

            self.update_water_table()
            self.update_production_management_data()
            if hasattr(self, 'growth_dashboard'):
                self.growth_dashboard.load_data()
                self.growth_dashboard.update_all_charts()

    def clear_all_water_parameters(self):
        if QtWidgets.QMessageBox.question(self, "تأیید", "آیا از حذف همه پارامترهای آب مطمئن هستید؟") == QtWidgets.QMessageBox.Yes:
            self.db.execute_query("DELETE FROM water_parameters WHERE cycle_id = %s", (self.current_cycle.id,))
            self.load_current_data()

    def update_water_table(self):
        current_cage = self.cage_combo.currentData() if self.cage_combo.count() > 0 else None

        if current_cage:
            filtered_water = [w for w in self.water_parameters if str(w.cage_id) == str(current_cage)]
        else:
            filtered_water = self.water_parameters

        self.water_table.setRowCount(len(filtered_water))
        self.water_table.setColumnCount(9)
        self.water_table.setHorizontalHeaderLabels(["تاریخ", "قفس", "زمان", "دما", "اکسیژن", "شوری", "pH", "یادداشت", "عملیات"])
        self.water_table.setColumnWidth(0, 100)
        self.water_table.setColumnWidth(1, 80)
        self.water_table.setColumnWidth(2, 90)
        self.water_table.setColumnWidth(3, 60)
        self.water_table.setColumnWidth(4, 70)
        self.water_table.setColumnWidth(5, 60)
        self.water_table.setColumnWidth(6, 50)
        self.water_table.setColumnWidth(8, 80)
        self.water_table.horizontalHeader().setStretchLastSection(False)
        self.water_table.horizontalHeader().setSectionResizeMode(7, QtWidgets.QHeaderView.Stretch)

        for i, p in enumerate(filtered_water):
            self.water_table.setItem(i, 0, QtWidgets.QTableWidgetItem(p.date))
            self.water_table.setItem(i, 1, QtWidgets.QTableWidgetItem(p.cage_id))
            self.water_table.setItem(i, 2, QtWidgets.QTableWidgetItem(p.time if hasattr(p, 'time') else ""))
            self.water_table.setItem(i, 3, QtWidgets.QTableWidgetItem(f"{p.temperature:.1f}" if hasattr(p, 'temperature') else "0"))
            self.water_table.setItem(i, 4, QtWidgets.QTableWidgetItem(f"{p.dissolved_oxygen:.1f}" if hasattr(p, 'dissolved_oxygen') else "0"))
            self.water_table.setItem(i, 5, QtWidgets.QTableWidgetItem(f"{p.salinity:.1f}" if hasattr(p, 'salinity') else "0"))
            self.water_table.setItem(i, 6, QtWidgets.QTableWidgetItem(f"{p.ph:.1f}" if hasattr(p, 'ph') else "0"))
            self.water_table.setItem(i, 7, QtWidgets.QTableWidgetItem(p.note if hasattr(p, 'note') and p.note else ""))

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
        filtered_harvests = [h for h in self.harvest_records if str(h.cage_id) == str(current_cage)] if current_cage else self.harvest_records

        self.harvest_table.setRowCount(len(filtered_harvests))
        self.harvest_table.setColumnCount(9)
        self.harvest_table.setHorizontalHeaderLabels(["تاریخ", "تعداد", "وزن متوسط", "کل وزن(kg)", "مشتری", "قیمت(kg)", "کل مبلغ", "یادداشت", "عملیات"])
        self.harvest_table.setColumnWidth(0, 100)
        self.harvest_table.setColumnWidth(1, 80)
        self.harvest_table.setColumnWidth(2, 100)
        self.harvest_table.setColumnWidth(3, 100)
        self.harvest_table.setColumnWidth(4, 100)
        self.harvest_table.setColumnWidth(5, 100)
        self.harvest_table.setColumnWidth(6, 120)
        self.harvest_table.setColumnWidth(7, 150)
        self.harvest_table.setColumnWidth(8, 80)

        for i, h in enumerate(filtered_harvests):
            self.harvest_table.setItem(i, 0, QtWidgets.QTableWidgetItem(h.harvest_date))
            self.harvest_table.setItem(i, 1, QtWidgets.QTableWidgetItem(str(h.harvest_count)))
            self.harvest_table.setItem(i, 2, QtWidgets.QTableWidgetItem(f"{h.average_weight:.0f}"))
            self.harvest_table.setItem(i, 3, QtWidgets.QTableWidgetItem(f"{h.total_weight_kg:,.0f}"))
            self.harvest_table.setItem(i, 4, QtWidgets.QTableWidgetItem(h.customer))
            self.harvest_table.setItem(i, 5, QtWidgets.QTableWidgetItem(f"{h.price_per_kg:,.0f}"))
            self.harvest_table.setItem(i, 6, QtWidgets.QTableWidgetItem(f"{h.total_amount:,.0f}"))
            self.harvest_table.setItem(i, 7, QtWidgets.QTableWidgetItem(h.note))

            btn_widget = QtWidgets.QWidget()
            btn_layout = QtWidgets.QHBoxLayout(btn_widget)
            btn_layout.setContentsMargins(0, 0, 0, 0)
            btn_layout.setSpacing(2)
            edit_btn = QtWidgets.QToolButton()
            edit_btn.setIcon(qta.icon('fa5s.edit', color='#569CD6'))
            edit_btn.setIconSize(QtCore.QSize(16, 16))
            edit_btn.setFixedSize(24, 24)
            edit_btn.clicked.connect(partial(self.edit_harvest, i))
            delete_btn = QtWidgets.QToolButton()
            delete_btn.setIcon(qta.icon('fa5s.trash-alt', color='#F48771'))
            delete_btn.setIconSize(QtCore.QSize(16, 16))
            delete_btn.setFixedSize(24, 24)
            delete_btn.clicked.connect(partial(self.delete_harvest, i))
            btn_layout.addWidget(edit_btn)
            btn_layout.addWidget(delete_btn)
            btn_layout.addStretch()
            self.harvest_table.setCellWidget(i, 8, btn_widget)

        self.harvest_table.horizontalHeader().setStretchLastSection(False)
        self.harvest_table.horizontalHeader().setSectionResizeMode(7, QtWidgets.QHeaderView.Stretch)

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

        # ========== تب‌های جدید ==========
        self.diet_tab = self.create_diet_tab()
        self.tabs.addTab(self.diet_tab, "🍽️ جیره‌بندی")

        self.health_tab = self.create_health_tab()
        self.tabs.addTab(self.health_tab, "💊 بهداشت و درمان")

        layout.addWidget(self.tabs)

    def create_hatchery_tab(self):
        tab = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout(tab)
        title = QtWidgets.QLabel("مدیریت هچری (تخمگشایی و لارو)")
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

        toolbar = QtWidgets.QHBoxLayout()
        toolbar.setSpacing(8)

        cage_label = QtWidgets.QLabel("قفس:")
        cage_label.setStyleSheet("color: #569CD6; font-weight: bold;")
        toolbar.addWidget(cage_label)

        self.cage_combo = QtWidgets.QComboBox()
        self.cage_combo.setMinimumWidth(150)
        self.cage_combo.setStyleSheet("""
            QComboBox {
                background-color: #3C3C3C;
                color: #C8C8C8;
                border: 1px solid #3E3E42;
                border-radius: 4px;
                padding: 6px 12px;
            }
            QComboBox:hover {
                border-color: #569CD6;
            }
            QComboBox:disabled {
                background-color: #2D2D30;
                color: #6C6C6C;
            }
        """)
        self.cage_combo.currentIndexChanged.connect(self.on_cage_changed)
        toolbar.addWidget(self.cage_combo)

        toolbar.addSpacing(20)

        self.start_cycle_btn = QtWidgets.QPushButton("🚀 شروع دوره")
        self.start_cycle_btn.setStyleSheet("""
            QPushButton {
                background-color: #2E8B57;
                color: white;
                font-weight: bold;
                font-size: 12px;
                border: none;
                border-radius: 4px;
                padding: 8px 16px;
            }
            QPushButton:hover {
                background-color: #3CB371;
            }
        """)
        self.start_cycle_btn.clicked.connect(self.start_production_cycle)
        toolbar.addWidget(self.start_cycle_btn)

        self.edit_cycle_btn = QtWidgets.QPushButton("✏️ ویرایش دوره")
        self.edit_cycle_btn.setStyleSheet("""
            QPushButton {
                background-color: #D4A574;
                color: #1E1E1E;
                font-weight: bold;
                font-size: 12px;
                border: none;
                border-radius: 4px;
                padding: 8px 16px;
            }
            QPushButton:hover {
                background-color: #E0B080;
            }
        """)
        self.edit_cycle_btn.clicked.connect(self.edit_production_cycle)
        toolbar.addWidget(self.edit_cycle_btn)

        self.harvest_btn = QtWidgets.QPushButton("💰 ثبت برداشت")
        self.harvest_btn.setStyleSheet("""
            QPushButton {
                background-color: #0E639C;
                color: white;
                font-weight: bold;
                font-size: 12px;
                border: none;
                border-radius: 4px;
                padding: 8px 16px;
            }
            QPushButton:hover {
                background-color: #1177BB;
            }
        """)
        self.harvest_btn.clicked.connect(self.add_harvest)
        toolbar.addWidget(self.harvest_btn)

        separator = QtWidgets.QLabel("  |  ")
        separator.setStyleSheet("color: #3E3E42;")
        toolbar.addWidget(separator)

        delete_all_style = """
            QPushButton {
                background-color: #8B2C2C;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 4px 10px;
            }
            QPushButton:hover {
                background-color: #A33C3C;
            }
        """

        self.add_biomass_btn = QtWidgets.QPushButton("📊 زیست توده")
        self.add_biomass_btn.setStyleSheet("""
            QPushButton {
                background-color: #4A4A3A;
                color: #C8C8C8;
                border: 1px solid #5A5A4A;
                border-radius: 4px;
                padding: 6px 12px;
            }
            QPushButton:hover {
                background-color: #5A5A4A;
                color: white;
            }
        """)
        self.add_biomass_btn.clicked.connect(self.add_biomass)
        toolbar.addWidget(self.add_biomass_btn)

        self.add_feed_btn = QtWidgets.QPushButton("➕ تغذیه")
        self.add_feed_btn.setStyleSheet("""
            QPushButton {
                background-color: #3A3A4A;
                color: #C8C8C8;
                border: 1px solid #4A4A5A;
                border-radius: 4px;
                padding: 6px 12px;
            }
            QPushButton:hover {
                background-color: #4A4A5A;
                color: white;
            }
        """)
        self.add_feed_btn.clicked.connect(self.add_feed)
        toolbar.addWidget(self.add_feed_btn)

        self.add_mortality_btn = QtWidgets.QPushButton("⚠️ تلفات")
        self.add_mortality_btn.setStyleSheet("""
            QPushButton {
                background-color: #4A3A3A;
                color: #C8C8C8;
                border: 1px solid #5A4A4A;
                border-radius: 4px;
                padding: 6px 12px;
            }
            QPushButton:hover {
                background-color: #5A4A4A;
                color: white;
            }
        """)
        self.add_mortality_btn.clicked.connect(self.add_mortality)
        toolbar.addWidget(self.add_mortality_btn)

        self.add_water_btn = QtWidgets.QPushButton("💧 پارامترهای آب")
        self.add_water_btn.setStyleSheet("""
            QPushButton {
                background-color: #3A4A4A;
                color: #C8C8C8;
                border: 1px solid #4A5A5A;
                border-radius: 4px;
                padding: 6px 12px;
            }
            QPushButton:hover {
                background-color: #4A5A5A;
                color: white;
            }
        """)
        self.add_water_btn.clicked.connect(self.add_water_parameter)
        toolbar.addWidget(self.add_water_btn)

        toolbar.addStretch()
        layout.addLayout(toolbar)

        self.cycle_info_label = QtWidgets.QLabel("📋 هیچ دوره فعالی برای این قفس وجود ندارد")
        self.cycle_info_label.setStyleSheet("color: #C8C8C8; font-size: 12px; padding: 8px; background-color: #252526; border-radius: 4px;")
        layout.addWidget(self.cycle_info_label)

        self.inner_tabs = QtWidgets.QTabWidget()
        self.inner_tabs.setStyleSheet("""
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

        biomass_tab = QtWidgets.QWidget()
        biomass_layout = QtWidgets.QVBoxLayout(biomass_tab)
        biomass_toolbar = QtWidgets.QHBoxLayout()
        biomass_toolbar.addStretch()
        self.clear_biomass_btn = QtWidgets.QPushButton("🗑️ حذف همه زیست تودهها")
        self.clear_biomass_btn.setStyleSheet(delete_all_style)
        self.clear_biomass_btn.clicked.connect(self.clear_all_biomasses)
        biomass_toolbar.addWidget(self.clear_biomass_btn)
        biomass_layout.addLayout(biomass_toolbar)
        self.biomass_table = QtWidgets.QTableWidget()
        biomass_layout.addWidget(self.biomass_table)
        self.inner_tabs.addTab(biomass_tab, "📊 زیست توده")

        feed_tab = QtWidgets.QWidget()
        feed_layout = QtWidgets.QVBoxLayout(feed_tab)
        feed_toolbar = QtWidgets.QHBoxLayout()
        feed_toolbar.addStretch()
        self.clear_feed_btn = QtWidgets.QPushButton("🗑️ حذف همه تغذیهها")
        self.clear_feed_btn.setStyleSheet(delete_all_style)
        self.clear_feed_btn.clicked.connect(self.clear_all_feeds)
        feed_toolbar.addWidget(self.clear_feed_btn)
        feed_layout.addLayout(feed_toolbar)
        self.feed_table = QtWidgets.QTableWidget()
        feed_layout.addWidget(self.feed_table)
        self.inner_tabs.addTab(feed_tab, "🍽️ تغذیه")

        mortality_tab = QtWidgets.QWidget()
        mortality_layout = QtWidgets.QVBoxLayout(mortality_tab)
        mortality_toolbar = QtWidgets.QHBoxLayout()
        mortality_toolbar.addStretch()
        self.clear_mortality_btn = QtWidgets.QPushButton("🗑️ حذف همه تلفاتها")
        self.clear_mortality_btn.setStyleSheet(delete_all_style)
        self.clear_mortality_btn.clicked.connect(self.clear_all_mortalities)
        mortality_toolbar.addWidget(self.clear_mortality_btn)
        mortality_layout.addLayout(mortality_toolbar)
        self.mortality_table = QtWidgets.QTableWidget()
        mortality_layout.addWidget(self.mortality_table)
        self.inner_tabs.addTab(mortality_tab, "⚠️ تلفات")

        water_tab = QtWidgets.QWidget()
        water_layout = QtWidgets.QVBoxLayout(water_tab)
        water_toolbar = QtWidgets.QHBoxLayout()
        water_toolbar.addStretch()
        self.clear_water_btn = QtWidgets.QPushButton("🗑️ حذف همه پارامترهای آب")
        self.clear_water_btn.setStyleSheet(delete_all_style)
        self.clear_water_btn.clicked.connect(self.clear_all_water_parameters)
        water_toolbar.addWidget(self.clear_water_btn)
        water_layout.addLayout(water_toolbar)
        self.water_table = QtWidgets.QTableWidget()
        water_layout.addWidget(self.water_table)
        self.inner_tabs.addTab(water_tab, "💧 پارامترهای آب")

        harvest_tab = QtWidgets.QWidget()
        harvest_layout = QtWidgets.QVBoxLayout(harvest_tab)
        self.harvest_table = QtWidgets.QTableWidget()
        self.harvest_table.setMinimumHeight(200)
        harvest_layout.addWidget(self.harvest_table)
        self.inner_tabs.addTab(harvest_tab, "💰 برداشتها")

        self.production_management_tab = ProductionManagementTab()
        self.inner_tabs.addTab(self.production_management_tab, "📊 شاخصهای پرورش")

        dashboard_tab = QtWidgets.QWidget()
        dashboard_layout = QtWidgets.QVBoxLayout(dashboard_tab)
        self.growth_dashboard = GrowthDashboard(self, self.current_farm, self.current_mooring)
        dashboard_layout.addWidget(self.growth_dashboard)
        self.inner_tabs.addTab(dashboard_tab, "📊 داشبورد تحلیل پرورش")

        layout.addWidget(self.inner_tabs)

        self.update_cage_list()

        return tab

    # ==================== تب جیره‌بندی ====================

    def create_diet_tab(self):
        """ایجاد تب جیره‌بندی تخصصی"""
        tab = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout(tab)
        layout.setSpacing(10)
        layout.setContentsMargins(10, 10, 10, 10)

        title = QtWidgets.QLabel("🍽️ مدیریت جیره‌بندی تخصصی")
        title.setAlignment(QtCore.Qt.AlignCenter)
        title.setStyleSheet("font-size: 16px; font-weight: bold; color: #569CD6; padding: 10px;")
        layout.addWidget(title)

        # بخش انتخاب قفس و دوره
        group1 = QtWidgets.QGroupBox("انتخاب قفس و دوره پرورش")
        group1.setStyleSheet("""
            QGroupBox {
                border: 1px solid #3E3E42;
                border-radius: 5px;
                margin-top: 10px;
                padding-top: 10px;
                color: #569CD6;
                font-weight: bold;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }
        """)
        group1_layout = QtWidgets.QHBoxLayout(group1)
        group1_layout.setSpacing(15)
        group1_layout.setContentsMargins(15, 15, 15, 10)
        
        group1_layout.addWidget(QtWidgets.QLabel("قفس:"))
        self.diet_cage_combo = QtWidgets.QComboBox()
        self.diet_cage_combo.setMinimumWidth(150)
        self.diet_cage_combo.setStyleSheet("background-color: #3C3C3C; color: #C8C8C8; border: 1px solid #3E3E42; border-radius: 4px; padding: 5px;")
        self.diet_cage_combo.currentIndexChanged.connect(self.on_diet_cage_changed)
        group1_layout.addWidget(self.diet_cage_combo)
        
        group1_layout.addSpacing(20)
        
        group1_layout.addWidget(QtWidgets.QLabel("دوره پرورش:"))
        self.diet_cycle_combo = QtWidgets.QComboBox()
        self.diet_cycle_combo.setMinimumWidth(200)
        self.diet_cycle_combo.setStyleSheet("background-color: #3C3C3C; color: #C8C8C8; border: 1px solid #3E3E42; border-radius: 4px; padding: 5px;")
        self.diet_cycle_combo.currentIndexChanged.connect(self.on_diet_cycle_changed)
        group1_layout.addWidget(self.diet_cycle_combo)
        
        group1_layout.addStretch()
        layout.addWidget(group1)

        # بخش اطلاعات پایه
        group2 = QtWidgets.QGroupBox("اطلاعات پایه دوره پرورش")
        group2.setStyleSheet("""
            QGroupBox {
                border: 1px solid #3E3E42;
                border-radius: 5px;
                margin-top: 10px;
                padding-top: 10px;
                color: #569CD6;
                font-weight: bold;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }
        """)
        group2_layout = QtWidgets.QGridLayout(group2)
        group2_layout.setSpacing(8)
        group2_layout.setContentsMargins(15, 20, 15, 15)
        group2_layout.setColumnStretch(1, 1)
        
        self.species_label = QtWidgets.QLabel("گونه: --")
        self.species_label.setStyleSheet("color: #C8C8C8; background-color: #2D2D30; padding: 5px; border-radius: 4px;")
        
        self.avg_weight_label = QtWidgets.QLabel("وزن میانگین: -- گرم")
        self.avg_weight_label.setStyleSheet("color: #C8C8C8; background-color: #2D2D30; padding: 5px; border-radius: 4px;")
        
        self.temp_label = QtWidgets.QLabel("دمای آب: -- °C")
        self.temp_label.setStyleSheet("color: #C8C8C8; background-color: #2D2D30; padding: 5px; border-radius: 4px;")
        
        self.target_weight_label = QtWidgets.QLabel("وزن هدف: -- گرم")
        self.target_weight_label.setStyleSheet("color: #C8C8C8; background-color: #2D2D30; padding: 5px; border-radius: 4px;")
        
        self.target_fcr_label = QtWidgets.QLabel("FCR هدف: --")
        self.target_fcr_label.setStyleSheet("color: #C8C8C8; background-color: #2D2D30; padding: 5px; border-radius: 4px;")
        
        self.biomass_label = QtWidgets.QLabel("زیست‌توده: -- kg")
        self.biomass_label.setStyleSheet("color: #C8C8C8; background-color: #2D2D30; padding: 5px; border-radius: 4px;")
        
        group2_layout.addWidget(self.species_label, 0, 0)
        group2_layout.addWidget(self.avg_weight_label, 0, 1)
        group2_layout.addWidget(self.temp_label, 1, 0)
        group2_layout.addWidget(self.target_weight_label, 1, 1)
        group2_layout.addWidget(self.target_fcr_label, 2, 0)
        group2_layout.addWidget(self.biomass_label, 2, 1)
        
        layout.addWidget(group2)

        # بخش تنظیمات جیره
        group3 = QtWidgets.QGroupBox("تنظیمات فرمولاسیون جیره")
        group3.setStyleSheet("""
            QGroupBox {
                border: 1px solid #3E3E42;
                border-radius: 5px;
                margin-top: 10px;
                padding-top: 10px;
                color: #569CD6;
                font-weight: bold;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }
        """)
        group3_layout = QtWidgets.QGridLayout(group3)
        group3_layout.setSpacing(10)
        group3_layout.setContentsMargins(15, 20, 15, 15)
        group3_layout.setColumnStretch(1, 1)
        
        group3_layout.addWidget(QtWidgets.QLabel("نرخ خوراک روزانه:"), 0, 0)
        self.feed_rate_spin = QtWidgets.QDoubleSpinBox()
        self.feed_rate_spin.setRange(0.5, 10.0)
        self.feed_rate_spin.setSingleStep(0.1)
        self.feed_rate_spin.setSuffix(" % وزن بدن")
        self.feed_rate_spin.setMinimumWidth(150)
        self.feed_rate_spin.setStyleSheet("background-color: #3C3C3C; color: #C8C8C8; border: 1px solid #3E3E42; border-radius: 4px; padding: 5px;")
        self.feed_rate_spin.valueChanged.connect(self.calculate_daily_feed)
        group3_layout.addWidget(self.feed_rate_spin, 0, 1)
        
        group3_layout.addWidget(QtWidgets.QLabel("نوع خوراک:"), 1, 0)
        self.feed_type_combo = QtWidgets.QComboBox()
        self.feed_type_combo.addItems(["شروع (0-20 گرم)", "رشد (20-100 گرم)", "پایانی (100+ گرم)"])
        self.feed_type_combo.setMinimumWidth(150)
        self.feed_type_combo.setStyleSheet("background-color: #3C3C3C; color: #C8C8C8; border: 1px solid #3E3E42; border-radius: 4px; padding: 5px;")
        group3_layout.addWidget(self.feed_type_combo, 1, 1)
        
        group3_layout.addWidget(QtWidgets.QLabel("تاریخ شروع اعتبار:"), 2, 0)
        self.start_date_edit = JalaliDateEdit()
        self.start_date_edit.setMinimumWidth(150)
        group3_layout.addWidget(self.start_date_edit, 2, 1)
        
        group3_layout.addWidget(QtWidgets.QLabel("تاریخ پایان اعتبار:"), 3, 0)
        self.end_date_edit = JalaliDateEdit()
        self.end_date_edit.setMinimumWidth(150)
        group3_layout.addWidget(self.end_date_edit, 3, 1)
        
        group3_layout.addWidget(QtWidgets.QLabel("خوراک روزانه محاسبه شده:"), 4, 0)
        self.daily_feed_label = QtWidgets.QLabel("0 کیلوگرم")
        self.daily_feed_label.setStyleSheet("color: #4EC9B0; font-weight: bold; font-size: 14px; background-color: #2D2D30; padding: 5px; border-radius: 4px;")
        group3_layout.addWidget(self.daily_feed_label, 4, 1)
        
        group3_layout.addWidget(QtWidgets.QLabel("کل خوراک مورد نیاز:"), 5, 0)
        self.total_feed_label = QtWidgets.QLabel("0 کیلوگرم")
        self.total_feed_label.setStyleSheet("color: #4EC9B0; font-weight: bold; font-size: 14px; background-color: #2D2D30; padding: 5px; border-radius: 4px;")
        group3_layout.addWidget(self.total_feed_label, 5, 1)
        
        group3_layout.addWidget(QtWidgets.QLabel("پیشنهاد FCR:"), 6, 0)
        self.suggested_fcr_label = QtWidgets.QLabel("--")
        self.suggested_fcr_label.setStyleSheet("color: #DCDCAA; font-weight: bold; background-color: #2D2D30; padding: 5px; border-radius: 4px;")
        group3_layout.addWidget(self.suggested_fcr_label, 6, 1)
        
        layout.addWidget(group3)

        # دکمه ذخیره
        save_btn = QtWidgets.QPushButton("💾 ذخیره فرمولاسیون جیره")
        save_btn.setMinimumHeight(45)
        save_btn.setStyleSheet("""
            QPushButton {
                background-color: #0E639C;
                color: white;
                font-weight: bold;
                border-radius: 5px;
                font-size: 13px;
                border: none;
            }
            QPushButton:hover {
                background-color: #1177BB;
            }
        """)
        save_btn.clicked.connect(self.save_diet_formulation)
        layout.addWidget(save_btn)

        # بخش پیشنهادات تغذیه
        group4 = QtWidgets.QGroupBox("پیشنهادات تغذیه روزانه")
        group4.setStyleSheet("""
            QGroupBox {
                border: 1px solid #3E3E42;
                border-radius: 5px;
                margin-top: 10px;
                padding-top: 10px;
                color: #569CD6;
                font-weight: bold;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }
        """)
        group4_layout = QtWidgets.QVBoxLayout(group4)
        group4_layout.setContentsMargins(10, 15, 10, 10)
        
        self.recommendations_table = QtWidgets.QTableWidget()
        self.recommendations_table.setColumnCount(5)
        self.recommendations_table.setHorizontalHeaderLabels(["تاریخ", "مقدار (کیلوگرم)", "زمان", "وضعیت", "عملیات"])
        self.recommendations_table.horizontalHeader().setStretchLastSection(True)
        self.recommendations_table.setColumnWidth(0, 100)
        self.recommendations_table.setColumnWidth(1, 120)
        self.recommendations_table.setColumnWidth(2, 100)
        self.recommendations_table.setColumnWidth(3, 100)
        self.recommendations_table.setMinimumHeight(150)
        self.recommendations_table.setStyleSheet("""
            QTableWidget {
                border: 1px solid #3E3E42;
                border-radius: 4px;
                background-color: #2D2D30;
                alternate-background-color: #252526;
                gridline-color: #3E3E42;
            }
            QTableWidget::item:selected {
                background-color: #3A3A3A;
            }
            QHeaderView::section {
                background-color: #252526;
                color: #C8C8C8;
                border: none;
                border-bottom: 1px solid #3E3E42;
                padding: 6px;
                font-weight: bold;
            }
        """)
        group4_layout.addWidget(self.recommendations_table)
        layout.addWidget(group4)

        self.load_diet_cages()
        return tab

    def create_health_tab(self):
        """ایجاد تب بهداشت و درمان"""
        tab = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout(tab)
        
        title = QtWidgets.QLabel("💊 مدیریت بهداشت و درمان")
        title.setAlignment(QtCore.Qt.AlignCenter)
        title.setStyleSheet("font-size: 14px; font-weight: bold; color: #569CD6; padding: 10px;")
        layout.addWidget(title)
        
        info = QtWidgets.QLabel(
            "بخش بهداشت و درمان در حال توسعه...\n\n"
            "قابلیت‌های آینده:\n"
            "• ثبت نسخه دامپزشک\n"
            "• مدیریت داروها و مکمل‌ها\n"
            "• برنامه درمانی روزانه"
        )
        info.setAlignment(QtCore.Qt.AlignCenter)
        info.setWordWrap(True)
        info.setStyleSheet("color: #C8C8C8; font-size: 12px; padding: 50px;")
        layout.addWidget(info)
        
        return tab

    # ==================== توابع جیره‌بندی ====================

    def load_diet_cages(self):
        """بارگذاری قفس‌ها در کامبوباکس جیره‌بندی"""
        self.diet_cage_combo.clear()
        self.diet_cage_combo.addItem("--- انتخاب قفس ---", None)
        
        if self.current_mooring and hasattr(self.current_mooring, 'cages'):
            for cage in self.current_mooring.cages:
                self.diet_cage_combo.addItem(f"{cage.id}", cage.id)
            if self.diet_cage_combo.count() > 1:
                self.diet_cage_combo.setCurrentIndex(1)

    def on_diet_cage_changed(self):
        """تغییر قفس در تب جیره‌بندی"""
        self.load_diet_cycles()

    def load_diet_cycles(self):
        """بارگذاری دوره‌های پرورش برای قفس انتخاب شده"""
        self.diet_cycle_combo.clear()
        self.diet_cycle_combo.addItem("--- انتخاب دوره پرورش ---", None)
        
        cage_id = self.diet_cage_combo.currentData()
        if cage_id:
            cycles = self.db.fetch_all("""
                SELECT cycle_id as id, start_date, species 
                FROM production_cycles 
                WHERE cage_id = %s AND is_active = 1
                ORDER BY start_date DESC
            """, (cage_id,))
            for cycle in cycles:
                species_text = cycle['species'] if cycle['species'] else 'نامشخص'
                self.diet_cycle_combo.addItem(f"{species_text} - {cycle['start_date']}", cycle['id'])
            if self.diet_cycle_combo.count() > 1:
                self.diet_cycle_combo.setCurrentIndex(1)

    def on_diet_cycle_changed(self):
        """تغییر دوره پرورش در تب جیره‌بندی"""
        cycle_id = self.diet_cycle_combo.currentData()
        if not cycle_id:
            self.species_label.setText("گونه: --")
            self.avg_weight_label.setText("وزن میانگین: -- گرم")
            self.temp_label.setText("دمای آب: -- °C")
            self.target_weight_label.setText("وزن هدف: -- گرم")
            self.target_fcr_label.setText("FCR هدف: --")
            self.biomass_label.setText("زیست‌توده: -- kg")
            self.feed_rate_spin.setValue(2.5)
            self.daily_feed_label.setText("0 کیلوگرم")
            self.total_feed_label.setText("0 کیلوگرم")
            return
        
        cycle = self.db.fetch_one("SELECT * FROM production_cycles WHERE cycle_id = %s", (cycle_id,))
        if cycle:
            species_name = cycle['species'] if cycle['species'] else 'نامشخص'
            self.species_label.setText(f"گونه: {species_name}")
            self.target_weight_label.setText(f"وزن هدف: {cycle['target_weight'] or 0:.0f} گرم")
            self.target_fcr_label.setText(f"FCR هدف: {cycle.get('target_fcr', 1.5)}")
            
            last_biomass = self.db.fetch_one("""
                SELECT estimated_weight, estimated_count 
                FROM biomasses 
                WHERE cycle_id = %s 
                ORDER BY date DESC LIMIT 1
            """, (cycle_id,))
            
            if last_biomass:
                avg_weight = last_biomass['estimated_weight']
                count = last_biomass['estimated_count']
                biomass_kg = (avg_weight * count) / 1000
                self.avg_weight_label.setText(f"وزن میانگین: {avg_weight:.0f} گرم")
                self.biomass_label.setText(f"زیست‌توده: {biomass_kg:.0f} kg")
                
                last_temp = self.db.fetch_one("""
                    SELECT temperature 
                    FROM water_parameters 
                    WHERE cage_id = %s 
                    ORDER BY date DESC LIMIT 1
                """, (cycle['cage_id'],))
                if last_temp:
                    temp = last_temp['temperature']
                    self.temp_label.setText(f"دمای آب: {temp:.1f} °C")
                    suggested_rate = self.db.calculate_feed_rate(species_name, avg_weight, temp)
                    self.feed_rate_spin.setValue(suggested_rate)
                    
                    suggested_feed_type = self.db.get_feed_type_by_weight(avg_weight)
                    idx = self.feed_type_combo.findText(suggested_feed_type)
                    if idx >= 0:
                        self.feed_type_combo.setCurrentIndex(idx)
            
            import jdatetime
            from datetime import timedelta
            today = jdatetime.date.today()
            self.start_date_edit.set_jalali_date(f"{today.year}/{today.month:02d}/{today.day:02d}")
            end_date = jdatetime.date(today.year, today.month, today.day) + timedelta(days=7)
            end_date_str = "{}/{}/{}".format(end_date.year, end_date.month, end_date.day)
            self.end_date_edit.set_jalali_date(end_date_str)
            
            self.calculate_daily_feed()

    def calculate_daily_feed(self):
        """محاسبه خوراک روزانه بر اساس نرخ و زیست‌توده"""
        feed_rate = self.feed_rate_spin.value()
        biomass_text = self.biomass_label.text()
        import re
        numbers = re.findall(r'\d+', biomass_text)
        biomass_kg = float(numbers[0]) if numbers else 0
        daily_feed_kg = (biomass_kg * feed_rate) / 100
        self.daily_feed_label.setText(f"{daily_feed_kg:.1f} کیلوگرم")
        
        start_date = self.start_date_edit.get_jalali_date()
        end_date = self.end_date_edit.get_jalali_date()
        if start_date and end_date:
            from datetime import datetime
            start_parts = start_date.split('/')
            end_parts = end_date.split('/')
            start = datetime(int(start_parts[0]), int(start_parts[1]), int(start_parts[2]))
            end = datetime(int(end_parts[0]), int(end_parts[1]), int(end_parts[2]))
            days = (end - start).days + 1
            if days > 0:
                total_feed = daily_feed_kg * days
                self.total_feed_label.setText(f"{total_feed:.0f} کیلوگرم")

    def save_diet_formulation(self):
        """ذخیره فرمولاسیون جیره و تولید پیشنهادات"""
        cycle_id = self.diet_cycle_combo.currentData()
        cage_id = self.diet_cage_combo.currentData()
        
        if not cycle_id or not cage_id:
            QtWidgets.QMessageBox.warning(self, "خطا", "لطفاً قفس و دوره پرورش را انتخاب کنید")
            return
        
        feed_rate = self.feed_rate_spin.value()
        feed_type = self.feed_type_combo.currentText()
        start_date = self.start_date_edit.get_jalali_date()
        end_date = self.end_date_edit.get_jalali_date()
        
        cycle = self.db.fetch_one("SELECT * FROM production_cycles WHERE cycle_id = %s", (cycle_id,))
        last_biomass = self.db.fetch_one("""
            SELECT estimated_weight, estimated_count 
            FROM biomasses 
            WHERE cycle_id = %s 
            ORDER BY date DESC LIMIT 1
        """, (cycle_id,))
        
        if not last_biomass:
            QtWidgets.QMessageBox.warning(self, "خطا", "اطلاعات زیست‌توده یافت نشد")
            return
        
        avg_weight = last_biomass['estimated_weight']
        count = last_biomass['estimated_count']
        biomass_kg = (avg_weight * count) / 1000
        daily_feed_kg = (biomass_kg * feed_rate) / 100
        
        formulation_id = self.db.save_diet_formulation(
            cycle_id, cage_id, start_date, cycle['species'],
            avg_weight, 0, feed_rate, daily_feed_kg, feed_type,
            cycle.get('target_fcr', 1.5), 1, "ایجاد شده از طریق نرم‌افزار"
        )
        
        if not formulation_id:
            QtWidgets.QMessageBox.warning(self, "خطا", "خطا در ذخیره فرمولاسیون")
            return
        
        from datetime import datetime, timedelta
        start_parts = start_date.split('/')
        end_parts = end_date.split('/')
        current = datetime(int(start_parts[0]), int(start_parts[1]), int(start_parts[2]))
        end = datetime(int(end_parts[0]), int(end_parts[1]), int(end_parts[2]))
        
        while current <= end:
            rec_date = "{}/{}/{}".format(current.year, current.month, current.day)
            self.db.add_feeding_recommendation(formulation_id, rec_date, daily_feed_kg, "صبح (6-8)")
            current += timedelta(days=1)
        
        self.load_feeding_recommendations(formulation_id)
        QtWidgets.QMessageBox.information(self, "موفق", "فرمولاسیون جیره با موفقیت ذخیره شد")

    def load_feeding_recommendations(self, formulation_id):
        """بارگذاری پیشنهادات تغذیه برای نمایش در جدول"""
        recommendations = self.db.get_feeding_recommendations_by_formulation(formulation_id)
        self.recommendations_table.setRowCount(len(recommendations))
        
        for i, rec in enumerate(recommendations):
            self.recommendations_table.setItem(i, 0, QtWidgets.QTableWidgetItem(rec['recommendation_date']))
            self.recommendations_table.setItem(i, 1, QtWidgets.QTableWidgetItem(f"{rec['recommended_feed_kg']:.1f}"))
            self.recommendations_table.setItem(i, 2, QtWidgets.QTableWidgetItem(rec['recommended_feed_time']))
            
            status_text = { 'pending': '⏳ در انتظار', 'applied': '✅ اعمال شده', 'ignored': '❌ رد شده' }.get(rec['status'], '⏳ در انتظار')
            self.recommendations_table.setItem(i, 3, QtWidgets.QTableWidgetItem(status_text))
            
            if rec['status'] == 'pending':
                accept_btn = QtWidgets.QPushButton("✓ قبول")
                accept_btn.setFixedSize(60, 25)
                accept_btn.setStyleSheet("background-color: #2E8B57; color: white; border-radius: 3px;")
                accept_btn.clicked.connect(lambda checked, rid=rec['id']: self.apply_single_recommendation(rid))
                self.recommendations_table.setCellWidget(i, 4, accept_btn)
            else:
                self.recommendations_table.setItem(i, 4, QtWidgets.QTableWidgetItem("-"))

    def apply_single_recommendation(self, recommendation_id):
        """اعمال یک پیشنهاد به برنامه پرورش"""
        if not self.current_plan_id:
            QtWidgets.QMessageBox.warning(self, "خطا", "لطفاً ابتدا یک برنامه پرورش انتخاب کنید")
            return
        
        rec = self.db.fetch_one("SELECT * FROM feeding_recommendations WHERE id = %s", (recommendation_id,))
        if rec:
            self.db.add_plan_task(
                self.current_plan_id, None,
                f"تغذیه روزانه - {rec['recommended_feed_kg']} kg",
                f"پیشنهاد تغذیه خودکار",
                'feeding',
                rec['recommended_date'],
                '08:00:00',
                60,
                None,
                'واحد تغذیه',
                2
            )
            self.db.update_feeding_recommendation_status(recommendation_id, 'applied')
            self.load_feeding_recommendations(rec['diet_formulation_id'])
            QtWidgets.QMessageBox.information(self, "موفق", "پیشنهاد تغذیه به برنامه پرورش اضافه شد")