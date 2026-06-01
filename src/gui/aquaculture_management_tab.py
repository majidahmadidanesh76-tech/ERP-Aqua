"""
صفحه مدیریت آبزی‌پروری - شامل هچری، نرسری و پرورش در دریا
"""

from PyQt5 import QtWidgets, QtCore
import qtawesome as qta

from .dialogs.feed_dialog import FeedDialog


class AquacultureManagementTab(QtWidgets.QWidget):
    def __init__(self, parent=None, farm=None, mooring=None):
        super().__init__(parent)
        self.current_farm = farm
        self.current_mooring = mooring
        self.feeds = []  # لیست برای ذخیره تغذیه‌ها
        self.setup_ui()
    
    def set_farm_and_mooring(self, farm, mooring):
        """تنظیم مزرعه و مورینگ جاری (از صفحه طراحی مزرعه)"""
        self.current_farm = farm
        self.current_mooring = mooring
        self.update_feed_table()
    
    def setup_ui(self):
        layout = QtWidgets.QVBoxLayout(self)
        
        # تب‌ها
        self.tabs = QtWidgets.QTabWidget()
        self.tabs.setTabPosition(QtWidgets.QTabWidget.North)
        
        # تب هچری
        self.hatchery_tab = self.create_hatchery_tab()
        self.tabs.addTab(self.hatchery_tab, "🐟 هچری")
        
        # تب نرسری
        self.nursery_tab = self.create_nursery_tab()
        self.tabs.addTab(self.nursery_tab, "🌱 نرسری")
        
        # تب پرورش در دریا
        self.growout_tab = self.create_growout_tab()
        self.tabs.addTab(self.growout_tab, "🌊 پرورش در دریا")
        
        layout.addWidget(self.tabs)
    
    def create_hatchery_tab(self):
        """بخش هچری - تخم‌گشایی و لارو"""
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
        """بخش نرسری - رشد اولیه"""
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
        """بخش پرورش در دریا - با جدول تغذیه"""
        tab = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout(tab)
        
        # نوار ابزار بالای جدول
        toolbar = QtWidgets.QHBoxLayout()
        
        title = QtWidgets.QLabel("📊 ثبت و مدیریت عملیات روزانه قفس‌ها")
        title.setStyleSheet("font-size: 14px; font-weight: bold; color: #569CD6;")
        toolbar.addWidget(title)
        
        toolbar.addStretch()
        
        # دکمه افزودن تغذیه جدید
        self.add_feed_btn = QtWidgets.QPushButton("➕ ثبت تغذیه")
        self.add_feed_btn.setIcon(qta.icon('fa5s.plus', color='white'))
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
        
        # دکمه حذف همه (برای تست)
        self.clear_btn = QtWidgets.QPushButton("🗑️ حذف همه")
        self.clear_btn.setIcon(qta.icon('fa5s.trash-alt', color='white'))
        self.clear_btn.setStyleSheet("""
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
        self.clear_btn.clicked.connect(self.clear_all_feeds)
        toolbar.addWidget(self.clear_btn)
        
        layout.addLayout(toolbar)
        
        # جدول ثبت تغذیه
        self.feed_table = QtWidgets.QTableWidget()
        self.feed_table.setColumnCount(6)
        self.feed_table.setHorizontalHeaderLabels([
            "تاریخ", "قفس", "نوع غذا", "مقدار (kg)", "زمان", "یادداشت"
        ])
        self.feed_table.horizontalHeader().setStretchLastSection(True)
        self.feed_table.setStyleSheet("""
            QTableWidget {
                border: none;
                outline: none;
                background-color: #2D2D30;
            }
            QTableWidget::item {
                border: none;
                padding: 4px;
            }
        """)
        layout.addWidget(self.feed_table)
        
        return tab
    
    def add_feed(self):
        """باز کردن دیالوگ ثبت تغذیه"""
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
            # ذخیره تغذیه جدید در لیست
            self.feeds.append(dialog.feed)
            # بروزرسانی جدول
            self.update_feed_table()
            QtWidgets.QMessageBox.information(self, "موفق", "تغذیه با موفقیت ثبت شد")
    
    def clear_all_feeds(self):
        """حذف همه تغذیه‌ها (برای تست)"""
        reply = QtWidgets.QMessageBox.question(
            self, 
            "تأیید", 
            "آیا از حذف همه تغذیه‌ها مطمئن هستید؟",
            QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No
        )
        if reply == QtWidgets.QMessageBox.Yes:
            self.feeds.clear()
            self.update_feed_table()
            QtWidgets.QMessageBox.information(self, "موفق", "همه تغذیه‌ها حذف شدند")
    
    def update_feed_table(self):
        """بروزرسانی جدول تغذیه از لیست feeds"""
        self.feed_table.setRowCount(len(self.feeds))
        
        for i, feed in enumerate(self.feeds):
            self.feed_table.setItem(i, 0, QtWidgets.QTableWidgetItem(feed.date))
            self.feed_table.setItem(i, 1, QtWidgets.QTableWidgetItem(feed.cage_id))
            self.feed_table.setItem(i, 2, QtWidgets.QTableWidgetItem(feed.feed_type))
            self.feed_table.setItem(i, 3, QtWidgets.QTableWidgetItem(str(feed.feed_amount)))
            self.feed_table.setItem(i, 4, QtWidgets.QTableWidgetItem(feed.feed_time))
            self.feed_table.setItem(i, 5, QtWidgets.QTableWidgetItem(feed.note))