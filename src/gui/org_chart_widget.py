"""
ویجت نمایش ساختار سازمانی - نسخه نهایی با آرشیو مکاتبات
"""

from PyQt5 import QtWidgets, QtCore, QtGui
import qtawesome as qta
from ..database.db_handler import DatabaseHandler
from datetime import datetime

class OrgChartWidget(QtWidgets.QWidget):

    def __init__(self, parent=None, current_user=None):
        super().__init__(parent)
        self.db = DatabaseHandler()
        self.current_user = current_user
        self.current_item = None
        self.current_personnel = None
        self.setup_ui()
        self.load_data()

    def setup_ui(self):
        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # نوار جستجو
        search_frame = QtWidgets.QFrame()
        search_frame.setFixedHeight(40)
        search_frame.setStyleSheet("""
            QFrame {
                background-color: rgba(45, 45, 48, 240);
                border-bottom: 1px solid rgba(86, 156, 214, 20);
            }
        """)
        search_layout = QtWidgets.QHBoxLayout(search_frame)
        search_layout.setContentsMargins(12, 4, 12, 4)
        
        self.search_edit = QtWidgets.QLineEdit()
        self.search_edit.setPlaceholderText("جستجو در ساختار سازمانی...")
        self.search_edit.setStyleSheet("""
            QLineEdit {
                background-color: rgba(55, 55, 60, 220);
                border: 1px solid rgba(86, 156, 214, 25);
                border-radius: 5px;
                padding: 5px 10px;
                color: #C8C8C8;
                font-size: 11px;
            }
            QLineEdit:focus {
                border-color: rgba(86, 156, 214, 50);
            }
            QLineEdit::placeholder {
                color: #808080;
            }
        """)
        self.search_edit.textChanged.connect(self.search_items)
        search_layout.addWidget(self.search_edit)
        layout.addWidget(search_frame)

        # نوار ابزار بالای چارت
        top_toolbar = QtWidgets.QHBoxLayout()
        top_toolbar.setContentsMargins(12, 8, 12, 8)
        top_toolbar.setSpacing(6)

        glass_btn_style = """
            QToolButton {
                background-color: rgba(55, 55, 60, 200);
                border: none;
                border-radius: 4px;
                padding: 4px;
                min-width: 30px;
                min-height: 30px;
            }
            QToolButton:hover {
                background-color: rgba(86, 156, 214, 40);
            }
        """

        self.new_btn = QtWidgets.QToolButton()
        self.new_btn.setIcon(qta.icon('fa5s.plus-circle', color='#C8C8C8'))
        self.new_btn.setIconSize(QtCore.QSize(14, 14))
        self.new_btn.setToolTip("شروع از ابتدا")
        self.new_btn.setStyleSheet(glass_btn_style)
        self.new_btn.clicked.connect(self.new_chart)
        top_toolbar.addWidget(self.new_btn)

        self.expand_all_btn = QtWidgets.QToolButton()
        self.expand_all_btn.setIcon(qta.icon('fa5s.chevron-down', color='#C8C8C8'))
        self.expand_all_btn.setIconSize(QtCore.QSize(14, 14))
        self.expand_all_btn.setToolTip("باز کردن همه")
        self.expand_all_btn.setStyleSheet(glass_btn_style)
        self.expand_all_btn.clicked.connect(self.expand_all)
        top_toolbar.addWidget(self.expand_all_btn)

        self.collapse_all_btn = QtWidgets.QToolButton()
        self.collapse_all_btn.setIcon(qta.icon('fa5s.chevron-right', color='#C8C8C8'))
        self.collapse_all_btn.setIconSize(QtCore.QSize(14, 14))
        self.collapse_all_btn.setToolTip("بستن همه")
        self.collapse_all_btn.setStyleSheet(glass_btn_style)
        self.collapse_all_btn.clicked.connect(self.collapse_all)
        top_toolbar.addWidget(self.collapse_all_btn)

        separator = QtWidgets.QFrame()
        separator.setFrameShape(QtWidgets.QFrame.VLine)
        separator.setStyleSheet("background-color: rgba(86, 156, 214, 20); max-width: 1px;")
        top_toolbar.addWidget(separator)

        self.add_unit_btn = QtWidgets.QToolButton()
        self.add_unit_btn.setIcon(qta.icon('fa5s.folder-plus', color='#C8C8C8'))
        self.add_unit_btn.setIconSize(QtCore.QSize(14, 14))
        self.add_unit_btn.setToolTip("افزودن واحد")
        self.add_unit_btn.setStyleSheet("""
            QToolButton {
                background-color: rgba(86, 156, 214, 35);
                border: none;
                border-radius: 4px;
                padding: 4px;
                min-width: 30px;
                min-height: 30px;
            }
            QToolButton:hover {
                background-color: rgba(86, 156, 214, 55);
            }
        """)
        self.add_unit_btn.clicked.connect(self.add_unit)
        top_toolbar.addWidget(self.add_unit_btn)

        self.add_person_btn = QtWidgets.QToolButton()
        self.add_person_btn.setIcon(qta.icon('fa5s.user-plus', color='#C8C8C8'))
        self.add_person_btn.setIconSize(QtCore.QSize(14, 14))
        self.add_person_btn.setToolTip("افزودن پرسنل")
        self.add_person_btn.setStyleSheet("""
            QToolButton {
                background-color: rgba(86, 156, 214, 35);
                border: none;
                border-radius: 4px;
                padding: 4px;
                min-width: 30px;
                min-height: 30px;
            }
            QToolButton:hover {
                background-color: rgba(86, 156, 214, 55);
            }
        """)
        self.add_person_btn.clicked.connect(self.add_personnel)
        top_toolbar.addWidget(self.add_person_btn)

        top_toolbar.addStretch()
        layout.addLayout(top_toolbar)

        # تقسیم صفحه به دو قسمت
        self.splitter = QtWidgets.QSplitter(QtCore.Qt.Horizontal)
        
        # سمت چپ: درخت سازمانی + پنل ویرایش
        left_widget = QtWidgets.QWidget()
        left_layout = QtWidgets.QVBoxLayout(left_widget)
        left_layout.setContentsMargins(0, 0, 0, 0)
        left_layout.setSpacing(5)
        
        tree_frame = QtWidgets.QFrame()
        tree_frame.setStyleSheet("""
            QFrame {
                background-color: transparent;
                border: 1px solid rgba(86, 156, 214, 20);
                border-radius: 6px;
                margin: 5px;
            }
        """)
        tree_layout = QtWidgets.QVBoxLayout(tree_frame)
        tree_layout.setContentsMargins(0, 0, 0, 0)

        self.tree = QtWidgets.QTreeWidget()
        self.tree.setHeaderHidden(True)
        self.tree.setIndentation(20)
        self.tree.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)
        self.tree.itemClicked.connect(self.on_item_clicked)
        self.tree.setStyleSheet("""
            QTreeWidget {
                background-color: rgba(40, 40, 45, 230);
                border: none;
                outline: none;
            }
            QTreeWidget::item {
                height: 30px;
                padding: 2px;
                border: none;
            }
            QTreeWidget::item:selected {
                background-color: rgba(86, 156, 214, 25);
            }
            QTreeWidget::item:hover {
                background-color: rgba(86, 156, 214, 15);
            }
        """)
        
        tree_layout.addWidget(self.tree)
        left_layout.addWidget(tree_frame)
        
        # پنل ویرایش
        edit_panel = QtWidgets.QFrame()
        edit_panel.setFixedHeight(38)
        edit_panel.setStyleSheet("""
            QFrame {
                background-color: rgba(45, 45, 48, 220);
                border: 1px solid rgba(86, 156, 214, 20);
                border-radius: 6px;
                margin: 5px;
            }
        """)
        edit_layout = QtWidgets.QHBoxLayout(edit_panel)
        edit_layout.setContentsMargins(6, 2, 6, 2)
        edit_layout.setSpacing(4)

        edit_layout.addWidget(QtWidgets.QLabel("نام:"))
        self.edit_name = QtWidgets.QLineEdit()
        self.edit_name.setFixedHeight(26)
        self.edit_name.setStyleSheet("""
            QLineEdit {
                background-color: rgba(55, 55, 60, 220);
                border: 1px solid rgba(86, 156, 214, 25);
                border-radius: 3px;
                padding: 2px 5px;
                color: #C8C8C8;
                font-size: 10px;
            }
        """)
        edit_layout.addWidget(self.edit_name)

        edit_layout.addWidget(QtWidgets.QLabel("سمت:"))
        self.edit_position = QtWidgets.QLineEdit()
        self.edit_position.setFixedHeight(26)
        self.edit_position.setStyleSheet("""
            QLineEdit {
                background-color: rgba(55, 55, 60, 220);
                border: 1px solid rgba(86, 156, 214, 25);
                border-radius: 3px;
                padding: 2px 5px;
                color: #C8C8C8;
                font-size: 10px;
            }
        """)
        edit_layout.addWidget(self.edit_position)

        self.update_btn = QtWidgets.QToolButton()
        self.update_btn.setIcon(qta.icon('fa5s.edit', color='#C8C8C8'))
        self.update_btn.setIconSize(QtCore.QSize(12, 12))
        self.update_btn.setToolTip("بروزرسانی")
        self.update_btn.setFixedSize(24, 24)
        self.update_btn.setStyleSheet("""
            QToolButton {
                background-color: rgba(55, 55, 60, 200);
                border: none;
                border-radius: 3px;
            }
            QToolButton:hover {
                background-color: rgba(86, 156, 214, 40);
            }
        """)
        self.update_btn.clicked.connect(self.update_selected_item)
        edit_layout.addWidget(self.update_btn)

        self.delete_btn = QtWidgets.QToolButton()
        self.delete_btn.setIcon(qta.icon('fa5s.trash-alt', color='#C8C8C8'))
        self.delete_btn.setIconSize(QtCore.QSize(12, 12))
        self.delete_btn.setToolTip("حذف")
        self.delete_btn.setFixedSize(24, 24)
        self.delete_btn.setStyleSheet("""
            QToolButton {
                background-color: rgba(55, 55, 60, 200);
                border: none;
                border-radius: 3px;
            }
            QToolButton:hover {
                background-color: rgba(86, 156, 214, 40);
            }
        """)
        self.delete_btn.clicked.connect(self.delete_selected_item)
        edit_layout.addWidget(self.delete_btn)

        edit_layout.addStretch()
        left_layout.addWidget(edit_panel)
        
        # سمت راست: کارتابل و جزئیات
        right_widget = QtWidgets.QWidget()
        right_layout = QtWidgets.QVBoxLayout(right_widget)
        right_layout.setContentsMargins(5, 5, 5, 5)
        right_layout.setSpacing(8)
        
        self.personnel_title = QtWidgets.QLabel("انتخاب پرسنل")
        self.personnel_title.setAlignment(QtCore.Qt.AlignCenter)
        self.personnel_title.setStyleSheet("""
            font-size: 13px;
            font-weight: bold;
            color: #C8C8C8;
            padding: 8px;
            background-color: rgba(55, 55, 60, 200);
            border: 1px solid rgba(86, 156, 214, 25);
            border-radius: 6px;
        """)
        right_layout.addWidget(self.personnel_title)
        
        self.right_tabs = QtWidgets.QTabWidget()
        self.right_tabs.setTabPosition(QtWidgets.QTabWidget.North)
        self.right_tabs.setStyleSheet("""
            QTabWidget::pane {
                border: 1px solid rgba(86, 156, 214, 20);
                border-radius: 6px;
                background: rgba(40, 40, 45, 230);
            }
            QTabBar::tab {
                background-color: rgba(55, 55, 60, 200);
                padding: 5px 10px;
                margin: 2px;
                border-radius: 4px;
                min-width: 70px;
            }
            QTabBar::tab:selected {
                background-color: rgba(86, 156, 214, 30);
                color: #C8C8C8;
            }
            QTabBar::tab:hover {
                background-color: rgba(86, 156, 214, 20);
            }
        """)
        
        self.tasks_tab = self.create_tasks_tab()
        self.right_tabs.addTab(self.tasks_tab, "📋 کارتابل")
        
        self.report_tab = self.create_report_tab()
        self.right_tabs.addTab(self.report_tab, "📝 ثبت گزارش")
        
        self.info_tab = self.create_info_tab()
        self.right_tabs.addTab(self.info_tab, "ℹ️ اطلاعات")
        
        self.history_tab = self.create_history_tab()
        self.right_tabs.addTab(self.history_tab, "📜 تاریخچه")
        
        self.approval_tab = None
        
        right_layout.addWidget(self.right_tabs)
        
        self.splitter.addWidget(left_widget)
        self.splitter.addWidget(right_widget)
        self.splitter.setSizes([350, 650])
        
        layout.addWidget(self.splitter)

        self.empty_label = QtWidgets.QLabel("برای شروع، روی دکمه «شروع از ابتدا» کلیک کنید\nیا یک واحد اضافه کنید")
        self.empty_label.setAlignment(QtCore.Qt.AlignCenter)
        self.empty_label.setStyleSheet("color: #808080; font-size: 12px; padding: 40px;")
        self.empty_label.hide()
        layout.addWidget(self.empty_label)

    def create_tasks_tab(self):
        tab = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout(tab)
        layout.setContentsMargins(5, 5, 5, 5)
        
        self.tasks_table = QtWidgets.QTableWidget()
        self.tasks_table.setColumnCount(5)
        self.tasks_table.setHorizontalHeaderLabels(["تاریخ", "وظیفه", "زمان", "وضعیت", ""])
        self.tasks_table.setColumnWidth(0, 90)
        self.tasks_table.setColumnWidth(1, 160)
        self.tasks_table.setColumnWidth(2, 90)
        self.tasks_table.setColumnWidth(3, 80)
        self.tasks_table.setColumnWidth(4, 50)
        self.tasks_table.horizontalHeader().setStretchLastSection(True)
        self.tasks_table.setStyleSheet("""
            QTableWidget {
                background-color: rgba(45, 45, 48, 200);
                border: 1px solid rgba(86, 156, 214, 15);
                border-radius: 5px;
                gridline-color: rgba(86, 156, 214, 10);
            }
            QTableWidget::item {
                color: #C8C8C8;
                padding: 4px;
            }
            QHeaderView::section {
                background-color: rgba(50, 50, 55, 200);
                color: #C8C8C8;
                border: none;
                border-bottom: 1px solid rgba(86, 156, 214, 20);
                padding: 4px;
            }
        """)
        layout.addWidget(self.tasks_table)
        return tab

    def create_history_tab(self):
        """ایجاد تب تاریخچه گزارش‌ها"""
        tab = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout(tab)
        layout.setContentsMargins(5, 5, 5, 5)
        
        self.history_table = QtWidgets.QTableWidget()
        self.history_table.setColumnCount(5)
        self.history_table.setHorizontalHeaderLabels(["وظیفه", "نسخه", "تاریخ ارسال", "وضعیت", "نظر مدیر"])
        self.history_table.setColumnWidth(0, 150)
        self.history_table.setColumnWidth(1, 60)
        self.history_table.setColumnWidth(2, 120)
        self.history_table.setColumnWidth(3, 80)
        self.history_table.horizontalHeader().setStretchLastSection(True)
        self.history_table.setStyleSheet("""
            QTableWidget {
                background-color: rgba(45, 45, 48, 200);
                border: 1px solid rgba(86, 156, 214, 15);
                border-radius: 5px;
            }
            QTableWidget::item {
                color: #C8C8C8;
                padding: 4px;
            }
            QHeaderView::section {
                background-color: rgba(50, 50, 55, 200);
                color: #C8C8C8;
                border: none;
                border-bottom: 1px solid rgba(86, 156, 214, 20);
                padding: 4px;
            }
        """)
        layout.addWidget(self.history_table)
        
        return tab

    def create_report_tab(self):
        tab = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout(tab)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(8)
        
        # انتخاب وظیفه
        task_layout = QtWidgets.QHBoxLayout()
        task_label = QtWidgets.QLabel("وظیفه:")
        task_label.setStyleSheet("color: #C8C8C8;")
        task_layout.addWidget(task_label)
        
        self.report_task_combo = QtWidgets.QComboBox()
        self.report_task_combo.setStyleSheet("""
            QComboBox {
                background-color: rgba(55, 55, 60, 220);
                color: #C8C8C8;
                border: 1px solid rgba(86, 156, 214, 25);
                border-radius: 4px;
                padding: 5px;
            }
            QComboBox:disabled {
                color: #808080;
            }
        """)
        task_layout.addWidget(self.report_task_combo)
        task_layout.addStretch()
        layout.addLayout(task_layout)
        
        # انتخاب مدیر تایید کننده
        manager_layout = QtWidgets.QHBoxLayout()
        manager_label = QtWidgets.QLabel("ارسال به:")
        manager_label.setStyleSheet("color: #C8C8C8;")
        manager_layout.addWidget(manager_label)
        
        self.report_manager_combo = QtWidgets.QComboBox()
        self.report_manager_combo.setStyleSheet("""
            QComboBox {
                background-color: rgba(55, 55, 60, 220);
                color: #C8C8C8;
                border: 1px solid rgba(86, 156, 214, 25);
                border-radius: 4px;
                padding: 5px;
            }
            QComboBox:disabled {
                color: #808080;
            }
        """)
        manager_layout.addWidget(self.report_manager_combo)
        manager_layout.addStretch()
        layout.addLayout(manager_layout)
        
        # شرح گزارش
        report_label = QtWidgets.QLabel("شرح انجام کار:")
        report_label.setStyleSheet("color: #C8C8C8;")
        layout.addWidget(report_label)
        
        self.report_text = QtWidgets.QTextEdit()
        self.report_text.setPlaceholderText("شرح کاملی از کار انجام شده را وارد کنید...")
        self.report_text.setMinimumHeight(160)
        self.report_text.setStyleSheet("""
            QTextEdit {
                background-color: rgba(55, 55, 60, 220);
                border: 1px solid rgba(86, 156, 214, 25);
                border-radius: 4px;
                color: #C8C8C8;
                padding: 8px;
            }
        """)
        layout.addWidget(self.report_text)
        
        # دکمه ارسال
        btn_layout = QtWidgets.QHBoxLayout()
        btn_layout.addStretch()
        
        self.submit_report_btn = QtWidgets.QToolButton()
        self.submit_report_btn.setIcon(qta.icon('fa5s.paper-plane', color='#C8C8C8'))
        self.submit_report_btn.setIconSize(QtCore.QSize(14, 14))
        self.submit_report_btn.setToolTip("ارسال گزارش برای تایید")
        self.submit_report_btn.setText("ارسال")
        self.submit_report_btn.setStyleSheet("""
            QToolButton {
                background-color: rgba(55, 55, 60, 200);
                border: 1px solid rgba(86, 156, 214, 30);
                border-radius: 4px;
                padding: 5px 12px;
            }
            QToolButton:hover {
                background-color: rgba(86, 156, 214, 40);
            }
        """)
        self.submit_report_btn.clicked.connect(self.submit_report)
        btn_layout.addWidget(self.submit_report_btn)
        
        layout.addLayout(btn_layout)
        
        return tab

    def create_info_tab(self):
        tab = QtWidgets.QWidget()
        layout = QtWidgets.QFormLayout(tab)
        layout.setLabelAlignment(QtCore.Qt.AlignRight)
        layout.setSpacing(10)
        layout.setContentsMargins(10, 10, 10, 10)
        
        label_style = "color: #C8C8C8;"
        value_style = "color: #C8C8C8; background-color: rgba(55,55,60,180); padding: 4px 8px; border-radius: 4px;"
        
        name_label = QtWidgets.QLabel("نام:")
        name_label.setStyleSheet(label_style)
        self.info_name = QtWidgets.QLabel("-")
        self.info_name.setStyleSheet(value_style)
        layout.addRow(name_label, self.info_name)
        
        pos_label = QtWidgets.QLabel("سمت:")
        pos_label.setStyleSheet(label_style)
        self.info_position = QtWidgets.QLabel("-")
        self.info_position.setStyleSheet(value_style)
        layout.addRow(pos_label, self.info_position)
        
        unit_label = QtWidgets.QLabel("واحد:")
        unit_label.setStyleSheet(label_style)
        self.info_unit = QtWidgets.QLabel("-")
        self.info_unit.setStyleSheet(value_style)
        layout.addRow(unit_label, self.info_unit)
        
        access_label = QtWidgets.QLabel("سطح دسترسی:")
        access_label.setStyleSheet(label_style)
        self.info_access = QtWidgets.QLabel("-")
        self.info_access.setStyleSheet(value_style)
        layout.addRow(access_label, self.info_access)
        
        return tab

    def create_approval_tab(self):
        """ایجاد تب تأیید گزارش‌ها برای مدیران"""
        tab = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout(tab)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(8)
        
        # جدول گزارش‌ها
        self.approval_table = QtWidgets.QTableWidget()
        self.approval_table.setColumnCount(4)
        self.approval_table.setHorizontalHeaderLabels(["وظیفه", "از", "تاریخ ارسال", ""])
        self.approval_table.setColumnWidth(0, 120)
        self.approval_table.setColumnWidth(1, 100)
        self.approval_table.setColumnWidth(2, 120)
        self.approval_table.setColumnWidth(3, 60)
        self.approval_table.horizontalHeader().setStretchLastSection(True)
        self.approval_table.setStyleSheet("""
            QTableWidget {
                background-color: rgba(45, 45, 48, 200);
                border: 1px solid rgba(86, 156, 214, 15);
                border-radius: 5px;
                gridline-color: rgba(86, 156, 214, 10);
            }
            QTableWidget::item {
                color: #C8C8C8;
                padding: 4px;
            }
            QHeaderView::section {
                background-color: rgba(50, 50, 55, 200);
                color: #C8C8C8;
                border: none;
                border-bottom: 1px solid rgba(86, 156, 214, 20);
                padding: 4px;
            }
        """)
        self.approval_table.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self.approval_table.itemSelectionChanged.connect(self.on_approval_selected)
        layout.addWidget(self.approval_table)
        
        # پنل جزئیات گزارش
        detail_frame = QtWidgets.QFrame()
        detail_frame.setStyleSheet("""
            QFrame {
                background-color: rgba(50, 50, 55, 200);
                border: 1px solid rgba(86, 156, 214, 20);
                border-radius: 6px;
            }
        """)
        detail_layout = QtWidgets.QVBoxLayout(detail_frame)
        detail_layout.setSpacing(5)
        detail_layout.setContentsMargins(10, 10, 10, 10)
        
        self.approval_title = QtWidgets.QLabel("انتخاب کنید")
        self.approval_title.setStyleSheet("font-size: 13px; font-weight: bold; color: #569CD6;")
        detail_layout.addWidget(self.approval_title)
        
        detail_layout.addWidget(QtWidgets.QLabel("متن گزارش:"))
        self.approval_report_text = QtWidgets.QTextEdit()
        self.approval_report_text.setReadOnly(True)
        self.approval_report_text.setMaximumHeight(120)
        self.approval_report_text.setStyleSheet("""
            QTextEdit {
                background-color: rgba(55, 55, 60, 220);
                border: 1px solid rgba(86, 156, 214, 25);
                border-radius: 4px;
                color: #C8C8C8;
                padding: 6px;
            }
        """)
        detail_layout.addWidget(self.approval_report_text)
        
        # دلیل رد
        self.reject_reason_frame = QtWidgets.QWidget()
        reject_layout = QtWidgets.QVBoxLayout(self.reject_reason_frame)
        reject_layout.setContentsMargins(0, 5, 0, 0)
        
        reject_layout.addWidget(QtWidgets.QLabel("دلیل رد (در صورت رد):"))
        self.reject_reason_text = QtWidgets.QTextEdit()
        self.reject_reason_text.setMaximumHeight(60)
        self.reject_reason_text.setPlaceholderText("لطفاً دلیل رد گزارش را وارد کنید...")
        self.reject_reason_text.setStyleSheet("""
            QTextEdit {
                background-color: rgba(55, 55, 60, 220);
                border: 1px solid rgba(86, 156, 214, 25);
                border-radius: 4px;
                color: #C8C8C8;
                padding: 5px;
            }
        """)
        reject_layout.addWidget(self.reject_reason_text)
        self.reject_reason_frame.hide()
        detail_layout.addWidget(self.reject_reason_frame)
        
        # دکمه‌ها
        btn_layout = QtWidgets.QHBoxLayout()
        btn_layout.addStretch()
        
        self.approve_btn = QtWidgets.QPushButton("✓ تایید و پاراف")
        self.approve_btn.setFixedSize(120, 32)
        self.approve_btn.setStyleSheet("""
            QPushButton {
                background-color: #2E8B57;
                color: white;
                border: none;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #3CB371;
            }
        """)
        self.approve_btn.clicked.connect(lambda: self.approve_current_report(True))
        btn_layout.addWidget(self.approve_btn)
        
        self.reject_btn = QtWidgets.QPushButton("✗ رد با ذکر دلیل")
        self.reject_btn.setFixedSize(120, 32)
        self.reject_btn.setStyleSheet("""
            QPushButton {
                background-color: #8B2C2C;
                color: white;
                border: none;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #A33C3C;
            }
        """)
        self.reject_btn.clicked.connect(lambda: self.approve_current_report(False))
        btn_layout.addWidget(self.reject_btn)
        
        detail_layout.addLayout(btn_layout)
        
        layout.addWidget(detail_frame)
        
        self.current_selected_report = None
        self.current_selected_row = -1
        
        return tab

    def on_approval_selected(self):
        """هنگام انتخاب یک گزارش در جدول تایید"""
        selected = self.approval_table.selectedItems()
        if selected:
            row = selected[0].row()
            if hasattr(self, 'pending_reports') and row < len(self.pending_reports):
                self.show_report_detail(row)

    def show_report_detail(self, index):
        """نمایش جزئیات گزارش انتخاب شده"""
        if index < 0 or index >= len(self.pending_reports):
            return
        
        report = self.pending_reports[index]
        self.current_selected_report = report
        self.current_selected_row = index
        
        self.approval_title.setText(f"گزارش: {report['task_type']} - {report.get('requester_name', report['assigned_to'])}")
        self.approval_report_text.setText(report.get('report_text', 'متن گزارش موجود نیست'))
        self.reject_reason_text.clear()
        self.reject_reason_frame.hide()

    def approve_current_report(self, approved):
        """تایید یا رد گزارش انتخاب شده"""
        if self.current_selected_report is None:
            QtWidgets.QMessageBox.warning(self, "خطا", "لطفاً ابتدا یک گزارش را انتخاب کنید")
            return
        
        report = self.current_selected_report
        report_id = report['id']
        reject_reason = None
        
        if not approved:
            reject_reason = self.reject_reason_text.toPlainText().strip()
            if not reject_reason:
                QtWidgets.QMessageBox.warning(self, "خطا", "لطفاً دلیل رد گزارش را وارد کنید")
                return
        
        status = 'approved' if approved else 'rejected'
        
        if approved:
            self.db.db.execute_query(
                """UPDATE daily_tasks 
                   SET approval_status = %s, 
                       approved_at = NOW(), 
                       approved_by = %s,
                       approved_by_name = %s,
                       reviewer_signature = CONCAT('تایید شده توسط ', %s, ' در تاریخ ', DATE_FORMAT(NOW(), '%%Y/%%m/%%d'))
                   WHERE id = %s""",
                (status, self.current_personnel.get('id'), 
                 self.current_personnel.get('name'), 
                 self.current_personnel.get('name'), 
                 report_id)
            )
            msg = f"✅ گزارش تایید شد\n\nتایید کننده: {self.current_personnel.get('name')}\nتاریخ: {datetime.now().strftime('%Y/%m/%d %H:%M')}"
        else:
            self.db.db.execute_query(
                """UPDATE daily_tasks 
                   SET approval_status = %s, 
                       approved_at = NOW(), 
                       approved_by = %s,
                       approved_by_name = %s,
                       rejected_reason = %s
                   WHERE id = %s""",
                (status, self.current_personnel.get('id'), 
                 self.current_personnel.get('name'), 
                 reject_reason, 
                 report_id)
            )
            msg = f"❌ گزارش رد شد\n\nدلیل: {reject_reason}\nرد کننده: {self.current_personnel.get('name')}\n\nلطفاً پرسنل گزارش را اصلاح و مجدداً ارسال کند."
        
        QtWidgets.QMessageBox.information(self, "موفق", msg)
        
        if self.current_personnel:
            self.load_pending_reports(self.current_personnel.get('name', ''), self.current_personnel.get('id', 0))

    def create_tree_item(self, name, position, tasks=0, is_manager=False, item_id=None):
        icon = "📁" if is_manager else "👤"
        text = f"{icon} {name}"
        color = "#7AB8E0" if is_manager else "#C8C8C8"
        if position:
            text += f"  —  {position}"
        if tasks > 0:
            text += f"  📋 {tasks}"
        
        item = QtWidgets.QTreeWidgetItem([text])
        item.setForeground(0, QtGui.QColor(color))
        
        if is_manager:
            font = QtGui.QFont("Segoe UI", 9)
            font.setBold(True)
            item.setFont(0, font)
        
        item.setData(0, QtCore.Qt.UserRole, {"id": item_id, "name": name, "position": position, "is_manager": is_manager})
        return item

    def load_managers_for_approval(self):
        """بارگذاری لیست همه مدیران برای تایید گزارش"""
        self.report_manager_combo.clear()
        
        all_managers = self.db.db.fetch_all(
            "SELECT id, name, access_level FROM org_personnel WHERE access_level >= 3 ORDER BY access_level DESC, name"
        )
        
        if not all_managers:
            self.report_manager_combo.addItem("هیچ مدیری در سیستم تعریف نشده است", None)
            self.report_manager_combo.setEnabled(False)
            return
        
        for m in all_managers:
            level_name = {3: "مدیر", 4: "معاون", 5: "مدیرعامل", 6: "ادمین"}
            role = level_name.get(m['access_level'], "مدیر")
            self.report_manager_combo.addItem(f"{m['name']} ({role})", m['id'])
        
        self.report_manager_combo.setEnabled(True)

    def load_pending_reports(self, manager_name, manager_id):
        """بارگذاری گزارش‌های در انتظار تایید برای مدیر"""
        reports = self.db.db.fetch_all(
            """SELECT dt.*, 
                      dt.report_text, 
                      dt.submitted_at, 
                      dt.approval_status,
                      dt.assigned_manager,
                      p.name as requester_name
               FROM daily_tasks dt
               JOIN org_personnel p ON dt.assigned_to = p.name
               WHERE dt.assigned_manager = %s 
                 AND dt.approval_status = 'pending'
               ORDER BY dt.submitted_at DESC""",
            (manager_id,)
        )
        
        self.approval_table.setRowCount(len(reports))
        self.pending_reports = reports
        
        for i, r in enumerate(reports):
            self.approval_table.setItem(i, 0, QtWidgets.QTableWidgetItem(r['task_type']))
            self.approval_table.setItem(i, 1, QtWidgets.QTableWidgetItem(r.get('requester_name', r['assigned_to'])))
            self.approval_table.setItem(i, 2, QtWidgets.QTableWidgetItem(str(r['submitted_at'])[:16] if r['submitted_at'] else "-"))
            
            view_btn = QtWidgets.QPushButton("مشاهده")
            view_btn.setFixedSize(60, 25)
            view_btn.setStyleSheet("""
                QPushButton {
                    background-color: #0E639C;
                    color: white;
                    border: none;
                    border-radius: 3px;
                }
                QPushButton:hover {
                    background-color: #1177BB;
                }
            """)
            view_btn.clicked.connect(lambda checked, idx=i: self.show_report_detail(idx))
            self.approval_table.setCellWidget(i, 3, view_btn)
        
        self.approval_title.setText("انتخاب کنید")
        self.approval_report_text.clear()
        self.current_selected_report = None
        self.current_selected_row = -1

    def load_history(self, personnel_name, personnel_id):
        """بارگذاری تاریخچه گزارش‌های پرسنل"""
        tasks = self.db.db.fetch_all(
            """SELECT id, task_type, revision_count, submitted_at, approval_status, rejected_reason
               FROM daily_tasks 
               WHERE assigned_to = %s 
               ORDER BY submitted_at DESC""",
            (personnel_name,)
        )
        
        history_data = []
        for task in tasks:
            history_data.append({
                'task_type': task['task_type'],
                'revision': task['revision_count'],
                'submitted_at': task['submitted_at'],
                'status': task['approval_status'],
                'reason': task.get('rejected_reason', '')
            })
        
        self.history_table.setRowCount(len(history_data))
        for i, h in enumerate(history_data):
            self.history_table.setItem(i, 0, QtWidgets.QTableWidgetItem(h['task_type']))
            self.history_table.setItem(i, 1, QtWidgets.QTableWidgetItem(str(h['revision'])))
            self.history_table.setItem(i, 2, QtWidgets.QTableWidgetItem(str(h['submitted_at'])[:16] if h['submitted_at'] else "-"))
            
            status_text = ""
            if h['status'] == 'approved':
                status_text = "✅ تایید شده"
            elif h['status'] == 'rejected':
                status_text = "❌ رد شده"
            else:
                status_text = "⏳ در انتظار"
            self.history_table.setItem(i, 3, QtWidgets.QTableWidgetItem(status_text))
            self.history_table.setItem(i, 4, QtWidgets.QTableWidgetItem(h['reason'] if h['reason'] else "-"))

    def update_right_panel(self, personnel_data):
        """بروزرسانی پنل سمت راست با اطلاعات پرسنل انتخاب شده"""
        if not personnel_data:
            self.personnel_title.setText("انتخاب پرسنل")
            self.tasks_table.setRowCount(0)
            self.report_task_combo.clear()
            self.report_manager_combo.clear()
            self.report_task_combo.setEnabled(False)
            self.report_manager_combo.setEnabled(False)
            self.history_table.setRowCount(0)
            
            for i in range(self.right_tabs.count()):
                if self.right_tabs.tabText(i) == "✅ تایید":
                    self.right_tabs.removeTab(i)
                    break
            return
        
        name = personnel_data.get('name', '')
        position = personnel_data.get('position', '')
        personnel_id = personnel_data.get('id', 0)
        unit_id = personnel_data.get('unit_id', 0)
        access_level = personnel_data.get('access_level', 1)
        
        unit_name = "-"
        if unit_id:
            unit = self.db.db.fetch_one("SELECT name FROM org_units WHERE id = %s", (unit_id,))
            if unit:
                unit_name = unit['name']
        
        self.personnel_title.setText(f"👤 {name} - {position if position else 'پرسنل'}")
        
        self.info_name.setText(name)
        self.info_position.setText(position if position else "-")
        self.info_unit.setText(unit_name)
        
        access_names = {1: "کارمند عادی", 2: "سرپرست", 3: "مدیر", 4: "معاون", 5: "مدیرعامل", 6: "ادمین"}
        self.info_access.setText(access_names.get(access_level, "نامشخص"))
        
        self.load_personnel_tasks(name, personnel_id)
        self.load_history(name, personnel_id)
        
        self.report_task_combo.clear()
        tasks = self.db.db.fetch_all(
            "SELECT id, task_type, task_date FROM daily_tasks WHERE assigned_to = %s AND status != 'done' AND approval_status != 'approved' ORDER BY task_date DESC",
            (name,)
        )
        for task in tasks:
            self.report_task_combo.addItem(f"{task['task_date']} - {task['task_type']}", task['id'])
        self.report_task_combo.setEnabled(len(tasks) > 0)
        if len(tasks) == 0:
            self.report_task_combo.addItem("هیچ وظیفه فعالی وجود ندارد", None)
        
        self.load_managers_for_approval()
        
        for i in range(self.right_tabs.count()):
            if self.right_tabs.tabText(i) == "✅ تایید":
                self.right_tabs.removeTab(i)
                break
        
        if access_level >= 3:
            self.approval_tab = self.create_approval_tab()
            self.right_tabs.addTab(self.approval_tab, "✅ تایید")
            self.load_pending_reports(name, personnel_id)

    def load_personnel_tasks(self, name, personnel_id):
        tasks = self.db.db.fetch_all(
            "SELECT * FROM daily_tasks WHERE assigned_to = %s ORDER BY task_date DESC",
            (name,)
        )
        
        self.tasks_table.setRowCount(len(tasks))
        
        for i, task in enumerate(tasks):
            self.tasks_table.setItem(i, 0, QtWidgets.QTableWidgetItem(str(task['task_date'])))
            self.tasks_table.setItem(i, 1, QtWidgets.QTableWidgetItem(task['task_type']))
            self.tasks_table.setItem(i, 2, QtWidgets.QTableWidgetItem(task['shift_time']))
            
            if task['approval_status'] == 'approved':
                status_text = "✓ تایید شده"
                status_color = "#4EC9B0"
            elif task['approval_status'] == 'rejected':
                status_text = "✗ رد شده"
                status_color = "#F48771"
            elif task['status'] == 'done':
                status_text = "✓ انجام شده"
                status_color = "#7AB8E0"
            else:
                status_text = "○ در انتظار"
                status_color = "#808080"
            
            status_item = QtWidgets.QTableWidgetItem(status_text)
            status_item.setForeground(QtGui.QColor(status_color))
            self.tasks_table.setItem(i, 3, status_item)
            
            if task['status'] != 'done' and task['approval_status'] != 'approved':
                complete_btn = QtWidgets.QToolButton()
                complete_btn.setIcon(qta.icon('fa5s.check', color='#7AB8E0'))
                complete_btn.setIconSize(QtCore.QSize(12, 12))
                complete_btn.setToolTip("تکمیل وظیفه")
                complete_btn.setFixedSize(24, 24)
                complete_btn.setStyleSheet("""
                    QToolButton {
                        background-color: rgba(55, 55, 60, 200);
                        border: none;
                        border-radius: 3px;
                    }
                    QToolButton:hover {
                        background-color: rgba(86, 156, 214, 40);
                    }
                """)
                complete_btn.clicked.connect(lambda checked, tid=task['id']: self.complete_task(tid, name))
                self.tasks_table.setCellWidget(i, 4, complete_btn)

    def submit_report(self):
        if not self.current_personnel:
            QtWidgets.QMessageBox.warning(self, "خطا", "هیچ پرسنلی انتخاب نشده است")
            return
        
        task_id = self.report_task_combo.currentData()
        if not task_id:
            QtWidgets.QMessageBox.warning(self, "خطا", "لطفاً یک وظیفه را انتخاب کنید")
            return
        
        manager_id = self.report_manager_combo.currentData()
        if not manager_id:
            QtWidgets.QMessageBox.warning(self, "خطا", "لطفاً مدیر تایید کننده را انتخاب کنید")
            return
        
        report_text = self.report_text.toPlainText().strip()
        if not report_text:
            QtWidgets.QMessageBox.warning(self, "خطا", "لطفاً شرح گزارش را وارد کنید")
            return
        
        # دریافت شماره بازنگری فعلی
        current_task = self.db.db.fetch_one("SELECT revision_count FROM daily_tasks WHERE id = %s", (task_id,))
        new_revision = (current_task['revision_count'] or 0) + 1 if current_task else 1
        
        # بروزرسانی وظیفه با گزارش جدید
        self.db.db.execute_query(
            """UPDATE daily_tasks 
               SET report_text = %s, 
                   submitted_at = NOW(), 
                   approval_status = 'pending',
                   assigned_manager = %s,
                   revision_count = %s,
                   rejected_reason = NULL
               WHERE id = %s""",
            (report_text, manager_id, new_revision, task_id)
        )
        
        QtWidgets.QMessageBox.information(self, "موفق", 
            f"گزارش با موفقیت ارسال شد (نسخه {new_revision})\nدر انتظار تایید مدیر")
        self.report_text.clear()
        self.load_personnel_tasks(self.current_personnel.get('name', ''), self.current_personnel.get('id', 0))
        self.update_right_panel(self.current_personnel)

    def complete_task(self, task_id, name):
        self.db.db.execute_query("UPDATE daily_tasks SET status = 'done' WHERE id = %s", (task_id,))
        self.load_personnel_tasks(name, 0)
        if self.current_personnel:
            self.update_right_panel(self.current_personnel)
        QtWidgets.QMessageBox.information(self, "موفق", "وظیفه تکمیل شد")

    def load_data(self):
        self.tree.clear()
        root_units = self.db.db.fetch_all("SELECT * FROM org_units WHERE parent_id IS NULL ORDER BY id")
        for unit in root_units:
            self.add_unit_to_tree(None, unit)
        self.update_empty_state()

    def add_unit_to_tree(self, parent_item, unit_data):
        unit_id = unit_data['id']
        name = unit_data['name']
        position = unit_data.get('position', '')
        
        item = self.create_tree_item(name, position, 0, True, unit_id)
        
        if parent_item is None:
            self.tree.addTopLevelItem(item)
        else:
            parent_item.addChild(item)
        
        personnel_list = self.db.db.fetch_all("SELECT * FROM org_personnel WHERE unit_id = %s", (unit_id,))
        for p in personnel_list:
            self.add_personnel_to_tree(item, p)
        
        child_units = self.db.db.fetch_all("SELECT * FROM org_units WHERE parent_id = %s", (unit_id,))
        for child_unit in child_units:
            self.add_unit_to_tree(item, child_unit)
        
        if parent_item:
            parent_item.setExpanded(True)

    def add_personnel_to_tree(self, parent_item, personnel_data):
        personnel_id = personnel_data['id']
        name = personnel_data['name']
        position = personnel_data.get('position', '')
        tasks_count = personnel_data.get('tasks_count', 0)
        access_level = personnel_data.get('access_level', 1)
        
        item = self.create_tree_item(name, position, tasks_count, False, personnel_id)
        parent_item.addChild(item)

    def on_item_clicked(self, item, column):
        data = item.data(0, QtCore.Qt.UserRole)
        if data:
            self.current_item = item
            is_manager = data.get("is_manager", False)
            self.edit_name.setText(data.get("name", ""))
            self.edit_position.setText(data.get("position", ""))
            
            if not is_manager:
                self.current_personnel = data
                personnel = self.db.db.fetch_one("SELECT * FROM org_personnel WHERE id = %s", (data.get("id"),))
                if personnel:
                    self.update_right_panel(personnel)
            else:
                self.current_personnel = None
                self.personnel_title.setText(f"📁 {data.get('name', '')} - واحد سازمانی")
                self.tasks_table.setRowCount(0)
                self.report_task_combo.clear()
                self.report_manager_combo.clear()
                self.history_table.setRowCount(0)
                self.report_task_combo.addItem("هیچ وظیفه فعالی وجود ندارد", None)
                self.report_task_combo.setEnabled(False)
                self.report_manager_combo.setEnabled(False)

    def update_selected_item(self):
        if not self.current_item:
            QtWidgets.QMessageBox.warning(self, "خطا", "لطفاً یک آیتم را انتخاب کنید")
            return
        
        new_name = self.edit_name.text().strip()
        new_position = self.edit_position.text().strip()
        if not new_name:
            QtWidgets.QMessageBox.warning(self, "خطا", "نام نمی‌تواند خالی باشد")
            return
        
        data = self.current_item.data(0, QtCore.Qt.UserRole)
        if data:
            item_id = data.get("id")
            is_manager = data.get("is_manager", False)
            
            if is_manager:
                self.db.db.execute_query(
                    "UPDATE org_units SET name = %s, position = %s WHERE id = %s",
                    (new_name, new_position, item_id)
                )
            else:
                self.db.db.execute_query(
                    "UPDATE org_personnel SET name = %s, position = %s WHERE id = %s",
                    (new_name, new_position, item_id)
                )
            
            self.load_data()
            QtWidgets.QMessageBox.information(self, "موفق", "اطلاعات بروزرسانی شد")

    def delete_selected_item(self):
        if not self.current_item:
            QtWidgets.QMessageBox.warning(self, "خطا", "لطفاً یک آیتم را انتخاب کنید")
            return
        
        data = self.current_item.data(0, QtCore.Qt.UserRole)
        if not data:
            return
        
        item_id = data.get("id")
        is_manager = data.get("is_manager", False)
        name = data.get("name", "")
        
        reply = QtWidgets.QMessageBox.question(self, "تأیید حذف", 
                                               f"آیا از حذف «{name}» مطمئن هستید؟",
                                               QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)
        if reply == QtWidgets.QMessageBox.Yes:
            if is_manager:
                self.db.db.execute_query("DELETE FROM org_units WHERE id = %s", (item_id,))
            else:
                self.db.db.execute_query("DELETE FROM org_personnel WHERE id = %s", (item_id,))
            
            self.load_data()
            self.current_item = None

    def update_empty_state(self):
        if self.tree.topLevelItemCount() == 0:
            self.tree.hide()
            self.empty_label.show()
        else:
            self.tree.show()
            self.empty_label.hide()

    def add_unit(self):
        parent_id = None
        parent_name = "ریشه"
        
        if self.current_item:
            data = self.current_item.data(0, QtCore.Qt.UserRole)
            if data:
                if not data.get("is_manager", False):
                    QtWidgets.QMessageBox.warning(self, "خطا", "نمی‌توانید زیرمجموعه پرسنل اضافه کنید.")
                    return
                parent_id = data.get("id")
                parent_name = data.get("name", "")
        
        name, ok = QtWidgets.QInputDialog.getText(self, "افزودن واحد", f"نام واحد (زیرمجموعه {parent_name}):")
        if ok and name.strip():
            level = 1
            if parent_id:
                parent_data = self.db.db.fetch_one("SELECT level FROM org_units WHERE id = %s", (parent_id,))
                if parent_data:
                    level = parent_data['level'] + 1
            
            self.db.db.execute_query(
                "INSERT INTO org_units (name, position, parent_id, level, access_level) VALUES (%s, %s, %s, %s, %s)",
                (name.strip(), None, parent_id, level, 1)
            )
            self.load_data()
            self.current_item = None

    def add_personnel(self):
        if not self.current_item:
            QtWidgets.QMessageBox.warning(self, "خطا", "لطفاً یک واحد را انتخاب کنید.")
            return
        
        data = self.current_item.data(0, QtCore.Qt.UserRole)
        if not data or not data.get("is_manager", False):
            QtWidgets.QMessageBox.warning(self, "خطا", "لطفاً یک واحد را انتخاب کنید.")
            return
        
        unit_id = data.get("id")
        unit_name = data.get("name", "")
        
        dialog = QtWidgets.QDialog(self)
        dialog.setWindowTitle("افزودن پرسنل جدید")
        dialog.setModal(True)
        dialog.resize(400, 280)
        dialog.setStyleSheet("""
            QDialog {
                background-color: #252526;
            }
            QLabel {
                color: #C8C8C8;
            }
            QLineEdit, QComboBox {
                background-color: #3C3C3C;
                border: 1px solid #3E3E42;
                border-radius: 4px;
                padding: 5px;
                color: #C8C8C8;
            }
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
        
        layout = QtWidgets.QFormLayout(dialog)
        layout.setLabelAlignment(QtCore.Qt.AlignRight)
        layout.setSpacing(12)
        
        name_edit = QtWidgets.QLineEdit()
        name_edit.setPlaceholderText("نام پرسنل")
        layout.addRow("نام:", name_edit)
        
        position_edit = QtWidgets.QLineEdit()
        position_edit.setPlaceholderText("سمت (اختیاری)")
        layout.addRow("سمت:", position_edit)
        
        access_combo = QtWidgets.QComboBox()
        access_combo.addItem("کارمند عادی (فقط خودش)", 1)
        access_combo.addItem("سرپرست (خودش + زیردستان)", 2)
        access_combo.addItem("مدیر (خودش + زیردستان + واحد)", 3)
        access_combo.addItem("معاون (کل معاونت)", 4)
        access_combo.addItem("مدیرعامل (کل سازمان)", 5)
        access_combo.addItem("ادمین (دسترسی کامل)", 6)
        layout.addRow("سطح دسترسی:", access_combo)
        
        btn_layout = QtWidgets.QHBoxLayout()
        ok_btn = QtWidgets.QPushButton("ذخیره")
        cancel_btn = QtWidgets.QPushButton("انصراف")
        cancel_btn.setStyleSheet("background-color: #3C3C3C; color: #C8C8C8; border: 1px solid #3E3E42;")
        cancel_btn.clicked.connect(dialog.reject)
        ok_btn.clicked.connect(dialog.accept)
        btn_layout.addWidget(ok_btn)
        btn_layout.addWidget(cancel_btn)
        layout.addRow(btn_layout)
        
        if dialog.exec_() != QtWidgets.QDialog.Accepted:
            return
        
        name = name_edit.text().strip()
        if not name:
            QtWidgets.QMessageBox.warning(self, "خطا", "لطفاً نام پرسنل را وارد کنید")
            return
        
        position = position_edit.text().strip()
        access_level = access_combo.currentData()
        
        self.db.db.execute_query(
            "INSERT INTO org_personnel (name, position, unit_id, access_level, tasks_count) VALUES (%s, %s, %s, %s, %s)",
            (name, position if position else None, unit_id, access_level, 0)
        )
        
        self.load_data()
        self.current_item = None
        QtWidgets.QMessageBox.information(self, "موفق", f"پرسنل «{name}» با سطح دسترسی {access_combo.currentText()} اضافه شد")

    def new_chart(self):
        reply = QtWidgets.QMessageBox.question(self, "شروع از ابتدا", 
                                               "آیا از پاک کردن کامل ساختار سازمانی مطمئن هستید؟",
                                               QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)
        if reply == QtWidgets.QMessageBox.Yes:
            self.db.db.execute_query("DELETE FROM org_personnel")
            self.db.db.execute_query("DELETE FROM org_units")
            self.load_data()

    def search_items(self, text):
        if not text:
            iterator = QtWidgets.QTreeWidgetItemIterator(self.tree)
            while iterator.value():
                iterator.value().setHidden(False)
                iterator += 1
            self.collapse_all()
            return
        
        iterator = QtWidgets.QTreeWidgetItemIterator(self.tree)
        while iterator.value():
            iterator.value().setHidden(True)
            iterator += 1
        
        iterator = QtWidgets.QTreeWidgetItemIterator(self.tree)
        while iterator.value():
            item = iterator.value()
            if text.lower() in item.text(0).lower():
                item.setHidden(False)
                parent = item.parent()
                while parent:
                    parent.setExpanded(True)
                    parent.setHidden(False)
                    parent = parent.parent()
            iterator += 1

    def expand_all(self):
        self.tree.expandAll()

    def collapse_all(self):
        self.tree.collapseAll()