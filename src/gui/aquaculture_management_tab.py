"""
صفحه مدیریت آبزی پروری - شامل هچری، نرسری و پرورش در دریا
نسخه دیتابیس - با ذخیره و بارگذاری صحیح دادهها
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
        """ویرایش دوره پرورش فعال"""
        if not self.current_cycle:
            QtWidgets.QMessageBox.warning(self, "خطا", "هیچ دوره فعالی برای ویرایش وجود ندارد")
            return
        
        can_edit, dependent_table = self.db.check_cycle_dependencies(self.current_cycle.id)
        
        if not can_edit:
            QtWidgets.QMessageBox.warning(
                self, 
                "خطا", 
                f"امکان ویرایش دوره وجود ندارد.\n\n"
                f"دوره دارای داده‌های {dependent_table} است.\n"
                f"لطفاً ابتدا داده‌های {dependent_table} را حذف کنید، سپس دوره را ویرایش نمایید."
            )
            return
        
        dialog = CycleDialog(self, mode="edit", current_cycle=self.current_cycle)
        if dialog.exec_():
            result = dialog.result_data
            success = self.db.update_production_cycle(
                self.current_cycle.id,
                result.get("date"),
                result.get("species"),
                result.get("initial_count"),
                result.get("initial_weight"),
                result.get("target_weight"),
                result.get("note")
            )
            if success:
                self.load_current_data()
                self.update_cycle_display()
                self.update_production_management_data()
                QtWidgets.QMessageBox.information(self, "موفق", "دوره پرورش ویرایش شد")
            else:
                QtWidgets.QMessageBox.warning(self, "خطا", "خطا در ویرایش دوره پرورش")

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

                QtWidgets.QMessageBox.information(self, "موفق", 
                    f"برداشت با موفقیت ثبت شد\n"
                    f"تعداد: {result.get('harvest_count'):,} عدد\n"
                    f"کل مبلغ: {result.get('total_amount'):,.0f} تومان")
            else:
                QtWidgets.QMessageBox.warning(self, "خطا", "خطا در ثبت برداشت")

    def edit_harvest(self, index):
        if not self.current_cycle:
            return
        current_cage = self.cage_combo.currentData() if self.cage_combo.count() > 0 else None
        if current_cage:
            filtered = [h for h in self.harvest_records if h.cage_id == current_cage]
        else:
            filtered = self.harvest_records
        if index >= len(filtered):
            return
        harvest = filtered[index]
        
        dialog = HarvestDialog(self, current_farm=self.current_farm, current_mooring=self.current_mooring, 
                              cycle=self.current_cycle, harvest={
                                  'harvest_date': harvest.harvest_date,
                                  'harvest_count': harvest.harvest_count,
                                  'average_weight': harvest.average_weight,
                                  'total_weight_kg': harvest.total_weight_kg,
                                  'customer': harvest.customer,
                                  'price_per_kg': harvest.price_per_kg,
                                  'total_amount': harvest.total_amount,
                                  'is_final': harvest.is_final,
                                  'note': harvest.note
                              })
        if dialog.exec_():
            if hasattr(harvest, 'id') and harvest.id:
                self.db.delete_harvest(harvest.id)
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
                QtWidgets.QMessageBox.information(self, "موفق", "برداشت ویرایش شد")
            else:
                QtWidgets.QMessageBox.warning(self, "خطا", "خطا در ویرایش برداشت")

    def delete_harvest(self, index):
        if QtWidgets.QMessageBox.question(self, "تأیید", "آیا از حذف این برداشت مطمئن هستید؟") == QtWidgets.QMessageBox.Yes:
            current_cage = self.cage_combo.currentData() if self.cage_combo.count() > 0 else None
            if current_cage:
                filtered = [h for h in self.harvest_records if h.cage_id == current_cage]
                if index < len(filtered):
                    to_delete = filtered[index]
                    if hasattr(to_delete, 'id') and to_delete.id:
                        self.db.delete_harvest(to_delete.id)
                    for i, h in enumerate(self.harvest_records):
                        if h.id == to_delete.id and h.harvest_date == to_delete.harvest_date:
                            self.harvest_records.pop(i)
                            break
            
            self.update_harvest_table()
            self.update_cycle_display()
            self.update_production_management_data()
            if hasattr(self, 'growth_dashboard'):
                self.growth_dashboard.load_data()
                self.growth_dashboard.update_all_charts()

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
            filtered = [b for b in self.biomasses if b.cage_id == current_cage]
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
        if QtWidgets.QMessageBox.question(self, "تأیید", "آیا از حذف این زیست توده مطمئن هستید؟") == QtWidgets.QMessageBox.Yes:
            current_cage = self.cage_combo.currentData() if self.cage_combo.count() > 0 else None
            if current_cage:
                filtered = [b for b in self.biomasses if b.cage_id == current_cage]
                if index < len(filtered):
                    to_delete = filtered[index]
                    if hasattr(to_delete, 'id') and to_delete.id:
                        self.db.delete_biomass(to_delete.id)
                    for i, b in enumerate(self.biomasses):
                        if b.id == to_delete.id and b.date == to_delete.date:
                            self.biomasses.pop(i)
                            break
            
            self.update_biomass_table()
            self.update_production_management_data()
            if hasattr(self, 'growth_dashboard'):
                self.growth_dashboard.load_data()
                self.growth_dashboard.update_all_charts()

    def clear_all_biomasses(self):
        if QtWidgets.QMessageBox.question(self, "تأیید", "آیا از حذف همه زیست توده‌ها مطمئن هستید؟") == QtWidgets.QMessageBox.Yes:
            current_cage = self.cage_combo.currentData() if self.cage_combo.count() > 0 else None
            if current_cage:
                for b in self.biomasses:
                    if b.cage_id == current_cage and hasattr(b, 'id') and b.id:
                        self.db.delete_biomass(b.id)
                self.biomasses = [b for b in self.biomasses if b.cage_id != current_cage]
            
            self.update_biomass_table()
            self.update_production_management_data()
            if hasattr(self, 'growth_dashboard'):
                self.growth_dashboard.load_data()
                self.growth_dashboard.update_all_charts()

    def update_biomass_table(self):
        current_cage = self.cage_combo.currentData() if self.cage_combo.count() > 0 else None
        
        if current_cage:
            filtered_biomasses = [b for b in self.biomasses if b.cage_id == current_cage]
        else:
            filtered_biomasses = self.biomasses

        self.biomass_table.setRowCount(len(filtered_biomasses))
        self.biomass_table.setColumnCount(7)
        self.biomass_table.setHorizontalHeaderLabels(["تاریخ", "قفس", "وزن (گرم)", "تعداد تخمینی", "تعداد نمونه", "یادداشت", ""])
        self.biomass_table.setColumnWidth(0, 100)
        self.biomass_table.setColumnWidth(1, 80)
        self.biomass_table.setColumnWidth(2, 100)
        self.biomass_table.setColumnWidth(3, 120)
        self.biomass_table.setColumnWidth(4, 100)
        self.biomass_table.setColumnWidth(6, 70)
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
        """ویرایش تغذیه"""
        if not self.current_cycle:
            return
        current_cage = self.cage_combo.currentData() if self.cage_combo.count() > 0 else None
        if current_cage:
            filtered = [f for f in self.feeds if f.cage_id == current_cage]
        else:
            filtered = self.feeds
        if index >= len(filtered):
            return
        feed = filtered[index]
        
        dialog = FeedDialog(self, current_farm=self.current_farm, current_mooring=self.current_mooring, feed=feed)
        if dialog.exec_():
            # حذف رکورد قدیمی
            if hasattr(feed, 'id') and feed.id:
                self.db.execute_query("DELETE FROM feeds WHERE id = %s", (feed.id,))
            # ذخیره رکورد جدید
            result = self.db.save_feed(
                self.current_cycle.cage_id,
                self.current_cycle.id,
                dialog.feed.date,
                dialog.feed.feed_type,
                dialog.feed.feed_amount,
                dialog.feed.feed_time,
                dialog.feed.note
            )
            if result:
                self.load_current_data()
                self.update_feed_table()
                self.update_production_management_data()
                if hasattr(self, 'growth_dashboard'):
                    self.growth_dashboard.load_data()
                    self.growth_dashboard.update_all_charts()
                QtWidgets.QMessageBox.information(self, "موفق", "تغذیه ویرایش شد")
            else:
                QtWidgets.QMessageBox.warning(self, "خطا", "خطا در ویرایش تغذیه")

    def delete_feed(self, index):
        if QtWidgets.QMessageBox.question(self, "تأیید", "حذف شود؟") == QtWidgets.QMessageBox.Yes:
            self.feeds.pop(index)
            self.update_feed_table()
            self.update_production_management_data()
            if hasattr(self, 'growth_dashboard'):
                self.growth_dashboard.load_data()
                self.growth_dashboard.update_all_charts()

    def clear_all_feeds(self):
        if QtWidgets.QMessageBox.question(self, "تأیید", "همه تغذیهها حذف شوند؟") == QtWidgets.QMessageBox.Yes:
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
        """ویرایش تلفات"""
        if not self.current_cycle:
            return
        current_cage = self.cage_combo.currentData() if self.cage_combo.count() > 0 else None
        if current_cage:
            filtered = [m for m in self.mortalities if m.cage_id == current_cage]
        else:
            filtered = self.mortalities
        if index >= len(filtered):
            return
        mortality = filtered[index]
        
        dialog = MortalityDialog(self, current_farm=self.current_farm, current_mooring=self.current_mooring, mortality=mortality)
        if dialog.exec_():
            # حذف رکورد قدیمی
            if hasattr(mortality, 'id') and mortality.id:
                self.db.execute_query("DELETE FROM mortalities WHERE id = %s", (mortality.id,))
            # ذخیره رکورد جدید
            result = self.db.save_mortality(
                self.current_cycle.cage_id,
                self.current_cycle.id,
                dialog.mortality.date,
                dialog.mortality.count,
                dialog.mortality.cause,
                dialog.mortality.note
            )
            if result:
                self.load_current_data()
                self.update_mortality_table()
                self.update_production_management_data()
                if hasattr(self, 'growth_dashboard'):
                    self.growth_dashboard.load_data()
                    self.growth_dashboard.update_all_charts()
                QtWidgets.QMessageBox.information(self, "موفق", "تلفات ویرایش شد")
            else:
                QtWidgets.QMessageBox.warning(self, "خطا", "خطا در ویرایش تلفات")

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
        """ویرایش پارامتر آب"""
        if not self.current_cycle:
            return
        current_cage = self.cage_combo.currentData() if self.cage_combo.count() > 0 else None
        if current_cage:
            filtered = [w for w in self.water_parameters if w.cage_id == current_cage]
        else:
            filtered = self.water_parameters
        if index >= len(filtered):
            return
        param = filtered[index]
        
        dialog = WaterParameterDialog(self, current_farm=self.current_farm, current_mooring=self.current_mooring, parameter=param)
        if dialog.exec_():
            # حذف رکورد قدیمی
            if hasattr(param, 'id') and param.id:
                self.db.execute_query("DELETE FROM water_parameters WHERE id = %s", (param.id,))
            # ذخیره رکورد جدید
            result = self.db.save_water_parameter(
                self.current_cycle.cage_id,
                self.current_cycle.id,
                dialog.parameter.date,
                dialog.parameter.time,
                dialog.parameter.temperature,
                dialog.parameter.dissolved_oxygen,
                dialog.parameter.salinity,
                dialog.parameter.ph,
                dialog.parameter.note
            )
            if result:
                self.load_current_data()
                self.update_water_table()
                self.update_production_management_data()
                if hasattr(self, 'growth_dashboard'):
                    self.growth_dashboard.load_data()
                    self.growth_dashboard.update_all_charts()
                QtWidgets.QMessageBox.information(self, "موفق", "پارامتر آب ویرایش شد")
            else:
                QtWidgets.QMessageBox.warning(self, "خطا", "خطا در ویرایش پارامتر آب")

    def delete_water_parameter(self, index):
        if QtWidgets.QMessageBox.question(self, "تأیید", "آیا از حذف این پارامتر آب مطمئن هستید؟") == QtWidgets.QMessageBox.Yes:
            current_cage = self.cage_combo.currentData() if self.cage_combo.count() > 0 else None
            if current_cage:
                filtered = [w for w in self.water_parameters if w.cage_id == current_cage]
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
            current_cage = self.cage_combo.currentData() if self.cage_combo.count() > 0 else None
            if current_cage:
                for w in self.water_parameters:
                    if w.cage_id == current_cage and hasattr(w, 'id') and w.id:
                        if hasattr(self.db, 'delete_water_parameter'):
                            self.db.delete_water_parameter(w.id)
                self.water_parameters = [w for w in self.water_parameters if w.cage_id != current_cage]
            
            self.update_water_table()
            self.update_production_management_data()
            if hasattr(self, 'growth_dashboard'):
                self.growth_dashboard.load_data()
                self.growth_dashboard.update_all_charts()

    def update_water_table(self):
        current_cage = self.cage_combo.currentData() if self.cage_combo.count() > 0 else None
        
        if current_cage:
            filtered_water = [w for w in self.water_parameters if w.cage_id == current_cage]
        else:
            filtered_water = self.water_parameters

        self.water_table.setRowCount(len(filtered_water))
        self.water_table.setColumnCount(9)
        self.water_table.setHorizontalHeaderLabels(["تاریخ", "قفس", "زمان", "دما", "اکسیژن", "شوری", "pH", "یادداشت", ""])
        self.water_table.setColumnWidth(0, 100)
        self.water_table.setColumnWidth(1, 80)
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
        filtered_harvests = [h for h in self.harvest_records if h.cage_id == current_cage] if current_cage else self.harvest_records

        self.harvest_table.setRowCount(len(filtered_harvests))
        self.harvest_table.setColumnCount(9)
        self.harvest_table.setHorizontalHeaderLabels(["تاریخ", "تعداد", "وزن متوسط", "کل وزن(kg)", "مشتری", "قیمت(kg)", "کل مبلغ", "یادداشت", ""])
        self.harvest_table.setColumnWidth(0, 100)
        self.harvest_table.setColumnWidth(1, 80)
        self.harvest_table.setColumnWidth(2, 100)
        self.harvest_table.setColumnWidth(3, 100)
        self.harvest_table.setColumnWidth(4, 100)
        self.harvest_table.setColumnWidth(5, 100)
        self.harvest_table.setColumnWidth(6, 120)
        self.harvest_table.setColumnWidth(7, 150)
        self.harvest_table.setColumnWidth(8, 70)

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
        self.clear_biomass_btn = QtWidgets.QPushButton("🗑️ حذف همه زیست توده‌ها")
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
        self.clear_feed_btn = QtWidgets.QPushButton("🗑️ حذف همه تغذیه‌ها")
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
        self.clear_mortality_btn = QtWidgets.QPushButton("🗑️ حذف همه تلفات‌ها")
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
        self.inner_tabs.addTab(self.production_management_tab, "📊 شاخص‌های پرورش")

        dashboard_tab = QtWidgets.QWidget()
        dashboard_layout = QtWidgets.QVBoxLayout(dashboard_tab)
        self.growth_dashboard = GrowthDashboard(self, self.current_farm, self.current_mooring)
        dashboard_layout.addWidget(self.growth_dashboard)
        self.inner_tabs.addTab(dashboard_tab, "📊 داشبورد تحلیل پرورش")

        layout.addWidget(self.inner_tabs)

        self.update_cage_list()

        return tab