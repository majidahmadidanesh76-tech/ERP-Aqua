"""
تقویم شمسی سفارشی برای ERP-Aqua
"""

from PyQt5 import QtWidgets, QtCore, QtGui
import jdatetime


class PersianCalendar(QtWidgets.QDialog):
    """دیالوگ تقویم شمسی"""
    
    def __init__(self, parent=None, selected_date=None):
        super().__init__(parent)
        self.setWindowTitle("انتخاب تاریخ شمسی")
        self.setModal(True)
        self.resize(380, 320)
        self.setStyleSheet("""
            QDialog {
                background-color: #252526;
            }
            QPushButton {
                background-color: #0E639C;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 5px;
            }
            QPushButton:hover {
                background-color: #1177BB;
            }
            QTableWidget {
                background-color: #2D2D30;
                border: 1px solid #3E3E42;
                gridline-color: #3E3E42;
            }
            QTableWidget::item {
                color: #C8C8C8;
            }
            QHeaderView::section {
                background-color: #252526;
                color: #569CD6;
            }
        """)
        
        self.selected_date = selected_date if selected_date else jdatetime.date.today()
        self.current_year = self.selected_date.year
        self.current_month = self.selected_date.month
        self.selected_day = self.selected_date.day
        
        self.setup_ui()
        self.show_month()
    
    def setup_ui(self):
        layout = QtWidgets.QVBoxLayout(self)
        
        # ========== عنوان سال و ماه ==========
        title_layout = QtWidgets.QHBoxLayout()
        
        self.prev_btn = QtWidgets.QPushButton("◀")
        self.prev_btn.setFixedSize(35, 30)
        self.prev_btn.clicked.connect(self.prev_month)
        title_layout.addWidget(self.prev_btn)
        
        self.month_label = QtWidgets.QLabel()
        self.month_label.setAlignment(QtCore.Qt.AlignCenter)
        self.month_label.setStyleSheet("font-size: 16px; font-weight: bold; color: #569CD6;")
        title_layout.addWidget(self.month_label)
        
        self.next_btn = QtWidgets.QPushButton("▶")
        self.next_btn.setFixedSize(35, 30)
        self.next_btn.clicked.connect(self.next_month)
        title_layout.addWidget(self.next_btn)
        
        layout.addLayout(title_layout)
        
        # ========== روزهای هفته ==========
        self.week_table = QtWidgets.QTableWidget()
        self.week_table.setColumnCount(7)
        self.week_table.setRowCount(6)
        self.week_table.horizontalHeader().setVisible(False)
        self.week_table.verticalHeader().setVisible(False)
        self.week_table.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.week_table.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        
        # تنظیم عرض ستون‌ها
        for i in range(7):
            self.week_table.setColumnWidth(i, 48)
        
        # تنظیم ارتفاع ردیف‌ها
        for i in range(6):
            self.week_table.setRowHeight(i, 38)
        
        # کلیک روی جدول
        self.week_table.cellClicked.connect(self.on_cell_clicked)
        
        layout.addWidget(self.week_table)
        
        # ========== دکمه‌ها ==========
        btn_layout = QtWidgets.QHBoxLayout()
        cancel_btn = QtWidgets.QPushButton("انصراف")
        cancel_btn.setFixedHeight(32)
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(cancel_btn)
        
        ok_btn = QtWidgets.QPushButton("انتخاب")
        ok_btn.setFixedHeight(32)
        ok_btn.clicked.connect(self.accept)
        btn_layout.addWidget(ok_btn)
        
        layout.addLayout(btn_layout)
    
    def on_cell_clicked(self, row, col):
        """کلیک روی یک سلول جدول"""
        item = self.week_table.item(row, col)
        if item and item.text().isdigit():
            # پاک کردن هایلایت قبلی
            for r in range(6):
                for c in range(7):
                    it = self.week_table.item(r, c)
                    if it and it.background().color() == QtGui.QColor("#0E639C"):
                        it.setBackground(QtGui.QColor("#2D2D30"))
                        it.setForeground(QtGui.QColor("#C8C8C8"))
            
            # هایلایت جدید
            item.setBackground(QtGui.QColor("#0E639C"))
            item.setForeground(QtGui.QColor("#FFFFFF"))
            self.selected_day = int(item.text())
    
    def show_month(self):
        """نمایش ماه جاری"""
        # نام ماه‌های شمسی
        month_names = [
            "فروردین", "اردیبهشت", "خرداد", "تیر", "مرداد", "شهریور",
            "مهر", "آبان", "آذر", "دی", "بهمن", "اسفند"
        ]
        self.month_label.setText(f"{month_names[self.current_month - 1]} {self.current_year}")
        
        # تنظیم هدر روزهای هفته
        week_days = ["ش", "ی", "د", "س", "چ", "پ", "ج"]
        for i, day in enumerate(week_days):
            item = QtWidgets.QTableWidgetItem(day)
            item.setTextAlignment(QtCore.Qt.AlignCenter)
            item.setBackground(QtGui.QColor("#252526"))
            item.setForeground(QtGui.QColor("#569CD6"))
            self.week_table.setVerticalHeaderItem(i, None)
            self.week_table.setHorizontalHeaderItem(i, item)
        
        # محاسبه روز اول ماه
        first_day = jdatetime.date(self.current_year, self.current_month, 1)
        start_weekday = first_day.weekday()  # 0=شنبه در jdatetime
        
        # تعداد روزهای ماه
        if self.current_month <= 6:
            days_in_month = 31
        elif self.current_month <= 11:
            days_in_month = 30
        else:
            # ماه اسفند
            next_year = self.current_year + 1
            try:
                jdatetime.date(next_year, 1, 1)
                days_in_month = 29
            except:
                days_in_month = 30
        
        # پاک کردن جدول
        self.week_table.clearContents()
        
        # پر کردن روزها
        row = 0
        col = start_weekday
        for day in range(1, days_in_month + 1):
            item = QtWidgets.QTableWidgetItem(str(day))
            item.setTextAlignment(QtCore.Qt.AlignCenter)
            
            # مشخص کردن روز انتخاب شده
            if day == self.selected_day and self.current_month == self.selected_date.month and self.current_year == self.selected_date.year:
                item.setBackground(QtGui.QColor("#0E639C"))
                item.setForeground(QtGui.QColor("#FFFFFF"))
            else:
                item.setBackground(QtGui.QColor("#2D2D30"))
                item.setForeground(QtGui.QColor("#C8C8C8"))
            
            self.week_table.setItem(row, col, item)
            
            col += 1
            if col >= 7:
                col = 0
                row += 1
    
    def prev_month(self):
        """ماه قبل"""
        if self.current_month == 1:
            self.current_month = 12
            self.current_year -= 1
        else:
            self.current_month -= 1
        self.show_month()
    
    def next_month(self):
        """ماه بعد"""
        if self.current_month == 12:
            self.current_month = 1
            self.current_year += 1
        else:
            self.current_month += 1
        self.show_month()
    
    def accept(self):
        """پذیرش تاریخ انتخاب شده"""
        self.selected_date = jdatetime.date(self.current_year, self.current_month, self.selected_day)
        super().accept()
    
    def get_selected_date(self):
        """دریافت تاریخ انتخاب شده به صورت رشته"""
        return f"{self.selected_date.year}/{self.selected_date.month:02d}/{self.selected_date.day:02d}"