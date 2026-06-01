"""
کلاس‌های مدل داده (Data Models) برای ERP-Aqua
شامل تمام ساختارهای داده‌ای برنامه
"""

# ==================== مدل شرکت ====================

class Company:
    """مدل اطلاعات شرکت"""
    def __init__(self):
        self.id = ""
        self.name = ""
        self.reg_no = ""
        self.address = ""
        self.phone = ""
        self.email = ""
        self.logo_path = ""


# ==================== مدل اجزای سیستم ====================

class Buoy:
    """مدل بویه"""
    def __init__(self):
        self.id = ""
        self.mooring_id = ""
        self.utm_x = 0.0
        self.utm_y = 0.0
        self.buoy_type = "main"
        self.color = "#A0A0A0"
        self.material = "پلاستیک"
        self.volume = 0.0
        self.install_date = ""
        self.has_light = False
        self.body_color = "#A0A0A0"
        self.status = "سالم"
        self.note = ""


class Anchor:
    """مدل لنگر"""
    def __init__(self):
        self.id = ""
        self.mooring_id = ""
        self.utm_x = 0.0
        self.utm_y = 0.0
        self.anchor_type = "steel"
        self.weight = 1500
        self.color = "#6A9955"
        self.material = "فولاد"
        self.install_date = ""
        self.install_depth = 0.0
        self.status = "سالم"
        self.body_color = "#6A9955"
        self.note = ""


class AnchorChain:
    """مدل زنجیر لنگر"""
    def __init__(self):
        self.id = ""
        self.mooring_id = ""
        self.start_id = ""
        self.end_id = ""
        self.start_x = 0.0
        self.start_y = 0.0
        self.end_x = 0.0
        self.end_y = 0.0
        self.diameter = 30
        self.use_manual_start = False
        self.use_manual_end = False
        self.color = "#C58688"
        self.chain_type = "ساده"
        self.material = "فولاد"
        self.install_date = ""
        self.status = "سالم"
        self.note = ""


class AnchorRope:
    """مدل طناب اصلی"""
    def __init__(self):
        self.id = ""
        self.mooring_id = ""
        self.start_id = ""
        self.end_id = ""
        self.start_x = 0.0
        self.start_y = 0.0
        self.end_x = 0.0
        self.end_y = 0.0
        self.material = "پلی پروپیلن"
        self.diameter = 64
        self.use_manual_start = False
        self.use_manual_end = False
        self.color = "#C8C8C8"
        self.strand_count = 3
        self.length = 50.0
        self.install_date = ""
        self.status = "سالم"
        self.note = ""


class BuoyChain:
    """مدل زنجیر بویه (اتصال عمودی بین بویه و کلکتور - در زیر آب)"""
    def __init__(self):
        self.id = ""
        self.mooring_id = ""
        self.diameter = 20
        self.length = 10.0
        self.material = "فولاد"
        self.chain_type = "ساده"
        self.install_date = ""
        self.status = "سالم"
        self.buoy_id = ""
        self.collector_id = ""
        self.note = ""
        # فیلدهای زیر برای سازگاری با دیالوگ لیست اجزا
        self.start_buoy_id = ""
        self.end_buoy_id = ""
        self.color = "#A0A0A0"


class Shackle:
    """مدل شاکل (اتصال‌دهنده)"""
    def __init__(self):
        self.id = ""                     # شناسه شاکل
        self.mooring_id = ""             # شناسه مورینگ
        self.shackle_type = "یو شکل"     # نوع: یو شکل / نعلی
        self.quantity = 1                # تعداد شاکل
        self.size = 25                   # سایز (mm)
        self.capacity = 5.0              # تناژ (تن)
        self.material = "فولاد"          # جنس: فولاد، استیل، گالوانیزه
        self.connected_id = ""           # شناسه قطعه متصل
        self.install_date = ""           # تاریخ نصب
        self.status = "سالم"             # وضعیت: سالم، نیاز به تعمیر، خراب
        self.note = ""                   # یادداشت
