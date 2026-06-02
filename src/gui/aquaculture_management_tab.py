"""
صفحه مدیریت آبزی‌پروری - شامل هچری، نرسری و پرورش در دریا
"""

import json
import os
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
from src.core.models import DailyFeed, DailyMortality, WaterParameter, Biomass, ProductionCycle, HarvestRecord


class AquacultureManagementTab(QtWidgets.QWidget):
    def __init__(self, parent=None, farm=None, mooring=None):
        super().__init__(parent)
        self.current_farm = farm
        self.current_mooring = mooring
        self.feeds = []
        self.mortalities = []
        self.water_parameters = []
        self.biomasses = []
        self.production_cycles = []
        self.harvest_records = []
        self.data_file = "aquaculture_data.json"
        self.load_all_data()
        self.setup_ui()
        
        if self.current_farm and self.current_mooring:
            self.load_current_data()
    
    def set_farm_and_mooring(self, farm, mooring):
        self.current_farm = farm
        self.current_mooring = mooring
        self.load_current_data()
        if hasattr(self, 'growth_dashboard'):
            self.growth_dashboard.set_farm_and_mooring(farm, mooring)
            self.growth_dashboard.load_data()
            self.growth_dashboard.update_all_charts()
    
    def load_all_data(self):
        self.all_feeds = []
        self.all_mortalities = []
        self.all_water_parameters = []
        self.all_biomasses = []
        self.all_cycles = []
        self.all_harvests = []
        
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.all_feeds = data.get('feeds', [])
                    self.all_mortalities = data.get('mortalities', [])
                    self.all_water_parameters = data.get('water_parameters', [])
                    self.all_biomasses = data.get('biomasses', [])
                    self.all_cycles = data.get('production_cycles', [])
                    self.all_harvests = data.get('harvest_records', [])
            except Exception as e:
                print(f"خطا در بارگذاری: {e}")
    
    def save_all_data(self):
        try:
            data = {
                'feeds': self.all_feeds,
                'mortalities': self.all_mortalities,
                'water_parameters': self.all_water_parameters,
                'biomasses': self.all_biomasses,
                'production_cycles': self.all_cycles,
                'harvest_records': self.all_harvests
            }
            with open(self.data_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"خطا در ذخیره: {e}")
    
    def get_key(self):
        if not self.current_farm or not self.current_mooring:
            return None
        return f"{self.current_farm.id}_{self.current_mooring.id}"
    
    def load_current_data(self):
        key = self.get_key()
        if not key:
            return
        
        # بارگذاری تغذیه
        self.feeds = []
        for item in self.all_feeds:
            if item.get('key') == key:
                for f in item.get('feeds', []):
                    feed = DailyFeed()
                    feed.farm_id = f.get('farm_id', '')
                    feed.mooring_id = f.get('mooring_id', '')
                    feed.cage_id = f.get('cage_id', '')
                    feed.date = f.get('date', '')
                    feed.feed_type = f.get('feed_type', '')
                    feed.feed_amount = f.get('feed_amount', 0.0)
                    feed.feed_time = f.get('feed_time', '')
                    feed.fcr = f.get('fcr', 0.0)
                    feed.note = f.get('note', '')
                    self.feeds.append(feed)
                break
        
        # بارگذاری تلفات
        self.mortalities = []
        for item in self.all_mortalities:
            if item.get('key') == key:
                for m in item.get('mortalities', []):
                    mortality = DailyMortality()
                    mortality.farm_id = m.get('farm_id', '')
                    mortality.mooring_id = m.get('mooring_id', '')
                    mortality.cage_id = m.get('cage_id', '')
                    mortality.date = m.get('date', '')
                    mortality.count = m.get('count', 0)
                    mortality.cause = m.get('cause', '')
                    mortality.note = m.get('note', '')
                    self.mortalities.append(mortality)
                break
        
        # بارگذاری پارامترهای آب
        self.water_parameters = []
        for item in self.all_water_parameters:
            if item.get('key') == key:
                for p in item.get('parameters', []):
                    param = WaterParameter()
                    param.farm_id = p.get('farm_id', '')
                    param.mooring_id = p.get('mooring_id', '')
                    param.cage_id = p.get('cage_id', '')
                    param.date = p.get('date', '')
                    param.time = p.get('time', '')
                    param.temperature = p.get('temperature', 0.0)
                    param.dissolved_oxygen = p.get('dissolved_oxygen', 0.0)
                    param.salinity = p.get('salinity', 0.0)
                    param.ph = p.get('ph', 0.0)
                    param.note = p.get('note', '')
                    self.water_parameters.append(param)
                break
        
        # بارگذاری زیست‌توده
        self.biomasses = []
        for item in self.all_biomasses:
            if item.get('key') == key:
                for b in item.get('biomasses', []):
                    biomass = Biomass()
                    biomass.farm_id = b.get('farm_id', '')
                    biomass.mooring_id = b.get('mooring_id', '')
                    biomass.cage_id = b.get('cage_id', '')
                    biomass.date = b.get('date', '')
                    biomass.estimated_weight = b.get('estimated_weight', 0.0)
                    biomass.estimated_count = b.get('estimated_count', 0)
                    biomass.sample_size = b.get('sample_size', 0)
                    biomass.initial_count = b.get('initial_count', 0)
                    biomass.note = b.get('note', '')
                    self.biomasses.append(biomass)
                break
        
        # بارگذاری دوره‌های پرورش
        self.production_cycles = []
        for item in self.all_cycles:
            if item.get('key') == key:
                for c in item.get('cycles', []):
                    cycle = ProductionCycle()
                    cycle.id = c.get('id', '')
                    cycle.farm_id = c.get('farm_id', '')
                    cycle.mooring_id = c.get('mooring_id', '')
                    cycle.cage_id = c.get('cage_id', '')
                    cycle.start_date = c.get('start_date', '')
                    cycle.species = c.get('species', '')
                    cycle.initial_count = c.get('initial_count', 0)
                    cycle.initial_weight = c.get('initial_weight', 0.0)
                    cycle.target_weight = c.get('target_weight', 0.0)
                    cycle.total_harvested_count = c.get('total_harvested_count', 0)
                    cycle.total_harvested_kg = c.get('total_harvested_kg', 0.0)
                    cycle.remaining_count = c.get('remaining_count', 0)
                    cycle.is_active = c.get('is_active', True)
                    cycle.is_completed = c.get('is_completed', False)
                    cycle.note = c.get('note', '')
                    self.production_cycles.append(cycle)
                break
        
        # بارگذاری برداشت‌ها
        self.harvest_records = []
        for item in self.all_harvests:
            if item.get('key') == key:
                for h in item.get('harvests', []):
                    harvest = HarvestRecord()
                    harvest.id = h.get('id', '')
                    harvest.farm_id = h.get('farm_id', '')
                    harvest.mooring_id = h.get('mooring_id', '')
                    harvest.cage_id = h.get('cage_id', '')
                    harvest.cycle_id = h.get('cycle_id', '')
                    harvest.harvest_date = h.get('harvest_date', '')
                    harvest.harvest_count = h.get('harvest_count', 0)
                    harvest.average_weight = h.get('average_weight', 0.0)
                    harvest.total_weight_kg = h.get('total_weight_kg', 0.0)
                    harvest.customer = h.get('customer', '')
                    harvest.price_per_kg = h.get('price_per_kg', 0.0)
                    harvest.total_amount = h.get('total_amount', 0.0)
                    harvest.is_final = h.get('is_final', False)
                    harvest.note = h.get('note', '')
                    self.harvest_records.append(harvest)
                break
        
        self.update_feed_table()
        self.update_mortality_table()
        self.update_water_table()
        self.update_biomass_table()
        self.update_harvest_table()
        self.update_cycle_display()
        self.update_cage_list()
        
        if hasattr(self, 'growth_dashboard'):
            self.growth_dashboard.load_data()
            self.growth_dashboard.update_all_charts()
    
    def save_current_data(self):
        key = self.get_key()
        if not key:
            return
        
        # ذخیره تغذیه
        feeds_data = []
        for feed in self.feeds:
            feeds_data.append({
                'farm_id': feed.farm_id, 'mooring_id': feed.mooring_id,
                'cage_id': feed.cage_id, 'date': feed.date,
                'feed_type': feed.feed_type, 'feed_amount': feed.feed_amount,
                'feed_time': feed.feed_time, 'fcr': feed.fcr, 'note': feed.note
            })
        
        found = False
        for i, item in enumerate(self.all_feeds):
            if item.get('key') == key:
                self.all_feeds[i]['feeds'] = feeds_data
                found = True
                break
        if not found:
            self.all_feeds.append({'key': key, 'feeds': feeds_data})
        
        # ذخیره تلفات
        mortalities_data = []
        for mortality in self.mortalities:
            mortalities_data.append({
                'farm_id': mortality.farm_id, 'mooring_id': mortality.mooring_id,
                'cage_id': mortality.cage_id, 'date': mortality.date,
                'count': mortality.count, 'cause': mortality.cause, 'note': mortality.note
            })
        
        found = False
        for i, item in enumerate(self.all_mortalities):
            if item.get('key') == key:
                self.all_mortalities[i]['mortalities'] = mortalities_data
                found = True
                break
        if not found:
            self.all_mortalities.append({'key': key, 'mortalities': mortalities_data})
        
        # ذخیره پارامترهای آب
        water_data = []
        for param in self.water_parameters:
            water_data.append({
                'farm_id': param.farm_id, 'mooring_id': param.mooring_id,
                'cage_id': param.cage_id, 'date': param.date, 'time': param.time,
                'temperature': param.temperature, 'dissolved_oxygen': param.dissolved_oxygen,
                'salinity': param.salinity, 'ph': param.ph, 'note': param.note
            })
        
        found = False
        for i, item in enumerate(self.all_water_parameters):
            if item.get('key') == key:
                self.all_water_parameters[i]['parameters'] = water_data
                found = True
                break
        if not found:
            self.all_water_parameters.append({'key': key, 'parameters': water_data})
        
        # ذخیره زیست‌توده
        biomass_data = []
        for biomass in self.biomasses:
            biomass_data.append({
                'farm_id': biomass.farm_id, 'mooring_id': biomass.mooring_id,
                'cage_id': biomass.cage_id, 'date': biomass.date,
                'estimated_weight': biomass.estimated_weight,
                'estimated_count': biomass.estimated_count,
                'sample_size': biomass.sample_size,
                'initial_count': biomass.initial_count,
                'note': biomass.note
            })
        
        found = False
        for i, item in enumerate(self.all_biomasses):
            if item.get('key') == key:
                self.all_biomasses[i]['biomasses'] = biomass_data
                found = True
                break
        if not found:
            self.all_biomasses.append({'key': key, 'biomasses': biomass_data})
        
        # ذخیره دوره‌های پرورش
        cycles_data = []
        for cycle in self.production_cycles:
            cycles_data.append({
                'id': cycle.id, 'farm_id': cycle.farm_id, 'mooring_id': cycle.mooring_id,
                'cage_id': cycle.cage_id, 'start_date': cycle.start_date,
                'species': cycle.species, 'initial_count': cycle.initial_count,
                'initial_weight': cycle.initial_weight, 'target_weight': cycle.target_weight,
                'total_harvested_count': cycle.total_harvested_count,
                'total_harvested_kg': cycle.total_harvested_kg,
                'remaining_count': cycle.remaining_count,
                'is_active': cycle.is_active, 'is_completed': cycle.is_completed,
                'note': cycle.note
            })
        
        found = False
        for i, item in enumerate(self.all_cycles):
            if item.get('key') == key:
                self.all_cycles[i]['cycles'] = cycles_data
                found = True
                break
        if not found:
            self.all_cycles.append({'key': key, 'cycles': cycles_data})
        
        # ذخیره برداشت‌ها
        harvests_data = []
        for harvest in self.harvest_records:
            harvests_data.append({
                'id': harvest.id, 'farm_id': harvest.farm_id, 'mooring_id': harvest.mooring_id,
                'cage_id': harvest.cage_id, 'cycle_id': harvest.cycle_id,
                'harvest_date': harvest.harvest_date, 'harvest_count': harvest.harvest_count,
                'average_weight': harvest.average_weight, 'total_weight_kg': harvest.total_weight_kg,
                'customer': harvest.customer, 'price_per_kg': harvest.price_per_kg,
                'total_amount': harvest.total_amount, 'is_final': harvest.is_final,
                'note': harvest.note
            })
        
        found = False
        for i, item in enumerate(self.all_harvests):
            if item.get('key') == key:
                self.all_harvests[i]['harvests'] = harvests_data
                found = True
                break
        if not found:
            self.all_harvests.append({'key': key, 'harvests': harvests_data})
        
        self.save_all_data()
    
    # ==================== مدیریت قفس و دوره پرورش ====================
    
    def update_cage_list(self):
        """پر کردن لیست قفس‌ها در کامبوباکس"""
        self.cage_combo.clear()
        if self.current_mooring and hasattr(self.current_mooring, 'cages'):
            for cage in self.current_mooring.cages:
                self.cage_combo.addItem(cage.id, cage.id)
            if self.cage_combo.count() > 0:
                self.cage_combo.setCurrentIndex(0)
                self.on_cage_changed()
    
    def on_cage_changed(self):
        """تغییر قفس"""
        self.update_cycle_display()
        if hasattr(self, 'growth_dashboard'):
            self.growth_dashboard.update_all_charts()
    
    def get_active_cycle(self, cage_id):
        """دریافت دوره فعال برای قفس مشخص"""
        for cycle in self.production_cycles:
            if cycle.cage_id == cage_id and cycle.is_active and not cycle.is_completed:
                return cycle
        return None
    
    def update_cycle_display(self):
        """به‌روزرسانی نمایش اطلاعات دوره فعال"""
        cage_id = self.cage_combo.currentData() if self.cage_combo.count() > 0 else None
        
        if cage_id:
            active_cycle = self.get_active_cycle(cage_id)
            if active_cycle:
                text = (f"📋 دوره فعال: {active_cycle.start_date} | "
                       f"گونه: {active_cycle.species} | "
                       f"تعداد اولیه: {active_cycle.initial_count:,} | "
                       f"تعداد باقیمانده: {active_cycle.remaining_count:,} | "
                       f"برداشت شده: {active_cycle.total_harvested_kg:,.0f} kg")
                self.cycle_info_label.setText(text)
                self.cycle_info_label.setStyleSheet("color: #4EC9B0; font-size: 12px; padding: 5px; background-color: #252526; border-radius: 4px;")
            else:
                self.cycle_info_label.setText("📋 هیچ دوره فعالی برای این قفس وجود ندارد")
                self.cycle_info_label.setStyleSheet("color: #F48771; font-size: 12px; padding: 5px; background-color: #252526; border-radius: 4px;")
        else:
            self.cycle_info_label.setText("📋 لطفاً یک قفس انتخاب کنید")
    
    def start_production_cycle(self):
        """شروع دوره پرورش برای قفس انتخاب شده"""
        if not self.current_farm or not self.current_mooring:
            QtWidgets.QMessageBox.warning(self, "خطا", "لطفاً ابتدا مزرعه و مورینگ را انتخاب کنید")
            return
        
        cage_id = self.cage_combo.currentData() if self.cage_combo.count() > 0 else None
        
        if not cage_id:
            QtWidgets.QMessageBox.warning(self, "خطا", "لطفاً یک قفس را انتخاب کنید")
            return
        
        if self.get_active_cycle(cage_id):
            QtWidgets.QMessageBox.warning(self, "خطا", "این قفس در حال حاضر یک دوره فعال دارد")
            return
        
        dialog = CycleDialog(self, mode="start")
        if dialog.exec_():
            result = dialog.result_data
            cycle = ProductionCycle()
            cycle.id = f"cycle_{len(self.production_cycles) + 1}_{cage_id}"
            cycle.farm_id = self.current_farm.id
            cycle.mooring_id = self.current_mooring.id
            cycle.cage_id = cage_id
            cycle.start_date = result.get("date")
            cycle.species = result.get("species")
            cycle.initial_count = result.get("initial_count")
            cycle.initial_weight = result.get("initial_weight")
            cycle.target_weight = result.get("target_weight")
            cycle.remaining_count = result.get("initial_count")
            cycle.is_active = True
            cycle.is_completed = False
            cycle.note = result.get("note")
            
            self.production_cycles.append(cycle)
            self.save_current_data()
            self.update_cycle_display()
            QtWidgets.QMessageBox.information(self, "موفق", f"دوره پرورش با موفقیت شروع شد\nتعداد اولیه: {cycle.initial_count:,} عدد")
    
    def add_harvest(self):
        """ثبت برداشت مرحله‌ای"""
        if not self.current_farm or not self.current_mooring:
            QtWidgets.QMessageBox.warning(self, "خطا", "لطفاً ابتدا مزرعه و مورینگ را انتخاب کنید")
            return
        
        cage_id = self.cage_combo.currentData() if self.cage_combo.count() > 0 else None
        
        if not cage_id:
            QtWidgets.QMessageBox.warning(self, "خطا", "لطفاً یک قفس را انتخاب کنید")
            return
        
        active_cycle = self.get_active_cycle(cage_id)
        if not active_cycle:
            QtWidgets.QMessageBox.warning(self, "خطا", "هیچ دوره فعالی برای این قفس وجود ندارد. لطفاً ابتدا دوره پرورش را شروع کنید.")
            return
        
        dialog = HarvestDialog(self, current_farm=self.current_farm, current_mooring=self.current_mooring, cycle=active_cycle)
        if dialog.exec_():
            result = dialog.result_data
            harvest = HarvestRecord()
            harvest.id = f"harvest_{len(self.harvest_records) + 1}"
            harvest.farm_id = self.current_farm.id
            harvest.mooring_id = self.current_mooring.id
            harvest.cage_id = cage_id
            harvest.cycle_id = active_cycle.id
            harvest.harvest_date = result.get("harvest_date")
            harvest.harvest_count = result.get("harvest_count")
            harvest.average_weight = result.get("average_weight")
            harvest.total_weight_kg = result.get("total_weight_kg")
            harvest.customer = result.get("customer")
            harvest.price_per_kg = result.get("price_per_kg")
            harvest.total_amount = result.get("total_amount")
            harvest.is_final = result.get("is_final")
            harvest.note = result.get("note")
            
            self.harvest_records.append(harvest)
            
            active_cycle.total_harvested_count += harvest.harvest_count
            active_cycle.total_harvested_kg += harvest.total_weight_kg
            active_cycle.remaining_count = active_cycle.initial_count - active_cycle.total_harvested_count
            
            if harvest.is_final:
                active_cycle.is_completed = True
                active_cycle.is_active = False
            
            self.save_current_data()
            self.update_harvest_table()
            self.update_cycle_display()
            
            QtWidgets.QMessageBox.information(self, "موفق", 
                f"برداشت با موفقیت ثبت شد\n"
                f"تعداد: {harvest.harvest_count:,} عدد\n"
                f"کل مبلغ: {harvest.total_amount:,.0f} تومان")
    
    def update_harvest_table(self):
        """به‌روزرسانی جدول برداشت‌ها"""
        self.harvest_table.setRowCount(len(self.harvest_records))
        for i, h in enumerate(self.harvest_records):
            self.harvest_table.setItem(i, 0, QtWidgets.QTableWidgetItem(h.harvest_date))
            self.harvest_table.setItem(i, 1, QtWidgets.QTableWidgetItem(str(h.harvest_count)))
            self.harvest_table.setItem(i, 2, QtWidgets.QTableWidgetItem(f"{h.average_weight:.0f}"))
            self.harvest_table.setItem(i, 3, QtWidgets.QTableWidgetItem(f"{h.total_weight_kg:,.0f}"))
            self.harvest_table.setItem(i, 4, QtWidgets.QTableWidgetItem(h.customer))
            self.harvest_table.setItem(i, 5, QtWidgets.QTableWidgetItem(f"{h.price_per_kg:,.0f}"))
            self.harvest_table.setItem(i, 6, QtWidgets.QTableWidgetItem(f"{h.total_amount:,.0f}"))
            self.harvest_table.setItem(i, 7, QtWidgets.QTableWidgetItem(h.note))
    
    # ==================== عملیات زیست‌توده ====================
    
    def add_biomass(self):
        if not self.current_farm or not self.current_mooring:
            QtWidgets.QMessageBox.warning(self, "خطا", "لطفاً مزرعه و مورینگ را انتخاب کنید")
            return
        dialog = BiomassDialog(self, current_farm=self.current_farm, current_mooring=self.current_mooring, harvests=self.harvest_records)
        if dialog.exec_():
            dialog.biomass.farm_id = self.current_farm.id
            dialog.biomass.mooring_id = self.current_mooring.id
            self.biomasses.append(dialog.biomass)
            self.save_current_data()
            self.update_biomass_table()
            if hasattr(self, 'growth_dashboard'):
                self.growth_dashboard.load_data()
                self.growth_dashboard.update_all_charts()
            QtWidgets.QMessageBox.information(self, "موفق", "زیست‌توده ثبت شد")
    
    def edit_biomass(self, index):
        dialog = BiomassDialog(self, current_farm=self.current_farm, current_mooring=self.current_mooring, biomass=self.biomasses[index], harvests=self.harvest_records)
        if dialog.exec_():
            self.biomasses[index] = dialog.biomass
            self.save_current_data()
            self.update_biomass_table()
            if hasattr(self, 'growth_dashboard'):
                self.growth_dashboard.load_data()
                self.growth_dashboard.update_all_charts()
            QtWidgets.QMessageBox.information(self, "موفق", "زیست‌توده ویرایش شد")
    
    def delete_biomass(self, index):
        if QtWidgets.QMessageBox.question(self, "تأیید", "حذف شود؟") == QtWidgets.QMessageBox.Yes:
            self.biomasses.pop(index)
            self.save_current_data()
            self.update_biomass_table()
            if hasattr(self, 'growth_dashboard'):
                self.growth_dashboard.load_data()
                self.growth_dashboard.update_all_charts()
    
    def clear_all_biomasses(self):
        if QtWidgets.QMessageBox.question(self, "تأیید", "همه زیست‌توده حذف شوند؟") == QtWidgets.QMessageBox.Yes:
            self.biomasses.clear()
            self.save_current_data()
            self.update_biomass_table()
            if hasattr(self, 'growth_dashboard'):
                self.growth_dashboard.load_data()
                self.growth_dashboard.update_all_charts()
    
    def update_biomass_table(self):
        self.biomass_table.setRowCount(len(self.biomasses))
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
        
        for i, b in enumerate(self.biomasses):
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
        dialog = FeedDialog(self, current_farm=self.current_farm, current_mooring=self.current_mooring)
        if dialog.exec_():
            dialog.feed.farm_id = self.current_farm.id
            dialog.feed.mooring_id = self.current_mooring.id
            self.feeds.append(dialog.feed)
            self.save_current_data()
            self.update_feed_table()
            if hasattr(self, 'growth_dashboard'):
                self.growth_dashboard.load_data()
                self.growth_dashboard.update_all_charts()
    
    def edit_feed(self, index):
        dialog = FeedDialog(self, current_farm=self.current_farm, current_mooring=self.current_mooring, feed=self.feeds[index])
        if dialog.exec_():
            self.feeds[index] = dialog.feed
            self.save_current_data()
            self.update_feed_table()
            if hasattr(self, 'growth_dashboard'):
                self.growth_dashboard.load_data()
                self.growth_dashboard.update_all_charts()
    
    def delete_feed(self, index):
        if QtWidgets.QMessageBox.question(self, "تأیید", "حذف شود؟") == QtWidgets.QMessageBox.Yes:
            self.feeds.pop(index)
            self.save_current_data()
            self.update_feed_table()
            if hasattr(self, 'growth_dashboard'):
                self.growth_dashboard.load_data()
                self.growth_dashboard.update_all_charts()
    
    def clear_all_feeds(self):
        if QtWidgets.QMessageBox.question(self, "تأیید", "همه تغذیه‌ها حذف شوند؟") == QtWidgets.QMessageBox.Yes:
            self.feeds.clear()
            self.save_current_data()
            self.update_feed_table()
            if hasattr(self, 'growth_dashboard'):
                self.growth_dashboard.load_data()
                self.growth_dashboard.update_all_charts()
    
    def update_feed_table(self):
        self.feed_table.setRowCount(len(self.feeds))
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
        
        for i, feed in enumerate(self.feeds):
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
        dialog = MortalityDialog(self, current_farm=self.current_farm, current_mooring=self.current_mooring)
        if dialog.exec_():
            dialog.mortality.farm_id = self.current_farm.id
            dialog.mortality.mooring_id = self.current_mooring.id
            self.mortalities.append(dialog.mortality)
            self.save_current_data()
            self.update_mortality_table()
            if hasattr(self, 'growth_dashboard'):
                self.growth_dashboard.load_data()
                self.growth_dashboard.update_all_charts()
    
    def edit_mortality(self, index):
        dialog = MortalityDialog(self, current_farm=self.current_farm, current_mooring=self.current_mooring, mortality=self.mortalities[index])
        if dialog.exec_():
            self.mortalities[index] = dialog.mortality
            self.save_current_data()
            self.update_mortality_table()
            if hasattr(self, 'growth_dashboard'):
                self.growth_dashboard.load_data()
                self.growth_dashboard.update_all_charts()
    
    def delete_mortality(self, index):
        if QtWidgets.QMessageBox.question(self, "تأیید", "حذف شود؟") == QtWidgets.QMessageBox.Yes:
            self.mortalities.pop(index)
            self.save_current_data()
            self.update_mortality_table()
            if hasattr(self, 'growth_dashboard'):
                self.growth_dashboard.load_data()
                self.growth_dashboard.update_all_charts()
    
    def clear_all_mortalities(self):
        if QtWidgets.QMessageBox.question(self, "تأیید", "همه تلفات حذف شوند؟") == QtWidgets.QMessageBox.Yes:
            self.mortalities.clear()
            self.save_current_data()
            self.update_mortality_table()
            if hasattr(self, 'growth_dashboard'):
                self.growth_dashboard.load_data()
                self.growth_dashboard.update_all_charts()
    
    def update_mortality_table(self):
        self.mortality_table.setRowCount(len(self.mortalities))
        self.mortality_table.setColumnCount(6)
        self.mortality_table.setHorizontalHeaderLabels(["تاریخ", "قفس", "تعداد", "علت", "یادداشت", ""])
        self.mortality_table.setColumnWidth(0, 100)
        self.mortality_table.setColumnWidth(1, 100)
        self.mortality_table.setColumnWidth(2, 70)
        self.mortality_table.setColumnWidth(3, 130)
        self.mortality_table.setColumnWidth(5, 60)
        self.mortality_table.horizontalHeader().setStretchLastSection(False)
        self.mortality_table.horizontalHeader().setSectionResizeMode(4, QtWidgets.QHeaderView.Stretch)
        
        for i, m in enumerate(self.mortalities):
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
        dialog = WaterParameterDialog(self, current_farm=self.current_farm, current_mooring=self.current_mooring)
        if dialog.exec_():
            dialog.parameter.farm_id = self.current_farm.id
            dialog.parameter.mooring_id = self.current_mooring.id
            self.water_parameters.append(dialog.parameter)
            self.save_current_data()
            self.update_water_table()
            if hasattr(self, 'growth_dashboard'):
                self.growth_dashboard.load_data()
                self.growth_dashboard.update_all_charts()
    
    def edit_water_parameter(self, index):
        dialog = WaterParameterDialog(self, current_farm=self.current_farm, current_mooring=self.current_mooring, parameter=self.water_parameters[index])
        if dialog.exec_():
            self.water_parameters[index] = dialog.parameter
            self.save_current_data()
            self.update_water_table()
            if hasattr(self, 'growth_dashboard'):
                self.growth_dashboard.load_data()
                self.growth_dashboard.update_all_charts()
    
    def delete_water_parameter(self, index):
        if QtWidgets.QMessageBox.question(self, "تأیید", "حذف شود؟") == QtWidgets.QMessageBox.Yes:
            self.water_parameters.pop(index)
            self.save_current_data()
            self.update_water_table()
            if hasattr(self, 'growth_dashboard'):
                self.growth_dashboard.load_data()
                self.growth_dashboard.update_all_charts()
    
    def clear_all_water_parameters(self):
        if QtWidgets.QMessageBox.question(self, "تأیید", "همه پارامترها حذف شوند؟") == QtWidgets.QMessageBox.Yes:
            self.water_parameters.clear()
            self.save_current_data()
            self.update_water_table()
            if hasattr(self, 'growth_dashboard'):
                self.growth_dashboard.load_data()
                self.growth_dashboard.update_all_charts()
    
    def update_water_table(self):
        self.water_table.setRowCount(len(self.water_parameters))
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
        
        for i, p in enumerate(self.water_parameters):
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