"""
ثابت‌ها و تنظیمات عمومی برنامه ERP-Aqua
"""

# ==================== اطلاعات برنامه ====================
APP_NAME = "ERP-Aqua"
APP_VERSION = "1.0.0"
APP_COMPANY = "شرکت توسعه دهنده"
APP_WEBSITE = "www.example.com"

# ==================== مسیرهای پیش‌فرض ====================
DEFAULT_DATA_FILE = "data/farms.json"
DEFAULT_SETTINGS_FILE = "data/settings.json"
DEFAULT_LOGO_FOLDER = "company_logos"
DEFAULT_LOG_FOLDER = "logs"
DEFAULT_EXPORT_FOLDER = "exports"

# ==================== تنظیمات نقشه (Graphics View) ====================
DEFAULT_ZOOM_FACTOR = 1.2
DEFAULT_BUOY_SIZE = 28
DEFAULT_ANCHOR_WIDTH = 22
DEFAULT_ANCHOR_HEIGHT = 16

# ==================== رنگ‌های پیش‌فرض اجزا ====================
DEFAULT_BUOY_COLOR = "#A0A0A0"
DEFAULT_ANCHOR_COLOR = "#6A9955"
DEFAULT_CHAIN_COLOR = "#C58688"
DEFAULT_ROPE_COLOR = "#C8C8C8"
DEFAULT_BUOY_CHAIN_COLOR = "#A0A0A0"
DEFAULT_SHACKLE_COLOR = "#D4A574"
DEFAULT_BRIDLE_COLOR = "#D4A574"
DEFAULT_CAGE_COLOR = "#569CD6"
DEFAULT_NET_COLOR = "#4EC9B0"
DEFAULT_COLLECTOR_COLOR = "#CE9178"

# ==================== تنظیمات جدول ====================
TABLE_ROW_HEIGHT = 28
TABLE_ACTION_COLUMN_WIDTH = 70

# ==================== محدوده مختصات ====================
COORDINATE_MIN = -9999999
COORDINATE_MAX = 9999999

# ==================== تنظیمات دیالوگ ====================
DIALOG_MIN_WIDTH = 400
DIALOG_MIN_HEIGHT = 300

# ==================== پیام‌های خطا ====================
ERROR_EMPTY_FIELD = "لطفاً این فیلد را پر کنید"
ERROR_INVALID_DATA = "داده وارد شده معتبر نیست"
ERROR_SELECT_ITEM = "لطفاً یک مورد را انتخاب کنید"
ERROR_NO_MOORING = "لطفاً ابتدا یک مورینگ انتخاب کنید"
ERROR_NO_FARM = "لطفاً ابتدا یک مزرعه انتخاب کنید"

# ==================== پیام‌های موفقیت ====================
SUCCESS_SAVE = "داده‌ها با موفقیت ذخیره شد"
SUCCESS_LOAD = "داده‌ها با موفقیت بارگذاری شد"
SUCCESS_DELETE = "مورد با موفقیت حذف شد"

# ==================== ToolTip ها ====================
TOOLTIP_ADD_FARM = "افزودن مزرعه جدید"
TOOLTIP_EDIT_FARM = "ویرایش مزرعه"
TOOLTIP_DELETE_FARM = "حذف مزرعه"
TOOLTIP_ADD_MOORING = "افزودن مورینگ جدید"
TOOLTIP_EDIT_MOORING = "ویرایش مورینگ"
TOOLTIP_DELETE_MOORING = "حذف مورینگ"
TOOLTIP_SAVE = "ذخیره داده‌ها در فایل"
TOOLTIP_LOAD = "بارگذاری داده‌ها از فایل"
TOOLTIP_FINAL_LIST = "نمایش لیست کامل اجزای مورینگ"


# ==================== استایل‌های دکمه‌ها ====================

# استایل دکمه شیشه‌ای برای آیکون‌های بالای نقشه
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

# استایل آیکون‌های کوچک لیست اجزا
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

# استایل پنل شیشه‌ای
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

# استایل تب‌ها (برای دیالوگ لیست نهایی)
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