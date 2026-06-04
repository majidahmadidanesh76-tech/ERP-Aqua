"""
ویجت نمایش ساختار سازمانی به صورت درختی
"""

from PyQt5 import QtWidgets, QtCore, QtGui
import qtawesome as qta

class OrgChartWidget(QtWidgets.QWidget):
    """نمایش ساختار سازمانی به صورت درختی"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        self.load_sample_data()

    def setup_ui(self):
        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)

        # عنوان
        title = QtWidgets.QLabel("🏢 ساختار سازمانی شرکت")
        title.setAlignment(QtCore.Qt.AlignCenter)
        title.setStyleSheet("font-size: 18px; font-weight: bold; color: #569CD6; padding: 10px;")
        layout.addWidget(title)

        # نوار ابزار
        toolbar = QtWidgets.QHBoxLayout()
        
        self.refresh_btn = QtWidgets.QPushButton("🔄 بازخوانی")
        self.refresh_btn.clicked.connect(self.refresh_tree)
        toolbar.addWidget(self.refresh_btn)
        
        self.expand_all_btn = QtWidgets.QPushButton("📂 باز کردن همه")
        self.expand_all_btn.clicked.connect(self.expand_all)
        toolbar.addWidget(self.expand_all_btn)
        
        self.collapse_all_btn = QtWidgets.QPushButton("📁 بستن همه")
        self.collapse_all_btn.clicked.connect(self.collapse_all)
        toolbar.addWidget(self.collapse_all_btn)
        
        toolbar.addStretch()
        layout.addLayout(toolbar)

        # درخت سازمانی
        self.tree = QtWidgets.QTreeWidget()
        self.tree.setHeaderLabels(["نام", "سمت", "وظایف", "عملیات"])
        self.tree.setIndentation(25)
        self.tree.setStyleSheet("""
            QTreeWidget {
                background-color: #2D2D30;
                border: 1px solid #3E3E42;
                border-radius: 6px;
                alternate-background-color: #252526;
            }
            QTreeWidget::item {
                height: 35px;
                padding: 2px;
            }
            QTreeWidget::item:selected {
                background-color: #0E639C;
            }
            QHeaderView::section {
                background-color: #252526;
                color: #569CD6;
                padding: 6px;
                border: none;
                border-bottom: 1px solid #3E3E42;
            }
        """)
        
        # تنظیم عرض ستون‌ها
        self.tree.setColumnWidth(0, 250)
        self.tree.setColumnWidth(1, 150)
        self.tree.setColumnWidth(2, 100)
        self.tree.setColumnWidth(3, 120)
        
        layout.addWidget(self.tree)

    def load_sample_data(self):
        """بارگذاری داده‌های نمونه (بعداً به دیتابیس متصل می‌شود)"""
        self.tree.clear()
        
        # شرکت اصلی
        company = QtWidgets.QTreeWidgetItem(["🏢 شرکت پرورش ماهی شمال", "مدیرعامل", "", ""])
        company.setIcon(0, qta.icon('fa5s-building', color='#569CD6'))
        
        # ========== معاونت تولید ==========
        production_vp = QtWidgets.QTreeWidgetItem(["🌾 معاونت تولید", "معاون تولید", "", ""])
        production_vp.setIcon(0, qta.icon('fa5s-tractor', color='#4EC9B0'))
        
        # مدیر پرورش
        prod_manager = QtWidgets.QTreeWidgetItem(["🐟 مدیر پرورش", "مدیر پرورش", "5 وظیفه", ""])
        prod_manager.setIcon(0, qta.icon('fa5s-user-tie', color='#DCDCAA'))
        
        # اپراتورها
        op1 = QtWidgets.QTreeWidgetItem(["   👤 احمدی", "اپراتور قفس 1", "3 وظیفه", ""])
        op1.setIcon(0, qta.icon('fa5s-user', color='#C8C8C8'))
        op2 = QtWidgets.QTreeWidgetItem(["   👤 کریمی", "اپراتور قفس 2", "2 وظیفه", ""])
        op2.setIcon(0, qta.icon('fa5s-user', color='#C8C8C8'))
        op3 = QtWidgets.QTreeWidgetItem(["   👤 محمدی", "اپراتور قفس 3", "1 وظیفه", ""])
        op3.setIcon(0, qta.icon('fa5s-user', color='#C8C8C8'))
        
        prod_manager.addChild(op1)
        prod_manager.addChild(op2)
        prod_manager.addChild(op3)
        
        # مدیر هچری
        hatchery_manager = QtWidgets.QTreeWidgetItem(["🥚 مدیر هچری", "مدیر هچری", "3 وظیفه", ""])
        hatchery_manager.setIcon(0, qta.icon('fa5s-user-tie', color='#DCDCAA'))
        
        tech1 = QtWidgets.QTreeWidgetItem(["   👤 رضایی", "تکنسین هچری", "2 وظیفه", ""])
        tech1.setIcon(0, qta.icon('fa5s-user', color='#C8C8C8'))
        tech2 = QtWidgets.QTreeWidgetItem(["   👤 نادری", "تکنسین هچری", "1 وظیفه", ""])
        tech2.setIcon(0, qta.icon('fa5s-user', color='#C8C8C8'))
        
        hatchery_manager.addChild(tech1)
        hatchery_manager.addChild(tech2)
        
        production_vp.addChild(prod_manager)
        production_vp.addChild(hatchery_manager)
        
        # ========== معاونت فنی ==========
        technical_vp = QtWidgets.QTreeWidgetItem(["🔧 معاونت فنی و نگهداری", "معاون فنی", "", ""])
        technical_vp.setIcon(0, qta.icon('fa5s-tools', color='#F48771'))
        
        maint_manager = QtWidgets.QTreeWidgetItem(["⚙️ مدیر تعمیرات", "مدیر تعمیرات", "4 وظیفه", ""])
        maint_manager.setIcon(0, qta.icon('fa5s-user-tie', color='#DCDCAA'))
        
        electrician = QtWidgets.QTreeWidgetItem(["   👤 علی‌پور", "تکنسین برق", "3 وظیفه", ""])
        electrician.setIcon(0, qta.icon('fa5s-user', color='#C8C8C8'))
        mechanic = QtWidgets.QTreeWidgetItem(["   👤 موسوی", "تکنسین مکانیک", "2 وظیفه", ""])
        mechanic.setIcon(0, qta.icon('fa5s-user', color='#C8C8C8'))
        
        maint_manager.addChild(electrician)
        maint_manager.addChild(mechanic)
        
        technical_vp.addChild(maint_manager)
        
        # ========== معاونت مالی ==========
        finance_vp = QtWidgets.QTreeWidgetItem(["💰 معاونت مالی و اداری", "معاون مالی", "", ""])
        finance_vp.setIcon(0, qta.icon('fa5s-chart-line', color='#4EC9B0'))
        
        finance_manager = QtWidgets.QTreeWidgetItem(["📊 مدیر مالی", "مدیر مالی", "2 وظیفه", ""])
        finance_manager.setIcon(0, qta.icon('fa5s-user-tie', color='#DCDCAA'))
        accountant = QtWidgets.QTreeWidgetItem(["   👤 حسینی", "حسابدار", "3 وظیفه", ""])
        accountant.setIcon(0, qta.icon('fa5s-user', color='#C8C8C8'))
        
        finance_manager.addChild(accountant)
        finance_vp.addChild(finance_manager)
        
        # اضافه کردن به شرکت اصلی
        company.addChild(production_vp)
        company.addChild(technical_vp)
        company.addChild(finance_vp)
        
        self.tree.addTopLevelItem(company)
        
        # باز کردن سطح اول
        company.setExpanded(True)
        production_vp.setExpanded(True)
        technical_vp.setExpanded(True)
        finance_vp.setExpanded(True)
        
        # اضافه کردن دکمه‌های عملیات برای هر ردیف
        self.add_action_buttons()

    def add_action_buttons(self):
        """اضافه کردن دکمه‌های عملیات برای هر ردیف"""
        iterator = QtWidgets.QTreeWidgetItemIterator(self.tree)
        while iterator.value():
            item = iterator.value()
            if item.parent() is not None and "👤" in item.text(0):
                # ساخت ویجت دکمه‌ها
                widget = QtWidgets.QWidget()
                layout = QtWidgets.QHBoxLayout(widget)
                layout.setContentsMargins(0, 0, 0, 0)
                layout.setSpacing(5)
                
                # دکمه کارتابل
                task_btn = QtWidgets.QPushButton("📋 کارتابل")
                task_btn.setStyleSheet("""
                    QPushButton {
                        background-color: #0E639C;
                        color: white;
                        border: none;
                        border-radius: 4px;
                        padding: 4px 8px;
                        font-size: 10px;
                    }
                    QPushButton:hover {
                        background-color: #1177BB;
                    }
                """)
                task_btn.clicked.connect(lambda checked, name=item.text(0): self.open_task_dashboard(name))
                layout.addWidget(task_btn)
                
                layout.addStretch()
                self.tree.setItemWidget(item, 3, widget)
            iterator += 1

    def open_task_dashboard(self, name):
        """باز کردن کارتابل وظایف پرسنل"""
        QtWidgets.QMessageBox.information(self, "کارتابل", f"کارتابل وظایف {name}\n\nدر حال توسعه...")

    def refresh_tree(self):
        """بازخوانی درخت از دیتابیس"""
        self.load_sample_data()

    def expand_all(self):
        """باز کردن همه گره‌ها"""
        self.tree.expandAll()

    def collapse_all(self):
        """بستن همه گره‌ها"""
        self.tree.collapseAll()