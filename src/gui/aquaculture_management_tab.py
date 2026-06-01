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
from src.core.models import DailyFeed, DailyMortality, WaterParameter


class AquacultureManagementTab(QtWidgets.QWidget):
    def __init__(self, parent=None, farm=None, mooring=None):
        super().__init__(parent)
        self.current_farm = farm
        self.current_mooring = mooring
        self.feeds = []
        self.mortalities = []
        self.water_parameters = []
        self.data_file = "aquaculture_data.json"
        self.load_all_data()
        self.setup_ui()
    
    def set_farm_and_mooring(self, farm, mooring):
        self.current_farm = farm
        self.current_mooring = mooring
        self.load_current_feeds()
        self.load_current_mortalities()
        self.load_current_water_parameters()
        self.update_feed_table()
        self.update_mortality_table()
        self.update_water_table()
    
    # ==================== توابع ذخیره و بارگذاری ====================
    
    def load_all_data(self):
        self.all_feeds = []
        self.all_mortalities = []
        self.all_water_parameters = []
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.all_feeds = data.get('feeds', [])
                    self.all_mortalities = data.get('mortalities', [])
                    self.all_water_parameters = data.get('water_parameters', [])
            except Exception as e:
                print(f"خطا در بارگذاری داده‌ها: {e}")
                self.all_feeds = []
                self.all_mortalities = []
                self.all_water_parameters = []
    
    def save_all_data(self):
        try:
            data = {
                'feeds': self.all_feeds,
                'mortalities': self.all_mortalities,
                'water_parameters': self.all_water_parameters
            }
            with open(self.data_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"خطا در ذخیره داده‌ها: {e}")
    
    def get_mooring_key(self):
        if not self.current_farm or not self.current_mooring:
            return None
        return f"{self.current_farm.id}_{self.current_mooring.id}"
    
    # ==================== تغذیه (Feed) ====================
    
    def load_current_feeds(self):
        self.feeds = []
        key = self.get_mooring_key()
        if not key:
            return
        
        for item in self.all_feeds:
            if item.get('key') == key:
                for feed_data in item.get('feeds', []):
                    feed = DailyFeed()
                    feed.farm_id = feed_data.get('farm_id', '')
                    feed.mooring_id = feed_data.get('mooring_id', '')
                    feed.cage_id = feed_data.get('cage_id', '')
                    feed.date = feed_data.get('date', '')
                    feed.feed_type = feed_data.get('feed_type', '')
                    feed.feed_amount = feed_data.get('feed_amount', 0.0)
                    feed.feed_time = feed_data.get('feed_time', '')
                    feed.fcr = feed_data.get('fcr', 0.0)
                    feed.note = feed_data.get('note', '')
                    self.feeds.append(feed)
                break
    
    def save_current_feeds(self):
        key = self.get_mooring_key()
        if not key:
            return
        
        feeds_data = []
        for feed in self.feeds:
            feeds_data.append({
                'farm_id': feed.farm_id,
                'mooring_id': feed.mooring_id,
                'cage_id': feed.cage_id,
                'date': feed.date,
                'feed_type': feed.feed_type,
                'feed_amount': feed.feed_amount,
                'feed_time': feed.feed_time,
                'fcr': feed.fcr,
                'note': feed.note
            })
        
        found = False
        for i, item in enumerate(self.all_feeds):
            if item.get('key') == key:
                self.all_feeds[i]['feeds'] = feeds_data
                found = True
                break
        
        if not found:
            self.all_feeds.append({
                'key': key,
                'farm_id': self.current_farm.id if self.current_farm else '',
                'mooring_id': self.current_mooring.id if self.current_mooring else '',
                'feeds': feeds_data
            })
        
        self.save_all_data()
    
    # ==================== تلفات (Mortality) ====================
    
    def load_current_mortalities(self):
        self.mortalities = []
        key = self.get_mooring_key()
        if not key:
            return
        
        for item in self.all_mortalities:
            if item.get('key') == key:
                for mortality_data in item.get('mortalities', []):
                    mortality = DailyMortality()
                    mortality.farm_id = mortality_data.get('farm_id', '')
                    mortality.mooring_id = mortality_data.get('mooring_id', '')
                    mortality.cage_id = mortality_data.get('cage_id', '')
                    mortality.date = mortality_data.get('date', '')
                    mortality.count = mortality_data.get('count', 0)
                    mortality.cause = mortality_data.get('cause', '')
                    mortality.note = mortality_data.get('note', '')
                    self.mortalities.append(mortality)
                break
    
    def save_current_mortalities(self):
        key = self.get_mooring_key()
        if not key:
            return
        
        mortalities_data = []
        for mortality in self.mortalities:
            mortalities_data.append({
                'farm_id': mortality.farm_id,
                'mooring_id': mortality.mooring_id,
                'cage_id': mortality.cage_id,
                'date': mortality.date,
                'count': mortality.count,
                'cause': mortality.cause,
                'note': mortality.note
            })
        
        found = False
        for i, item in enumerate(self.all_mortalities):
            if item.get('key') == key:
                self.all_mortalities[i]['mortalities'] = mortalities_data
                found = True
                break
        
        if not found:
            self.all_mortalities.append({
                'key': key,
                'farm_id': self.current_farm.id if self.current_farm else '',
                'mooring_id': self.current_mooring.id if self.current_mooring else '',
                'mortalities': mortalities_data
            })
        
        self.save_all_data()
    
    # ==================== پارامترهای آب (Water Parameter) ====================
    
    def load_current_water_parameters(self):
        self.water_parameters = []
        key = self.get_mooring_key()
        if not key:
            return
        
        for item in self.all_water_parameters:
            if item.get('key') == key:
                for param_data in item.get('parameters', []):
                    param = WaterParameter()
                    param.farm_id = param_data.get('farm_id', '')
                    param.mooring_id = param_data.get('mooring_id', '')
                    param.cage_id = param_data.get('cage_id', '')
                    param.date = param_data.get('date', '')
                    param.time = param_data.get('time', '')
                    param.temperature = param_data.get('temperature', 0.0)
                    param.dissolved_oxygen = param_data.get('dissolved_oxygen', 0.0)
                    param.salinity = param_data.get('salinity', 0.0)
                    param.ph = param_data.get('ph', 0.0)
                    param.note = param_data.get('note', '')
                    self.water_parameters.append(param)
                break
    
    def save_current_water_parameters(self):
        key = self.get_mooring_key()
        if not key:
            return
        
        params_data = []
        for param in self.water_parameters:
            params_data.append({
                'farm_id': param.farm_id,
                'mooring_id': param.mooring_id,
                'cage_id': param.cage_id,
                'date': param.date,
                'time': param.time,
                'temperature': param.temperature,
                'dissolved_oxygen': param.dissolved_oxygen,
                'salinity': param.salinity,
                'ph': param.ph,
                'note': param.note
            })
        
        found = False
        for i, item in enumerate(self.all_water_parameters):
            if item.get('key') == key:
                self.all_water_parameters[i]['parameters'] = params_data
                found = True
                break
        
        if not found:
            self.all_water_parameters.append({
                'key': key,
                'farm_id': self.current_farm.id if self.current_farm else '',
                'mooring_id': self.current_mooring.id if self.current_mooring else '',
                'parameters': params_data
            })
        
        self.save_all_data()
    
    # ==================== عملیات تغذیه ====================
    
    def add_feed(self):
        if not self.current_farm or not self.current_mooring:
            QtWidgets.QMessageBox.warning(
                self, 
                "خطا", 
                "لطفاً ابتدا یک مزرعه و مورینگ را در صفحه طراحی مزرعه انتخاب کنید"
            )
            return
        
        dialog = FeedDialog(
            self, 
            farms=None, 
            current_farm=self.current_farm, 
            current_mooring=self.current_mooring
        )
        if dialog.exec_():
            dialog.feed.farm_id = self.current_farm.id
            dialog.feed.mooring_id = self.current_mooring.id
            self.feeds.append(dialog.feed)
            self.save_current_feeds()
            self.update_feed_table()
            QtWidgets.QMessageBox.information(self, "موفق", "تغذیه با موفقیت ثبت شد")
    
    def edit_feed(self, index):
        feed = self.feeds[index]
        dialog = FeedDialog(
            self, 
            farms=None, 
            current_farm=self.current_farm, 
            current_mooring=self.current_mooring, 
            feed=feed
        )
        if dialog.exec_():
            self.feeds[index] = dialog.feed
            self.save_current_feeds()
            self.update_feed_table()
            QtWidgets.QMessageBox.information(self, "موفق", "تغذیه با موفقیت ویرایش شد")
    
    def delete_feed(self, index):
        reply = QtWidgets.QMessageBox.question(
            self, 
            "تأیید حذف", 
            "آیا از حذف این رکورد تغذیه مطمئن هستید؟",
            QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No
        )
        if reply == QtWidgets.QMessageBox.Yes:
            self.feeds.pop(index)
            self.save_current_feeds()
            self.update_feed_table()
            QtWidgets.QMessageBox.information(self, "موفق", "رکورد تغذیه حذف شد")
    
    def clear_all_feeds(self):
        if not self.feeds:
            QtWidgets.QMessageBox.information(self, "اطلاع", "هیچ تغذیه‌ای برای حذف وجود ندارد")
            return
        reply = QtWidgets.QMessageBox.question(
            self, 
            "تأیید", 
            "آیا از حذف همه تغذیه‌های این مورینگ مطمئن هستید؟",
            QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No
        )
        if reply == QtWidgets.QMessageBox.Yes:
            self.feeds.clear()
            self.save_current_feeds()
            self.update_feed_table()
            QtWidgets.QMessageBox.information(self, "موفق", "همه تغذیه‌ها حذف شدند")
    
    def update_feed_table(self):
        self.feed_table.setRowCount(len(self.feeds))
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
            btn_layout.setSpacing(3)
            
            edit_btn = QtWidgets.QToolButton()
            edit_btn.setIcon(qta.icon('fa5s.edit', color='#569CD6'))
            edit_btn.setToolTip("ویرایش")
            edit_btn.clicked.connect(partial(self.edit_feed, i))
            
            delete_btn = QtWidgets.QToolButton()
            delete_btn.setIcon(qta.icon('fa5s.trash-alt', color='#F48771'))
            delete_btn.setToolTip("حذف")
            delete_btn.clicked.connect(partial(self.delete_feed, i))
            
            btn_layout.addWidget(edit_btn)
            btn_layout.addWidget(delete_btn)
            btn_layout.addStretch()
            self.feed_table.setCellWidget(i, 6, btn_widget)
        
        if self.feed_table.columnCount() < 7:
            self.feed_table.setColumnCount(7)
            self.feed_table.setHorizontalHeaderLabels([
                "تاریخ", "قفس", "نوع غذا", "مقدار (kg)", "زمان", "یادداشت", "عملیات"
            ])
            self.feed_table.setColumnWidth(6, 80)
    
    # ==================== عملیات تلفات ====================
    
    def add_mortality(self):
        if not self.current_farm or not self.current_mooring:
            QtWidgets.QMessageBox.warning(
                self, 
                "خطا", 
                "لطفاً ابتدا یک مزرعه و مورینگ را در صفحه طراحی مزرعه انتخاب کنید"
            )
            return
        
        dialog = MortalityDialog(
            self, 
            farms=None, 
            current_farm=self.current_farm, 
            current_mooring=self.current_mooring
        )
        if dialog.exec_():
            dialog.mortality.farm_id = self.current_farm.id
            dialog.mortality.mooring_id = self.current_mooring.id
            self.mortalities.append(dialog.mortality)
            self.save_current_mortalities()
            self.update_mortality_table()
            QtWidgets.QMessageBox.information(self, "موفق", "تلفات با موفقیت ثبت شد")
    
    def edit_mortality(self, index):
        mortality = self.mortalities[index]
        dialog = MortalityDialog(
            self, 
            farms=None, 
            current_farm=self.current_farm, 
            current_mooring=self.current_mooring, 
            mortality=mortality
        )
        if dialog.exec_():
            self.mortalities[index] = dialog.mortality
            self.save_current_mortalities()
            self.update_mortality_table()
            QtWidgets.QMessageBox.information(self, "موفق", "تلفات با موفقیت ویرایش شد")
    
    def delete_mortality(self, index):
        reply = QtWidgets.QMessageBox.question(
            self, 
            "تأیید حذف", 
            "آیا از حذف این رکورد تلفات مطمئن هستید؟",
            QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No
        )
        if reply == QtWidgets.QMessageBox.Yes:
            self.mortalities.pop(index)
            self.save_current_mortalities()
            self.update_mortality_table()
            QtWidgets.QMessageBox.information(self, "موفق", "رکورد تلفات حذف شد")
    
    def clear_all_mortalities(self):
        if not self.mortalities:
            QtWidgets.QMessageBox.information(self, "اطلاع", "هیچ تلفاتی برای حذف وجود ندارد")
            return
        reply = QtWidgets.QMessageBox.question(
            self, 
            "تأیید", 
            "آیا از حذف همه تلفات‌های این مورینگ مطمئن هستید؟",
            QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No
        )
        if reply == QtWidgets.QMessageBox.Yes:
            self.mortalities.clear()
            self.save_current_mortalities()
            self.update_mortality_table()
            QtWidgets.QMessageBox.information(self, "موفق", "همه تلفات‌ها حذف شدند")
    
    def update_mortality_table(self):
        self.mortality_table.setRowCount(len(self.mortalities))
        for i, mortality in enumerate(self.mortalities):
            self.mortality_table.setItem(i, 0, QtWidgets.QTableWidgetItem(mortality.date))
            self.mortality_table.setItem(i, 1, QtWidgets.QTableWidgetItem(mortality.cage_id))
            self.mortality_table.setItem(i, 2, QtWidgets.QTableWidgetItem(str(mortality.count)))
            self.mortality_table.setItem(i, 3, QtWidgets.QTableWidgetItem(mortality.cause))
            self.mortality_table.setItem(i, 4, QtWidgets.QTableWidgetItem(mortality.note))
            
            btn_widget = QtWidgets.QWidget()
            btn_layout = QtWidgets.QHBoxLayout(btn_widget)
            btn_layout.setContentsMargins(0, 0, 0, 0)
            btn_layout.setSpacing(3)
            
            edit_btn = QtWidgets.QToolButton()
            edit_btn.setIcon(qta.icon('fa5s.edit', color='#569CD6'))
            edit_btn.setToolTip("ویرایش")
            edit_btn.clicked.connect(partial(self.edit_mortality, i))
            
            delete_btn = QtWidgets.QToolButton()
            delete_btn.setIcon(qta.icon('fa5s.trash-alt', color='#F48771'))
            delete_btn.setToolTip("حذف")
            delete_btn.clicked.connect(partial(self.delete_mortality, i))
            
            btn_layout.addWidget(edit_btn)
            btn_layout.addWidget(delete_btn)
            btn_layout.addStretch()
            self.mortality_table.setCellWidget(i, 5, btn_widget)
        
        if self.mortality_table.columnCount() < 6:
            self.mortality_table.setColumnCount(6)
            self.mortality_table.setHorizontalHeaderLabels([
                "تاریخ", "قفس", "تعداد تلفات", "علت", "یادداشت", "عملیات"
            ])
            self.mortality_table.setColumnWidth(5, 80)
    
    # ==================== عملیات پارامترهای آب ====================
    
    def add_water_parameter(self):
        if not self.current_farm or not self.current_mooring:
            QtWidgets.QMessageBox.warning(
                self, 
                "خطا", 
                "لطفاً ابتدا یک مزرعه و مورینگ را در صفحه طراحی مزرعه انتخاب کنید"
            )
            return
        
        dialog = WaterParameterDialog(
            self, 
            farms=None, 
            current_farm=self.current_farm, 
            current_mooring=self.current_mooring
        )
        if dialog.exec_():
            dialog.parameter.farm_id = self.current_farm.id
            dialog.parameter.mooring_id = self.current_mooring.id
            self.water_parameters.append(dialog.parameter)
            self.save_current_water_parameters()
            self.update_water_table()
            QtWidgets.QMessageBox.information(self, "موفق", "پارامترهای آب با موفقیت ثبت شد")
    
    def edit_water_parameter(self, index):
        param = self.water_parameters[index]
        dialog = WaterParameterDialog(
            self, 
            farms=None, 
            current_farm=self.current_farm, 
            current_mooring=self.current_mooring, 
            parameter=param
        )
        if dialog.exec_():
            self.water_parameters[index] = dialog.parameter
            self.save_current_water_parameters()
            self.update_water_table()
            QtWidgets.QMessageBox.information(self, "موفق", "پارامترهای آب با موفقیت ویرایش شد")
    
    def delete_water_parameter(self, index):
        reply = QtWidgets.QMessageBox.question(
            self, 
            "تأیید حذف", 
            "آیا از حذف این رکورد پارامترهای آب مطمئن هستید؟",
            QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No
        )
        if reply == QtWidgets.QMessageBox.Yes:
            self.water_parameters.pop(index)
            self.save_current_water_parameters()
            self.update_water_table()
            QtWidgets.QMessageBox.information(self, "موفق", "رکورد پارامترهای آب حذف شد")
    
    def clear_all_water_parameters(self):
        if not self.water_parameters:
            QtWidgets.QMessageBox.information(self, "اطلاع", "هیچ پارامتر آبی برای حذف وجود ندارد")
            return
        reply = QtWidgets.QMessageBox.question(
            self, 
            "تأیید", 
            "آیا از حذف همه پارامترهای آب این مورینگ مطمئن هستید؟",
            QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No
        )
        if reply == QtWidgets.QMessageBox.Yes:
            self.water_parameters.clear()
            self.save_current_water_parameters()
            self.update_water_table()
            QtWidgets.QMessageBox.information(self, "موفق", "همه پارامترهای آب حذف شدند")
    
    def update_water_table(self):
        self.water_table.setRowCount(len(self.water_parameters))
        for i, param in enumerate(self.water_parameters):
            self.water_table.setItem(i, 0, QtWidgets.QTableWidgetItem(param.date))
            self.water_table.setItem(i, 1, QtWidgets.QTableWidgetItem(param.cage_id))
            self.water_table.setItem(i, 2, QtWidgets.QTableWidgetItem(param.time))
            self.water_table.setItem(i, 3, QtWidgets.QTableWidgetItem(f"{param.temperature:.1f}"))
            self.water_table.setItem(i, 4, QtWidgets.QTableWidgetItem(f"{param.dissolved_oxygen:.1f}"))
            self.water_table.setItem(i, 5, QtWidgets.QTableWidgetItem(f"{param.salinity:.1f}"))
            self.water_table.setItem(i, 6, QtWidgets.QTableWidgetItem(f"{param.ph:.1f}"))
            self.water_table.setItem(i, 7, QtWidgets.QTableWidgetItem(param.note))
            
            btn_widget = QtWidgets.QWidget()
            btn_layout = QtWidgets.QHBoxLayout(btn_widget)
            btn_layout.setContentsMargins(0, 0, 0, 0)
            btn_layout.setSpacing(3)
            
            edit_btn = QtWidgets.QToolButton()
            edit_btn.setIcon(qta.icon('fa5s.edit', color='#569CD6'))
            edit_btn.setToolTip("ویرایش")
            edit_btn.clicked.connect(partial(self.edit_water_parameter, i))
            
            delete_btn = QtWidgets.QToolButton()
            delete_btn.setIcon(qta.icon('fa5s.trash-alt', color='#F48771'))
            delete_btn.setToolTip("حذف")
            delete_btn.clicked.connect(partial(self.delete_water_parameter, i))
            
            btn_layout.addWidget(edit_btn)
            btn_layout.addWidget(delete_btn)
            btn_layout.addStretch()
            self.water_table.setCellWidget(i, 8, btn_widget)
        
        if self.water_table.columnCount() < 9:
            self.water_table.setColumnCount(9)
            self.water_table.setHorizontalHeaderLabels([
                "تاریخ", "قفس", "زمان", "دما", "اکسیژن", "شوری", "pH", "یادداشت", "عملیات"
            ])
            self.water_table.setColumnWidth(8, 80)
    
    # ==================== رابط کاربری ====================
    
    def setup_ui(self):
        layout = QtWidgets.QVBoxLayout(self)
        
        # استایل یکپارچه با کادرهای نازک و ملایم
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
            QTableWidget::item {
                border: none;
                padding: 4px;
                color: #C8C8C8;
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
            QToolButton {
                border: none;
                border-radius: 3px;
                padding: 2px;
            }
            QToolButton:hover {
                background-color: rgba(86, 156, 214, 50);
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
        
        # نوار ابزار اصلی (دکمه‌های ثبت)
        toolbar = QtWidgets.QHBoxLayout()
        
        title = QtWidgets.QLabel("📊 ثبت و مدیریت عملیات روزانه قفس‌ها")
        title.setStyleSheet("font-size: 14px; font-weight: bold; color: #569CD6;")
        toolbar.addWidget(title)
        toolbar.addStretch()
        
        # دکمه ثبت تغذیه
        self.add_feed_btn = QtWidgets.QPushButton("➕ ثبت تغذیه")
        self.add_feed_btn.setStyleSheet("""
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
        self.add_feed_btn.clicked.connect(self.add_feed)
        toolbar.addWidget(self.add_feed_btn)
        
        # دکمه ثبت تلفات
        self.add_mortality_btn = QtWidgets.QPushButton("⚠️ ثبت تلفات")
        self.add_mortality_btn.setStyleSheet("""
            QPushButton {
                background-color: #8B2C2C;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 6px 12px;
            }
            QPushButton:hover {
                background-color: #A33C3C;
            }
        """)
        self.add_mortality_btn.clicked.connect(self.add_mortality)
        toolbar.addWidget(self.add_mortality_btn)
        
        # دکمه ثبت پارامترهای آب
        self.add_water_btn = QtWidgets.QPushButton("💧 ثبت پارامترهای آب")
        self.add_water_btn.setStyleSheet("""
            QPushButton {
                background-color: #2C5C8C;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 6px 12px;
            }
            QPushButton:hover {
                background-color: #3C7CAC;
            }
        """)
        self.add_water_btn.clicked.connect(self.add_water_parameter)
        toolbar.addWidget(self.add_water_btn)
        
        layout.addLayout(toolbar)
        
        # تب‌های داخلی برای جداول
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
                padding: 4px 10px;
                margin: 1px;
                border-radius: 3px;
            }
            QTabBar::tab:selected {
                background-color: #0E639C;
                color: white;
            }
        """)
        
        # ========== جدول تغذیه ==========
        feed_tab = QtWidgets.QWidget()
        feed_layout = QtWidgets.QVBoxLayout(feed_tab)
        feed_layout.setContentsMargins(0, 0, 0, 0)
        
        feed_toolbar = QtWidgets.QHBoxLayout()
        feed_toolbar.addStretch()
        self.clear_feed_btn = QtWidgets.QPushButton("حذف همه تغذیه‌ها")
        self.clear_feed_btn.setStyleSheet("""
            QPushButton {
                background-color: #5C2C2C;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 4px 10px;
            }
            QPushButton:hover {
                background-color: #7C3C3C;
            }
        """)
        self.clear_feed_btn.clicked.connect(self.clear_all_feeds)
        feed_toolbar.addWidget(self.clear_feed_btn)
        feed_layout.addLayout(feed_toolbar)
        
        self.feed_table = QtWidgets.QTableWidget()
        self.feed_table.setAlternatingRowColors(True)
        feed_layout.addWidget(self.feed_table)
        self.inner_tabs.addTab(feed_tab, "🍽️ تغذیه")
        
        # ========== جدول تلفات ==========
        mortality_tab = QtWidgets.QWidget()
        mortality_layout = QtWidgets.QVBoxLayout(mortality_tab)
        mortality_layout.setContentsMargins(0, 0, 0, 0)
        
        mortality_toolbar = QtWidgets.QHBoxLayout()
        mortality_toolbar.addStretch()
        self.clear_mortality_btn = QtWidgets.QPushButton("حذف همه تلفات‌ها")
        self.clear_mortality_btn.setStyleSheet("""
            QPushButton {
                background-color: #5C2C2C;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 4px 10px;
            }
            QPushButton:hover {
                background-color: #7C3C3C;
            }
        """)
        self.clear_mortality_btn.clicked.connect(self.clear_all_mortalities)
        mortality_toolbar.addWidget(self.clear_mortality_btn)
        mortality_layout.addLayout(mortality_toolbar)
        
        self.mortality_table = QtWidgets.QTableWidget()
        self.mortality_table.setAlternatingRowColors(True)
        mortality_layout.addWidget(self.mortality_table)
        self.inner_tabs.addTab(mortality_tab, "⚠️ تلفات")
        
        # ========== جدول پارامترهای آب ==========
        water_tab = QtWidgets.QWidget()
        water_layout = QtWidgets.QVBoxLayout(water_tab)
        water_layout.setContentsMargins(0, 0, 0, 0)
        
        water_toolbar = QtWidgets.QHBoxLayout()
        water_toolbar.addStretch()
        self.clear_water_btn = QtWidgets.QPushButton("حذف همه پارامترهای آب")
        self.clear_water_btn.setStyleSheet("""
            QPushButton {
                background-color: #5C2C2C;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 4px 10px;
            }
            QPushButton:hover {
                background-color: #7C3C3C;
            }
        """)
        self.clear_water_btn.clicked.connect(self.clear_all_water_parameters)
        water_toolbar.addWidget(self.clear_water_btn)
        water_layout.addLayout(water_toolbar)
        
        self.water_table = QtWidgets.QTableWidget()
        self.water_table.setAlternatingRowColors(True)
        water_layout.addWidget(self.water_table)
        self.inner_tabs.addTab(water_tab, "💧 پارامترهای آب")
        
        layout.addWidget(self.inner_tabs)
        
        return tab