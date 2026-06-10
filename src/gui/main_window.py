"""
پنجره اصلی برنامه ERP-Aqua
شامل منوی افقی، سایدبار و استک ویجت صفحات
"""

from PyQt5 import QtWidgets, QtCore, QtGui
import qtawesome as qta
import os
import sys

from .styles import STYLE
from .org_chart_widget import OrgChartWidget
from .farm_tab import FarmDesignTab
from .production_planning_tab import ProductionPlanningTab
from ..core.constants import APP_NAME, APP_VERSION
from ..gui.dialogs import CompanyDialog
from ..gui.dialogs.login_dialog import LoginDialog
from ..gui.dialogs.change_password_dialog import ChangePasswordDialog
from ..gui.dialogs.manage_users_dialog import ManageUsersDialog

class MainWindow(QtWidgets.QMainWindow):
    """
    پنجره اصلی برنامه
    شامل منوی افقی، سایدبار سمت راست و صفحات اصلی
    """

    def __init__(self):
        super().__init__()

        # ========== نمایش دیالوگ لاگین ==========
        print("در حال نمایش دیالوگ لاگین...")
        login_dialog = LoginDialog(self)
        result = login_dialog.exec_()
        print(f"نتیجه دیالوگ لاگین: {result}")

        if not result:
            print("کاربر لاگین نکرد، برنامه بسته میشود")
            sys.exit(0)

        self.current_user = login_dialog.get_current_user()
        print(f"کاربر جاری: {self.current_user}")

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

        # ==================== منوی افقی بالای صفحه ====================
        self.setup_menubar()

        # ==================== سایدبار سمت راست ====================
        self.setup_sidebar(main_layout)

        # ==================== صفحات اصلی ====================
        self.setup_pages(main_layout)

        # بارگذاری آخرین انتخاب مزرعه و مورینگ
        if hasattr(self, 'design_page'):
            self.design_page.load_last_selection()

        # نمایش پیام خوشآمدگویی
        QtWidgets.QMessageBox.information(
            self, 
            "خوش آمدید", 
            f"به ERP-Aqua خوش آمدید {user_name}\n\n"
            f"نقش شما: {self.current_user['role'] if self.current_user else 'مدیر'}"
        )

    def setup_menubar(self):
        """تنظیم منوی افقی بالای صفحه"""
        menubar = self.menuBar()
        menubar.setStyleSheet("""
            QMenuBar {
                background-color: #252526;
                color: #C8C8C8;
                border-bottom: 1px solid #3E3E42;
                font-weight: normal;
                font-size: 12px;
            }
            QMenuBar::item {
                background-color: transparent;
                padding: 5px 10px;
                margin: 0px;
                border-radius: 4px;
            }
            QMenuBar::item:selected {
                background-color: #2A2D2E;
                color: #569CD6;
            }
        """)

        # ========== منوی صفحه اصلی ==========
        home_menu = menubar.addMenu("صفحه اصلی")
        dashboard_action = home_menu.addAction("داشبورد")
        home_menu.addSeparator()

        # ========== زیرمنوی اطلاعات پایه ==========
        base_info_menu = home_menu.addMenu("📋 اطلاعات پایه")

        equip_action = base_info_menu.addAction("🛠️ مدیریت تجهیزات")
        equip_action.triggered.connect(self.open_equipment_management)

        species_action = base_info_menu.addAction("🐟 مدیریت گونههای ماهی")
        species_action.triggered.connect(self.open_species_management)

        base_info_menu.addSeparator()

        # تعریف شرکت جدید (فقط برای ادمین)
        add_company_action = home_menu.addAction("تعریف شرکت جدید")
        add_company_action.triggered.connect(self.add_company)

        home_menu.addAction("تنظیمات")
        home_menu.addSeparator()

        # منوی کاربر
        user_menu = home_menu.addMenu("👤 کاربر")
        change_password_action = user_menu.addAction("تغییر رمز عبور")
        change_password_action.triggered.connect(self.change_password)

        if self.current_user and self.current_user['role'] == 'admin':
            user_menu.addSeparator()
            manage_users_action = user_menu.addAction("مدیریت کاربران")
            manage_users_action.triggered.connect(self.manage_users)

        home_menu.addSeparator()
        logout_action = home_menu.addAction("خروج از حساب")
        logout_action.triggered.connect(self.logout)

        home_menu.addSeparator()
        exit_action = home_menu.addAction("خروج")
        exit_action.triggered.connect(self.close)

        # ========== منوی طراحی مزرعه ==========
        design_menu = menubar.addMenu("طراحی مزرعه")
        design_action = design_menu.addAction("طراحی مزرعه")
        design_action.triggered.connect(lambda: self.stacked.setCurrentIndex(1))

        # ========== منوی برنامهریزی تولید ==========
        planning_menu = menubar.addMenu("برنامه ریزی تولید")
        planning_action = planning_menu.addAction("📋 برنامه ریزی تولید")
        planning_action.triggered.connect(lambda: self.open_planning_section(0))

        # ========== منوی مدیریت آبزیپروری ==========
        aquaculture_menu = menubar.addMenu("مدیریت آبزی پروری")

        hatchery_action = aquaculture_menu.addAction("هچری")
        hatchery_action.setShortcut("Ctrl+H")
        hatchery_action.triggered.connect(lambda: self.open_aquaculture_section(0))

        nursery_action = aquaculture_menu.addAction("نرسری")
        nursery_action.setShortcut("Ctrl+N")
        nursery_action.triggered.connect(lambda: self.open_aquaculture_section(1))

        growout_action = aquaculture_menu.addAction("پرورش در دریا")
        growout_action.setShortcut("Ctrl+G")
        growout_action.triggered.connect(lambda: self.open_aquaculture_section(2))

        # ========== منوی نظارت ==========
        monitor_menu = menubar.addMenu("نظارت")
        monitor_menu.addAction("دما و کیفیت آب")
        monitor_menu.addAction("دوربینها")
        monitor_menu.addAction("هشدارها")

        # ========== منوی فروش و سفارشات ==========
        sales_menu = menubar.addMenu("فروش و سفارشات")
        sales_menu.addAction("ثبت سفارش")
        sales_menu.addAction("لیست مشتریان")
        sales_menu.addAction("گزارش فروش")

        # اتصال منوها به صفحات
        dashboard_action.triggered.connect(lambda: self.stacked.setCurrentIndex(0))
        design_action.triggered.connect(lambda: self.stacked.setCurrentIndex(1))
        planning_action.triggered.connect(lambda: self.open_planning_section(0))

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
        """تنظیم سایدبار سمت راست"""
        sidebar = QtWidgets.QFrame()
        sidebar.setFixedWidth(220)
        sidebar.setProperty("class", "sidebar")
        sidebar_layout = QtWidgets.QVBoxLayout(sidebar)
        sidebar_layout.setContentsMargins(10, 20, 10, 20)
        sidebar_layout.setSpacing(4)
        sidebar_layout.setAlignment(QtCore.Qt.AlignTop)

        # ویجت نمایش شرکت (لوگو + نام)
        self.setup_company_widget(sidebar_layout)

        # دکمههای منوی سایدبار
        menu_items = [
            ("ساختار سازمانی", 0, 'fa5s.sitemap'),
            ("طراحی مزرعه", 1, 'fa5s.map-marked-alt'),
            ("برنامه ریزی تولید", 2, 'fa5s.calendar-alt'),
            ("مدیریت آبزی پروری", 3, 'fa5s.fish'),
            ("نظارت", 4, 'fa5s.chart-line'),
            ("فروش و سفارشات", 5, 'fa5s.shopping-cart')
        ]

        self.stacked = QtWidgets.QStackedWidget()

        for text, idx, icon_name in menu_items:
            btn = QtWidgets.QPushButton(f"  {text}")
            btn.setIcon(qta.icon(icon_name, color='#C8C8C8'))
            btn.setIconSize(QtCore.QSize(18, 18))
            btn.setFixedHeight(35)
            btn.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
            btn.setStyleSheet("""
                QPushButton {
                    background-color: transparent;
                    color: #C8C8C8;
                    font-size: 12px;
                    text-align: left;
                    padding-left: 15px;
                    border: none;
                    border-radius: 6px;
                    margin: 0px;
                }
                QPushButton:hover {
                    background-color: rgba(86, 156, 214, 25);
                    color: #FFFFFF;
                }
                QPushButton:pressed {
                    background-color: rgba(86, 156, 214, 40);
                }
            """)

            # اصلاح مهم: مدیریت آبزی پروری باید تب پرورش در دریا را باز کند (index=2)
            if text == "مدیریت آبزی پروری":
                btn.clicked.connect(lambda: self.open_aquaculture_section(2))
            elif text == "برنامه ریزی تولید":
                btn.clicked.connect(lambda: self.open_planning_section(0))
            else:
                btn.clicked.connect(lambda _, i=idx: self.stacked.setCurrentIndex(i))

            sidebar_layout.addWidget(btn)

        sidebar_layout.addStretch()
        parent_layout.addWidget(sidebar)

    def setup_company_widget(self, parent_layout):
        """تنظیم ویجت نمایش شرکت در سایدبار"""
        self.company_widget = QtWidgets.QWidget()
        company_layout = QtWidgets.QVBoxLayout(self.company_widget)
        company_layout.setContentsMargins(0, 0, 0, 15)
        company_layout.setSpacing(8)

        self.logo_display = QtWidgets.QLabel()
        self.logo_display.setFixedSize(70, 70)
        self.logo_display.setAlignment(QtCore.Qt.AlignCenter)
        self.logo_display.setStyleSheet("border: 1px solid #3E3E42; border-radius: 8px; background-color: #1E1E1E;")
        self.logo_display.setText("🐟")
        self.logo_display.setFont(QtGui.QFont("Segoe UI", 24))
        company_layout.addWidget(self.logo_display, alignment=QtCore.Qt.AlignCenter)

        self.company_name_label = QtWidgets.QLabel("مدیریت مزارع")
        self.company_name_label.setAlignment(QtCore.Qt.AlignCenter)
        self.company_name_label.setStyleSheet("font-size: 12px; color: #C8C8C8; font-weight: bold;")
        company_layout.addWidget(self.company_name_label)

        parent_layout.addWidget(self.company_widget)

    def setup_pages(self, parent_layout):
        """تنظیم صفحات اصلی برنامه"""
        # صفحه 0: ساختار سازمانی (با ارسال کاربر جاری)
        self.org_chart_page = OrgChartWidget(self, self.current_user)
        self.stacked.addWidget(self.org_chart_page)

        # صفحه 1: طراحی مزرعه
        self.design_page = FarmDesignTab()
        self.stacked.addWidget(self.design_page)

        # صفحه 2: برنامهریزی تولید
        self.planning_tab = ProductionPlanningTab()
        self.stacked.addWidget(self.planning_tab)

        # صفحه 3: مدیریت آبزیپروری
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
        """
        باز کردن صفحه مدیریت آبزیپروری با تب انتخابی
        0 = هچری
        1 = نرسری
        2 = پرورش در دریا
        """
        if hasattr(self, 'aquaculture_tab'):
            self.stacked.setCurrentWidget(self.aquaculture_tab)
            if hasattr(self.aquaculture_tab, 'tabs'):
                # اطمینان از اینکه index در محدوده است
                if index < 0 or index > 2:
                    index = 2
                self.aquaculture_tab.tabs.setCurrentIndex(index)
                
                # دریافت مزرعه و مورینگ از صفحه طراحی
                if hasattr(self.design_page, 'current_farm') and hasattr(self.design_page, 'current_mooring'):
                    farm = self.design_page.current_farm
                    mooring = self.design_page.current_mooring
                    
                    if farm and mooring:
                        self.aquaculture_tab.set_farm_and_mooring(farm, mooring)
                        print(f"DEBUG: set_farm_and_mooring با farm={farm.id}, mooring={mooring.id}")
                    else:
                        # اگر انتخاب نشده، سعی کنید آخرین انتخاب را بارگذاری کنید
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
                    

    def add_company(self):
        """تعریف شرکت جدید"""
        dialog = CompanyDialog(self)
        if dialog.exec_():
            self.current_company = dialog.company
            self.update_company_display(self.current_company)
            QtWidgets.QMessageBox.information(self, "موفق", f"شرکت '{self.current_company.name}' با موفقیت ثبت شد")

    def update_company_display(self, company):
        """بروزرسانی نمایش لوگو و نام شرکت در سایدبار"""
        if company and company.name:
            self.company_name_label.setText(company.name)
        else:
            self.company_name_label.setText("مدیریت مزارع")

        if company and company.logo_path and os.path.exists(company.logo_path):
            pixmap = QtGui.QPixmap(company.logo_path)
            if not pixmap.isNull():
                scaled = pixmap.scaled(70, 70, QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation)
                self.logo_display.setPixmap(scaled)
                self.logo_display.setText("")
                return

        self.logo_display.setText("🐟")
        self.logo_display.setFont(QtGui.QFont("Segoe UI", 24))

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
            # راهاندازی مجدد برنامه
            QtWidgets.QApplication.quit()

    def closeEvent(self, event):
        """ذخیره انتخاب‌ها قبل از بستن برنامه"""
        if hasattr(self, 'design_page'):
            self.design_page.save_current_selection()
        event.accept()