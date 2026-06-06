"""
smart_rules.py
اسکریپت تولید پیشنهادات هوشمند - نسخه با قوانین قابل تنظیم
"""

from src.database.db_handler import DatabaseHandler
from datetime import datetime, timedelta

db = DatabaseHandler()

def run_smart_rules():
    print(f"[{datetime.now()}] شروع اجرای قوانین هوشمند...")
    
    # خواندن مقادیر از دیتابیس
    TEMP_ALERT_HIGH = db.get_rule_value('temp_alert_high', 24)
    TEMP_CRITICAL_HIGH = db.get_rule_value('temp_critical_high', 26)
    O2_ALERT_LOW = db.get_rule_value('o2_alert_low', 5)
    O2_CRITICAL_LOW = db.get_rule_value('o2_critical_low', 4)
    SALINITY_MIN = db.get_rule_value('salinity_min', 25)
    SALINITY_MAX = db.get_rule_value('salinity_max', 40)
    MORTALITY_THRESHOLD = db.get_rule_value('mortality_threshold', 0.1)
    NET_CLEAN_DAYS = int(db.get_rule_value('net_clean_days', 30))
    HARVEST_THRESHOLD = db.get_rule_value('harvest_threshold', 0.9)
    MAX_SUGGESTIONS = int(db.get_rule_value('max_suggestions_per_day', 10))
    
    print(f"  دمای هشدار: {TEMP_ALERT_HIGH}°C | دمای بحرانی: {TEMP_CRITICAL_HIGH}°C")
    print(f"  اکسیژن هشدار: {O2_ALERT_LOW} mg/L | اکسیژن بحرانی: {O2_CRITICAL_LOW} mg/L")
    print(f"  شوری مطلوب: {SALINITY_MIN}-{SALINITY_MAX} ppt")
    
    suggestions_count = 0
    
    # 1. هشدار دمای بالا
    high_temp = db.fetch_all("""
        SELECT wp.cage_id, wp.temperature, wp.date, pc.target_weight
        FROM water_parameters wp
        JOIN production_cycles pc ON wp.cage_id = pc.cage_id AND pc.is_active = 1
        WHERE wp.temperature > %s AND wp.date >= CURDATE()
    """, (TEMP_ALERT_HIGH,))
    
    for ht in high_temp:
        if suggestions_count >= MAX_SUGGESTIONS:
            break
        temp = float(ht['temperature']) if ht['temperature'] else 0
        is_critical = temp >= TEMP_CRITICAL_HIGH
        priority = 1 if is_critical else 2
        
        action = "کاهش 30% خوراک، بازرسی تور" if not is_critical else "قطع خوراک، بازرسی فوری تور، پایش 24 ساعته"
        
        db.add_ai_suggestion(
            'alert',
            f"{'بحرانی - ' if is_critical else ''}هشدار دمای بالا در قفس {ht['cage_id']}",
            f"دمای ثبت‌شده: {temp} درجه سانتی‌گراد. پیشنهاد: {action}.",
            priority=priority,
            reasoning=f"دمای آب {'از حد بحرانی عبور کرده' if is_critical else 'از حد هشدار بالاتر رفته است'} (حد مجاز: {TEMP_ALERT_HIGH}°C)."
        )
        print(f"  - هشدار دما برای قفس {ht['cage_id']} اضافه شد")
        suggestions_count += 1

    # 2. هشدار اکسیژن پایین
    low_o2 = db.fetch_all("""
        SELECT wp.cage_id, wp.dissolved_oxygen, wp.date
        FROM water_parameters wp
        JOIN production_cycles pc ON wp.cage_id = pc.cage_id AND pc.is_active = 1
        WHERE wp.dissolved_oxygen < %s AND wp.date >= CURDATE()
    """, (O2_ALERT_LOW,))
    
    for lo in low_o2:
        if suggestions_count >= MAX_SUGGESTIONS:
            break
        oxygen = float(lo['dissolved_oxygen']) if lo['dissolved_oxygen'] else 0
        is_critical = oxygen < O2_CRITICAL_LOW
        priority = 1 if is_critical else 2
        
        action = "کاهش خوراک، بازرسی تور" if not is_critical else "قطع کامل خوراک، بازرسی فوری تور، بررسی جریان آب"
        
        db.add_ai_suggestion(
            'alert',
            f"{'بحرانی - ' if is_critical else ''}کاهش اکسیژن در قفس {lo['cage_id']}",
            f"اکسیژن محلول: {oxygen} mg/L. پیشنهاد: {action}.",
            priority=priority,
            reasoning=f"اکسیژن از حد {'بحرانی' if is_critical else 'هشدار'} پایین‌تر رفته است (حد مجاز: {O2_ALERT_LOW} mg/L)."
        )
        print(f"  - هشدار اکسیژن برای قفس {lo['cage_id']} اضافه شد")
        suggestions_count += 1

    # 3. هشدار شوری نامطلوب
    bad_salinity = db.fetch_all("""
        SELECT wp.cage_id, wp.salinity, wp.date
        FROM water_parameters wp
        JOIN production_cycles pc ON wp.cage_id = pc.cage_id AND pc.is_active = 1
        WHERE (wp.salinity < %s OR wp.salinity > %s) AND wp.date >= CURDATE()
    """, (SALINITY_MIN, SALINITY_MAX))
    
    for bs in bad_salinity:
        if suggestions_count >= MAX_SUGGESTIONS:
            break
        salinity = float(bs['salinity']) if bs['salinity'] else 0
        is_low = salinity < SALINITY_MIN
        msg = f"شوری پایین‌تر از حد مطلوب ({salinity} < {SALINITY_MIN})" if is_low else f"شوری بالاتر از حد مطلوب ({salinity} > {SALINITY_MAX})"
        
        db.add_ai_suggestion(
            'alert',
            f"شوری نامطلوب در قفس {bs['cage_id']}",
            f"{msg}. پیشنهاد: بازرسی ماهی برای علائم استرس.",
            priority=2,
            reasoning=f"شوری از محدوده بهینه ({SALINITY_MIN}-{SALINITY_MAX} ppt) خارج شده است."
        )
        print(f"  - هشدار شوری برای قفس {bs['cage_id']} اضافه شد")
        suggestions_count += 1

    # 4. پیشنهاد شستشوی تور
    last_clean = db.fetch_one("""
        SELECT MAX(completed_at) as last_clean 
        FROM maintenance_plan_tasks 
        WHERE task_title LIKE '%شستشوی تور%' AND execution_status = 'completed'
    """)
    
    if last_clean and last_clean['last_clean']:
        days_since = (datetime.now() - last_clean['last_clean']).days
        if days_since >= NET_CLEAN_DAYS:
            db.add_ai_suggestion(
                'maintenance',
                "شستشوی دوره‌ای تور",
                f"آخرین شستشوی تور {days_since} روز پیش انجام شده است. شستشو هر {NET_CLEAN_DAYS} روز یکبار توصیه می‌شود.",
                priority=2,
                suggested_date=datetime.now().date() + timedelta(days=3),
                reasoning=f"برای جلوگیری از گرفتگی تور و حفظ جریان آب، شستشوی دوره‌ای هر {NET_CLEAN_DAYS} روز ضروری است."
            )
            print(f"  - پیشنهاد شستشوی تور اضافه شد")
            suggestions_count += 1

    # 5. پیشنهاد برداشت
    biomasses = db.fetch_all("""
        SELECT b.cage_id, b.estimated_weight, b.date, pc.target_weight 
        FROM biomasses b
        JOIN production_cycles pc ON b.cage_id = pc.cage_id AND pc.is_active = 1
        WHERE b.date = (SELECT MAX(date) FROM biomasses WHERE cage_id = b.cage_id)
    """)
    
    for b in biomasses:
        if suggestions_count >= MAX_SUGGESTIONS:
            break
        estimated_weight = float(b['estimated_weight']) if b['estimated_weight'] else 0
        target_weight = float(b['target_weight']) if b['target_weight'] else 0
        
        if target_weight > 0 and estimated_weight >= HARVEST_THRESHOLD * target_weight:
            db.add_ai_suggestion(
                'harvest',
                f"نزدیک شدن به وزن هدف در قفس {b['cage_id']}",
                f"وزن فعلی: {estimated_weight:.0f} گرم | وزن هدف: {target_weight:.0f} گرم.",
                priority=2,
                suggested_date=datetime.now().date() + timedelta(days=14),
                reasoning=f"وزن ماهی به {int(HARVEST_THRESHOLD*100)}% وزن هدف رسیده است. برنامه‌ریزی برداشت توصیه می‌شود."
            )
            print(f"  - پیشنهاد برداشت برای قفس {b['cage_id']} اضافه شد")
            suggestions_count += 1

    # 6. هشدار تلفات غیرعادی
    mortalities = db.fetch_all("""
        SELECT m.cage_id, SUM(m.count) as daily_total, m.date,
               (SELECT AVG(count) FROM mortalities WHERE cage_id = m.cage_id AND date >= DATE_SUB(m.date, INTERVAL 7 DAY)) as weekly_avg
        FROM mortalities m
        WHERE m.date >= CURDATE()
        GROUP BY m.cage_id, m.date
    """)
    
    for m in mortalities:
        if suggestions_count >= MAX_SUGGESTIONS:
            break
        weekly_avg = float(m['weekly_avg']) if m['weekly_avg'] else 0
        daily_total = float(m['daily_total']) if m['daily_total'] else 0
        
        if weekly_avg > 0 and daily_total > MORTALITY_THRESHOLD * weekly_avg:
            db.add_ai_suggestion(
                'alert',
                f"تلفات غیرعادی در قفس {m['cage_id']}",
                f"تلفات امروز: {daily_total:.0f} عدد | میانگین هفته قبل: {weekly_avg:.0f} عدد. پیشنهاد: بازرسی فوری.",
                priority=1,
                reasoning=f"تلفات بیش از {int(MORTALITY_THRESHOLD*100)}% میانگین هفته قبل است."
            )
            print(f"  - هشدار تلفات برای قفس {m['cage_id']} اضافه شد")
            suggestions_count += 1

    # 7. هشدار ترکیبی (دما + اکسیژن)
    combined_temp_o2 = db.get_rule_value('combined_temp_o2_alert', 2)
    combined_alerts = db.fetch_all("""
        SELECT wp1.cage_id, wp1.temperature, wp2.dissolved_oxygen, wp1.date
        FROM water_parameters wp1
        JOIN water_parameters wp2 ON wp1.cage_id = wp2.cage_id AND wp1.date = wp2.date
        JOIN production_cycles pc ON wp1.cage_id = pc.cage_id AND pc.is_active = 1
        WHERE wp1.temperature > %s AND wp2.dissolved_oxygen < %s AND wp1.date >= CURDATE()
    """, (TEMP_ALERT_HIGH - combined_temp_o2, O2_ALERT_LOW + combined_temp_o2))
    
    for ca in combined_alerts:
        if suggestions_count >= MAX_SUGGESTIONS:
            break
        temp = float(ca['temperature']) if ca['temperature'] else 0
        oxygen = float(ca['dissolved_oxygen']) if ca['dissolved_oxygen'] else 0
        db.add_ai_suggestion(
            'alert',
            f"شرایط بحرانی در قفس {ca['cage_id']}",
            f"دمای بالا ({temp}°C) همراه با اکسیژن پایین ({oxygen} mg/L). اقدام فوری: قطع خوراک، بازرسی فوری تور.",
            priority=1,
            reasoning="ترکیب دمای بالا و اکسیژن پایین بسیار خطرناک است."
        )
        print(f"  - هشدار ترکیبی برای قفس {ca['cage_id']} اضافه شد")
        suggestions_count += 1

    print(f"[{datetime.now()}] اجرای قوانین هوشمند به پایان رسید. {suggestions_count} پیشنهاد ایجاد شد.")


if __name__ == "__main__":
    run_smart_rules()