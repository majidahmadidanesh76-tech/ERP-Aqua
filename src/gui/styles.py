"""
تم حرفه‌ای "دریای آبی" برای ERP-Aqua
فقط استایل - بدون تغییر در منطق برنامه
"""

STYLE = """
/* ======================================================
   تم "دریای آبی" - مخصوص ERP-Aqua
   ====================================================== */

* {
    font-family: 'Segoe UI', 'Vazir', 'IranSans', Tahoma, Geneva, Verdana, sans-serif;
    font-size: 12px;
}

/* ========== پس‌زمینه اصلی ========== */
QMainWindow, QWidget {
    background-color: #F0F4F9;
    color: #1E2A3A;
}

/* ========== سایدبار با رنگ آبی ملایم ========== */
.sidebar {
    background-color: #2B8CC4;
    border-right: none;
}

.sidebar QPushButton {
    background-color: transparent;
    color: #FFFFFF;
    font-size: 12px;
    font-weight: 600;
    text-align: left;
    padding: 8px 0px 8px 32px;
    border: none;
    border-radius: 8px;
    margin: 2px 8px;
    min-height: 32px;
}

.sidebar QPushButton:hover {
    background-color: rgba(255, 255, 255, 0.15);
}

.sidebar QPushButton:pressed {
    background-color: rgba(255, 255, 255, 0.25);
}

.sidebar QPushButton::icon {
    margin-right: 8px;
}

/* ========== منوی افقی ========== */
QMenuBar {
    background-color: #FFFFFF;
    color: #1E2A3A;
    border-bottom: 1px solid #DCE5ED;
    font-weight: 500;
}

QMenuBar::item {
    background-color: transparent;
    padding: 8px 16px;
    border-radius: 8px;
}

QMenuBar::item:selected {
    background-color: #E6F0FA;
    color: #1A7AB5;
}

QMenu {
    background-color: #FFFFFF;
    color: #1E2A3A;
    border: 1px solid #DCE5ED;
    border-radius: 12px;
    padding: 6px;
}

QMenu::item {
    padding: 8px 32px 8px 16px;
    border-radius: 8px;
    margin: 2px;
}

QMenu::item:selected {
    background-color: #E6F0FA;
    color: #1A7AB5;
}

/* ========== جدول‌ها ========== */
QTableWidget {
    background-color: #FFFFFF;
    border: 2px solid #2B8CC4;
    border-radius: 12px;
    gridline-color: #E8EDF2;
    selection-background-color: #D6E9FF;
    selection-color: #0A5C8E;
    outline: none;
}

QTableWidget::item {
    padding: 10px 12px;
    border-bottom: 1px solid #E8EDF2;
    color: #1E2A3A;
    font-weight: 500;
}

QTableWidget::item:hover {
    background-color: #F5F9FF;
}

QTableWidget::item:selected {
    background-color: #D6E9FF;
    color: #0A5C8E;
    border-left: 3px solid #2B8CC4;
}

QHeaderView::section {
    background-color: #2B8CC4;
    color: #FFFFFF;
    padding: 10px 12px;
    border: none;
    font-weight: 700;
    font-size: 12px;
}

/* ========== دکمه‌های ستون عملیات - آیکون‌های قابل مشاهده ========== */
QTableWidget QToolButton {
    background-color: #E8F0FE;
    border: 1px solid #2B8CC4;
    border-radius: 6px;
    padding: 6px;
    min-width: 28px;
    min-height: 28px;
}

QTableWidget QToolButton:hover {
    background-color: #2B8CC4;
}

QTableWidget QToolButton:hover QToolButton::icon {
    color: white;
}

QTableWidget QToolButton:pressed {
    background-color: #1A7AB5;
}

/* ========== کامبوباکس ========== */
QComboBox {
    background-color: #FFFFFF;
    border: 1px solid #D0D8E0;
    border-radius: 10px;
    padding: 7px 14px;
    color: #1E2A3A;
}

QComboBox:hover {
    border-color: #2B8CC4;
    background-color: #F5F9FF;
}

/* ========== دکمه‌ها ========== */
QPushButton {
    background-color: #2B8CC4;
    color: white;
    border: none;
    border-radius: 10px;
    padding: 8px 16px;
    font-weight: 600;
}

QPushButton:hover {
    background-color: #1A7AB5;
}

QPushButton:pressed {
    background-color: #0A5C8E;
}

/* دکمه ثانویه */
QPushButton[secondary="true"] {
    background-color: #EFF3F8;
    color: #2B8CC4;
    border: 1px solid #D0D8E0;
}

QPushButton[secondary="true"]:hover {
    background-color: #E6F0FA;
    border-color: #2B8CC4;
}

/* دکمه موفقیت */
QPushButton[success="true"] {
    background-color: #0F9D58;
}

QPushButton[success="true"]:hover {
    background-color: #0B8043;
}

/* دکمه خطر */
QPushButton[danger="true"] {
    background-color: #DB4437;
}

QPushButton[danger="true"]:hover {
    background-color: #C5221F;
}

/* ========== دکمه‌های ابزار ========== */
QToolButton {
    background-color: transparent;
    border: none;
    padding: 6px;
    border-radius: 8px;
    color: #5F6C80;
}

QToolButton:hover {
    background-color: #E6F0FA;
    color: #2B8CC4;
}

/* دکمه شیشه‌ای */
.glass-btn {
    background-color: rgba(255, 255, 255, 0.9);
    border: 1px solid rgba(43, 140, 196, 0.4);
    border-radius: 10px;
    padding: 6px;
}

.glass-btn:hover {
    background-color: #FFFFFF;
    border-color: #2B8CC4;
}

/* ========== لیست ویجت ========== */
QListWidget {
    background-color: #FFFFFF;
    border: 1px solid #DCE5ED;
    border-radius: 12px;
    padding: 6px;
}

QListWidget::item {
    padding: 8px 14px;
    border-radius: 8px;
    margin: 2px;
}

QListWidget::item:hover {
    background-color: #E6F0FA;
}

QListWidget::item:selected {
    background-color: #D6E9FF;
    color: #0A5C8E;
}

/* ========== نقشه ========== */
QGraphicsView {
    background-color: #FFFFFF !important;
    border: 1px solid rgba(43, 140, 196, 0.2) !important;
    border-radius: 16px !important;
}

/* ========== اسکرول بار ========== */
QScrollBar:vertical {
    background-color: #F0F2F5;
    width: 7px;
    border-radius: 3px;
}

QScrollBar::handle:vertical {
    background-color: #B0C4DE;
    border-radius: 3px;
    min-height: 30px;
}

QScrollBar::handle:vertical:hover {
    background-color: #2B8CC4;
}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0px;
}

/* ========== دیالوگ‌ها ========== */
QDialog {
    background-color: #FFFFFF;
    border-radius: 16px;
}

QDialog QLabel {
    color: #1E2A3A;
}

QDialog QLineEdit, QDialog QComboBox, QDialog QDoubleSpinBox, 
QDialog QSpinBox, QDialog QTextEdit, QDialog QDateEdit {
    background-color: #FFFFFF;
    border: 1px solid #D0D8E0;
    border-radius: 10px;
    padding: 8px 14px;
    color: #1E2A3A;
}

QDialog QLineEdit:focus, QDialog QComboBox:focus {
    border-color: #2B8CC4;
}

QDialog QPushButton {
    background-color: #2B8CC4;
    color: white;
    border: none;
    border-radius: 10px;
    padding: 8px 20px;
    font-weight: 600;
}

QDialog QPushButton:hover {
    background-color: #1A7AB5;
}

QDialog QPushButton:last-child {
    background-color: #EFF3F8;
    color: #1E2A3A;
    border: 1px solid #D0D8E0;
}

QDialog QPushButton:last-child:hover {
    background-color: #E6F0FA;
    border-color: #2B8CC4;
}

/* ========== تب‌ها ========== */
QTabWidget::pane {
    border: none;
    border-radius: 12px;
    background-color: #FFFFFF;
}

QTabBar::tab {
    background-color: transparent;
    color: #5F6C80;
    padding: 10px 20px;
    margin: 2px;
    border-radius: 10px;
    font-weight: 500;
}

QTabBar::tab:selected {
    background-color: #2B8CC4;
    color: white;
}

QTabBar::tab:hover:!selected {
    background-color: #E6F0FA;
    color: #2B8CC4;
}

/* ========== ToolTip ========== */
QToolTip {
    background-color: #1E2A3A;
    color: #FFFFFF;
    border: none;
    font-size: 11px;
    padding: 6px 14px;
    border-radius: 10px;
}

/* ========== Group Box ========== */
QGroupBox {
    color: #2B8CC4;
    border: 1px solid #DCE5ED;
    border-radius: 12px;
    margin-top: 12px;
    padding-top: 12px;
    font-weight: 600;
}

QGroupBox::title {
    subcontrol-origin: margin;
    left: 12px;
    padding: 0 10px;
}

/* ========== پیام خطا ========== */
QMessageBox QLabel {
    color: #1E2A3A;
}

QMessageBox QPushButton {
    min-width: 80px;
}
"""

