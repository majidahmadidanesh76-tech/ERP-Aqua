"""
scheduler.py
برنامه‌ریز برای اجرای خودکار قوانین هوشمند
"""

import schedule
import time
from datetime import datetime
import subprocess

def run_smart_rules():
    print(f"[{datetime.now()}] اجرای قوانین هوشمند...")
    subprocess.run(["python", "smart_rules.py"])

# هر روز ساعت 6 صبح اجرا شود
schedule.every().day.at("06:00").do(run_smart_rules)

print("Scheduler started. Waiting for 6:00 AM...")
while True:
    schedule.run_pending()
    time.sleep(60)