class BridleRope:
    """مدل طناب برایدل (اتصال قفس به بویه)"""
    def __init__(self):
        self.id = ""                     # شناسه طناب برایدل
        self.mooring_id = ""             # شناسه مورینگ
        self.diameter = 40               # قطر (mm)
        self.length = 15.0               # طول (متر)
        self.material = "پلی پروپیلن"    # جنس: پلی پروپیلن، پلی اتیلن، داینما، نایلون
        self.strand_count = 3            # تعداد رشته
        self.install_date = ""           # تاریخ نصب
        self.status = "سالم"             # وضعیت: سالم، نیاز به تعمیر، خراب
        self.cage_x = 0.0                # مختصات X قفس
        self.cage_y = 0.0                # مختصات Y قفس
        self.buoy_id = ""                # شناسه بویه متصل
        self.color = "#D4A574"           # رنگ نمایش در نقشه
        self.note = ""                   # یادداشت
class Cage:
    """مدل قفس پرورش ماهی"""
    def __init__(self):
        self.id = ""                     # شناسه قفس
        self.mooring_id = ""             # شناسه مورینگ
        self.diameter = 10.0             # قطر (متر) - برای نقشه مهم است
        self.material = "فولاد"          # جنس: فولاد، گالوانیزه، استیل، پلاستیک
        self.install_date = ""           # تاریخ نصب
        self.status = "سالم"             # وضعیت: سالم، نیاز به تعمیر، خراب
        self.utm_x = 0.0                 # مختصات X مرکز قفس
        self.utm_y = 0.0                 # مختصات Y مرکز قفس
        self.color = "#569CD6"           # رنگ نمایش در نقشه
        self.note = ""                   # یادداشت


class Net:
    """مدل تور قفس (زیر قفس نصب می‌شود - در نقشه نمایش داده نمی‌شود)"""
    def __init__(self):
        self.id = ""                     # شناسه تور
        self.mooring_id = ""             # شناسه مورینگ
        self.cage_id = ""                # شناسه قفس متصل
        self.diameter = 10               # قطر طناب تور (mm)
        self.mesh_size = 50              # اندازه چشمه (mm)
        self.material = "داینما"         # جنس: داینما، نایلون، پلی‌اتیلن، پلی‌استر، فولاد
        self.depth = 4.0                 # عمق (متر)
        self.install_date = ""           # تاریخ نصب
        self.status = "سالم"             # وضعیت: سالم، نیاز به تعمیر، خراب
        self.note = ""                   # یادداشت

class Collector:
    """مدل کلکتور (متمرکزکننده زیر بویه)"""
    def __init__(self):
        self.id = ""                     # شناسه کلکتور
        self.mooring_id = ""             # شناسه مورینگ
        self.diameter = 1.0              # قطر (متر)
        self.thickness = 10              # ضخامت (mm)
        self.depth = 12.0                # عمق (متر)
        self.material = "فولاد"          # جنس: فولاد، گالوانیزه، استیل، پلاستیک
        self.install_date = ""           # تاریخ نصب
        self.status = "سالم"             # وضعیت: سالم، نیاز به تعمیر، خراب
        self.buoy_id = ""                # شناسه بویه متصل
        self.color = "#CE9178"           # رنگ نمایش در نقشه
        self.note = ""                   # یادداشت

class Mooring:
    """مدل مورینگ (مجموعه‌ای از اجزا)"""
    def __init__(self, id, name=""):
        self.id = id
        self.name = name if name else id
        self.buoys = []
        self.anchors = []
        self.anchor_chains = []
        self.anchor_ropes = []
        self.buoy_chains = []
        self.shackles = []
        self.bridle_ropes = []
        self.cages = []
        self.nets = []
        self.collectors = []


class Farm:
    """مدل مزرعه (شامل چند مورینگ)"""
    def __init__(self, id, name, center_x=0.0, center_y=0.0):
        self.id = id
        self.name = name
        self.center_x = center_x
        self.center_y = center_y
        self.moorings = []