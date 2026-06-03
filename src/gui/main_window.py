"""
پنجره اصلی برنامه ERP-Aqua
شامل منوی افقی، سایدبار و استک ویجت صفحات
"""

from PyQt5 import QtWidgets, QtCore, QtGui
import qtawesome as qta
import os
import sys

from .styles import STYLE
from .dashboard import DashboardPage
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
            print("کاربر لاگین نکرد، برنامه بسته می‌شود")
            sys.exit(0)

        self.current_user = login_dialog.get_current_user()
        print(f"کاربر جاری: {self.current_user}")

        # تنظیم عنوان پنجره
        self.setWindowTitle(f"{APP_NAME} - نسخه {APP_VERSION}")
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

        add_company_action = home_menu.addAction("تعریف شرکت جدید")
        add_company_action.triggered.connect(self.add_company)

        home_menu.addAction("تنظیمات")
        home_menu.addSeparator()

        user_menu = home_menu.addMenu("👤 کاربر")
        change_password_action = user_menu.addAction("تغییر رمز عبور")
        change_password_action.triggered.connect(self.change_password)

        if self.current_user and self.current_user['role'] == 'admin':
            user_menu.addSeparator()
            manage_users_action = user_menu.addAction("مدیریت کاربران")
            manage_users_action.triggered.connect(self.manage_users)

        home_menu.addSeparator()
        exit_action = home_menu.addAction("خروج")
        exit_action.triggered.connect(self.close)

        # ========== منوی طراحی مزرعه ==========
        design_menu = menubar.addMenu("طراحی مزرعه")
        design_action = design_menu.addAction("طراحی مزرعه")

        # ========== منوی برنامه‌ریزی تولید ==========
        planning_menu = menubar.addMenu("برنامه‌ریزی تولید")
        growth_action = planning_menu.addAction("📅 تقویم رشد")
        shift_action = planning_menu.addAction("🧑‍🌾 برنامه شیفتی")
        planning_menu.addSeparator()
        budget_action = planning_menu.addAction("📊 بودجه‌بندی سالانه")

        # اتصال به صفحات
        growth_action.triggered.connect(lambda: self.open_planning_section(0))
        shift_action.triggered.connect(lambda: self.open_planning_section(1))
        budget_action.triggered.connect(lambda: self.open_planning_section(2))

        # ========== منوی مدیریت آبزی پروری ==========
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
        growth_action.triggered.connect(lambda: self.stacked.setCurrentIndex(2))

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

        # دکمه‌های منوی سایدبار
        menu_items = [
            ("صفحه اصلی", 0, 'fa5s.home'),
            ("طراحی مزرعه", 1, 'fa5s.map-marked-alt'),
            ("برنامه‌ریزی تولید", 2, 'fa5s.calendar-alt'),
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

            if text == "مدیریت آبزی پروری":
                btn.clicked.connect(lambda: self.open_aquaculture_section(0))
            elif text == "برنامه‌ریزی تولید":
                btn.clicked.connect(lambda: self.open_planning_section(0))
            else:
                btn.clicked.connect(lambda _, i=idx: self.stacked.setCurrentIndex(i))

            sidebar_layout.addWidget(btn)

        # ========== ویجت نمایش کاربر جاری ==========
        sidebar_layout.addStretch()
        
        user_frame = QtWidgets.QFrame()
        user_frame.setStyleSheet("""
            QFrame {
                background-color: #252526;
                border: 1px solid #3E3E42;
                border-radius: 8px;
                padding: 8px;
                margin-top: 10px;
            }
        """)
        user_layout = QtWidgets.QVBoxLayout(user_frame)
        user_layout.setSpacing(5)
        
        user_icon = QtWidgets.QLabel("👤")
        user_icon.setAlignment(QtCore.Qt.AlignCenter)
        user_icon.setStyleSheet("font-size: 20px;")
        user_layout.addWidget(user_icon)
        
        user_name = self.current_user['name'] if self.current_user else 'کاربر'
        user_name_label = QtWidgets.QLabel(user_name)
        user_name_label.setAlignment(QtCore.Qt.AlignCenter)
        user_name_label.setStyleSheet("color: #569CD6; font-size: 12px; font-weight: bold;")
        user_layout.addWidget(user_name_label)
        
        user_role = self.current_user['role'] if self.current_user else 'user'
        role_text = "مدیر سیستم" if user_role == "admin" else "کاربر عادی"
        user_role_label = QtWidgets.QLabel(role_text)
        user_role_label.setAlignment(QtCore.Qt.AlignCenter)
        user_role_label.setStyleSheet("color: #C8C8C8; font-size: 10px;")
        user_layout.addWidget(user_role_label)
        
        sidebar_layout.addWidget(user_frame)

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
        # صفحه 0: داشبورد
        self.dashboard_page = DashboardPage()
        self.stacked.addWidget(self.dashboard_page)

        # صفحه 1: طراحی مزرعه
        self.design_page = FarmDesignTab()
        self.stacked.addWidget(self.design_page)

        # صفحه 2: برنامه‌ریزی تولید
        self.planning_tab = ProductionPlanningTab()
        self.stacked.addWidget(self.planning_tab)

        # صفحه 3: مدیریت آبزی پروری
        from .aquaculture_management_tab import AquacultureManagementTab
        self.aquaculture_tab = AquacultureManagementTab()
        self.stacked.addWidget(self.aquaculture_tab)

        # صفحات در حال توسعه
        developing_pages = [
            "صفحه نظارت در حال توسعه...",
            "صفحه فروش و سفارشات در حال توسعه..."
        ]

        for text in developing_pages:
            page = QtWidgets.QLabel(text)
            page.setAlignment(QtCore.Qt.AlignCenter)
            page.setStyleSheet("color:#569CD6;background:#1E1E1E;padding:25px;border:1px solid #3E3E42;")
            self.stacked.addWidget(page)

        parent_layout.addWidget(self.stacked, 1)

    def open_aquaculture_section(self, index=0):
        """باز کردن صفحه مدیریت آبزی پروری با تب انتخابی"""
        if hasattr(self, 'aquaculture_tab'):
            self.stacked.setCurrentWidget(self.aquaculture_tab)
            if hasattr(self.aquaculture_tab, 'tabs'):
                self.aquaculture_tab.tabs.setCurrentIndex(index)
                if hasattr(self.design_page, 'current_farm') and hasattr(self.design_page, 'current_mooring'):
                    self.aquaculture_tab.set_farm_and_mooring(
                        self.design_page.current_farm, 
                        self.design_page.current_mooring
                    )

    def open_planning_section(self, index=0):
        """باز کردن صفحه برنامه‌ریزی تولید با تب انتخابی"""
        if hasattr(self, 'planning_tab'):
            self.stacked.setCurrentWidget(self.planning_tab)
            if hasattr(self.planning_tab, 'tabs'):
                self.planning_tab.tabs.setCurrentIndex(index)
                if hasattr(self.design_page, 'current_farm') and hasattr(self.design_page, 'current_mooring'):
                    self.planning_tab.current_farm = self.design_page.current_farm
                    self.planning_tab.current_mooring = self.design_page.current_mooring
                    self.planning_tab.load_data()

    def add_company(self):
        dialog = CompanyDialog(self)
        if dialog.exec_():
            self.current_company = dialog.company
            self.update_company_display(self.current_company)
            QtWidgets.QMessageBox.information(self, "موفق", f"شرکت '{self.current_company.name}' با موفقیت ثبت شد")

    def update_company_display(self, company):
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
        dialog = ChangePasswordDialog(self, self.current_user['username'])
        if dialog.exec_():
            QtWidgets.QMessageBox.information(self, "موفق", "رمز عبور با موفقیت تغییر کرد")

    def manage_users(self):
        dialog = ManageUsersDialog(self)
        dialog.exec_()