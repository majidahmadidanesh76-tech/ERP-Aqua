import sys
import os

# اضافه کردن مسیر فعلی به PATH
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.database.db_handler import DatabaseHandler

db = DatabaseHandler()

# بررسی قفس‌ها
print("=" * 50)
print("بررسی قفس‌ها:")
cages = db.fetch_all("SELECT id, mooring_id FROM cages")
if cages:
    for cage in cages:
        print(f"  - قفس: {cage['id']} (مورینگ: {cage['mooring_id']})")
else:
    print("  ⚠️ هیچ قفسی در دیتابیس وجود ندارد!")

# بررسی دوره‌های پرورش فعال
print("\nبررسی دوره‌های پرورش فعال:")
cycles = db.fetch_all("""
    SELECT cycle_id, cage_id, start_date, species, is_active 
    FROM production_cycles 
    WHERE is_active = 1
""")
if cycles:
    for cycle in cycles:
        print(f"  - دوره {cycle['cycle_id']}: قفس {cycle['cage_id']} - {cycle['species']} - شروع: {cycle['start_date']}")
else:
    print("  ⚠️ هیچ دوره پرورش فعالی وجود ندارد!")

print("=" * 50)