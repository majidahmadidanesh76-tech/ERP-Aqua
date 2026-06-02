"""
تنظیمات و ایجاد دیتابیس MySQL برای ERP-Aqua
"""

import mysql.connector
from mysql.connector import Error

# تنظیمات اتصال به MySQL
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': '',  # در XAMPP پیش‌فرض خالی است
    'database': 'erp_aqua'
}

def create_database():
    """ایجاد دیتابیس اگر وجود نداشته باشد"""
    try:
        # اتصال بدون انتخاب دیتابیس
        conn = mysql.connector.connect(
            host='localhost',
            user='root',
            password=''
        )
        cursor = conn.cursor()
        cursor.execute("CREATE DATABASE IF NOT EXISTS erp_aqua CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
        print("✅ دیتابیس erp_aqua ایجاد شد")
        cursor.close()
        conn.close()
        return True
    except Error as e:
        print(f"❌ خطا در ایجاد دیتابیس: {e}")
        return False

def create_tables():
    """ایجاد جداول مورد نیاز"""
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        # 1. جدول مزارع (Farms)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS farms (
                id VARCHAR(50) PRIMARY KEY,
                name VARCHAR(100) NOT NULL,
                center_x DOUBLE DEFAULT 0,
                center_y DOUBLE DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        print("✅ جدول farms ایجاد شد")
        
        # 2. جدول مورینگ‌ها (Moorings)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS moorings (
                id VARCHAR(50) PRIMARY KEY,
                farm_id VARCHAR(50) NOT NULL,
                name VARCHAR(100),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (farm_id) REFERENCES farms(id) ON DELETE CASCADE
            )
        """)
        print("✅ جدول moorings ایجاد شد")
        
        # 3. جدول قفس‌ها (Cages)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS cages (
                id VARCHAR(50) PRIMARY KEY,
                mooring_id VARCHAR(50) NOT NULL,
                diameter DOUBLE DEFAULT 10,
                material VARCHAR(50) DEFAULT 'فولاد',
                utm_x DOUBLE DEFAULT 0,
                utm_y DOUBLE DEFAULT 0,
                color VARCHAR(20) DEFAULT '#569CD6',
                install_date VARCHAR(20),
                status VARCHAR(20) DEFAULT 'سالم',
                note TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (mooring_id) REFERENCES moorings(id) ON DELETE CASCADE
            )
        """)
        print("✅ جدول cages ایجاد شد")
        
        # 4. جدول دوره‌های پرورش (Production Cycles)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS production_cycles (
                id INTEGER PRIMARY KEY AUTO_INCREMENT,
                cage_id VARCHAR(50) NOT NULL,
                start_date VARCHAR(20) NOT NULL,
                species VARCHAR(50),
                initial_count INTEGER DEFAULT 0,
                initial_weight DOUBLE DEFAULT 0,
                target_weight DOUBLE DEFAULT 0,
                target_fcr DOUBLE DEFAULT 1.5,
                is_active BOOLEAN DEFAULT 1,
                is_completed BOOLEAN DEFAULT 0,
                note TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (cage_id) REFERENCES cages(id) ON DELETE CASCADE
            )
        """)
        print("✅ جدول production_cycles ایجاد شد")
        
        # 5. جدول تغذیه (Feeds)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS feeds (
                id INTEGER PRIMARY KEY AUTO_INCREMENT,
                cage_id VARCHAR(50) NOT NULL,
                cycle_id INTEGER,
                date VARCHAR(20) NOT NULL,
                feed_type VARCHAR(50),
                feed_amount DOUBLE DEFAULT 0,
                feed_time VARCHAR(50),
                note TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (cage_id) REFERENCES cages(id) ON DELETE CASCADE,
                FOREIGN KEY (cycle_id) REFERENCES production_cycles(id) ON DELETE SET NULL
            )
        """)
        print("✅ جدول feeds ایجاد شد")
        
        # 6. جدول تلفات (Mortalities)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS mortalities (
                id INTEGER PRIMARY KEY AUTO_INCREMENT,
                cage_id VARCHAR(50) NOT NULL,
                cycle_id INTEGER,
                date VARCHAR(20) NOT NULL,
                count INTEGER DEFAULT 0,
                cause VARCHAR(100),
                note TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (cage_id) REFERENCES cages(id) ON DELETE CASCADE,
                FOREIGN KEY (cycle_id) REFERENCES production_cycles(id) ON DELETE SET NULL
            )
        """)
        print("✅ جدول mortalities ایجاد شد")
        
        # 7. جدول پارامترهای آب (Water Parameters)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS water_parameters (
                id INTEGER PRIMARY KEY AUTO_INCREMENT,
                cage_id VARCHAR(50) NOT NULL,
                cycle_id INTEGER,
                date VARCHAR(20) NOT NULL,
                time VARCHAR(50),
                temperature DOUBLE DEFAULT 0,
                dissolved_oxygen DOUBLE DEFAULT 0,
                salinity DOUBLE DEFAULT 0,
                ph DOUBLE DEFAULT 0,
                note TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (cage_id) REFERENCES cages(id) ON DELETE CASCADE,
                FOREIGN KEY (cycle_id) REFERENCES production_cycles(id) ON DELETE SET NULL
            )
        """)
        print("✅ جدول water_parameters ایجاد شد")
        
        # 8. جدول زیست‌توده (Biomasses)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS biomasses (
                id INTEGER PRIMARY KEY AUTO_INCREMENT,
                cage_id VARCHAR(50) NOT NULL,
                cycle_id INTEGER,
                date VARCHAR(20) NOT NULL,
                estimated_weight DOUBLE DEFAULT 0,
                estimated_count INTEGER DEFAULT 0,
                sample_size INTEGER DEFAULT 0,
                note TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (cage_id) REFERENCES cages(id) ON DELETE CASCADE,
                FOREIGN KEY (cycle_id) REFERENCES production_cycles(id) ON DELETE SET NULL
            )
        """)
        print("✅ جدول biomasses ایجاد شد")
        
        # 9. جدول برداشت‌ها (Harvests)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS harvests (
                id INTEGER PRIMARY KEY AUTO_INCREMENT,
                cage_id VARCHAR(50) NOT NULL,
                cycle_id INTEGER NOT NULL,
                harvest_date VARCHAR(20) NOT NULL,
                harvest_count INTEGER DEFAULT 0,
                average_weight DOUBLE DEFAULT 0,
                total_weight_kg DOUBLE DEFAULT 0,
                customer VARCHAR(100),
                price_per_kg DOUBLE DEFAULT 0,
                total_amount DOUBLE DEFAULT 0,
                is_final BOOLEAN DEFAULT 0,
                note TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (cage_id) REFERENCES cages(id) ON DELETE CASCADE,
                FOREIGN KEY (cycle_id) REFERENCES production_cycles(id) ON DELETE CASCADE
            )
        """)
        print("✅ جدول harvests ایجاد شد")
        
        conn.commit()
        cursor.close()
        conn.close()
        print("✅ همه جداول با موفقیت ایجاد شدند")
        return True
        
    except Error as e:
        print(f"❌ خطا در ایجاد جداول: {e}")
        return False

def setup_database():
    """راه‌اندازی کامل دیتابیس"""
    print("🚀 شروع راه‌اندازی دیتابیس...")
    if create_database():
        if create_tables():
            print("✅ راه‌اندازی دیتابیس با موفقیت انجام شد")
        else:
            print("❌ خطا در ایجاد جداول")
    else:
        print("❌ خطا در ایجاد دیتابیس")

if __name__ == "__main__":
    setup_database()