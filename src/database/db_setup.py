"""
تنظیمات و ایجاد دیتابیس MySQL برای ERP-Aqua
نسخه کامل با همه جداول
"""

import mysql.connector
from mysql.connector import Error

# تنظیمات اتصال به MySQL
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': '',  # در XAMPP پیشفرض خالی است
    'database': 'erp_aqua'
}

def create_database():
    """ایجاد دیتابیس اگر وجود نداشته باشد"""
    try:
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

        # 2. جدول مورینگها (Moorings)
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

        # 3. جدول قفسها (Cages)
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

        # 4. جدول بویهها (Buoys)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS buoys (
                id VARCHAR(50) PRIMARY KEY,
                mooring_id VARCHAR(50) NOT NULL,
                buoy_type VARCHAR(20) DEFAULT 'main',
                utm_x DOUBLE DEFAULT 0,
                utm_y DOUBLE DEFAULT 0,
                color VARCHAR(20) DEFAULT '#A0A0A0',
                material VARCHAR(50) DEFAULT 'پلاستیک',
                volume DOUBLE DEFAULT 0,
                install_date VARCHAR(20),
                has_light BOOLEAN DEFAULT 0,
                body_color VARCHAR(20) DEFAULT '#A0A0A0',
                status VARCHAR(20) DEFAULT 'سالم',
                note TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (mooring_id) REFERENCES moorings(id) ON DELETE CASCADE
            )
        """)
        print("✅ جدول buoys ایجاد شد")

        # 5. جدول لنگرها (Anchors)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS anchors (
                id VARCHAR(50) PRIMARY KEY,
                mooring_id VARCHAR(50) NOT NULL,
                anchor_type VARCHAR(20) DEFAULT 'steel',
                utm_x DOUBLE DEFAULT 0,
                utm_y DOUBLE DEFAULT 0,
                weight DOUBLE DEFAULT 1500,
                color VARCHAR(20) DEFAULT '#6A9955',
                material VARCHAR(50) DEFAULT 'فولاد',
                install_date VARCHAR(20),
                install_depth DOUBLE DEFAULT 0,
                status VARCHAR(20) DEFAULT 'سالم',
                note TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (mooring_id) REFERENCES moorings(id) ON DELETE CASCADE
            )
        """)
        print("✅ جدول anchors ایجاد شد")

        # 6. جدول زنجیر لنگر (Anchor Chains)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS anchor_chains (
                id VARCHAR(50) PRIMARY KEY,
                mooring_id VARCHAR(50) NOT NULL,
                start_id VARCHAR(50),
                end_id VARCHAR(50),
                start_x DOUBLE DEFAULT 0,
                start_y DOUBLE DEFAULT 0,
                end_x DOUBLE DEFAULT 0,
                end_y DOUBLE DEFAULT 0,
                diameter DOUBLE DEFAULT 30,
                use_manual_start BOOLEAN DEFAULT 0,
                use_manual_end BOOLEAN DEFAULT 0,
                color VARCHAR(20) DEFAULT '#C58688',
                chain_type VARCHAR(50) DEFAULT 'ساده',
                material VARCHAR(50) DEFAULT 'فولاد',
                install_date VARCHAR(20),
                status VARCHAR(20) DEFAULT 'سالم',
                note TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (mooring_id) REFERENCES moorings(id) ON DELETE CASCADE
            )
        """)
        print("✅ جدول anchor_chains ایجاد شد")

        # 7. جدول طناب لنگر (Anchor Ropes)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS anchor_ropes (
                id VARCHAR(50) PRIMARY KEY,
                mooring_id VARCHAR(50) NOT NULL,
                start_id VARCHAR(50),
                end_id VARCHAR(50),
                start_x DOUBLE DEFAULT 0,
                start_y DOUBLE DEFAULT 0,
                end_x DOUBLE DEFAULT 0,
                end_y DOUBLE DEFAULT 0,
                material VARCHAR(50) DEFAULT 'پلی پروپیلن',
                diameter DOUBLE DEFAULT 64,
                use_manual_start BOOLEAN DEFAULT 0,
                use_manual_end BOOLEAN DEFAULT 0,
                color VARCHAR(20) DEFAULT '#C8C8C8',
                strand_count INT DEFAULT 3,
                length DOUBLE DEFAULT 50,
                install_date VARCHAR(20),
                status VARCHAR(20) DEFAULT 'سالم',
                note TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (mooring_id) REFERENCES moorings(id) ON DELETE CASCADE
            )
        """)
        print("✅ جدول anchor_ropes ایجاد شد")

        # 8. جدول زنجیر بویه (Buoy Chains)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS buoy_chains (
                id VARCHAR(50) PRIMARY KEY,
                mooring_id VARCHAR(50) NOT NULL,
                buoy_id VARCHAR(50),
                collector_id VARCHAR(50),
                diameter DOUBLE DEFAULT 20,
                length DOUBLE DEFAULT 10,
                material VARCHAR(50) DEFAULT 'فولاد',
                chain_type VARCHAR(50) DEFAULT 'ساده',
                install_date VARCHAR(20),
                status VARCHAR(20) DEFAULT 'سالم',
                note TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (mooring_id) REFERENCES moorings(id) ON DELETE CASCADE
            )
        """)
        print("✅ جدول buoy_chains ایجاد شد")

        # 9. جدول شاکل (Shackles)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS shackles (
                id VARCHAR(50) PRIMARY KEY,
                mooring_id VARCHAR(50) NOT NULL,
                shackle_type VARCHAR(50) DEFAULT 'یو شکل',
                quantity INT DEFAULT 1,
                size INT DEFAULT 25,
                capacity DOUBLE DEFAULT 5,
                material VARCHAR(50) DEFAULT 'فولاد',
                connected_id VARCHAR(50),
                install_date VARCHAR(20),
                status VARCHAR(20) DEFAULT 'سالم',
                note TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (mooring_id) REFERENCES moorings(id) ON DELETE CASCADE
            )
        """)
        print("✅ جدول shackles ایجاد شد")

        # 10. جدول طناب برایدل (Bridle Ropes)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS bridle_ropes (
                id VARCHAR(50) PRIMARY KEY,
                mooring_id VARCHAR(50) NOT NULL,
                buoy_id VARCHAR(50),
                cage_x DOUBLE DEFAULT 0,
                cage_y DOUBLE DEFAULT 0,
                diameter DOUBLE DEFAULT 40,
                length DOUBLE DEFAULT 15,
                material VARCHAR(50) DEFAULT 'پلی پروپیلن',
                strand_count INT DEFAULT 3,
                install_date VARCHAR(20),
                status VARCHAR(20) DEFAULT 'سالم',
                color VARCHAR(20) DEFAULT '#D4A574',
                note TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (mooring_id) REFERENCES moorings(id) ON DELETE CASCADE
            )
        """)
        print("✅ جدول bridle_ropes ایجاد شد")

        # 11. جدول تور (Nets)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS nets (
                id VARCHAR(50) PRIMARY KEY,
                mooring_id VARCHAR(50) NOT NULL,
                cage_id VARCHAR(50),
                diameter INT DEFAULT 10,
                mesh_size INT DEFAULT 50,
                material VARCHAR(50) DEFAULT 'داینما',
                depth DOUBLE DEFAULT 4,
                install_date VARCHAR(20),
                status VARCHAR(20) DEFAULT 'سالم',
                note TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (mooring_id) REFERENCES moorings(id) ON DELETE CASCADE
            )
        """)
        print("✅ جدول nets ایجاد شد")

        # 12. جدول کلکتور (Collectors)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS collectors (
                id VARCHAR(50) PRIMARY KEY,
                mooring_id VARCHAR(50) NOT NULL,
                buoy_id VARCHAR(50),
                diameter DOUBLE DEFAULT 1,
                thickness INT DEFAULT 10,
                depth DOUBLE DEFAULT 12,
                material VARCHAR(50) DEFAULT 'فولاد',
                install_date VARCHAR(20),
                status VARCHAR(20) DEFAULT 'سالم',
                color VARCHAR(20) DEFAULT '#CE9178',
                note TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (mooring_id) REFERENCES moorings(id) ON DELETE CASCADE
            )
        """)
        print("✅ جدول collectors ایجاد شد")

        # 13. جدول دورههای پرورش (Production Cycles)
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

        # 14. جدول تغذیه (Feeds)
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

        # 15. جدول تلفات (Mortalities)
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

        # 16. جدول پارامترهای آب (Water Parameters)
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

        # 17. جدول زیستتوده (Biomasses)
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

        # 18. جدول برداشتها (Harvests)
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
    """راهاندازی کامل دیتابیس"""
    print("🚀 شروع راهاندازی دیتابیس...")
    if create_database():
        if create_tables():
            print("✅ راهاندازی دیتابیس با موفقیت انجام شد")
        else:
            print("❌ خطا در ایجاد جداول")
    else:
        print("❌ خطا در ایجاد دیتابیس")

if __name__ == "__main__":
    setup_database()