# ==================== استایل‌های کمکی ====================

GLASS_BTN_STYLE = """
    QToolButton {
        background-color: rgba(255, 255, 255, 0.9);
        border: 1px solid rgba(43, 140, 196, 0.4);
        border-radius: 10px;
        padding: 6px;
    }
    QToolButton:hover {
        background-color: #FFFFFF;
        border-color: #2B8CC4;
    }
"""

SMALL_ICON_STYLE = """
    QToolButton {
        background-color: #F8FAFE;
        border: none;
        border-radius: 10px;
        padding: 6px;
        min-width: 34px;
        min-height: 34px;
    }
    QToolButton:hover {
        background-color: #E6F0FA;
        border: 1px solid #2B8CC4;
    }
    QToolButton:checked {
        background-color: #D6E9FF;
        border: 2px solid #2B8CC4;
    }
"""

GLASS_PANEL_STYLE = """
    QWidget {
        background-color: rgba(255, 255, 255, 0.95);
        border-radius: 16px;
        border: 1px solid rgba(43, 140, 196, 0.3);
        margin: 4px;
    }
"""

TAB_STYLE = """
    QTabWidget::pane {
        border: none;
        border-radius: 12px;
        background-color: #FFFFFF;
    }
    QTabBar::tab {
        background-color: transparent;
        color: #5F6C80;
        padding: 8px 18px;
        margin: 2px;
        border: none;
        font-weight: 500;
        border-radius: 8px;
    }
    QTabBar::tab:selected {
        background-color: #2B8CC4;
        color: white;
    }
    QTabBar::tab:hover:!selected {
        background-color: #E6F0FA;
        color: #2B8CC4;
    }
"""

SUCCESS_BTN_STYLE = """
    QPushButton {
        background-color: #0F9D58;
        color: white;
        border: none;
        border-radius: 10px;
        padding: 8px 18px;
        font-weight: 600;
    }
    QPushButton:hover {
        background-color: #0B8043;
    }
"""

WARNING_BTN_STYLE = """
    QPushButton {
        background-color: #F4B400;
        color: white;
        border: none;
        border-radius: 10px;
        padding: 8px 18px;
        font-weight: 600;
    }
    QPushButton:hover {
        background-color: #E37400;
    }
"""

DANGER_BTN_STYLE = """
    QPushButton {
        background-color: #DB4437;
        color: white;
        border: none;
        border-radius: 10px;
        padding: 8px 18px;
        font-weight: 600;
    }
    QPushButton:hover {
        background-color: #C5221F;
    }
"""