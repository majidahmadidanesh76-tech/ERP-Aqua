"""
ابزارهای تبدیل و مدیریت تاریخ برای ERP-Aqua
پشتیبانی از تاریخ شمسی و میلادی
"""

import jdatetime
from datetime import datetime, date

class DateUtils:
    """کلاس ابزارهای تاریخ"""
    
    # فرمت‌های استاندارد
    SHAMSI_FORMAT = "YYYY/MM/DD"
    GREGORIAN_FORMAT = "YYYY-MM-DD"
    
    @staticmethod
    def shamsi_to_gregorian(shamsi_date_str):
        """
        تبدیل تاریخ شمسی به میلادی
        
        Args:
            shamsi_date_str: رشته تاریخ شمسی به فرمت 'YYYY/MM/DD' یا 'YYYY-MM-DD'
            
        Returns:
            رشته تاریخ میلادی به فرمت 'YYYY-MM-DD' یا None در صورت خطا
        """
        if not shamsi_date_str:
            return None
        
        try:
            # پاکسازی ورودی
            shamsi_date_str = shamsi_date_str.strip()
            
            # تعیین جداکننده
            if '/' in shamsi_date_str:
                parts = shamsi_date_str.split('/')
            elif '-' in shamsi_date_str:
                parts = shamsi_date_str.split('-')
            else:
                return None
            
            if len(parts) != 3:
                return None
            
            year = int(parts[0])
            month = int(parts[1])
            day = int(parts[2])
            
            # اعتبارسنجی
            if year < 1300 or year > 1500:
                return None
            if month < 1 or month > 12:
                return None
            if day < 1 or day > 31:
                return None
            
            shamsi_date = jdatetime.date(year, month, day)
            gregorian_date = shamsi_date.togregorian()
            
            return f"{gregorian_date.year}-{gregorian_date.month:02d}-{gregorian_date.day:02d}"
            
        except Exception as e:
            print(f"Error converting shamsi to gregorian: {e}")
            return None
    
    @staticmethod
    def gregorian_to_shamsi(gregorian_date_str):
        """
        تبدیل تاریخ میلادی به شمسی
        
        Args:
            gregorian_date_str: رشته تاریخ میلادی به فرمت 'YYYY-MM-DD'
            
        Returns:
            رشته تاریخ شمسی به فرمت 'YYYY/MM/DD' یا None در صورت خطا
        """
        if not gregorian_date_str:
            return None
        
        try:
            # پاکسازی ورودی
            gregorian_date_str = gregorian_date_str.strip()
            
            # تعیین جداکننده
            if '-' in gregorian_date_str:
                parts = gregorian_date_str.split('-')
            elif '/' in gregorian_date_str:
                parts = gregorian_date_str.split('/')
            else:
                return None
            
            if len(parts) != 3:
                return None
            
            year = int(parts[0])
            month = int(parts[1])
            day = int(parts[2])
            
            gregorian_date = date(year, month, day)
            shamsi_date = jdatetime.date.fromgregorian(date=gregorian_date)
            
            return f"{shamsi_date.year}/{shamsi_date.month:02d}/{shamsi_date.day:02d}"
            
        except Exception as e:
            print(f"Error converting gregorian to shamsi: {e}")
            return None
    
    @staticmethod
    def get_current_shamsi():
        """دریافت تاریخ امروز به شمسی"""
        today = jdatetime.date.today()
        return f"{today.year}/{today.month:02d}/{today.day:02d}"
    
    @staticmethod
    def get_current_gregorian():
        """دریافت تاریخ امروز به میلادی"""
        today = date.today()
        return f"{today.year}-{today.month:02d}-{today.day:02d}"
    
    @staticmethod
    def add_days_to_shamsi(shamsi_date_str, days):
        """
        افزودن تعداد روز به تاریخ شمسی
        
        Args:
            shamsi_date_str: تاریخ شمسی به فرمت 'YYYY/MM/DD'
            days: تعداد روز برای افزودن
            
        Returns:
            تاریخ شمسی جدید
        """
        gregorian = DateUtils.shamsi_to_gregorian(shamsi_date_str)
        if not gregorian:
            return None
        
        from datetime import timedelta
        gregorian_date = datetime.strptime(gregorian, "%Y-%m-%d").date()
        new_gregorian = gregorian_date + timedelta(days=days)
        
        return DateUtils.gregorian_to_shamsi(str(new_gregorian))
    
    @staticmethod
    def is_valid_shamsi(date_str):
        """بررسی اعتبار تاریخ شمسی"""
        try:
            if '/' in date_str:
                parts = date_str.split('/')
            elif '-' in date_str:
                parts = date_str.split('-')
            else:
                return False
            
            if len(parts) != 3:
                return False
            
            year = int(parts[0])
            month = int(parts[1])
            day = int(parts[2])
            
            if year < 1300 or year > 1500:
                return False
            
            jdatetime.date(year, month, day)
            return True
            
        except:
            return False
    
    @staticmethod
    def format_shamsi_for_display(shamsi_date_str):
        """
        فرمت‌دهی تاریخ شمسی برای نمایش
        تبدیل '1405/03/16' به '1405/03/16'
        """
        if not shamsi_date_str:
            return "-"
        return shamsi_date_str
    
    @staticmethod
    def format_shamsi_for_db(shamsi_date_str):
        """
        فرمت‌دهی تاریخ شمسی برای ذخیره در دیتابیس
        """
        if not shamsi_date_str:
            return None
        return shamsi_date_str