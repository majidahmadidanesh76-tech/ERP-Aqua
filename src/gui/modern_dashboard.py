"""
داشبورد مدرن و حرفه‌ای ERP-Aqua
با افکت شیشه‌ای برجسته (Glassmorphism) و چپ‌چین اعداد
"""

import os
import sys
from PyQt5 import QtWidgets, QtCore, QtGui
import qtawesome as qta
import jdatetime

# ========== تنظیم فونت فارسی برای matplotlib ==========
try:
    import matplotlib.pyplot as plt
    from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
    from matplotlib.figure import Figure
    import matplotlib as mpl
    import arabic_reshaper
    from bidi.algorithm import get_display
    MATPLOTLIB_AVAILABLE = True
    
    mpl.rcParams["font.family"] = "Tahoma"
    
    def fa_matplotlib(text):
        return get_display(arabic_reshaper.reshape(text))
    
    print("✅ کتابخانه‌های فارسی matplotlib با موفقیت بارگذاری شدند")
    
except ImportError as e:
    MATPLOTLIB_AVAILABLE = False
    print(f"⚠️ خطا در بارگذاری کتابخانه‌های فارسی: {e}")
    def fa_matplotlib(text):
        return text

from ..database.db_handler import DatabaseHandler


class ModernDashboard(QtWidgets.QWidget):
    """داشبورد مدیریتی مدرن برای صفحه اصلی"""

    def __init__(self, parent=None, current_user=None):
        super().__init__(parent)
        self.db = DatabaseHandler()
        self.current_user = current_user
        self.setup_ui()
        self.load_data()

    def setup_ui(self):
        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(10)

        # ========== هدر ==========
        header = QtWidgets.QHBoxLayout()
        title = QtWidgets.QLabel("🐟 ERP-Aqua")
        title.setStyleSheet("font-size: 18px; font-weight: bold; color: #1A73E8; background: transparent;")
        header.addWidget(title)

        self.date_label = QtWidgets.QLabel()
        self.date_label.setStyleSheet("color: #5F6368; font-size: 10px; background: transparent;")
        header.addStretch()
        header.addWidget(self.date_label)
        layout.addLayout(header)

        subtitle = QtWidgets.QLabel("مدیریت هوشمند مزرعه پرورش ماهی")
        subtitle.setStyleSheet("color: #5F6368; font-size: 11px; margin-bottom: 5px; background: transparent;")
        layout.addWidget(subtitle)

        # ========== ردیف 1: 5 کارت آماری با افکت شیشه‌ای ==========
        row1 = QtWidgets.QHBoxLayout()
        row1.setSpacing(8)

        self.card_fish = self.create_stat_card("تعداد کل ماهی", "0", "🐟", "#1A73E8")
        self.card_weight = self.create_stat_card("وزن کل", "0 تن", "⚖️", "#0F9D58")
        self.card_feed = self.create_stat_card("مصرف خوراک", "0 تن", "🍽️", "#F4B400")
        self.card_mortality = self.create_stat_card("نرخ تلفات", "0%", "⚠️", "#DB4437")
        self.card_profit = self.create_stat_card("سود خالص ماه جاری", "0", "💰", "#8E24AA")

        row1.addWidget(self.card_fish)
        row1.addWidget(self.card_weight)
        row1.addWidget(self.card_feed)
        row1.addWidget(self.card_mortality)
        row1.addWidget(self.card_profit)
        layout.addLayout(row1)

        # ========== ردیف 2: 3 نمودار (ارتفاع بیشتر) با افکت شیشه‌ای ==========
        row2 = QtWidgets.QHBoxLayout()
        row2.setSpacing(8)

        self.growth_chart = self.create_chart_card("روند رشد وزن", 210)
        row2.addWidget(self.growth_chart)

        self.feed_chart = self.create_chart_card("مصرف خوراک ماهانه", 210)
        row2.addWidget(self.feed_chart)

        self.fcr_chart = self.create_chart_card("ضریب تبدیل FCR", 210)
        row2.addWidget(self.fcr_chart)

        layout.addLayout(row2)

        # ========== ردیف 3: 3 نمودار (ارتفاع کمتر) با افکت شیشه‌ای ==========
        row3 = QtWidgets.QHBoxLayout()
        row3.setSpacing(8)

        self.compare_chart = self.create_chart_card("مقایسه وزن واقعی و برنامه", 170)
        row3.addWidget(self.compare_chart)

        self.size_chart = self.create_chart_card("توزیع سایز ماهی", 170)
        row3.addWidget(self.size_chart)

        self.tasks_widget = self.create_tasks_card(170)
        row3.addWidget(self.tasks_widget)

        layout.addLayout(row3)

        # ========== فوتر ==========
        footer = QtWidgets.QLabel(f"نسخه 2.1.0 | سال مالی 1403 | شرکت توسعه دهنده")
        footer.setAlignment(QtCore.Qt.AlignCenter)
        footer.setStyleSheet("color: #9AA0A6; font-size: 9px; margin-top: 8px; background: transparent;")
        layout.addWidget(footer)

        # تنظیم تاریخ
        today = jdatetime.date.today()
        self.date_label.setText(f"{today.year}/{today.month:02d}/{today.day:02d}")

    def create_stat_card(self, title, value, icon, color):
        card = QtWidgets.QFrame()
        card.setFixedHeight(95)
        # استایل شیشه‌ای برجسته
        card.setStyleSheet(f"""
            QFrame {{
                background-color: rgba(255, 255, 255, 0.85);
                border-radius: 12px;
                border: 1px solid rgba(255, 255, 255, 0.5);
            }}
        """)
        
        # اضافه کردن سایه به کارت
        shadow = QtWidgets.QGraphicsDropShadowEffect(card)
        shadow.setBlurRadius(15)
        shadow.setOffset(0, 3)
        shadow.setColor(QtGui.QColor(0, 0, 0, 40))
        card.setGraphicsEffect(shadow)
        
        layout = QtWidgets.QVBoxLayout(card)
        layout.setSpacing(4)
        layout.setContentsMargins(12, 8, 12, 8)

        top_layout = QtWidgets.QHBoxLayout()
        icon_label = QtWidgets.QLabel(icon)
        icon_label.setStyleSheet(f"font-size: 18px; color: {color}; border: none; background: transparent;")
        title_label = QtWidgets.QLabel(title)
        title_label.setStyleSheet("font-size: 10px; color: #5F6368; font-weight: bold; border: none; background: transparent;")
        top_layout.addWidget(icon_label)
        top_layout.addWidget(title_label)
        top_layout.addStretch()
        layout.addLayout(top_layout)

        # چپ‌چین کردن عدد
        value_label = QtWidgets.QLabel(value)
        value_label.setStyleSheet(f"font-size: 20px; font-weight: bold; color: {color}; border: none; background: transparent;")
        value_label.setAlignment(QtCore.Qt.AlignLeft)
        layout.addWidget(value_label)

        trend_label = QtWidgets.QLabel("در حال بروزرسانی...")
        trend_label.setStyleSheet("font-size: 8px; color: #9AA0A6; border: none; background: transparent;")
        trend_label.setAlignment(QtCore.Qt.AlignLeft)
        layout.addWidget(trend_label)

        card.value_label = value_label
        card.trend_label = trend_label
        return card

    def create_chart_card(self, title, height):
        card = QtWidgets.QFrame()
        card.setMinimumHeight(height)
        # استایل شیشه‌ای برجسته
        card.setStyleSheet("""
            QFrame {
                background-color: rgba(255, 255, 255, 0.85);
                border-radius: 12px;
                border: 1px solid rgba(255, 255, 255, 0.5);
            }
        """)
        
        # اضافه کردن سایه به کارت
        shadow = QtWidgets.QGraphicsDropShadowEffect(card)
        shadow.setBlurRadius(15)
        shadow.setOffset(0, 3)
        shadow.setColor(QtGui.QColor(0, 0, 0, 40))
        card.setGraphicsEffect(shadow)
        
        layout = QtWidgets.QVBoxLayout(card)
        layout.setSpacing(3)
        layout.setContentsMargins(8, 6, 8, 6)

        title_label = QtWidgets.QLabel(title)
        title_label.setStyleSheet("font-size: 10px; font-weight: bold; color: #1A2C3E; border: none; background: transparent;")
        title_label.setAlignment(QtCore.Qt.AlignCenter)
        layout.addWidget(title_label)

        if MATPLOTLIB_AVAILABLE:
            fig_height = (height - 30) / 100
            figure = Figure(figsize=(2.8, fig_height), facecolor='none', dpi=100)
            canvas = FigureCanvas(figure)
            canvas.setStyleSheet("background: transparent;")
            layout.addWidget(canvas)
            card.canvas = canvas
            card.figure = figure
        else:
            label = QtWidgets.QLabel("نمودار در دسترس نیست")
            label.setAlignment(QtCore.Qt.AlignCenter)
            label.setStyleSheet("color: #9AA0A6; padding: 20px; font-size: 9px; border: none; background: transparent;")
            layout.addWidget(label)
            card.canvas = None

        return card

    def create_tasks_card(self, height):
        card = QtWidgets.QFrame()
        card.setMinimumHeight(height)
        # استایل شیشه‌ای برجسته
        card.setStyleSheet("""
            QFrame {
                background-color: rgba(255, 255, 255, 0.85);
                border-radius: 12px;
                border: 1px solid rgba(255, 255, 255, 0.5);
            }
        """)
        
        # اضافه کردن سایه به کارت
        shadow = QtWidgets.QGraphicsDropShadowEffect(card)
        shadow.setBlurRadius(15)
        shadow.setOffset(0, 3)
        shadow.setColor(QtGui.QColor(0, 0, 0, 40))
        card.setGraphicsEffect(shadow)
        
        layout = QtWidgets.QVBoxLayout(card)
        layout.setSpacing(3)
        layout.setContentsMargins(10, 6, 10, 6)

        title_layout = QtWidgets.QHBoxLayout()
        title_label = QtWidgets.QLabel("📋 وظایف و برنامه‌ها")
        title_label.setStyleSheet("font-size: 10px; font-weight: bold; color: #1A2C3E; border: none; background: transparent;")
        title_layout.addWidget(title_label)
        title_layout.addStretch()

        more_btn = QtWidgets.QPushButton("مشاهده همه")
        more_btn.setFixedSize(70, 22)
        more_btn.setStyleSheet("""
            QPushButton {
                background-color: rgba(232, 240, 254, 0.8);
                color: #1A73E8;
                border: none;
                border-radius: 11px;
                font-size: 8px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #D2E3FC;
            }
        """)
        title_layout.addWidget(more_btn)
        layout.addLayout(title_layout)

        self.tasks_list = QtWidgets.QListWidget()
        self.tasks_list.setStyleSheet("""
            QListWidget {
                border: none;
                background-color: transparent;
                outline: none;
            }
            QListWidget::item {
                padding: 5px 4px;
                border-bottom: 1px solid rgba(0,0,0,0.05);
                font-size: 9px;
                background: transparent;
            }
        """)
        layout.addWidget(self.tasks_list)

        return card

    def load_data(self):
        """بارگذاری داده‌های نمونه"""
        self.card_fish.value_label.setText("125,420")
        self.card_fish.trend_label.setText("📈 +8.4%")

        self.card_weight.value_label.setText("12.84 تن")
        self.card_weight.trend_label.setText("📈 +6.7%")

        self.card_feed.value_label.setText("28.37 تن")
        self.card_feed.trend_label.setText("📈 +5.1%")

        self.card_mortality.value_label.setText("0.82%")
        self.card_mortality.trend_label.setText("📉 -0.3%")

        self.card_profit.value_label.setText("2.46 میلیارد")
        self.card_profit.trend_label.setText("📈 +12.3%")

        # نمونه وظایف
        tasks = [
            ("🎣 انتظار بچه ماهی به استخر 1", "3 خرداد"),
            ("📝 ثبت تلفات روزانه قفس 2", "2 خرداد"),
            ("💧 نمونه‌برداری آب قفس 3", "1 خرداد"),
            ("🔧 تعمیر پمپ هوادهی", "امروز"),
        ]
        for task, date in tasks:
            item = QtWidgets.QListWidgetItem(f"{task} — {date}")
            self.tasks_list.addItem(item)

        if MATPLOTLIB_AVAILABLE:
            self.draw_growth_chart()
            self.draw_feed_chart()
            self.draw_fcr_chart()
            self.draw_compare_chart()
            self.draw_size_pie_chart()

    def draw_growth_chart(self):
        if not hasattr(self.growth_chart, 'figure'):
            return
        self.growth_chart.figure.clear()
        ax = self.growth_chart.figure.add_subplot(111)
        ax.set_facecolor('none')
        months = [fa_matplotlib(x) for x in ['آذر', 'دی', 'بهمن', 'اسفند', 'فروردین', 'اردیبهشت', 'خرداد']]
        weights = [120, 150, 180, 210, 240, 270, 300]
        ax.plot(months, weights, marker='o', color='#1A73E8', linewidth=2, markersize=4)
        ax.fill_between(range(len(months)), weights, alpha=0.15, color='#1A73E8')
        ax.set_ylabel(fa_matplotlib('وزن (گرم)'), fontsize=8)
        ax.tick_params(axis='x', labelsize=7, rotation=0)
        ax.tick_params(axis='y', labelsize=7)
        ax.set_ylim(0, 350)
        self.growth_chart.figure.tight_layout(pad=0.3)
        self.growth_chart.canvas.draw()

    def draw_feed_chart(self):
        if not hasattr(self.feed_chart, 'figure'):
            return
        self.feed_chart.figure.clear()
        ax = self.feed_chart.figure.add_subplot(111)
        ax.set_facecolor('none')
        months = [fa_matplotlib(x) for x in ['آذر', 'دی', 'بهمن', 'اسفند', 'فروردین', 'اردیبهشت', 'خرداد']]
        feeds = [15, 18, 22, 25, 28, 32, 35]
        ax.bar(months, feeds, color='#F4B400', alpha=0.8, width=0.6)
        ax.set_ylabel(fa_matplotlib('خوراک (تن)'), fontsize=8)
        ax.tick_params(axis='x', labelsize=7, rotation=0)
        ax.tick_params(axis='y', labelsize=7)
        ax.set_ylim(0, 40)
        self.feed_chart.figure.tight_layout(pad=0.3)
        self.feed_chart.canvas.draw()

    def draw_fcr_chart(self):
        if not hasattr(self.fcr_chart, 'figure'):
            return
        self.fcr_chart.figure.clear()
        ax = self.fcr_chart.figure.add_subplot(111)
        ax.set_facecolor('none')
        months = [fa_matplotlib(x) for x in ['آذر', 'دی', 'بهمن', 'اسفند', 'فروردین', 'اردیبهشت', 'خرداد']]
        fcr = [1.8, 1.7, 1.6, 1.55, 1.5, 1.45, 1.4]
        ax.plot(months, fcr, marker='s', color='#8E24AA', linewidth=2, markersize=4)
        ax.fill_between(range(len(months)), fcr, alpha=0.15, color='#8E24AA')
        ax.set_ylabel('FCR', fontsize=8)
        ax.tick_params(axis='x', labelsize=7, rotation=0)
        ax.tick_params(axis='y', labelsize=7)
        ax.set_ylim(1.3, 2.0)
        self.fcr_chart.figure.tight_layout(pad=0.3)
        self.fcr_chart.canvas.draw()

    def draw_compare_chart(self):
        """نمودار مقایسه وزن واقعی و برنامه (هدف)"""
        if not hasattr(self.compare_chart, 'figure'):
            return
        self.compare_chart.figure.clear()
        ax = self.compare_chart.figure.add_subplot(111)
        ax.set_facecolor('none')
        months = [fa_matplotlib(x) for x in ['آذر', 'دی', 'بهمن', 'اسفند', 'فروردین', 'اردیبهشت', 'خرداد']]
        
        actual_weights = [120, 150, 180, 210, 240, 270, 300]
        target_weights = [130, 160, 190, 220, 250, 280, 310]
        
        ax.plot(months, actual_weights, marker='o', color='#1A73E8', linewidth=2, markersize=4, label=fa_matplotlib('واقعی'))
        ax.plot(months, target_weights, marker='s', color='#DB4437', linewidth=2, markersize=4, label=fa_matplotlib('برنامه'))
        ax.fill_between(range(len(months)), actual_weights, target_weights, alpha=0.2, color='#1A73E8')
        ax.set_ylabel(fa_matplotlib('وزن (گرم)'), fontsize=8)
        ax.tick_params(axis='x', labelsize=7, rotation=0)
        ax.tick_params(axis='y', labelsize=7)
        ax.set_ylim(0, 350)
        ax.legend(loc='upper left', fontsize=7, facecolor='none')
        self.compare_chart.figure.tight_layout(pad=0.3)
        self.compare_chart.canvas.draw()

    def draw_size_pie_chart(self):
        if not hasattr(self.size_chart, 'figure'):
            return
        self.size_chart.figure.clear()
        ax = self.size_chart.figure.add_subplot(111)
        sizes = [15, 35, 30, 20]
        labels = [fa_matplotlib(x) for x in ['۱۰۰ گرم', '۲۰۰ گرم', '۳۰۰ گرم', 'بیشتر']]
        colors = ['#1A73E8', '#0F9D58', '#F4B400', '#DB4437']
        ax.pie(sizes, labels=labels, colors=colors, autopct='%1.0f%%', startangle=90)
        ax.axis('equal')
        self.size_chart.figure.tight_layout(pad=0.3)
        self.size_chart.canvas.draw()