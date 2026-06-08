"""
صفحه برنامهریزی تولید - کانتینر تب‌ها
"""

from PyQt5 import QtWidgets, QtCore, QtGui
import qtawesome as qta

from .tabs.production_tab import ProductionTab
from .tabs.maintenance_tab import MaintenanceTab
from .tabs.smart_tab import SmartTab
from .tabs.gantt_tab import GanttTab


class ProductionPlanningTab(QtWidgets.QWidget):
    def __init__(self, parent=None, farm=None, mooring=None):
        super().__init__(parent)
        self.current_farm = farm
        self.current_mooring = mooring
        self.setup_ui()

    def setup_ui(self):
        layout = QtWidgets.QVBoxLayout(self)
        layout.setSpacing(10)
        layout.setContentsMargins(10, 10, 10, 10)

        title = QtWidgets.QLabel("📋 برنامهریزی تولید حرفهای")
        title.setAlignment(QtCore.Qt.AlignCenter)
        title.setStyleSheet("font-size: 18px; font-weight: bold; color: #569CD6; padding: 10px;")
        layout.addWidget(title)

        self.main_tabs = QtWidgets.QTabWidget()
        self.main_tabs.setStyleSheet("""
            QTabWidget::pane {
                border: 1px solid #3E3E42;
                border-radius: 4px;
                background: #1E1E1E;
            }
            QTabBar::tab {
                background-color: #2D2D30;
                color: #C8C8C8;
                padding: 8px 20px;
                margin: 2px;
                border-radius: 4px;
            }
            QTabBar::tab:selected {
                background-color: #0E639C;
                color: white;
            }
        """)

        # تب پرورش
        self.production_tab = ProductionTab(self.current_farm, self.current_mooring)
        self.main_tabs.addTab(self.production_tab, "🐟 برنامه پرورش")

        # تب نت
        self.maintenance_tab = MaintenanceTab()
        self.main_tabs.addTab(self.maintenance_tab, "🛠️ برنامه نت")

        # تب پیشنهادات هوشمند
        self.smart_tab = SmartTab()
        self.main_tabs.addTab(self.smart_tab, "🤖 پیشنهادات هوشمند")

        # تب گانت
        self.gantt_tab = GanttTab()
        self.main_tabs.addTab(self.gantt_tab, "📊 نمای گانت")

        layout.addWidget(self.main_tabs)