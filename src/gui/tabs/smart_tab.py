"""
تب پیشنهادات هوشمند
"""

from PyQt5 import QtWidgets, QtCore, QtGui
import qtawesome as qta

from ...database.db_handler import DatabaseHandler


class SmartTab(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.db = DatabaseHandler()
        self.setup_ui()
        self.load_data()

    def setup_ui(self):
        layout = QtWidgets.QVBoxLayout(self)
        layout.setSpacing(10)
        layout.setContentsMargins(10, 10, 10, 10)

        title = QtWidgets.QLabel("🤖 پیشنهادات هوشمند سیستم")
        title.setAlignment(QtCore.Qt.AlignCenter)
        title.setStyleSheet("font-size: 14px; font-weight: bold; color: #569CD6; padding: 5px;")
        layout.addWidget(title)

        # نوار ابزار
        toolbar = QtWidgets.QHBoxLayout()
        
        glass_icon_style = """
            QToolButton {
                background-color: rgba(60, 60, 65, 180);
                border: 1px solid rgba(86, 156, 214, 80);
                border-radius: 3px;
            }
            QToolButton:hover { background-color: rgba(86, 156, 214, 100); }
        """

        self.refresh_btn = QtWidgets.QToolButton()
        self.refresh_btn.setIcon(qta.icon('fa5s.sync-alt', color='#C8C8C8'))
        self.refresh_btn.setFixedSize(30, 30)
        self.refresh_btn.setStyleSheet(glass_icon_style)
        self.refresh_btn.setToolTip("بروزرسانی پیشنهادات")
        self.refresh_btn.clicked.connect(self.load_data)
        toolbar.addWidget(self.refresh_btn)

        self.settings_btn = QtWidgets.QToolButton()
        self.settings_btn.setIcon(qta.icon('fa5s.cog', color='#C8C8C8'))
        self.settings_btn.setFixedSize(30, 30)
        self.settings_btn.setStyleSheet(glass_icon_style)
        self.settings_btn.setToolTip("تنظیمات قوانین هوشمند")
        self.settings_btn.clicked.connect(self.open_settings)
        toolbar.addWidget(self.settings_btn)

        toolbar.addStretch()
        layout.addLayout(toolbar)

        # جدول پیشنهادات
        self.table = QtWidgets.QTableWidget()
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels(["نوع", "عنوان", "توضیحات", "اولویت", "تاریخ پیشنهادی", "دلیل", "عملیات"])
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.setColumnWidth(0, 80)
        self.table.setColumnWidth(1, 150)
        self.table.setColumnWidth(2, 200)
        self.table.setColumnWidth(3, 60)
        self.table.setColumnWidth(4, 100)
        self.table.setColumnWidth(5, 200)
        self.table.setColumnWidth(6, 100)
        self.table.verticalHeader().setDefaultSectionSize(45)
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
                padding: 6px 4px;
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

    def load_data(self):
        """بارگذاری پیشنهادات هوشمند از دیتابیس"""
        suggestions = self.db.get_ai_suggestions()
        self.table.setRowCount(len(suggestions))

        type_names = {
            'alert': '⚠️ هشدار',
            'feeding': '🍽️ تغذیه',
            'maintenance': '🛠️ نت',
            'harvest': '💰 برداشت',
            'inspection': '🔍 بازرسی',
            'strategic': '📊 استراتژیک'
        }

        priority_colors = {1: '#F48771', 2: '#DCDCAA', 3: '#C8C8C8'}
        priority_text = {1: 'فوری', 2: 'متوسط', 3: 'کم'}

        glass_btn_style = """
            QPushButton {
                background-color: rgba(60, 60, 65, 200);
                color: #C8C8C8;
                border: 1px solid rgba(86, 156, 214, 80);
                border-radius: 4px;
                font-weight: bold;
                padding: 5px 10px;
            }
            QPushButton:hover { background-color: rgba(86, 156, 214, 100); color: white; }
        """

        for i, sug in enumerate(suggestions):
            self.table.setItem(i, 0, QtWidgets.QTableWidgetItem(type_names.get(sug['suggestion_type'], sug['suggestion_type'])))
            self.table.setItem(i, 1, QtWidgets.QTableWidgetItem(sug['title'][:50]))
            self.table.setItem(i, 2, QtWidgets.QTableWidgetItem(sug['description'][:80]))
            priority_item = QtWidgets.QTableWidgetItem(priority_text.get(sug['priority'], 'متوسط'))
            priority_item.setForeground(QtGui.QColor(priority_colors.get(sug['priority'], '#C8C8C8')))
            self.table.setItem(i, 3, priority_item)
            self.table.setItem(i, 4, QtWidgets.QTableWidgetItem(str(sug['suggested_date'] or '-')))
            self.table.setItem(i, 5, QtWidgets.QTableWidgetItem(sug['reasoning'][:100] if sug['reasoning'] else '-'))

            btn_widget = QtWidgets.QWidget()
            btn_layout = QtWidgets.QHBoxLayout(btn_widget)
            btn_layout.setContentsMargins(0, 0, 0, 0)
            btn_layout.setSpacing(5)

            if sug['status'] == 'pending':
                accept_btn = QtWidgets.QPushButton("✓ قبول")
                accept_btn.setFixedSize(60, 26)
                accept_btn.setStyleSheet(glass_btn_style.replace('rgba(86, 156, 214, 80)', '#2E8B57').replace('rgba(86, 156, 214, 100)', '#3CB371'))
                accept_btn.clicked.connect(lambda checked, sid=sug['id']: self.accept_suggestion(sid))

                reject_btn = QtWidgets.QPushButton("✗ رد")
                reject_btn.setFixedSize(60, 26)
                reject_btn.setStyleSheet(glass_btn_style.replace('rgba(86, 156, 214, 80)', '#8B2C2C').replace('rgba(86, 156, 214, 100)', '#A33C3C'))
                reject_btn.clicked.connect(lambda checked, sid=sug['id']: self.reject_suggestion(sid))

                btn_layout.addWidget(accept_btn)
                btn_layout.addWidget(reject_btn)
            else:
                status_text = "✅ پذیرفته شده" if sug['status'] == 'accepted' else "❌ رد شده"
                status_label = QtWidgets.QLabel(status_text)
                status_label.setStyleSheet("color: #808080; font-size: 11px;")
                btn_layout.addWidget(status_label)

            btn_layout.addStretch()
            self.table.setCellWidget(i, 6, btn_widget)

    def accept_suggestion(self, suggestion_id):
        """پذیرش پیشنهاد هوشمند"""
        self.db.accept_suggestion(suggestion_id)
        self.load_data()
        QtWidgets.QMessageBox.information(self, "موفق", "پیشنهاد با موفقیت پذیرفته شد")

    def reject_suggestion(self, suggestion_id):
        """رد پیشنهاد هوشمند"""
        self.db.reject_suggestion(suggestion_id)
        self.load_data()
        QtWidgets.QMessageBox.information(self, "اطلاع", "پیشنهاد رد شد")

    def open_settings(self):
        """باز کردن دیالوگ تنظیمات قوانین هوشمند"""
        try:
            from ..dialogs.smart_rules_settings_dialog import SmartRulesSettingsDialog
            dialog = SmartRulesSettingsDialog(self)
            dialog.exec_()
            self.load_data()
        except ImportError as e:
            QtWidgets.QMessageBox.warning(self, "خطا", f"فایل دیالوگ یافت نشد:\n{str(e)}")
        except Exception as e:
            QtWidgets.QMessageBox.warning(self, "خطا", f"خطا در باز کردن دیالوگ تنظیمات:\n{str(e)}")