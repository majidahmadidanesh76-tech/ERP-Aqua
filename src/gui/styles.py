"""
تم و استایل‌های برنامه ERP-Aqua
شامل تمام تنظیمات ظاهری برنامه
"""

STYLE = """
* {
    font-family: 'Segoe UI', 'IranSans', Tahoma, Geneva, Verdana, sans-serif;
    font-size: 12px;
}

QMainWindow, QWidget {
    background-color: #1E1E1E;
}

/* ==================== منوی کناری (سایدبار) ==================== */
.sidebar {
    background-color: #252526;
    border-left: 1px solid #3E3E42;
}

.sidebar QPushButton {
    background-color: #252526;
    color: #C8C8C8;
    font-size: 13px;
    font-weight: normal;
    text-align: left;
    padding-left: 40px;
    border: none;
    border-radius: 0px;
    margin: 0px;
    height: 35px;
}

.sidebar QPushButton:hover {
    background-color: #2A2D2E;
    color: #FFFFFF;
    border-left: 3px solid #569CD6;
}

.sidebar QPushButton:pressed {
    background-color: #37373D;
}

/* ==================== منوی افقی بالای صفحه ==================== */
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

QMenuBar::item:pressed {
    background-color: #264F78;
}

QMenu {
    background-color: #252526;
    color: #C8C8C8;
    border: 1px solid #3E3E42;
    border-radius: 4px;
    padding: 4px;
}

QMenu::item {
    padding: 5px 30px 5px 20px;
    border-radius: 4px;
    margin: 2px;
}

QMenu::item:selected {
    background-color: #2A2D2E;
    color: #569CD6;
}

QMenu::separator {
    height: 1px;
    background-color: #3E3E42;
    margin: 4px 8px;
}

/* ==================== جدول‌ها ==================== */
QTableWidget {
    background-color: #2D2D30;
    border: 1px solid #3E3E42;
    border-radius: 4px;
    gridline-color: #3E3E42;
    selection-background-color: #264F78;
    selection-color: #FFFFFF;
}

QTableWidget::item {
    padding: 4px 6px;
    border-bottom: 1px solid #3E3E42;
    color: #C8C8C8;
}

QTableWidget::item:hover {
    background-color: #3E3E42;
}

QHeaderView::section {
    background-color: #252526;
    color: #C8C8C8;
    padding: 4px 6px;
    border: none;
    border-bottom: 1px solid #3E3E42;
    font-weight: bold;
    height: 26px;
}

/* ==================== کامبوباکس ==================== */
QComboBox {
    background-color: #3C3C3C;
    border: 1px solid #3E3E42;
    border-radius: 4px;
    padding: 5px 10px;
    min-width: 130px;
    color: #C8C8C8;
}

QComboBox:hover {
    border-color: #569CD6;
}

QComboBox::drop-down {
    border: none;
    width: 0px;
}

QComboBox::down-arrow {
    image: none;
}

/* ==================== دکمه‌های ابزار ==================== */
QToolButton {
    background-color: transparent;
    border: none;
    padding: 3px;
    border-radius: 4px;
}

QToolButton:hover {
    background-color: rgba(86, 156, 214, 50);
}

QToolButton:pressed {
    background-color: rgba(86, 156, 214, 100);
}

/* دکمه شیشه‌ای برای زوم */
.glass-btn {
    background-color: rgba(60, 60, 60, 180);
    border: 1px solid rgba(86, 156, 214, 100);
    border-radius: 6px;
}

.glass-btn:hover {
    background-color: rgba(86, 156, 214, 150);
}

/* ==================== لیست ویجت ==================== */
QListWidget {
    background-color: #252526;
    border: 1px solid #3E3E42;
    border-radius: 4px;
    padding: 2px;
    color: #C8C8C8;
}

QListWidget::item {
    padding: 2px 6px;
    border-radius: 3px;
    margin: 1px;
    height: 24px;
}

QListWidget::item:hover {
    background-color: #2A2D2E;
}

QListWidget::item:selected {
    background-color: #264F78;
    color: #FFFFFF;
}

/* ==================== نقشه ==================== */
QGraphicsView {
    background-color: #2D2D30 !important;
    border: 1px solid #3E3E42 !important;
    border-radius: 6px !important;
}

/* ==================== اسکرول بار ==================== */
QScrollBar:vertical {
    background-color: #1E1E1E;
    width: 8px;
}

QScrollBar::handle:vertical {
    background-color: #686868;
    border-radius: 4px;
    min-height: 30px;
}

QScrollBar::handle:vertical:hover {
    background-color: #8A8A8A;
}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0px;
}

/* ==================== دیالوگ‌ها ==================== */
QDialog {
    background-color: #252526;
}

QDialog QLabel {
    color: #C8C8C8;
}

QDialog QLineEdit, QDialog QComboBox, QDialog QDoubleSpinBox, QDialog QSpinBox {
    background-color: #3C3C3C;
    border: 1px solid #3E3E42;
    border-radius: 4px;
    padding: 5px 8px;
    color: #C8C8C8;
}

QDialog QLineEdit:focus, QDialog QComboBox:focus {
    border-color: #569CD6;
}

QDialog QPushButton {
    background-color: #0E639C;
    color: white;
    border: none;
    border-radius: 4px;
    padding: 5px 14px;
}

QDialog QPushButton:hover {
    background-color: #1177BB;
}

/* ==================== ToolTip ==================== */
QToolTip {
    background-color: #0E639C;
    color: #FFFFFF;
    border: none;
    font-size: 11px;
    padding: 4px 8px;
    border-radius: 4px;
}
"""


