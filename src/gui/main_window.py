"""
پنجره اصلی برنامه ERP-Aqua
شامل سایدبار و استک ویجت صفحات (بدون منوی افقی)
"""

from PyQt5 import QtWidgets, QtCore, QtGui
import qtawesome as qta
import os
import sys

from .styles import STYLE
from .org_chart_widget import OrgChartWidget
from .farm_tab import FarmDesignTab
from .production_planning_tab import ProductionPlanningTab
from .modern_dashboard import ModernDashboard
from ..core.constants import APP_NAME, APP_VERSION
from ..gui.dialogs.login_dialog import LoginDialog
from ..gui.dialogs.change_password_dialog import ChangePasswordDialog
from ..gui.dialogs.manage_users_dialog import ManageUsersDialog


class MainWindow(QtWidgets.QMainWindow):
    """
    پنجره اصلی برنامه
    شامل سایدبار سمت راست و صفحات اصلی (بدون منوی افقی)
    """

    def __init__(self, current_user=None):
        super().__init__()
        
        # تنظیم کاربر جاری (اگر از لاگین نیامده باشد، کاربر پیش‌فرض)
        if current_user:
            self.current_user = current_user
        else:
            self.current_user = {'username': 'admin', 'name': 'مدیر سیستم', 'role': 'admin'}
        
        print(f"کاربر جاری در MainWindow: {self.current_user}")

        # تنظیم عنوان پنجره با نام کاربر
        user_name = self.current_user['name'] if self.current_user else 'کاربر'
        self.setWindowTitle(f"{APP_NAME} - نسخه {APP_VERSION} - خوش آمدید {user_name}")
        self.setGeometry(50, 50, 1400, 800)
        self.setStyleSheet(STYLE)
        self.showMaximized()

        self.current_company = None

        central = QtWidgets.QWidget()
        self.setCentralWidget(central)
        main_layout = QtWidgets.QHBoxLayout(central)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # ==================== سایدبار سمت راست ====================
        self.setup_sidebar(main_layout)

        # ==================== صفحات اصلی (استک ویجت) ====================
        self.stacked = QtWidgets.QStackedWidget()
        self.setup_pages(main_layout)

        # بارگذاری آخرین انتخاب مزرعه و مورینگ
        if hasattr(self, 'design_page'):
            self.design_page.load_last_selection()

        # نمایش پیام خوشآمدگویی (فقط در صورتی که از لاگین آمده باشد)
        if current_user:
            QtWidgets.QMessageBox.information(
                self,
                "خوش آمدید",
                f"به ERP-Aqua خوش آمدید {user_name}\n\n"
                f"نقش شما: {self.current_user['role'] if self.current_user else 'مدیر'}"
            )

    def open_equipment_management(self):
        """باز کردن دیالوگ مدیریت تجهیزات"""
        try:
            from .dialogs.equipment_management_dialog import EquipmentManagementDialog
            dialog = EquipmentManagementDialog(self)
            dialog.exec_()
        except ImportError as e:
            QtWidgets.QMessageBox.warning(self, "خطا", f"فایل دیالوگ مدیریت تجهیزات یافت نشد:\n{str(e)}")

    def open_species_management(self):
        """باز کردن دیالوگ مدیریت گونههای ماهی"""
        try:
            from .dialogs.species_dialog import SpeciesManagementDialog
            dialog = SpeciesManagementDialog(self)
            dialog.exec_()
        except ImportError as e:
            QtWidgets.QMessageBox.warning(self, "خطا", f"فایل دیالوگ مدیریت گونههای ماهی یافت نشد:\n{str(e)}")

    def setup_sidebar(self, parent_layout):
        """تنظیم سایدبار سمت راست با آیکون‌های رنگی و خط جداکننده"""
        sidebar = QtWidgets.QFrame()
        sidebar.setFixedWidth(250)
        sidebar.setProperty("class", "sidebar")
        sidebar_layout = QtWidgets.QVBoxLayout(sidebar)
        sidebar_layout.setContentsMargins(6, 60, 6, 8)
        sidebar_layout.setSpacing(0)
        sidebar_layout.setAlignment(QtCore.Qt.AlignTop)

        # دکمه‌های منوی سایدبار (فقط آیکون با setIcon، بدون آیکون در متن)
        menu_items = [
            ("داشبورد", 0, 'fa5s.tachometer-alt', '#569CD6'),
            ("ساختار سازمانی", 1, 'fa5s.users', '#FFD966'),
            ("طراحی مزرعه", 2, 'fa5s.map-marked-alt', '#4EC9B0'),
            ("برنامه ریزی تولید", 3, 'fa5s.calendar-alt', '#DCDCAA'),
            ("مدیریت آبزی پروری", 4, 'fa5s.fish', '#CE9178'),
            ("نظارت", 5, 'fa5s.chart-line', '#F48771'),
            ("فروش و سفارشات", 6, 'fa5s.truck', '#FFB347'),
        ]

        for text, idx, icon_name, color in menu_items:
            btn = QtWidgets.QPushButton(text)
            btn.setIcon(qta.icon(icon_name, color=color))
            btn.setIconSize(QtCore.QSize(18, 18))
            btn.setFixedHeight(38)
            btn.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))

            # اتصال به صفحات
            if text == "مدیریت آبزی پروری":
                btn.clicked.connect(lambda: self.open_aquaculture_section(2))
            elif text == "برنامه ریزی تولید":
                btn.clicked.connect(lambda: self.open_planning_section(0))
            elif text == "داشبورد":
                btn.clicked.connect(lambda: self.stacked.setCurrentIndex(0))
            elif text == "ساختار سازمانی":
                btn.clicked.connect(lambda: self.stacked.setCurrentIndex(1))
            elif text == "طراحی مزرعه":
                btn.clicked.connect(lambda: self.stacked.setCurrentIndex(2))
            else:
                btn.clicked.connect(lambda _, i=idx: self.stacked.setCurrentIndex(i))

            sidebar_layout.addWidget(btn)

            # اضافه کردن خط جداکننده (به جز آخرین آیتم)
            if text != "فروش و سفارشات":
                separator = QtWidgets.QFrame()
                separator.setFrameShape(QtWidgets.QFrame.HLine)
                separator.setFixedHeight(1)
                separator.setStyleSheet("background-color: rgba(255, 255, 255, 0.2); margin: 2px 12px;")
                sidebar_layout.addWidget(separator)

        # ========== بخش تنظیمات (اطلاعات پایه سابق) ==========
        # اضافه کردن خط جداکننده قبل از تنظیمات
        separator_before = QtWidgets.QFrame()
        separator_before.setFrameShape(QtWidgets.QFrame.HLine)
        separator_before.setFixedHeight(1)
        separator_before.setStyleSheet("background-color: rgba(255, 255, 255, 0.3); margin: 8px 12px;")
        sidebar_layout.addWidget(separator_before)

        # عنوان تنظیمات (غیر قابل کلیک)
        settings_title = QtWidgets.QLabel("⚙️ تنظیمات")
        settings_title.setStyleSheet("color: #FFFFFF; font-size: 11px; font-weight: bold; padding: 8px 0px 4px 20px; background: transparent;")
        sidebar_layout.addWidget(settings_title)

        # زیرشاخه مدیریت تجهیزات
        equip_btn = QtWidgets.QPushButton("مدیریت تجهیزات")
        equip_btn.setIcon(qta.icon('fa5s.tools', color='#9CDCFE'))
        equip_btn.setIconSize(QtCore.QSize(16, 16))
        equip_btn.setFixedHeight(32)
        equip_btn.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        equip_btn.clicked.connect(self.open_equipment_management)
        sidebar_layout.addWidget(equip_btn)

        # زیرشاخه مدیریت گونه‌های ماهی
        species_btn = QtWidgets.QPushButton("مدیریت گونه‌های ماهی")
        species_btn.setIcon(qta.icon('fa5s.fish', color='#4EC9B0'))
        species_btn.setIconSize(QtCore.QSize(16, 16))
        species_btn.setFixedHeight(32)
        species_btn.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        species_btn.clicked.connect(self.open_species_management)
        sidebar_layout.addWidget(species_btn)

        # اضافه کردن خط جداکننده بعد از تنظیمات
        separator_after = QtWidgets.QFrame()
        separator_after.setFrameShape(QtWidgets.QFrame.HLine)
        separator_after.setFixedHeight(1)
        separator_after.setStyleSheet("background-color: rgba(255, 255, 255, 0.2); margin: 8px 12px;")
        sidebar_layout.addWidget(separator_after)

        # دکمه کاربر
        user_btn = QtWidgets.QPushButton("کاربر")
        user_btn.setIcon(qta.icon('fa5s.user', color='#FFFFFF'))
        user_btn.setIconSize(QtCore.QSize(16, 16))
        user_btn.setFixedHeight(38)
        user_btn.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))

        # منوی کاربر (با استفاده از QMenu)
        user_menu = QtWidgets.QMenu()
        change_pass_action = user_menu.addAction("🔑 تغییر رمز عبور")
        change_pass_action.triggered.connect(self.change_password)

        if self.current_user and self.current_user['role'] == 'admin':
            user_menu.addSeparator()
            manage_users_action = user_menu.addAction("👥 مدیریت کاربران")
            manage_users_action.triggered.connect(self.manage_users)

        user_menu.addSeparator()
        logout_action = user_menu.addAction("🚪 خروج از حساب")
        logout_action.triggered.connect(self.logout)

        user_btn.setMenu(user_menu)
        sidebar_layout.addWidget(user_btn)

        sidebar_layout.addStretch()
        parent_layout.addWidget(sidebar)

    def setup_pages(self, parent_layout):
        """تنظیم صفحات اصلی برنامه"""
        # صفحه 0: داشبورد مدرن (ارسال کاربر جاری)
        self.stacked.addWidget(ModernDashboard(self, self.current_user))

        # صفحه 1: ساختار سازمانی (با ارسال کاربر جاری)
        self.org_chart_page = OrgChartWidget(self, self.current_user)
        self.stacked.addWidget(self.org_chart_page)

        # صفحه 2: طراحی مزرعه
        self.design_page = FarmDesignTab()
        self.stacked.addWidget(self.design_page)

        # صفحه 3: برنامهریزی تولید
        self.planning_tab = ProductionPlanningTab()
        self.stacked.addWidget(self.planning_tab)

        # صفحه 4: مدیریت آبزیپروری
        from .aquaculture_management_tab import AquacultureManagementTab
        self.aquaculture_tab = AquacultureManagementTab()
        self.stacked.addWidget(self.aquaculture_tab)

        # صفحات در حال توسعه
        developing_pages = ["نظارت", "فروش و سفارشات"]
        for text in developing_pages:
            page = QtWidgets.QLabel(f"{text}\nدر حال توسعه...")
            page.setAlignment(QtCore.Qt.AlignCenter)
            page.setStyleSheet("color:#808080;background:rgba(30,30,30,200);padding:25px;border:1px solid rgba(86,156,214,30);border-radius:10px;")
            self.stacked.addWidget(page)

        parent_layout.addWidget(self.stacked, 1)

    def open_aquaculture_section(self, index=2):
        """باز کردن صفحه مدیریت آبزیپروری با تب انتخابی"""
        if hasattr(self, 'aquaculture_tab'):
            self.stacked.setCurrentWidget(self.aquaculture_tab)
            if hasattr(self.aquaculture_tab, 'tabs'):
                if index < 0 or index > 2:
                    index = 2
                self.aquaculture_tab.tabs.setCurrentIndex(index)

                if hasattr(self.design_page, 'current_farm') and hasattr(self.design_page, 'current_mooring'):
                    farm = self.design_page.current_farm
                    mooring = self.design_page.current_mooring

                    if farm and mooring:
                        self.aquaculture_tab.set_farm_and_mooring(farm, mooring)
                        print(f"DEBUG: set_farm_and_mooring با farm={farm.id}, mooring={mooring.id}")
                    else:
                        if hasattr(self.design_page, 'load_last_selection'):
                            self.design_page.load_last_selection()
                            if self.design_page.current_farm and self.design_page.current_mooring:
                                self.aquaculture_tab.set_farm_and_mooring(
                                    self.design_page.current_farm,
                                    self.design_page.current_mooring
                                )
                                print(f"DEBUG: بارگذاری از فایل - farm={self.design_page.current_farm.id}, mooring={self.design_page.current_mooring.id}")

    def open_planning_section(self, index=0):
        """باز کردن صفحه برنامهریزی تولید"""
        if hasattr(self, 'planning_tab'):
            self.stacked.setCurrentWidget(self.planning_tab)
            if hasattr(self.planning_tab, 'main_tabs'):
                self.planning_tab.main_tabs.setCurrentIndex(index)
                if hasattr(self.design_page, 'current_farm') and hasattr(self.design_page, 'current_mooring'):
                    self.planning_tab.current_farm = self.design_page.current_farm
                    self.planning_tab.current_mooring = self.design_page.current_mooring

    def change_password(self):
        """تغییر رمز عبور کاربر جاری"""
        dialog = ChangePasswordDialog(self, self.current_user['username'])
        if dialog.exec_():
            QtWidgets.QMessageBox.information(self, "موفق", "رمز عبور با موفقیت تغییر کرد")

    def manage_users(self):
        """مدیریت کاربران (فقط ادمین)"""
        dialog = ManageUsersDialog(self)
        dialog.exec_()

    def logout(self):
        """خروج از حساب کاربری"""
        reply = QtWidgets.QMessageBox.question(
            self,
            "خروج",
            "آیا از خروج از حساب کاربری مطمئن هستید؟",
            QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No
        )
        if reply == QtWidgets.QMessageBox.Yes:
            self.close()
            QtWidgets.QApplication.quit()

    def closeEvent(self, event):
        """ذخیره انتخابها قبل از بستن برنامه"""
        if hasattr(self, 'design_page'):
            self.design_page.save_current_selection()
        event.accept()