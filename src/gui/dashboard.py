"""
صفحه داشبورد (خانه) برای ERP-Aqua
نمایش خلاصه اطلاعات و آمار
"""

from PyQt5 import QtWidgets, QtCore
import qtawesome as qta


class DashboardPage(QtWidgets.QWidget):
    """
    صفحه اصلی داشبورد برنامه
    شامل کارت‌های اطلاعاتی و هشدارها
    """
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
    
    def setup_ui(self):
        """تنظیم رابط کاربری داشبورد"""
        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(30, 40, 30, 80)
        layout.setSpacing(35)
        
        # عنوان اصلی
        title = QtWidgets.QLabel("🐟 مدیریت مزارع پرورش ماهی")
        title.setAlignment(QtCore.Qt.AlignCenter)
        title.setStyleSheet("font-size: 28px; font-weight: bold; color: #569CD6; padding: 20px;")
        layout.addWidget(title)
        
        # ==================== بخش هشدارها ====================
        alerts_frame = QtWidgets.QFrame()
        alerts_frame.setFixedHeight(60)
        alerts_layout = QtWidgets.QHBoxLayout(alerts_frame)
        alerts_layout.setSpacing(20)
        alerts_layout.setAlignment(QtCore.Qt.AlignCenter)
        
        alerts = [
            ("⚠️ کمبود غذا!", "#8B2C2C"),
            ("⚠️ مرگ و میر بالا!", "#78500B"),
            ("⚠️ دمای آب بالا!", "#78500B")
        ]
        
        for text, color in alerts:
            lbl = QtWidgets.QLabel(text)
            lbl.setAlignment(QtCore.Qt.AlignCenter)
            lbl.setStyleSheet(f"""
                background-color: {color}; 
                color: white; 
                font-weight: bold; 
                font-size: 13px; 
                padding: 8px 15px; 
                border-radius: 4px;
            """)
            lbl.setFixedHeight(45)
            alerts_layout.addWidget(lbl)
        
        layout.addWidget(alerts_frame)
        
        # ==================== بخش کارت‌های اطلاعاتی ====================
        cards_frame = QtWidgets.QFrame()
        cards_layout = QtWidgets.QHBoxLayout(cards_frame)
        cards_layout.setSpacing(25)
        cards_layout.setAlignment(QtCore.Qt.AlignCenter)
        
        cards = [
            ("مرگ و میر روزانه", "۲ ماهی", "📊"),
            ("ذخیره غذا", "۲۰۰ کیلوگرم", "🍽️"),
            ("تعداد قفس‌ها", "۱۲", "🏗️"),
            ("وزن کل ماهی", "۱.۲ تن", "🐟")
        ]
        
        for card_title, value, icon in cards:
            card = self.create_info_card(card_title, value, icon)
            cards_layout.addWidget(card)
        
        layout.addWidget(cards_frame)
        layout.addStretch()
    
    def create_info_card(self, title, value, icon):
        """
        ایجاد کارت اطلاعاتی
        
        Parameters:
        -----------
        title : str
            عنوان کارت
        value : str
            مقدار نمایشی
        icon : str
            آیکون کارت
            
        Returns:
        --------
        QFrame : کارت ساخته شده
        """
        card = QtWidgets.QFrame()
        card.setFixedSize(220, 160)
        card.setStyleSheet("""
            background-color: #252526; 
            border-radius: 6px; 
            border: 1px solid #3E3E42;
        """)
        
        card_layout = QtWidgets.QVBoxLayout(card)
        card_layout.setAlignment(QtCore.Qt.AlignCenter)
        card_layout.setSpacing(8)
        
        # آیکون
        lbl_icon = QtWidgets.QLabel(icon)
        lbl_icon.setAlignment(QtCore.Qt.AlignCenter)
        lbl_icon.setStyleSheet("font-size: 32px;")
        card_layout.addWidget(lbl_icon)
        
        # عنوان
        lbl_title = QtWidgets.QLabel(title)
        lbl_title.setAlignment(QtCore.Qt.AlignCenter)
        lbl_title.setStyleSheet("font-size: 13px; color: #C8C8C8;")
        card_layout.addWidget(lbl_title)
        
        # مقدار
        lbl_value = QtWidgets.QLabel(value)
        lbl_value.setAlignment(QtCore.Qt.AlignCenter)
        lbl_value.setStyleSheet("font-size: 22px; font-weight: bold; color: #569CD6;")
        card_layout.addWidget(lbl_value)
        
        return card