# ==================== استایل دکمه شیشه‌ای برای آیکون‌ها ====================

GLASS_BTN_STYLE = """
    QToolButton {
        background-color: transparent;
        border: none;
        padding: 5px;
        border-radius: 6px;
    }
    QToolButton:hover {
        background-color: rgba(86, 156, 214, 60);
    }
    QToolButton:pressed {
        background-color: rgba(86, 156, 214, 100);
    }
    QToolButton:checked {
        background-color: rgba(86, 156, 214, 120);
        border: 1px solid rgba(86, 156, 214, 200);
    }
"""


# ==================== استایل آیکون‌های کوچک لیست ====================

SMALL_ICON_STYLE = """
    QToolButton {
        background-color: rgba(60, 60, 65, 180);
        border: none;
        border-radius: 4px;
        padding: 2px;
        min-width: 24px;
        min-height: 24px;
    }
    QToolButton:hover {
        background-color: rgba(86, 156, 214, 100);
    }
    QToolButton:checked {
        background-color: rgba(86, 156, 214, 160);
        border: 1px solid rgba(86, 156, 214, 200);
    }
"""


# ==================== استایل پنل شیشه‌ای ====================

GLASS_PANEL_STYLE = """
    QWidget {
        background-color: rgba(37, 37, 38, 220);
        border-radius: 8px;
        border: 1px solid rgba(86, 156, 214, 80);
        margin: 2px;
    }
    QWidget:hover {
        border-color: rgba(86, 156, 214, 150);
    }
"""


# ==================== استایل تب‌ها (برای دیالوگ لیست نهایی) ====================

TAB_STYLE = """
    QTabWidget::pane {
        border: 1px solid #3E3E42;
        border-radius: 4px;
        background-color: #1E1E1E;
    }
    QTabBar::tab {
        background-color: #2D2D30;
        color: #C8C8C8;
        padding: 4px 10px;
        margin: 1px;
        border: none;
        font-weight: bold;
    }
    QTabBar::tab:selected {
        background-color: #1E1E1E;
        color: #569CD6;
        border-bottom: 2px solid #569CD6;
    }
    QTabBar::tab:hover:!selected {
        background-color: #37373D;
        color: #FFFFFF;
    }
"""