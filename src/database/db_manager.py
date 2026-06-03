"""
مدیریت اتصال و عملیات دیتابیس MySQL برای ERP-Aqua
نسخه کامل با همه متدها
"""

import mysql.connector
from mysql.connector import Error

# تنظیمات اتصال
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': '',
    'database': 'erp_aqua',
    'charset': 'utf8mb4',
    'use_unicode': True
}

class DatabaseManager:
    """مدیریت عملیات دیتابیس"""

    def __init__(self):
        self.connection = None
        self.connect()

    def connect(self):
        try:
            self.connection = mysql.connector.connect(**DB_CONFIG)
            print("✅ اتصال به دیتابیس برقرار شد")
            return True
        except Error as e:
            print(f"❌ خطا در اتصال به دیتابیس: {e}")
            return False

    def disconnect(self):
        if self.connection and self.connection.is_connected():
            self.connection.close()
            print("✅ اتصال به دیتابیس بسته شد")

    def execute_query(self, query, params=None):
        try:
            cursor = self.connection.cursor()
            cursor.execute(query, params or ())
            self.connection.commit()
            cursor.close()
            return True
        except Error as e:
            print(f"❌ خطا در اجرای کوئری: {e}")
            return False

    def fetch_all(self, query, params=None):
        try:
            cursor = self.connection.cursor(dictionary=True)
            cursor.execute(query, params or ())
            results = cursor.fetchall()
            cursor.close()
            return results
        except Error as e:
            print(f"❌ خطا در دریافت داده: {e}")
            return []

    def fetch_one(self, query, params=None):
        results = self.fetch_all(query, params)
        return results[0] if results else None

    def get_last_insert_id(self):
        cursor = self.connection.cursor()
        cursor.execute("SELECT LAST_INSERT_ID()")
        result = cursor.fetchone()
        cursor.close()
        return result[0] if result else None

    # ==================== مزرعه ====================

    def save_farm(self, farm_id, name, center_x=0, center_y=0):
        query = """
            INSERT INTO farms (id, name, center_x, center_y) 
            VALUES (%s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE 
                name = VALUES(name),
                center_x = VALUES(center_x),
                center_y = VALUES(center_y)
        """
        return self.execute_query(query, (farm_id, name, center_x, center_y))

    def get_all_farms(self):
        return self.fetch_all("SELECT * FROM farms ORDER BY name")

    def delete_farm(self, farm_id):
        return self.execute_query("DELETE FROM farms WHERE id = %s", (farm_id,))

    # ==================== مورینگ ====================

    def save_mooring(self, mooring_id, farm_id, name=None):
        query = """
            INSERT INTO moorings (id, farm_id, name) 
            VALUES (%s, %s, %s)
            ON DUPLICATE KEY UPDATE 
                name = VALUES(name)
        """
        return self.execute_query(query, (mooring_id, farm_id, name or mooring_id))

    def get_moorings_by_farm(self, farm_id):
        return self.fetch_all("SELECT * FROM moorings WHERE farm_id = %s", (farm_id,))

    def delete_mooring(self, mooring_id):
        return self.execute_query("DELETE FROM moorings WHERE id = %s", (mooring_id,))

    # ==================== قفس ====================

    def save_cage(self, cage_id, mooring_id, diameter=10, material="فولاد", 
                  utm_x=0, utm_y=0, color="#569CD6", install_date="", status="سالم", note=""):
        query = """
            INSERT INTO cages (id, mooring_id, diameter, material, utm_x, utm_y, 
                              color, install_date, status, note) 
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE 
                diameter = VALUES(diameter),
                material = VALUES(material),
                utm_x = VALUES(utm_x),
                utm_y = VALUES(utm_y),
                color = VALUES(color),
                install_date = VALUES(install_date),
                status = VALUES(status),
                note = VALUES(note)
        """
        return self.execute_query(query, (cage_id, mooring_id, diameter, material, 
                                          utm_x, utm_y, color, install_date, status, note))

    def get_cages_by_mooring(self, mooring_id):
        return self.fetch_all("SELECT * FROM cages WHERE mooring_id = %s", (mooring_id,))

    def delete_cage(self, cage_id):
        return self.execute_query("DELETE FROM cages WHERE id = %s", (cage_id,))

    # ==================== بویه ====================

    def save_buoy(self, buoy_id, mooring_id, buoy_type, utm_x, utm_y, color,
                  material, volume, install_date, has_light, body_color, status, note):
        query = """
            INSERT INTO buoys (id, mooring_id, buoy_type, utm_x, utm_y, color, 
                              material, volume, install_date, has_light, 
                              body_color, status, note)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE
                buoy_type = VALUES(buoy_type), utm_x = VALUES(utm_x), utm_y = VALUES(utm_y),
                color = VALUES(color), material = VALUES(material), volume = VALUES(volume),
                install_date = VALUES(install_date), has_light = VALUES(has_light),
                body_color = VALUES(body_color), status = VALUES(status), note = VALUES(note)
        """
        return self.execute_query(query, (buoy_id, mooring_id, buoy_type, utm_x, utm_y,
                                          color, material, volume, install_date,
                                          has_light, body_color, status, note))

    # ==================== لنگر ====================

    def save_anchor(self, anchor_id, mooring_id, anchor_type, utm_x, utm_y, weight,
                    color, material, install_date, install_depth, status, note):
        query = """
            INSERT INTO anchors (id, mooring_id, anchor_type, utm_x, utm_y, weight,
                                color, material, install_date, install_depth, status, note)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE
                anchor_type = VALUES(anchor_type), utm_x = VALUES(utm_x), utm_y = VALUES(utm_y),
                weight = VALUES(weight), color = VALUES(color), material = VALUES(material),
                install_date = VALUES(install_date), install_depth = VALUES(install_depth),
                status = VALUES(status), note = VALUES(note)
        """
        return self.execute_query(query, (anchor_id, mooring_id, anchor_type, utm_x, utm_y,
                                          weight, color, material, install_date,
                                          install_depth, status, note))

    # ==================== زنجیر لنگر ====================

    def save_anchor_chain(self, chain_id, mooring_id, start_id, end_id, start_x, start_y,
                          end_x, end_y, diameter, use_manual_start, use_manual_end,
                          color, chain_type, material, install_date, status, note):
        query = """
            INSERT INTO anchor_chains (id, mooring_id, start_id, end_id, start_x, start_y, end_x, end_y,
                                      diameter, use_manual_start, use_manual_end, color, chain_type, material,
                                      install_date, status, note)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE
                start_id = VALUES(start_id), end_id = VALUES(end_id),
                start_x = VALUES(start_x), start_y = VALUES(start_y),
                end_x = VALUES(end_x), end_y = VALUES(end_y),
                diameter = VALUES(diameter), use_manual_start = VALUES(use_manual_start),
                use_manual_end = VALUES(use_manual_end), color = VALUES(color),
                chain_type = VALUES(chain_type), material = VALUES(material),
                install_date = VALUES(install_date), status = VALUES(status), note = VALUES(note)
        """
        return self.execute_query(query, (chain_id, mooring_id, start_id, end_id,
                                          start_x, start_y, end_x, end_y,
                                          diameter, use_manual_start, use_manual_end,
                                          color, chain_type, material, install_date, status, note))

    # ==================== طناب لنگر ====================

    def save_anchor_rope(self, rope_id, mooring_id, start_id, end_id, start_x, start_y,
                         end_x, end_y, material, diameter, use_manual_start, use_manual_end,
                         color, strand_count, length, install_date, status, note):
        query = """
            INSERT INTO anchor_ropes (id, mooring_id, start_id, end_id, start_x, start_y, end_x, end_y,
                                     material, diameter, use_manual_start, use_manual_end, color,
                                     strand_count, length, install_date, status, note)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE
                start_id = VALUES(start_id), end_id = VALUES(end_id),
                start_x = VALUES(start_x), start_y = VALUES(start_y),
                end_x = VALUES(end_x), end_y = VALUES(end_y),
                material = VALUES(material), diameter = VALUES(diameter),
                use_manual_start = VALUES(use_manual_start), use_manual_end = VALUES(use_manual_end),
                color = VALUES(color), strand_count = VALUES(strand_count),
                length = VALUES(length), install_date = VALUES(install_date),
                status = VALUES(status), note = VALUES(note)
        """
        return self.execute_query(query, (rope_id, mooring_id, start_id, end_id,
                                          start_x, start_y, end_x, end_y,
                                          material, diameter, use_manual_start, use_manual_end,
                                          color, strand_count, length, install_date, status, note))

    # ==================== زنجیر بویه ====================

    def save_buoy_chain(self, chain_id, mooring_id, buoy_id, collector_id, diameter,
                        length, material, chain_type, install_date, status, note):
        query = """
            INSERT INTO buoy_chains (id, mooring_id, buoy_id, collector_id, diameter, length,
                                    material, chain_type, install_date, status, note)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE
                buoy_id = VALUES(buoy_id), collector_id = VALUES(collector_id),
                diameter = VALUES(diameter), length = VALUES(length),
                material = VALUES(material), chain_type = VALUES(chain_type),
                install_date = VALUES(install_date), status = VALUES(status), note = VALUES(note)
        """
        return self.execute_query(query, (chain_id, mooring_id, buoy_id, collector_id,
                                          diameter, length, material, chain_type,
                                          install_date, status, note))

    # ==================== شاکل ====================

    def save_shackle(self, shackle_id, mooring_id, shackle_type, quantity, size,
                     capacity, material, connected_id, install_date, status, note):
        query = """
            INSERT INTO shackles (id, mooring_id, shackle_type, quantity, size, capacity,
                                 material, connected_id, install_date, status, note)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE
                shackle_type = VALUES(shackle_type), quantity = VALUES(quantity),
                size = VALUES(size), capacity = VALUES(capacity),
                material = VALUES(material), connected_id = VALUES(connected_id),
                install_date = VALUES(install_date), status = VALUES(status), note = VALUES(note)
        """
        return self.execute_query(query, (shackle_id, mooring_id, shackle_type, quantity,
                                          size, capacity, material, connected_id,
                                          install_date, status, note))

    # ==================== طناب برایدل ====================

    def save_bridle_rope(self, bridle_id, mooring_id, buoy_id, cage_x, cage_y,
                         diameter, length, material, strand_count, install_date,
                         status, color, note):
        query = """
            INSERT INTO bridle_ropes (id, mooring_id, buoy_id, cage_x, cage_y, diameter, length,
                                     material, strand_count, install_date, status, color, note)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE
                buoy_id = VALUES(buoy_id), cage_x = VALUES(cage_x), cage_y = VALUES(cage_y),
                diameter = VALUES(diameter), length = VALUES(length),
                material = VALUES(material), strand_count = VALUES(strand_count),
                install_date = VALUES(install_date), status = VALUES(status),
                color = VALUES(color), note = VALUES(note)
        """
        return self.execute_query(query, (bridle_id, mooring_id, buoy_id, cage_x, cage_y,
                                          diameter, length, material, strand_count,
                                          install_date, status, color, note))

    # ==================== تور ====================

    def save_net(self, net_id, mooring_id, cage_id, diameter, mesh_size,
                 material, depth, install_date, status, note):
        query = """
            INSERT INTO nets (id, mooring_id, cage_id, diameter, mesh_size, material, depth,
                             install_date, status, note)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE
                cage_id = VALUES(cage_id), diameter = VALUES(diameter),
                mesh_size = VALUES(mesh_size), material = VALUES(material),
                depth = VALUES(depth), install_date = VALUES(install_date),
                status = VALUES(status), note = VALUES(note)
        """
        return self.execute_query(query, (net_id, mooring_id, cage_id, diameter, mesh_size,
                                          material, depth, install_date, status, note))

    # ==================== کلکتور ====================

    def save_collector(self, collector_id, mooring_id, buoy_id, diameter, thickness,
                       depth, material, install_date, status, color, note):
        query = """
            INSERT INTO collectors (id, mooring_id, buoy_id, diameter, thickness, depth,
                                   material, install_date, status, color, note)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE
                buoy_id = VALUES(buoy_id), diameter = VALUES(diameter),
                thickness = VALUES(thickness), depth = VALUES(depth),
                material = VALUES(material), install_date = VALUES(install_date),
                status = VALUES(status), color = VALUES(color), note = VALUES(note)
        """
        return self.execute_query(query, (collector_id, mooring_id, buoy_id, diameter,
                                          thickness, depth, material, install_date,
                                          status, color, note))

    # ==================== دوره پرورش ====================

    def start_production_cycle(self, cage_id, start_date, species, initial_count, 
                               initial_weight, target_weight, target_fcr=1.5, note=""):
        self.execute_query("UPDATE production_cycles SET is_active = 0 WHERE cage_id = %s", (cage_id,))
        query = """
            INSERT INTO production_cycles 
            (cage_id, start_date, species, initial_count, initial_weight, target_weight, target_fcr, is_active, note)
            VALUES (%s, %s, %s, %s, %s, %s, %s, 1, %s)
        """
        if self.execute_query(query, (cage_id, start_date, species, initial_count, 
                                      initial_weight, target_weight, target_fcr, note)):
            return self.get_last_insert_id()
        return None

    def update_production_cycle(self, cycle_id, start_date, species, initial_count,
                                initial_weight, target_weight, note=""):
        query = """
            UPDATE production_cycles 
            SET start_date = %s, species = %s, initial_count = %s, 
                initial_weight = %s, target_weight = %s, note = %s
            WHERE id = %s
        """
        return self.execute_query(query, (start_date, species, initial_count,
                                          initial_weight, target_weight, note, cycle_id))

    def get_active_cycle(self, cage_id):
        return self.fetch_one(
            "SELECT * FROM production_cycles WHERE cage_id = %s AND is_active = 1 AND is_completed = 0",
            (cage_id,)
        )

    def get_archived_cycles(self, cage_id):
        return self.fetch_all(
            "SELECT * FROM production_cycles WHERE cage_id = %s AND is_completed = 1 ORDER BY start_date DESC",
            (cage_id,)
        )

    def complete_cycle(self, cycle_id):
        return self.execute_query(
            "UPDATE production_cycles SET is_active = 0, is_completed = 1 WHERE id = %s",
            (cycle_id,)
        )

    def check_cycle_dependencies(self, cycle_id):
        """بررسی اینکه آیا دوره دارای دادههای وابسته است"""
        biomass_count = self.fetch_one("SELECT COUNT(*) as count FROM biomasses WHERE cycle_id = %s", (cycle_id,))
        if biomass_count and biomass_count['count'] > 0:
            return False, "زیست توده"

        feed_count = self.fetch_one("SELECT COUNT(*) as count FROM feeds WHERE cycle_id = %s", (cycle_id,))
        if feed_count and feed_count['count'] > 0:
            return False, "تغذیه"

        mortality_count = self.fetch_one("SELECT COUNT(*) as count FROM mortalities WHERE cycle_id = %s", (cycle_id,))
        if mortality_count and mortality_count['count'] > 0:
            return False, "تلفات"

        water_count = self.fetch_one("SELECT COUNT(*) as count FROM water_parameters WHERE cycle_id = %s", (cycle_id,))
        if water_count and water_count['count'] > 0:
            return False, "پارامترهای آب"

        harvest_count = self.fetch_one("SELECT COUNT(*) as count FROM harvests WHERE cycle_id = %s", (cycle_id,))
        if harvest_count and harvest_count['count'] > 0:
            return False, "برداشت"

        return True, ""

    # ==================== تغذیه ====================

    def save_feed(self, cage_id, cycle_id, date, feed_type, feed_amount, feed_time, note=""):
        query = """
            INSERT INTO feeds (cage_id, cycle_id, date, feed_type, feed_amount, feed_time, note)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """
        return self.execute_query(query, (cage_id, cycle_id, date, feed_type, feed_amount, feed_time, note))

    def get_feeds_by_cage_and_cycle(self, cage_id, cycle_id):
        if cycle_id:
            return self.fetch_all(
                "SELECT * FROM feeds WHERE cycle_id = %s ORDER BY date",
                (cycle_id,)
            )
        return self.fetch_all(
            "SELECT * FROM feeds WHERE cage_id = %s ORDER BY date",
            (cage_id,)
        )

    # ==================== تلفات ====================

    def save_mortality(self, cage_id, cycle_id, date, count, cause, note=""):
        query = """
            INSERT INTO mortalities (cage_id, cycle_id, date, count, cause, note)
            VALUES (%s, %s, %s, %s, %s, %s)
        """
        return self.execute_query(query, (cage_id, cycle_id, date, count, cause, note))

    def get_mortalities_by_cage_and_cycle(self, cage_id, cycle_id):
        if cycle_id:
            return self.fetch_all(
                "SELECT * FROM mortalities WHERE cycle_id = %s ORDER BY date",
                (cycle_id,)
            )
        return self.fetch_all(
            "SELECT * FROM mortalities WHERE cage_id = %s ORDER BY date",
            (cage_id,)
        )

    # ==================== پارامترهای آب ====================

    def save_water_parameter(self, cage_id, cycle_id, date, time, temperature, 
                            dissolved_oxygen, salinity, ph, note=""):
        query = """
            INSERT INTO water_parameters 
            (cage_id, cycle_id, date, time, temperature, dissolved_oxygen, salinity, ph, note)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        return self.execute_query(query, (cage_id, cycle_id, date, time, temperature, 
                                         dissolved_oxygen, salinity, ph, note))

    def get_water_parameters_by_cycle(self, cycle_id):
        return self.fetch_all(
            "SELECT * FROM water_parameters WHERE cycle_id = %s ORDER BY date",
            (cycle_id,)
        )

    # ==================== زیست توده ====================

    def save_biomass(self, cage_id, cycle_id, date, estimated_weight, estimated_count, sample_size, note=""):
        query = """
            INSERT INTO biomasses 
            (cage_id, cycle_id, date, estimated_weight, estimated_count, sample_size, note)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """
        return self.execute_query(query, (cage_id, cycle_id, date, estimated_weight, 
                                         estimated_count, sample_size, note))

    def get_biomasses_by_cage_and_cycle(self, cage_id, cycle_id):
        if cycle_id:
            return self.fetch_all(
                "SELECT * FROM biomasses WHERE cycle_id = %s ORDER BY date",
                (cycle_id,)
            )
        return self.fetch_all(
            "SELECT * FROM biomasses WHERE cage_id = %s ORDER BY date",
            (cage_id,)
        )

    # ==================== برداشت ====================

    def save_harvest(self, cage_id, cycle_id, harvest_date, harvest_count, average_weight,
                    total_weight_kg, customer, price_per_kg, total_amount, is_final, note=""):
        query = """
            INSERT INTO harvests 
            (cage_id, cycle_id, harvest_date, harvest_count, average_weight, total_weight_kg,
             customer, price_per_kg, total_amount, is_final, note)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        return self.execute_query(query, (cage_id, cycle_id, harvest_date, harvest_count, average_weight,
                                         total_weight_kg, customer, price_per_kg, total_amount, is_final, note))

    def get_harvests_by_cycle(self, cycle_id):
        return self.fetch_all("SELECT * FROM harvests WHERE cycle_id = %s ORDER BY harvest_date", (cycle_id,))

    def get_total_harvested_count(self, cycle_id):
        result = self.fetch_one("SELECT SUM(harvest_count) as total FROM harvests WHERE cycle_id = %s", (cycle_id,))
        return result['total'] if result and result['total'] else 0

    def get_total_feed_by_cycle(self, cycle_id):
        result = self.fetch_one("SELECT SUM(feed_amount) as total FROM feeds WHERE cycle_id = %s", (cycle_id,))
        return result['total'] if result and result['total'] else 0

    # ==================== وظایف روزانه ====================

    def save_daily_task(self, plan_id, task_date, task_type, assigned_to, shift_time, notes=""):
        """ذخیره وظیفه روزانه - بدون plan_id"""
        query = """
            INSERT INTO daily_tasks (task_date, task_type, assigned_to, shift_time, status, notes)
            VALUES (%s, %s, %s, %s, 'pending', %s)
        """
        return self.execute_query(query, (task_date, task_type, assigned_to, shift_time, notes))

    def get_daily_tasks_by_date(self, task_date):
        """دریافت وظایف یک تاریخ مشخص"""
        return self.fetch_all(
            "SELECT * FROM daily_tasks WHERE task_date = %s ORDER BY shift_time",
            (task_date,)
        )

    def update_task_status(self, task_id, status):
        """بهروزرسانی وضعیت وظیفه"""
        return self.execute_query(
            "UPDATE daily_tasks SET status = %s WHERE id = %s",
            (status, task_id)
        )

    def delete_task(self, task_id):
        """حذف وظیفه"""
        return self.execute_query("DELETE FROM daily_tasks WHERE id = %s", (task_id,))

    # ==================== برنامه‌های تولید ====================

    def save_production_plan(self, cage_id, species_id, stocking_date, harvest_date, feed_required):
        """ذخیره برنامه تولید جدید"""
        query = """
            INSERT INTO production_plans (cage_id, species_id, planned_stocking_date, 
                                          planned_harvest_date, estimated_feed_required, status)
            VALUES (%s, %s, %s, %s, %s, 'active')
        """
        return self.execute_query(query, (cage_id, species_id, stocking_date, harvest_date, feed_required))

    def get_production_plans_by_cage(self, cage_id):
        """دریافت برنامه‌های تولید برای یک قفس"""
        return self.fetch_all(
            "SELECT * FROM production_plans WHERE cage_id = %s ORDER BY planned_stocking_date DESC",
            (cage_id,)
        )

    # ==================== گونه‌های ماهی ====================

    def get_all_species(self):
        """دریافت لیست همه گونه‌های ماهی"""
        return self.fetch_all("SELECT * FROM fish_species ORDER BY name")

    def get_species_by_id(self, species_id):
        """دریافت اطلاعات یک گونه بر اساس ID"""
        return self.fetch_one("SELECT * FROM fish_species WHERE id = %s", (species_id,))

    def add_species(self, name, opt_temp_min, opt_temp_max, critical_temp, target_fcr, harvest_weight, daily_gain, description=""):
        """افزودن گونه جدید"""
        query = """
            INSERT INTO fish_species (name, optimal_temp_min, optimal_temp_max, critical_temp_high, 
                                      target_fcr, typical_harvest_weight, avg_daily_gain, description)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """
        return self.execute_query(query, (name, opt_temp_min, opt_temp_max, critical_temp, 
                                             target_fcr, harvest_weight, daily_gain, description))

    def update_species(self, species_id, name, opt_temp_min, opt_temp_max, critical_temp,
                       target_fcr, harvest_weight, daily_gain, description=""):
        """ویرایش گونه موجود"""
        query = """
            UPDATE fish_species 
            SET name = %s, optimal_temp_min = %s, optimal_temp_max = %s,
                critical_temp_high = %s, target_fcr = %s, typical_harvest_weight = %s,
                avg_daily_gain = %s, description = %s
            WHERE id = %s
        """
        return self.execute_query(query, (name, opt_temp_min, opt_temp_max, critical_temp,
                                             target_fcr, harvest_weight, daily_gain, description, species_id))

    def delete_species(self, species_id):
        """حذف گونه"""
        return self.execute_query("DELETE FROM fish_species WHERE id = %s", (species_id,))