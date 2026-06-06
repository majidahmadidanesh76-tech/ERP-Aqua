"""
صفحه مدیریت آبزی پروری - نسخه نهایی با رفع کامل مشکل جیره‌بندی
"""

from functools import partial
import re
import jdatetime
from datetime import timedelta

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
from ..utils import DateUtils
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
        self.load_diet_cages()

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
        """ایجاد تب جیره‌بندی تخصصی با تمام اصلاحات"""
        tab = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout(tab)
        layout.setSpacing(8)
        layout.setContentsMargins(8, 8, 8, 8)

        title = QtWidgets.QLabel("🍽️ مدیریت جیره‌بندی تخصصی")
        title.setAlignment(QtCore.Qt.AlignCenter)
        title.setStyleSheet("font-size: 14px; font-weight: bold; color: #569CD6; padding: 5px;")
        layout.addWidget(title)

        # ========== گروه 1: انتخاب قفس و دوره ==========
        group1 = QtWidgets.QGroupBox("انتخاب قفس و دوره پرورش")
        group1.setStyleSheet("""
            QGroupBox {
                border: 1px solid #3E3E42;
                border-radius: 5px;
                margin-top: 8px;
                padding-top: 8px;
                color: #4EC9B0;
                font-weight: bold;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
                color: #4EC9B0;
            }
        """)
        group1_layout = QtWidgets.QHBoxLayout(group1)
        group1_layout.setSpacing(12)
        group1_layout.setContentsMargins(12, 12, 12, 8)

        lbl_cage = QtWidgets.QLabel("قفس:")
        lbl_cage.setStyleSheet("color: #4EC9B0; font-weight: bold;")
        group1_layout.addWidget(lbl_cage)

        self.diet_cage_combo = QtWidgets.QComboBox()
        self.diet_cage_combo.setMinimumWidth(150)
        self.diet_cage_combo.setMinimumHeight(28)
        self.diet_cage_combo.setStyleSheet("""
            QComboBox {
                background-color: #3C3C3C;
                color: #C8C8C8;
                border: 1px solid #3E3E42;
                border-radius: 4px;
                padding: 4px;
            }
            QComboBox::drop-down {
                border: none;
            }
            QComboBox QAbstractItemView {
                background-color: #3C3C3C;
                color: #C8C8C8;
                selection-background-color: #0E639C;
            }
        """)
        self.diet_cage_combo.currentIndexChanged.connect(self.on_diet_cage_changed)
        group1_layout.addWidget(self.diet_cage_combo)

        group1_layout.addSpacing(15)

        lbl_cycle = QtWidgets.QLabel("دوره پرورش:")
        lbl_cycle.setStyleSheet("color: #4EC9B0; font-weight: bold;")
        group1_layout.addWidget(lbl_cycle)

        self.diet_cycle_combo = QtWidgets.QComboBox()
        self.diet_cycle_combo.setMinimumWidth(200)
        self.diet_cycle_combo.setMinimumHeight(28)
        self.diet_cycle_combo.setStyleSheet("""
            QComboBox {
                background-color: #3C3C3C;
                color: #C8C8C8;
                border: 1px solid #3E3E42;
                border-radius: 4px;
                padding: 4px;
            }
            QComboBox::drop-down {
                border: none;
            }
            QComboBox QAbstractItemView {
                background-color: #3C3C3C;
                color: #C8C8C8;
                selection-background-color: #0E639C;
            }
        """)
        self.diet_cycle_combo.currentIndexChanged.connect(self.on_diet_cycle_changed)
        group1_layout.addWidget(self.diet_cycle_combo)

        group1_layout.addStretch()
        layout.addWidget(group1)

        # ========== ردیف اصلی: دو گروه کنار هم ==========
        main_row_layout = QtWidgets.QHBoxLayout()
        main_row_layout.setSpacing(12)

        # ========== گروه 2: اطلاعات پایه ==========
        group2 = QtWidgets.QGroupBox("اطلاعات پایه دوره پرورش")
        group2.setStyleSheet("""
            QGroupBox {
                border: 1px solid #3E3E42;
                border-radius: 5px;
                margin-top: 8px;
                padding-top: 8px;
                color: #4EC9B0;
                font-weight: bold;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
                color: #4EC9B0;
            }
        """)
        
        group2_layout = QtWidgets.QFormLayout(group2)
        group2_layout.setSpacing(8)
        group2_layout.setContentsMargins(12, 15, 12, 12)
        group2_layout.setLabelAlignment(QtCore.Qt.AlignRight)

        label_style = "color: #4EC9B0; font-weight: bold; min-height: 28px;"
        value_style = "min-height: 28px; max-height: 28px; padding: 4px 8px; background-color: #2D2D30; border: 1px solid #3E3E42; border-radius: 4px; color: #C8C8C8; text-align: right;"

        # لیبل‌های عنوان
        lbl_species = QtWidgets.QLabel("گونه:")
        lbl_species.setStyleSheet(label_style)
        lbl_avg_weight = QtWidgets.QLabel("وزن میانگین:")
        lbl_avg_weight.setStyleSheet(label_style)
        lbl_temp = QtWidgets.QLabel("دمای آب:")
        lbl_temp.setStyleSheet(label_style)
        lbl_target = QtWidgets.QLabel("وزن هدف:")
        lbl_target.setStyleSheet(label_style)
        lbl_fcr = QtWidgets.QLabel("FCR هدف:")
        lbl_fcr.setStyleSheet(label_style)
        lbl_biomass = QtWidgets.QLabel("زیستتوده:")
        lbl_biomass.setStyleSheet(label_style)

        # باکس‌های مقادیر (همگی راست‌چین)
        self.species_label = QtWidgets.QLabel("--")
        self.species_label.setAlignment(QtCore.Qt.AlignRight)
        self.species_label.setStyleSheet(value_style)
        
        self.avg_weight_label = QtWidgets.QLabel("-- گرم")
        self.avg_weight_label.setAlignment(QtCore.Qt.AlignRight)
        self.avg_weight_label.setStyleSheet(value_style)
        
        self.temp_label = QtWidgets.QLabel("-- °C")
        self.temp_label.setAlignment(QtCore.Qt.AlignRight)
        self.temp_label.setStyleSheet(value_style)
        
        self.target_weight_label = QtWidgets.QLabel("-- گرم")
        self.target_weight_label.setAlignment(QtCore.Qt.AlignRight)
        self.target_weight_label.setStyleSheet(value_style)
        
        self.target_fcr_label = QtWidgets.QLabel("--")
        self.target_fcr_label.setAlignment(QtCore.Qt.AlignRight)
        self.target_fcr_label.setStyleSheet(value_style)
        
        self.biomass_label = QtWidgets.QLabel("-- kg")
        self.biomass_label.setAlignment(QtCore.Qt.AlignRight)
        self.biomass_label.setStyleSheet(value_style)

        group2_layout.addRow(lbl_species, self.species_label)
        group2_layout.addRow(lbl_avg_weight, self.avg_weight_label)
        group2_layout.addRow(lbl_temp, self.temp_label)
        group2_layout.addRow(lbl_target, self.target_weight_label)
        group2_layout.addRow(lbl_fcr, self.target_fcr_label)
        group2_layout.addRow(lbl_biomass, self.biomass_label)

        main_row_layout.addWidget(group2, 1)

        # ========== گروه 3: تنظیمات فرمولاسیون ==========
        group3 = QtWidgets.QGroupBox("تنظیمات فرمولاسیون جیره")
        group3.setStyleSheet("""
            QGroupBox {
                border: 1px solid #3E3E42;
                border-radius: 5px;
                margin-top: 8px;
                padding-top: 8px;
                color: #4EC9B0;
                font-weight: bold;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
                color: #4EC9B0;
            }
        """)
        
        group3_layout = QtWidgets.QFormLayout(group3)
        group3_layout.setSpacing(8)
        group3_layout.setContentsMargins(12, 15, 12, 12)
        group3_layout.setLabelAlignment(QtCore.Qt.AlignRight)

        input_label_style = "color: #4EC9B0; font-weight: bold; min-height: 28px;"
        input_style = "min-height: 28px; max-height: 28px;"
        calc_style = "min-height: 28px; max-height: 28px; padding: 4px 8px; background-color: #1E3A2F; border: 1px solid #3E3E42; border-radius: 4px; color: #4EC9B0; font-weight: bold; text-align: right;"

        lbl_rate = QtWidgets.QLabel("نرخ خوراک روزانه:")
        lbl_rate.setStyleSheet(input_label_style)
        lbl_type = QtWidgets.QLabel("نوع خوراک:")
        lbl_type.setStyleSheet(input_label_style)
        lbl_start = QtWidgets.QLabel("تاریخ شروع اعتبار:")
        lbl_start.setStyleSheet(input_label_style)
        lbl_end = QtWidgets.QLabel("تاریخ پایان اعتبار:")
        lbl_end.setStyleSheet(input_label_style)
       
        # زمان پیشنهادی تغذیه
        lbl_time = QtWidgets.QLabel("زمان پیشنهادی تغذیه:")
        lbl_time.setStyleSheet(input_label_style)
        self.feed_time_combo = QtWidgets.QComboBox()
        self.feed_time_combo.setMinimumHeight(28)
        self.feed_time_combo.setStyleSheet("""
            QComboBox {
                background-color: #3C3C3C;
                color: #C8C8C8;
                border: 1px solid #3E3E42;
                border-radius: 4px;
                padding: 4px;
                min-height: 28px;
            }
        """)
        self.feed_time_combo.addItems([
            "06:00 - صبح زود",
            "08:00 - صبح",
            "10:00 - اواسط صبح",
            "12:00 - ظهر",
            "14:00 - بعدازظهر",
            "16:00 - عصر",
            "18:00 - غروب",
            "20:00 - شب"
        ])
        group3_layout.addRow(lbl_time, self.feed_time_combo)        
        lbl_daily = QtWidgets.QLabel("خوراک روزانه:")
        lbl_daily.setStyleSheet(input_label_style)
        lbl_total = QtWidgets.QLabel("کل خوراک مورد نیاز:")
        lbl_total.setStyleSheet(input_label_style)
        lbl_suggest = QtWidgets.QLabel("پیشنهاد FCR:")
        lbl_suggest.setStyleSheet(input_label_style)

        self.feed_rate_spin = QtWidgets.QDoubleSpinBox()
        self.feed_rate_spin.setStyleSheet(input_style)
        self.feed_rate_spin.setRange(0.5, 10.0)
        self.feed_rate_spin.setSingleStep(0.1)
        self.feed_rate_spin.setSuffix(" % وزن بدن")
        self.feed_rate_spin.valueChanged.connect(self.calculate_daily_feed)

        self.feed_type_combo = QtWidgets.QComboBox()
        self.feed_type_combo.setMinimumHeight(28)
        self.feed_type_combo.setStyleSheet("""
            QComboBox {
                background-color: #3C3C3C;
                color: #C8C8C8;
                border: 1px solid #3E3E42;
                border-radius: 4px;
                padding: 4px;
                min-height: 28px;
            }
            QComboBox::drop-down {
                border: none;
            }
            QComboBox QAbstractItemView {
                background-color: #3C3C3C;
                color: #C8C8C8;
                selection-background-color: #0E639C;
                min-height: 25px;
                padding: 4px;
            }
            QComboBox QAbstractItemView::item {
                padding: 6px;
                min-height: 25px;
            }
        """)
        self.feed_type_combo.addItems(["شروع (0-20 گرم)", "رشد (20-100 گرم)", "پایانی (100+ گرم)"])

        self.start_date_edit = JalaliDateEdit()
        self.start_date_edit.setStyleSheet(input_style)

        self.end_date_edit = JalaliDateEdit()
        self.end_date_edit.setStyleSheet(input_style)

        self.daily_feed_label = QtWidgets.QLabel("0 کیلوگرم")
        self.daily_feed_label.setAlignment(QtCore.Qt.AlignRight)
        self.daily_feed_label.setStyleSheet(calc_style)

        self.total_feed_label = QtWidgets.QLabel("0 کیلوگرم")
        self.total_feed_label.setAlignment(QtCore.Qt.AlignRight)
        self.total_feed_label.setStyleSheet(calc_style)

        self.suggested_fcr_label = QtWidgets.QLabel("--")
        self.suggested_fcr_label.setAlignment(QtCore.Qt.AlignRight)
        self.suggested_fcr_label.setStyleSheet(calc_style)

        group3_layout.addRow(lbl_rate, self.feed_rate_spin)
        group3_layout.addRow(lbl_type, self.feed_type_combo)
        group3_layout.addRow(lbl_start, self.start_date_edit)
        group3_layout.addRow(lbl_end, self.end_date_edit)
        group3_layout.addRow(lbl_daily, self.daily_feed_label)
        group3_layout.addRow(lbl_total, self.total_feed_label)
        group3_layout.addRow(lbl_suggest, self.suggested_fcr_label)

        main_row_layout.addWidget(group3, 1)

        layout.addLayout(main_row_layout)

        # ========== دکمه ذخیره ==========
      
        save_btn = QtWidgets.QPushButton("💾 ذخیره فرمولاسیون جیره")
        save_btn.setMinimumHeight(38)
        save_btn.setStyleSheet("""
            QPushButton {
                background-color: rgba(100, 100, 100, 50);
                color: #C8C8C8;
                border: 1px solid rgba(150, 150, 150, 70);
                border-radius: 6px;
                font-weight: bold;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: rgba(100, 100, 100, 80);
                border-color: rgba(150, 150, 150, 120);
                color: white;
            }
            QPushButton:pressed {
                background-color: rgba(78, 201, 176, 60);
                border-color: #4EC9B0;
            }
        """)
        save_btn.clicked.connect(self.save_diet_formulation)
        layout.addWidget(save_btn)

        # ========== گروه 4: پیشنهادات تغذیه ==========
        group4 = QtWidgets.QGroupBox("پیشنهادات تغذیه روزانه")
        group4.setStyleSheet("""
            QGroupBox {
                border: 1px solid #3E3E42;
                border-radius: 5px;
                margin-top: 8px;
                padding-top: 8px;
                color: #4EC9B0;
                font-weight: bold;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
                color: #4EC9B0;
            }
        """)
        group4_layout = QtWidgets.QVBoxLayout(group4)
        group4_layout.setContentsMargins(10, 12, 10, 10)

        self.recommendations_table = QtWidgets.QTableWidget()
        self.recommendations_table.setColumnCount(5)
        self.recommendations_table.setHorizontalHeaderLabels(["تاریخ", "مقدار (کیلوگرم)", "زمان", "وضعیت", "عملیات"])
        self.recommendations_table.horizontalHeader().setStretchLastSection(True)
        self.recommendations_table.setMinimumHeight(140)
        self.recommendations_table.setStyleSheet("""
            QTableWidget {
                background-color: #2D2D30;
                alternate-background-color: #252526;
                gridline-color: #3E3E42;
                border: 1px solid #3E3E42;
            }
            QTableWidget::item {
                color: #C8C8C8;
                padding: 6px;
            }
            QHeaderView::section {
                background-color: #252526;
                color: #4EC9B0;
                padding: 6px;
                border: none;
                border-bottom: 1px solid #3E3E42;
            }
        """)
        group4_layout.addWidget(self.recommendations_table)
        layout.addWidget(group4)

        self.load_diet_cages()
        return tab

    def load_diet_cages(self):
        """بارگذاری قفس‌ها در کامبوباکس جیره‌بندی"""
        self.diet_cage_combo.clear()
        self.diet_cage_combo.addItem("--- انتخاب قفس ---", None)
        
        try:
            cages = self.db.fetch_all("SELECT id FROM cages ORDER BY id")
            for cage in cages:
                self.diet_cage_combo.addItem(f"قفس {cage['id']}", cage['id'])
            
            if self.diet_cage_combo.count() > 1:
                self.diet_cage_combo.setCurrentIndex(1)
                self.on_diet_cage_changed()
        except Exception as e:
            print(f"ERROR در load_diet_cages: {e}")

    def on_diet_cage_changed(self):
        """تغییر قفس در تب جیره‌بندی"""
        self.load_diet_cycles()

    def load_diet_cycles(self):
        """بارگذاری دوره‌های پرورش برای قفس انتخاب شده"""
        self.diet_cycle_combo.clear()
        self.diet_cycle_combo.addItem("--- انتخاب دوره پرورش ---", None)
        
        cage_id = self.diet_cage_combo.currentData()
        if not cage_id:
            return
        
        try:
            cycles = self.db.fetch_all("""
                SELECT cycle_id as id, start_date, species 
                FROM production_cycles 
                WHERE cage_id = %s AND is_active = 1
                ORDER BY start_date DESC
            """, (cage_id,))
            
            for cycle in cycles:
                species_text = cycle['species'] if cycle['species'] else 'نامشخص'
                display_text = f"{species_text} - شروع: {cycle['start_date']}"
                self.diet_cycle_combo.addItem(display_text, cycle['id'])
            
            if self.diet_cycle_combo.count() > 1:
                self.diet_cycle_combo.setCurrentIndex(1)
                self.on_diet_cycle_changed()
        except Exception as e:
            print(f"ERROR در load_diet_cycles: {e}")

    def on_diet_cycle_changed(self):
        """تغییر دوره پرورش در تب جیره‌بندی"""
        cycle_id = self.diet_cycle_combo.currentData()
        
        if not cycle_id:
            self.species_label.setText("گونه: --")
            self.avg_weight_label.setText("وزن میانگین: -- گرم")
            self.temp_label.setText("دمای آب: -- °C")
            self.target_weight_label.setText("وزن هدف: -- گرم")
            self.target_fcr_label.setText("FCR هدف: --")
            self.biomass_label.setText("زیستتوده: -- kg")
            self.feed_rate_spin.setValue(2.5)
            self.daily_feed_label.setText("0 کیلوگرم")
            self.total_feed_label.setText("0 کیلوگرم")
            self.recommendations_table.setRowCount(0)  # پاک کردن جدول پیشنهادات
            return

        cycle = self.db.fetch_one("SELECT * FROM production_cycles WHERE cycle_id = %s", (cycle_id,))
        if cycle:
            species_name = cycle['species'] if cycle['species'] else 'نامشخص'
            self.species_label.setText(species_name)
            self.target_weight_label.setText(f"{cycle['target_weight'] or 0:.0f} گرم")
            self.target_fcr_label.setText(f"{cycle.get('target_fcr', 1.5)}")

            last_biomass = self.db.fetch_one("""
                SELECT estimated_weight, estimated_count 
                FROM biomasses 
                WHERE cycle_id = %s 
                ORDER BY date DESC LIMIT 1
            """, (cycle_id,))

            if last_biomass:
                avg_weight = float(last_biomass['estimated_weight'])
                count = float(last_biomass['estimated_count'])
                biomass_kg = (avg_weight * count) / 1000
                self.avg_weight_label.setText(f"{avg_weight:.0f} گرم")
                self.biomass_label.setText(f"{biomass_kg:.0f} kg")

                last_temp = self.db.fetch_one("""
                    SELECT temperature 
                    FROM water_parameters 
                    WHERE cage_id = %s 
                    ORDER BY date DESC LIMIT 1
                """, (cycle['cage_id'],))
                
                if last_temp:
                    temp = float(last_temp['temperature'])
                    self.temp_label.setText(f"{temp:.1f} °C")
                    
                    suggested_rate = self.db.calculate_feed_rate(species_name, avg_weight, temp)
                    self.feed_rate_spin.setValue(suggested_rate)

                    suggested_feed_type = self.db.get_feed_type_by_weight(avg_weight)
                    idx = self.feed_type_combo.findText(suggested_feed_type)
                    if idx >= 0:
                        self.feed_type_combo.setCurrentIndex(idx)
            else:
                # اگر زیست‌توده وجود نداشت
                self.avg_weight_label.setText("-- گرم")
                self.biomass_label.setText("-- kg")

            today = jdatetime.date.today()
            self.start_date_edit.set_jalali_date(f"{today.year}/{today.month:02d}/{today.day:02d}")
            end_date = jdatetime.date(today.year, today.month, today.day) + timedelta(days=7)
            end_date_str = f"{end_date.year}/{end_date.month:02d}/{end_date.day:02d}"
            self.end_date_edit.set_jalali_date(end_date_str)

            # ========== اضافه کنید ==========
            self.load_diet_recommendations(cycle_id)
            # ================================
            
            self.calculate_daily_feed()  

    def calculate_daily_feed(self):
        """محاسبه خوراک روزانه بر اساس نرخ و زیستتوده"""
        feed_rate = self.feed_rate_spin.value()
        
        biomass_text = self.biomass_label.text()
        match = re.search(r'([\d,]+)', biomass_text)
        biomass_kg = float(match.group(1).replace(',', '')) if match else 0
        
        daily_feed_kg = (feed_rate / 100) * biomass_kg
        self.daily_feed_label.setText(f"{daily_feed_kg:,.0f} کیلوگرم")
        
        cycle_id = self.diet_cycle_combo.currentData()
        if cycle_id:
            cycle = self.db.fetch_one("SELECT target_weight, initial_weight, initial_count FROM production_cycles WHERE cycle_id = %s", (cycle_id,))
            if cycle and cycle['target_weight'] and cycle['initial_weight'] and cycle['initial_count']:
                target_weight = float(cycle['target_weight'])
                initial_weight = float(cycle['initial_weight'])
                initial_count = float(cycle['initial_count'])
                
                target_total_kg = (target_weight * initial_count) / 1000
                current_total_kg = biomass_kg
                remaining_gain_kg = max(0, target_total_kg - current_total_kg)
                
                target_fcr = float(cycle.get('target_fcr', 1.5))
                remaining_feed_kg = remaining_gain_kg * target_fcr
                self.total_feed_label.setText(f"{remaining_feed_kg:,.0f} کیلوگرم")
                self.suggested_fcr_label.setText(f"{target_fcr}")

    def create_suggestion_buttons(self, sug_id, start_date, end_date, amount, status, notes):
        """ایجاد دکمه‌های عملیات برای پیشنهاد"""
        # استخراج زمان از notes
        feed_time = "08:00"
        if notes and 'زمان پیشنهادی:' in notes:
            import re
            match = re.search(r'زمان پیشنهادی:\s*([^|]+)', notes)
            if match:
                feed_time = match.group(1).strip()
        
        btn_widget = QtWidgets.QWidget()
        btn_layout = QtWidgets.QHBoxLayout(btn_widget)
        btn_layout.setContentsMargins(2, 0, 2, 0)
        btn_layout.setSpacing(3)
        
        if status == 'pending':
            confirm_btn = QtWidgets.QToolButton()
            confirm_btn.setIcon(qta.icon('fa5s.check', color='#4EC9B0'))
            confirm_btn.setIconSize(QtCore.QSize(14, 14))
            confirm_btn.setToolTip("تایید")
            confirm_btn.setFixedSize(22, 22)
            confirm_btn.setStyleSheet("""
                QToolButton {
                    background-color: rgba(78, 201, 176, 30);
                    border: 1px solid rgba(78, 201, 176, 60);
                    border-radius: 3px;
                }
                QToolButton:hover {
                    background-color: rgba(78, 201, 176, 70);
                }
            """)
            confirm_btn.clicked.connect(lambda checked, sid=sug_id: self.confirm_suggestion(sid))
            btn_layout.addWidget(confirm_btn)
        
        edit_btn = QtWidgets.QToolButton()
        edit_btn.setIcon(qta.icon('fa5s.edit', color='#569CD6'))
        edit_btn.setIconSize(QtCore.QSize(14, 14))
        edit_btn.setToolTip("ویرایش")
        edit_btn.setFixedSize(22, 22)
        edit_btn.setStyleSheet("""
            QToolButton {
                background-color: rgba(86, 156, 214, 30);
                border: 1px solid rgba(86, 156, 214, 60);
                border-radius: 3px;
            }
            QToolButton:hover {
                background-color: rgba(86, 156, 214, 70);
            }
        """)
        edit_btn.clicked.connect(lambda: self.edit_suggestion_by_id(sug_id, start_date, end_date, amount, feed_time))
        btn_layout.addWidget(edit_btn)
        
        delete_btn = QtWidgets.QToolButton()
        delete_btn.setIcon(qta.icon('fa5s.trash-alt', color='#F48771'))
        delete_btn.setIconSize(QtCore.QSize(14, 14))
        delete_btn.setToolTip("حذف")
        delete_btn.setFixedSize(22, 22)
        delete_btn.setStyleSheet("""
            QToolButton {
                background-color: rgba(244, 135, 113, 30);
                border: 1px solid rgba(244, 135, 113, 60);
                border-radius: 3px;
            }
            QToolButton:hover {
                background-color: rgba(244, 135, 113, 70);
            }
        """)
        delete_btn.clicked.connect(lambda: self.delete_suggestion_by_id(sug_id, start_date))
        btn_layout.addWidget(delete_btn)
        
        btn_layout.addStretch()
        return btn_widget
    
    def edit_suggestion_by_id(self, sug_id, old_start, old_end, old_amount, old_time):
        """ویرایش پیشنهاد با دو تاریخ و زمان"""
        from ..widgets.jalali_date_edit import JalaliDateEdit
        
        dialog = QtWidgets.QDialog(self)
        dialog.setWindowTitle("ویرایش پیشنهاد تغذیه")
        dialog.setModal(True)
        dialog.resize(350, 280)
        dialog.setStyleSheet("background-color: #252526;")
        
        layout = QtWidgets.QFormLayout(dialog)
        layout.setLabelAlignment(QtCore.Qt.AlignRight)
        
        # تاریخ شروع
        start_edit = JalaliDateEdit()
        if old_start and old_start != "-":
            try:
                start_edit.set_jalali_date(old_start)
            except:
                pass
        
        # تاریخ پایان
        end_edit = JalaliDateEdit()
        if old_end and old_end != "-":
            try:
                end_edit.set_jalali_date(old_end)
            except:
                pass
        
        # مقدار
        amount_spin = QtWidgets.QDoubleSpinBox()
        amount_spin.setRange(0, 100000)
        amount_spin.setValue(old_amount)
        amount_spin.setSuffix(" kg")
        amount_spin.setStyleSheet("background-color: #3C3C3C; color: #C8C8C8; border: 1px solid #3E3E42; border-radius: 4px; padding: 4px;")
        
        # زمان
        time_combo = QtWidgets.QComboBox()
        time_combo.addItems(["06:00", "07:00", "08:00", "09:00", "10:00", "11:00", "12:00", 
                              "13:00", "14:00", "15:00", "16:00", "17:00", "18:00", "19:00", "20:00"])
        time_combo.setEditable(True)
        current_index = time_combo.findText(old_time)
        if current_index >= 0:
            time_combo.setCurrentIndex(current_index)
        else:
            time_combo.setEditText(old_time)
        
        layout.addRow("تاریخ شروع:", start_edit)
        layout.addRow("تاریخ پایان:", end_edit)
        layout.addRow("مقدار کل (kg):", amount_spin)
        layout.addRow("زمان پیشنهادی:", time_combo)
        
        btn_layout = QtWidgets.QHBoxLayout()
        ok_btn = QtWidgets.QPushButton("ذخیره")
        ok_btn.setStyleSheet("background-color: #0E639C; color: white; border-radius: 4px; padding: 6px 12px;")
        cancel_btn = QtWidgets.QPushButton("انصراف")
        cancel_btn.setStyleSheet("background-color: #3C3C3C; color: #C8C8C8; border-radius: 4px; padding: 6px 12px;")
        cancel_btn.clicked.connect(dialog.reject)
        ok_btn.clicked.connect(dialog.accept)
        btn_layout.addWidget(ok_btn)
        btn_layout.addWidget(cancel_btn)
        layout.addRow(btn_layout)
        
        if dialog.exec_():
            new_start = start_edit.get_jalali_date()
            new_end = end_edit.get_jalali_date()
            new_amount = amount_spin.value()
            new_time = time_combo.currentText()
            
            # بروزرسانی در دیتابیس
            self.db.execute_query("""
                UPDATE diet_suggestions 
                SET start_date = %s, end_date = %s, amount = %s, notes = %s
                WHERE id = %s
            """, (new_start, new_end, new_amount, f"خوراک روزانه: {(new_amount / 7):.0f} کیلوگرم | زمان پیشنهادی: {new_time}", sug_id))
            
            QtWidgets.QMessageBox.information(self, "موفق", "پیشنهاد با موفقیت ویرایش شد")
            
            cycle_id = self.diet_cycle_combo.currentData()
            self.load_diet_recommendations(cycle_id)

    def confirm_suggestion(self, sug_id):
        """تایید پیشنهاد و ارسال به برنامه ریزی تولید"""
        if not sug_id:
            QtWidgets.QMessageBox.warning(self, "خطا", "شناسه پیشنهاد یافت نشد")
            return
        
        # دریافت اطلاعات پیشنهاد
        suggestion = self.db.fetch_one("""
            SELECT start_date, end_date, amount, notes 
            FROM diet_suggestions WHERE id = %s
        """, (sug_id,))
        
        if not suggestion:
            QtWidgets.QMessageBox.warning(self, "خطا", "پیشنهاد یافت نشد")
            return
        
        # استخراج زمان از notes
        feed_time = "08:00"
        if suggestion['notes'] and 'زمان پیشنهادی:' in suggestion['notes']:
            import re
            match = re.search(r'زمان پیشنهادی:\s*([^|]+)', suggestion['notes'])
            if match:
                feed_time = match.group(1).strip()
        
        # بروزرسانی وضعیت
        self.db.execute_query("""
            UPDATE diet_suggestions 
            SET status = 'confirmed', confirmed_at = NOW() 
            WHERE id = %s
        """, (sug_id,))
        
        # ارسال به برنامه ریزی تولید
        cycle_id = self.diet_cycle_combo.currentData()
        cage_id = self.diet_cage_combo.currentData()
        start_date_shamsi = suggestion['start_date']
        end_date_shamsi = suggestion['end_date']
        amount = suggestion['amount']
        
        # تبدیل تاریخ شمسی به میلادی
        try:
            parts = start_date_shamsi.split('/')
            if len(parts) == 3:
                shamsi_date = jdatetime.date(int(parts[0]), int(parts[1]), int(parts[2]))
                gregorian_date = shamsi_date.togregorian()
                scheduled_date = f"{gregorian_date.year}-{gregorian_date.month:02d}-{gregorian_date.day:02d}"
            else:
                scheduled_date = start_date_shamsi
        except:
            scheduled_date = start_date_shamsi
        
        print(f"DEBUG: start_date_shamsi = {start_date_shamsi}")
        print(f"DEBUG: scheduled_date (gregorian) = {scheduled_date}")
        
        if cycle_id and cage_id:
            # پیدا کردن برنامه پرورش فعال
            existing_plan = self.db.fetch_one("""
                SELECT id, plan_title FROM production_plans 
                WHERE cage_id = %s AND plan_status IN ('draft', 'active')
                ORDER BY start_date DESC LIMIT 1
            """, (cage_id,))
            
            if existing_plan:
                plan_id = existing_plan['id']
                plan_title = existing_plan['plan_title']
            else:
                today = jdatetime.date.today()
                plan_title = f"برنامه تغذیه قفس {cage_id} - {today.year}"
                self.db.execute_query("""
                    INSERT INTO production_plans 
                    (cage_id, plan_title, plan_type, start_date, end_date, plan_status, notes)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                """, (cage_id, plan_title, "feeding", start_date_shamsi, end_date_shamsi, "draft", 
                       f"ایجاد خودکار از جیره‌بندی"))
                new_plan = self.db.fetch_one("SELECT LAST_INSERT_ID() as id")
                plan_id = new_plan['id'] if new_plan else None
            
            if plan_id:
                # اضافه کردن وظیفه به برنامه پرورش
                self.db.execute_query("""
                    INSERT INTO plan_tasks 
                    (plan_id, task_title, task_description, category, scheduled_date, 
                     scheduled_start_time, estimated_duration_minutes, assigned_to_unit, 
                     priority_level, execution_status)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, (plan_id, f"تغذیه قفس {cage_id}", 
                       f"بازه زمانی: {start_date_shamsi} تا {end_date_shamsi} - کل خوراک: {amount:.0f} کیلوگرم", 
                       "feeding", scheduled_date, feed_time, 30, "واحد تغذیه", 2, "pending"))
                
                print(f"DEBUG: وظیفه به plan_id={plan_id} اضافه شد")
        
        self.load_diet_recommendations(cycle_id)
        
        QtWidgets.QMessageBox.information(self, "موفق", 
            f"✅ پیشنهاد تغذیه تایید و به برنامه ریزی تولید ارسال شد.\n\n"
            f"📅 تاریخ شروع: {start_date_shamsi}\n"
            f"📅 تاریخ پایان: {end_date_shamsi}\n"
            f"⏰ زمان: {feed_time}\n\n"
            f"برای مشاهده به تب «برنامه ریزی تولید ← برنامه پرورش» بروید.")
    def delete_suggestion_by_id(self, sug_id, date):
        """حذف پیشنهاد از دیتابیس"""
        reply = QtWidgets.QMessageBox.question(
            self, "تأیید حذف", f"آیا از حذف این پیشنهاد مطمئن هستید؟",
            QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No
        )
        
        if reply == QtWidgets.QMessageBox.Yes:
            self.db.execute_query("DELETE FROM diet_suggestions WHERE id = %s", (sug_id,))
            QtWidgets.QMessageBox.information(self, "موفق", "پیشنهاد با موفقیت حذف شد")
            
            cycle_id = self.diet_cycle_combo.currentData()
            self.load_diet_recommendations(cycle_id)
    def save_diet_formulation(self):
        """ذخیره فرمولاسیون جیره و تولید یک پیشنهاد با بازه زمانی"""
        try:
            cycle_id = self.diet_cycle_combo.currentData()
            if not cycle_id:
                QtWidgets.QMessageBox.warning(self, "خطا", "لطفاً یک دوره پرورش را انتخاب کنید")
                return
            
            cage_id = self.diet_cage_combo.currentData()
            if not cage_id:
                QtWidgets.QMessageBox.warning(self, "خطا", "لطفاً یک قفس را انتخاب کنید")
                return
            
            # دریافت اطلاعات از فرم
            species = self.species_label.text()
            avg_weight_text = self.avg_weight_label.text().replace(" گرم", "")
            try:
                avg_weight = float(avg_weight_text)
            except:
                avg_weight = 0
            
            temp_text = self.temp_label.text().replace(" °C", "")
            try:
                water_temp = float(temp_text)
            except:
                water_temp = 20
            
            feed_rate = self.feed_rate_spin.value()
            feed_type = self.feed_type_combo.currentText()
            start_date = self.start_date_edit.text().strip()
            end_date = self.end_date_edit.text().strip()
            
            # دریافت زمان انتخاب شده
            feed_time = self.feed_time_combo.currentText()
            
            # محاسبه خوراک روزانه
            biomass_text = self.biomass_label.text()
            import re
            match = re.search(r'([\d,]+)', biomass_text)
            biomass_kg = float(match.group(1).replace(',', '')) if match else 0
            daily_feed_kg = (feed_rate / 100) * biomass_kg
            
            # محاسبه تعداد روزهای بین دو تاریخ
            try:
                start_parts = start_date.split('/')
                end_parts = end_date.split('/')
                if len(start_parts) == 3 and len(end_parts) == 3:
                    start_jalali = jdatetime.date(int(start_parts[0]), int(start_parts[1]), int(start_parts[2]))
                    end_jalali = jdatetime.date(int(end_parts[0]), int(end_parts[1]), int(end_parts[2]))
                    days_diff = (end_jalali - start_jalali).days + 1
                else:
                    days_diff = 7
            except:
                days_diff = 7
            
            total_feed_kg = daily_feed_kg * days_diff
            
            # حذف پیشنهادات قدیمی
            self.db.execute_query("DELETE FROM diet_suggestions WHERE cycle_id = %s", (cycle_id,))
            
            # ذخیره پیشنهاد جدید (زمان در notes ذخیره می‌شود)
            self.db.execute_query("""
                INSERT INTO diet_suggestions (cycle_id, start_date, end_date, amount, status, notes)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (cycle_id, start_date, end_date, total_feed_kg, "pending", 
                   f"خوراک روزانه: {daily_feed_kg:.0f} کیلوگرم | زمان پیشنهادی: {feed_time}"))
            
            # ذخیره فرمولاسیون
            self.db.execute_query("""
                INSERT INTO diet_formulations 
                (production_cycle_id, cage_id, formulation_date, species, avg_weight_gram,
                 water_temperature, daily_feed_rate, calculated_feed_kg, feed_type,
                 fcr_target, nutritionist_id, notes)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                cycle_id, cage_id, start_date, species, avg_weight,
                water_temp, feed_rate, daily_feed_kg, feed_type,
                1.5, 1, f"بازه زمانی: {start_date} تا {end_date}"
            ))
            
            self.load_diet_recommendations(cycle_id)
            
            QtWidgets.QMessageBox.information(self, "موفق", 
                f"✅ فرمولاسیون جیره ذخیره شد.\n\n"
                f"📅 از تاریخ: {start_date}\n"
                f"📅 تا تاریخ: {end_date}\n"
                f"⏰ زمان: {feed_time}\n"
                f"🍽️ خوراک روزانه: {daily_feed_kg:.0f} کیلوگرم\n"
                f"📊 خوراک کل بازه: {total_feed_kg:.0f} کیلوگرم")
                
        except Exception as e:
            print(f"ERROR: {e}")
            QtWidgets.QMessageBox.critical(self, "خطا", f"خطا: {str(e)}")
            
    def load_diet_recommendations(self, cycle_id):
        """بارگذاری پیشنهادات تغذیه با استخراج زمان از notes"""
        if not cycle_id:
            self.recommendations_table.setRowCount(0)
            return
        
        saved_suggestions = self.db.fetch_all("""
            SELECT id, start_date, end_date, amount, status, notes 
            FROM diet_suggestions 
            WHERE cycle_id = %s 
            ORDER BY id DESC
        """, (cycle_id,))
        
        if not saved_suggestions:
            self.recommendations_table.setRowCount(0)
            return
        
        self.recommendations_table.setRowCount(len(saved_suggestions))
        self.recommendations_table.setColumnCount(6)
        self.recommendations_table.setHorizontalHeaderLabels(
            ["تاریخ شروع", "تاریخ پایان", "مقدار کل (kg)", "زمان", "وضعیت", ""]
        )
        
        self.recommendations_table.setColumnWidth(0, 100)
        self.recommendations_table.setColumnWidth(1, 100)
        self.recommendations_table.setColumnWidth(2, 90)
        self.recommendations_table.setColumnWidth(3, 90)
        self.recommendations_table.setColumnWidth(4, 90)
        self.recommendations_table.setColumnWidth(5, 80)
        self.recommendations_table.verticalHeader().setDefaultSectionSize(40)
        
        for i, sug in enumerate(saved_suggestions):
            # تاریخ شروع
            item0 = QtWidgets.QTableWidgetItem(sug['start_date'] or "-")
            item0.setTextAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
            self.recommendations_table.setItem(i, 0, item0)
            
            # تاریخ پایان
            item1 = QtWidgets.QTableWidgetItem(sug['end_date'] or "-")
            item1.setTextAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
            self.recommendations_table.setItem(i, 1, item1)
            
            # مقدار کل
            item2 = QtWidgets.QTableWidgetItem(f"{sug['amount']:.0f}")
            item2.setTextAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
            self.recommendations_table.setItem(i, 2, item2)
            
            # استخراج زمان از notes
            feed_time_display = "08:00"
            if sug['notes'] and 'زمان پیشنهادی:' in sug['notes']:
                import re
                match = re.search(r'زمان پیشنهادی:\s*([^|]+)', sug['notes'])
                if match:
                    feed_time_display = match.group(1).strip()
            
            item3 = QtWidgets.QTableWidgetItem(feed_time_display)
            item3.setTextAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
            self.recommendations_table.setItem(i, 3, item3)
            
            # وضعیت
            status_text = "⏳ در انتظار" if sug['status'] == 'pending' else "✅ تایید شد"
            item4 = QtWidgets.QTableWidgetItem(status_text)
            item4.setTextAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
            self.recommendations_table.setItem(i, 4, item4)
            
            # دکمه‌ها
            btn_widget = self.create_suggestion_buttons(sug['id'], sug['start_date'], sug['end_date'], sug['amount'], sug['status'], sug['notes'])
            self.recommendations_table.setCellWidget(i, 5, btn_widget)
    def edit_suggestion_from_table(self, date, amount):
        """ویرایش پیشنهاد تغذیه از جدول"""
        # پیدا کردن ردیف مربوط به این تاریخ
        row = -1
        for r in range(self.recommendations_table.rowCount()):
            if self.recommendations_table.item(r, 0).text() == date:
                row = r
                break
        
        if row == -1:
            QtWidgets.QMessageBox.warning(self, "خطا", "پیشنهاد یافت نشد")
            return
        
        dialog = QtWidgets.QDialog(self)
        dialog.setWindowTitle("ویرایش پیشنهاد تغذیه")
        dialog.setModal(True)
        dialog.resize(300, 200)
        dialog.setStyleSheet("background-color: #252526;")
        
        layout = QtWidgets.QFormLayout(dialog)
        layout.setLabelAlignment(QtCore.Qt.AlignRight)
        
        # مقدار جدید
        amount_spin = QtWidgets.QDoubleSpinBox()
        amount_spin.setRange(0, 10000)
        amount_spin.setValue(amount)
        amount_spin.setSuffix(" kg")
        amount_spin.setStyleSheet("background-color: #3C3C3C; color: #C8C8C8; border: 1px solid #3E3E42; border-radius: 4px; padding: 4px;")
        
        # زمان جدید
        time_edit = QtWidgets.QTimeEdit()
        time_edit.setTime(QtCore.QTime(8, 0))
        time_edit.setStyleSheet("background-color: #3C3C3C; color: #C8C8C8; border: 1px solid #3E3E42; border-radius: 4px; padding: 4px;")
        
        layout.addRow("مقدار جدید (kg):", amount_spin)
        layout.addRow("زمان جدید:", time_edit)
        
        btn_layout = QtWidgets.QHBoxLayout()
        ok_btn = QtWidgets.QPushButton("ذخیره")
        ok_btn.setStyleSheet("background-color: #0E639C; color: white; border-radius: 4px; padding: 6px 12px;")
        cancel_btn = QtWidgets.QPushButton("انصراف")
        cancel_btn.setStyleSheet("background-color: #3C3C3C; color: #C8C8C8; border-radius: 4px; padding: 6px 12px;")
        cancel_btn.clicked.connect(dialog.reject)
        ok_btn.clicked.connect(dialog.accept)
        btn_layout.addWidget(ok_btn)
        btn_layout.addWidget(cancel_btn)
        layout.addRow(btn_layout)
        
        if dialog.exec_():
            new_amount = amount_spin.value()
            new_time = time_edit.time().toString("hh:mm")
            
            # بروزرسانی جدول
            self.recommendations_table.setItem(row, 1, QtWidgets.QTableWidgetItem(f"{new_amount:.0f}"))
            self.recommendations_table.setItem(row, 2, QtWidgets.QTableWidgetItem(new_time))
            
            QtWidgets.QMessageBox.information(self, "موفق", f"پیشنهاد با موفقیت ویرایش شد.\nمقدار جدید: {new_amount:.0f} kg\nزمان: {new_time}")
    
    def delete_suggestion_from_table(self, row, date):
        """حذف پیشنهاد تغذیه از جدول"""
        reply = QtWidgets.QMessageBox.question(
            self, 
            "تأیید حذف", 
            f"آیا از حذف پیشنهاد تاریخ {date} مطمئن هستید؟",
            QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No
        )
        
        if reply == QtWidgets.QMessageBox.Yes:
            self.recommendations_table.removeRow(row)
            QtWidgets.QMessageBox.information(self, "موفق", "پیشنهاد با موفقیت حذف شد")

    def create_health_tab(self):
        """ایجاد تب بهداشت و درمان کامل"""
        tab = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout(tab)
        layout.setSpacing(10)
        layout.setContentsMargins(10, 10, 10, 10)

        title = QtWidgets.QLabel("💊 مدیریت بهداشت و درمان")
        title.setAlignment(QtCore.Qt.AlignCenter)
        title.setStyleSheet("font-size: 16px; font-weight: bold; color: #569CD6; padding: 10px;")
        layout.addWidget(title)

        # ========== انتخاب قفس و دوره ==========
        selector_layout = QtWidgets.QHBoxLayout()
        selector_layout.setSpacing(15)

        selector_layout.addWidget(QtWidgets.QLabel("قفس:"))
        self.health_cage_combo = QtWidgets.QComboBox()
        self.health_cage_combo.setMinimumWidth(150)
        self.health_cage_combo.currentIndexChanged.connect(self.on_health_cage_changed)
        selector_layout.addWidget(self.health_cage_combo)

        selector_layout.addWidget(QtWidgets.QLabel("دوره پرورش:"))
        self.health_cycle_combo = QtWidgets.QComboBox()
        self.health_cycle_combo.setMinimumWidth(200)
        self.health_cycle_combo.currentIndexChanged.connect(self.on_health_cycle_changed)
        selector_layout.addWidget(self.health_cycle_combo)

        selector_layout.addStretch()
        layout.addLayout(selector_layout)

        # ========== تب‌های داخلی ==========
        health_tabs = QtWidgets.QTabWidget()
        health_tabs.setStyleSheet("""
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

        # تب 1: نسخه دامپزشک
        prescription_tab = self.create_prescription_tab()
        health_tabs.addTab(prescription_tab, "📋 نسخه دامپزشک")

        # تب 2: داروها
        medicines_tab = self.create_medicines_tab()
        health_tabs.addTab(medicines_tab, "💊 داروها")

        # تب 3: سابقه درمان
        history_tab = self.create_treatment_history_tab()
        health_tabs.addTab(history_tab, "📜 سابقه درمان")

        layout.addWidget(health_tabs)

        self.load_health_cages()
        return tab

    def create_prescription_tab(self):
        """ایجاد تب نسخه دامپزشک"""
        tab = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout(tab)

        # فرم ثبت نسخه
        form_group = QtWidgets.QGroupBox("ثبت نسخه جدید")
        form_layout = QtWidgets.QFormLayout(form_group)
        form_layout.setLabelAlignment(QtCore.Qt.AlignRight)

        self.prescription_date = JalaliDateEdit()
        form_layout.addRow("تاریخ نسخه:", self.prescription_date)

        self.vet_name = QtWidgets.QLineEdit()
        self.vet_name.setPlaceholderText("نام دامپزشک")
        form_layout.addRow("نام دامپزشک:", self.vet_name)

        self.diagnosis = QtWidgets.QTextEdit()
        self.diagnosis.setMaximumHeight(60)
        self.diagnosis.setPlaceholderText("تشخیص بیماری...")
        form_layout.addRow("تشخیص:", self.diagnosis)

        self.medicine_combo = QtWidgets.QComboBox()
        self.medicine_combo.setEditable(True)
        form_layout.addRow("دارو:", self.medicine_combo)

        self.dosage = QtWidgets.QDoubleSpinBox()
        self.dosage.setRange(0, 1000)
        self.dosage.setSuffix(" mg/kg")
        form_layout.addRow("دوز مصرفی:", self.dosage)

        self.duration = QtWidgets.QSpinBox()
        self.duration.setRange(1, 30)
        self.duration.setSuffix(" روز")
        form_layout.addRow("مدت درمان:", self.duration)

        self.prescription_notes = QtWidgets.QTextEdit()
        self.prescription_notes.setMaximumHeight(60)
        self.prescription_notes.setPlaceholderText("توضیحات اضافی...")
        form_layout.addRow("یادداشت:", self.prescription_notes)

        save_btn = QtWidgets.QPushButton("💾 ذخیره نسخه")
        save_btn.setStyleSheet("background-color: #0E639C; color: white; font-weight: bold; border-radius: 4px; padding: 6px 12px;")
        save_btn.clicked.connect(self.save_prescription)
        form_layout.addRow(save_btn)

        layout.addWidget(form_group)

        # جدول نسخه‌های ثبت شده
        records_group = QtWidgets.QGroupBox("نسخه‌های ثبت شده")
        records_layout = QtWidgets.QVBoxLayout(records_group)
        self.prescriptions_table = QtWidgets.QTableWidget()
        self.prescriptions_table.setColumnCount(5)
        self.prescriptions_table.setHorizontalHeaderLabels(["تاریخ", "دامپزشک", "تشخیص", "دارو", "مدت"])
        self.prescriptions_table.horizontalHeader().setStretchLastSection(True)
        records_layout.addWidget(self.prescriptions_table)
        layout.addWidget(records_group)

        return tab

    def create_medicines_tab(self):
        """ایجاد تب مدیریت داروها"""
        tab = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout(tab)

        # فرم افزودن دارو
        form_group = QtWidgets.QGroupBox("افزودن داروی جدید")
        form_layout = QtWidgets.QFormLayout(form_group)
        form_layout.setLabelAlignment(QtCore.Qt.AlignRight)

        self.medicine_name = QtWidgets.QLineEdit()
        self.medicine_name.setPlaceholderText("نام دارو")
        form_layout.addRow("نام دارو:", self.medicine_name)

        self.medicine_category = QtWidgets.QComboBox()
        self.medicine_category.addItems(["آنتی‌بیوتیک", "ضدالتهاب", "ضدانگل", "واکسن", "مکمل", "ضدعفونی‌کننده"])
        form_layout.addRow("دسته‌بندی:", self.medicine_category)

        self.medicine_stock = QtWidgets.QDoubleSpinBox()
        self.medicine_stock.setRange(0, 10000)
        self.medicine_stock.setSuffix(" واحد")
        form_layout.addRow("موجودی:", self.medicine_stock)

        self.medicine_unit = QtWidgets.QComboBox()
        self.medicine_unit.addItems(["ml", "mg", "gr", "عدد", "لیتر"])
        form_layout.addRow("واحد:", self.medicine_unit)

        self.expiry_date = JalaliDateEdit()
        form_layout.addRow("تاریخ انقضا:", self.expiry_date)

        add_btn = QtWidgets.QPushButton("➕ افزودن دارو")
        add_btn.setStyleSheet("background-color: #2E8B57; color: white; font-weight: bold; border-radius: 4px; padding: 6px 12px;")
        add_btn.clicked.connect(self.add_medicine)
        form_layout.addRow(add_btn)

        layout.addWidget(form_group)

        # جدول داروها
        medicines_group = QtWidgets.QGroupBox("لیست داروها")
        medicines_layout = QtWidgets.QVBoxLayout(medicines_group)
        self.medicines_table = QtWidgets.QTableWidget()
        self.medicines_table.setColumnCount(5)
        self.medicines_table.setHorizontalHeaderLabels(["نام دارو", "دسته‌بندی", "موجودی", "واحد", "انقضا"])
        self.medicines_table.horizontalHeader().setStretchLastSection(True)
        medicines_layout.addWidget(self.medicines_table)
        layout.addWidget(medicines_group)

        self.load_medicines()
        return tab

    def create_treatment_history_tab(self):
        """ایجاد تب سابقه درمان"""
        tab = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout(tab)

        self.treatment_table = QtWidgets.QTableWidget()
        self.treatment_table.setColumnCount(6)
        self.treatment_table.setHorizontalHeaderLabels(["تاریخ", "قفس", "دامپزشک", "تشخیص", "دارو", "وضعیت"])
        self.treatment_table.horizontalHeader().setStretchLastSection(True)
        layout.addWidget(self.treatment_table)

        return tab

    # ========== توابع کمکی بهداشت و درمان ==========

    def load_health_cages(self):
        """بارگذاری قفس‌ها در تب بهداشت"""
        self.health_cage_combo.clear()
        self.health_cage_combo.addItem("--- انتخاب قفس ---", None)
        if self.current_mooring and hasattr(self.current_mooring, 'cages'):
            for cage in self.current_mooring.cages:
                self.health_cage_combo.addItem(cage.id, cage.id)

    def on_health_cage_changed(self):
        """تغییر قفس در تب بهداشت"""
        self.load_health_cycles()

    def load_health_cycles(self):
        """بارگذاری دوره‌های پرورش در تب بهداشت"""
        self.health_cycle_combo.clear()
        self.health_cycle_combo.addItem("--- انتخاب دوره ---", None)
        cage_id = self.health_cage_combo.currentData()
        if cage_id:
            cycles = self.db.fetch_all("""
                SELECT cycle_id as id, start_date, species 
                FROM production_cycles 
                WHERE cage_id = %s AND is_active = 1
                ORDER BY start_date DESC
            """, (cage_id,))
            for cycle in cycles:
                self.health_cycle_combo.addItem(f"{cycle['species']} - {cycle['start_date']}", cycle['id'])

    def on_health_cycle_changed(self):
        """تغییر دوره در تب بهداشت"""
        self.load_prescriptions()
        self.load_treatment_history()

    def load_prescriptions(self):
        """بارگذاری نسخه‌های دامپزشک"""
        cycle_id = self.health_cycle_combo.currentData()
        if not cycle_id:
            self.prescriptions_table.setRowCount(0)
            return
        
        prescriptions = self.db.fetch_all("""
            SELECT prescription_date, veterinarian_name, diagnosis, notes, duration_days
            FROM veterinary_prescriptions 
            WHERE cycle_id = %s 
            ORDER BY prescription_date DESC
        """, (cycle_id,))
        
        self.prescriptions_table.setRowCount(len(prescriptions))
        for i, p in enumerate(prescriptions):
            self.prescriptions_table.setItem(i, 0, QtWidgets.QTableWidgetItem(p['prescription_date']))
            self.prescriptions_table.setItem(i, 1, QtWidgets.QTableWidgetItem(p['veterinarian_name']))
            self.prescriptions_table.setItem(i, 2, QtWidgets.QTableWidgetItem(p['diagnosis'][:50] if p['diagnosis'] else "-"))
            self.prescriptions_table.setItem(i, 3, QtWidgets.QTableWidgetItem(p['notes'][:50] if p['notes'] else "-"))
            self.prescriptions_table.setItem(i, 4, QtWidgets.QTableWidgetItem(f"{p['duration_days']} روز" if p['duration_days'] else "-"))

    def load_medicines(self):
        """بارگذاری لیست داروها"""
        medicines = self.db.fetch_all("SELECT name, category, stock_quantity, unit, expiry_date FROM medicines ORDER BY name")
        self.medicines_table.setRowCount(len(medicines))
        for i, m in enumerate(medicines):
            self.medicines_table.setItem(i, 0, QtWidgets.QTableWidgetItem(m['name']))
            self.medicines_table.setItem(i, 1, QtWidgets.QTableWidgetItem(m['category']))
            self.medicines_table.setItem(i, 2, QtWidgets.QTableWidgetItem(str(m['stock_quantity'])))
            self.medicines_table.setItem(i, 3, QtWidgets.QTableWidgetItem(m['unit']))
            self.medicines_table.setItem(i, 4, QtWidgets.QTableWidgetItem(m['expiry_date'] or "-"))

        # پر کردن کامبوباکس داروها
        self.medicine_combo.clear()
        for m in medicines:
            self.medicine_combo.addItem(f"{m['name']} ({m['stock_quantity']} {m['unit']})", m['name'])

    def load_treatment_history(self):
        """بارگذاری سابقه درمان"""
        cycle_id = self.health_cycle_combo.currentData()
        if not cycle_id:
            self.treatment_table.setRowCount(0)
            return
        
        treatments = self.db.fetch_all("""
            SELECT treatment_date, cage_id, veterinarian_name, diagnosis, medicine_name, status
            FROM treatment_records 
            WHERE cycle_id = %s 
            ORDER BY treatment_date DESC
        """, (cycle_id,))
        
        self.treatment_table.setRowCount(len(treatments))
        for i, t in enumerate(treatments):
            self.treatment_table.setItem(i, 0, QtWidgets.QTableWidgetItem(t['treatment_date']))
            self.treatment_table.setItem(i, 1, QtWidgets.QTableWidgetItem(t['cage_id']))
            self.treatment_table.setItem(i, 2, QtWidgets.QTableWidgetItem(t['veterinarian_name']))
            self.treatment_table.setItem(i, 3, QtWidgets.QTableWidgetItem(t['diagnosis'][:40] if t['diagnosis'] else "-"))
            self.treatment_table.setItem(i, 4, QtWidgets.QTableWidgetItem(t['medicine_name']))
            self.treatment_table.setItem(i, 5, QtWidgets.QTableWidgetItem(t['status'] or "در حال درمان"))

    def save_prescription(self):
        """ذخیره نسخه دامپزشک"""
        cycle_id = self.health_cycle_combo.currentData()
        if not cycle_id:
            QtWidgets.QMessageBox.warning(self, "خطا", "لطفاً یک دوره پرورش را انتخاب کنید")
            return
        
        if not self.vet_name.text().strip():
            QtWidgets.QMessageBox.warning(self, "خطا", "لطفاً نام دامپزشک را وارد کنید")
            return
        
        result = self.db.execute_query("""
            INSERT INTO veterinary_prescriptions 
            (cycle_id, prescription_date, veterinarian_name, diagnosis, notes, duration_days)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (
            cycle_id,
            self.prescription_date.get_jalali_date(),
            self.vet_name.text().strip(),
            self.diagnosis.toPlainText(),
            self.prescription_notes.toPlainText(),
            self.duration.value()
        ))
        
        if result:
            QtWidgets.QMessageBox.information(self, "موفق", "نسخه دامپزشک با موفقیت ثبت شد")
            self.vet_name.clear()
            self.diagnosis.clear()
            self.prescription_notes.clear()
            self.load_prescriptions()
        else:
            QtWidgets.QMessageBox.warning(self, "خطا", "خطا در ثبت نسخه")

    def add_medicine(self):
        """افزودن داروی جدید"""
        if not self.medicine_name.text().strip():
            QtWidgets.QMessageBox.warning(self, "خطا", "لطفاً نام دارو را وارد کنید")
            return
        
        result = self.db.execute_query("""
            INSERT INTO medicines (name, category, stock_quantity, unit, expiry_date)
            VALUES (%s, %s, %s, %s, %s)
        """, (
            self.medicine_name.text().strip(),
            self.medicine_category.currentText(),
            self.medicine_stock.value(),
            self.medicine_unit.currentText(),
            self.expiry_date.get_jalali_date()
        ))
        
        if result:
            QtWidgets.QMessageBox.information(self, "موفق", "دارو با موفقیت اضافه شد")
            self.medicine_name.clear()
            self.medicine_stock.setValue(0)
            self.load_medicines()
        else:
            QtWidgets.QMessageBox.warning(self, "خطا", "خطا در افزودن دارو")