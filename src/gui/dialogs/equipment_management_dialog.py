"""
دیالوگ مدیریت انواع تجهیزات (اطلاعات پایه)
"""

from PyQt5 import QtWidgets, QtCore
import qtawesome as qta
from ...database.db_handler import DatabaseHandler
from .dialog_style import DIALOG_STYLE, BUTTON_STYLE, CANCEL_BUTTON_STYLE
from .equipment_dialog import EquipmentDialog

class EquipmentManagementDialog(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet(DIALOG_STYLE)
        self.db = DatabaseHandler()
        self.setWindowTitle("🛠️ مدیریت انواع تجهیزات")
        self.setModal(True)
        self.resize(650, 450)
        self.setup_ui()
        self.load_data()

    def setup_ui(self):
        layout = QtWidgets.QVBoxLayout(self)
        layout.setSpacing(10)
        layout.setContentsMargins(15, 15, 15, 15)

        # عنوان
        title = QtWidgets.QLabel("مدیریت انواع تجهیزات")
        title.setAlignment(QtCore.Qt.AlignCenter)
        title.setStyleSheet("font-size: 16px; font-weight: bold; color: #569CD6; padding: 5px;")
        layout.addWidget(title)

        # نوار ابزار
        toolbar = QtWidgets.QHBoxLayout()
        toolbar.setSpacing(10)

        self.add_btn = QtWidgets.QPushButton("➕ افزودن")
        self.add_btn.setFixedSize(100, 32)
        self.add_btn.setStyleSheet(BUTTON_STYLE)
        self.add_btn.clicked.connect(self.add_equipment)

        self.edit_btn = QtWidgets.QPushButton("✏️ ویرایش")
        self.edit_btn.setFixedSize(100, 32)
        self.edit_btn.setStyleSheet(BUTTON_STYLE)
        self.edit_btn.clicked.connect(self.edit_equipment)

        self.delete_btn = QtWidgets.QPushButton("🗑️ حذف")
        self.delete_btn.setFixedSize(100, 32)
        self.delete_btn.setStyleSheet(BUTTON_STYLE)
        self.delete_btn.clicked.connect(self.delete_equipment)

        self.refresh_btn = QtWidgets.QPushButton("🔄 بازخوانی")
        self.refresh_btn.setFixedSize(100, 32)
        self.refresh_btn.setStyleSheet(BUTTON_STYLE)
        self.refresh_btn.clicked.connect(self.load_data)

        toolbar.addWidget(self.add_btn)
        toolbar.addWidget(self.edit_btn)
        toolbar.addWidget(self.delete_btn)
        toolbar.addWidget(self.refresh_btn)
        toolbar.addStretch()
        layout.addLayout(toolbar)

        # جدول تجهیزات
        self.table = QtWidgets.QTableWidget()
        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels(["شناسه", "نام تجهیز", "عنوان نمایشی"])
        self.table.setColumnWidth(0, 80)
        self.table.setColumnWidth(1, 200)
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self.table.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.table.setAlternatingRowColors(True)
        self.table.setStyleSheet("""
            QTableWidget {
                border: 1px solid #3E3E42;
                border-radius: 4px;
                background-color: #2D2D30;
                alternate-background-color: #252526;
                gridline-color: #3E3E42;
            }
            QTableWidget::item {
                padding: 6px;
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
                padding: 6px;
                font-weight: bold;
            }
        """)
        layout.addWidget(self.table)

        # دکمه بستن
        btn_close = QtWidgets.QPushButton("بستن")
        btn_close.setFixedSize(100, 32)
        btn_close.setStyleSheet(BUTTON_STYLE)
        btn_close.clicked.connect(self.accept)
        
        close_layout = QtWidgets.QHBoxLayout()
        close_layout.addStretch()
        close_layout.addWidget(btn_close)
        layout.addLayout(close_layout)

    def load_data(self):
        """بارگذاری دادهها از دیتابیس"""
        equipments = self.db.fetch_all("SELECT id, name, display_name FROM equipment_types ORDER BY name")
        self.table.setRowCount(len(equipments))
        
        for i, eq in enumerate(equipments):
            self.table.setItem(i, 0, QtWidgets.QTableWidgetItem(str(eq['id'])))
            self.table.setItem(i, 1, QtWidgets.QTableWidgetItem(eq['name']))
            self.table.setItem(i, 2, QtWidgets.QTableWidgetItem(eq['display_name'] or ""))
        
        if len(equipments) == 0:
            self.table.setRowCount(1)
            self.table.setSpan(0, 0, 1, 3)
            empty_item = QtWidgets.QTableWidgetItem("هیچ تجهیزی تعریف نشده است")
            empty_item.setTextAlignment(QtCore.Qt.AlignCenter)
            self.table.setItem(0, 0, empty_item)

    def add_equipment(self):
        """افزودن تجهیز جدید"""
        dialog = EquipmentDialog(self, db=self.db)
        if dialog.exec_():
            data = dialog.get_data()
            if data['name']:
                # بررسی عدم تکراری بودن
                existing = self.db.fetch_one("SELECT id FROM equipment_types WHERE name = %s", (data['name'],))
                if existing:
                    QtWidgets.QMessageBox.warning(self, "خطا", f"تجهیز با نام '{data['name']}' قبلاً وجود دارد")
                    return
                
                self.db.execute_query("""
                    INSERT INTO equipment_types (name, display_name)
                    VALUES (%s, %s)
                """, (data['name'], data['display_name']))
                self.load_data()
                QtWidgets.QMessageBox.information(self, "موفق", "تجهیز جدید با موفقیت اضافه شد")

    def edit_equipment(self):
        """ویرایش تجهیز انتخاب شده"""
        current_row = self.table.currentRow()
        if current_row < 0 or self.table.rowCount() == 0:
            QtWidgets.QMessageBox.warning(self, "خطا", "لطفاً یک ردیف را انتخاب کنید")
            return
        
        if self.table.item(current_row, 0) is None:
            return
        
        eq_id = int(self.table.item(current_row, 0).text())
        eq = self.db.fetch_one("SELECT * FROM equipment_types WHERE id = %s", (eq_id,))
        
        if eq:
            dialog = EquipmentDialog(self, equipment=eq, db=self.db)
            if dialog.exec_():
                data = dialog.get_data()
                self.db.execute_query("""
                    UPDATE equipment_types 
                    SET name = %s, display_name = %s
                    WHERE id = %s
                """, (data['name'], data['display_name'], eq_id))
                self.load_data()
                QtWidgets.QMessageBox.information(self, "موفق", "تجهیز با موفقیت ویرایش شد")

    def delete_equipment(self):
        """حذف تجهیز انتخاب شده"""
        current_row = self.table.currentRow()
        if current_row < 0 or self.table.rowCount() == 0:
            QtWidgets.QMessageBox.warning(self, "خطا", "لطفاً یک ردیف را انتخاب کنید")
            return
        
        if self.table.item(current_row, 0) is None:
            return
        
        eq_id = int(self.table.item(current_row, 0).text())
        eq_name = self.table.item(current_row, 1).text()

        # بررسی استفاده در برنامه‌های نت
        used = self.db.fetch_one("SELECT COUNT(*) as cnt FROM maintenance_plans WHERE asset_type = %s", (eq_name,))
        if used and used['cnt'] > 0:
            QtWidgets.QMessageBox.warning(self, "خطا", 
                f"این تجهیز در {used['cnt']} برنامه نت استفاده شده است. ابتدا آن برنامه‌ها را حذف یا ویرایش کنید.")
            return

        reply = QtWidgets.QMessageBox.question(self, "تأیید حذف", 
            f"آیا از حذف تجهیز '{eq_name}' مطمئن هستید؟",
            QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)
        
        if reply == QtWidgets.QMessageBox.Yes:
            self.db.execute_query("DELETE FROM equipment_types WHERE id = %s", (eq_id,))
            self.load_data()
            QtWidgets.QMessageBox.information(self, "موفق", "تجهیز با موفقیت حذف شد")