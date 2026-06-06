"""
واسط بین برنامه و دیتابیس - نسخه نهایی
شامل: مدیریت مزرعه، آبزی‌پروری، برنامه‌ریزی تولید، نت، پیشنهادات هوشمند، جیره‌بندی
"""

from .db_manager import DatabaseManager


class DatabaseHandler:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.db = DatabaseManager()
        return cls._instance

    # ==================== متدهای عمومی ====================
    def fetch_all(self, query, params=None):
        return self.db.fetch_all(query, params)

    def fetch_one(self, query, params=None):
        return self.db.fetch_one(query, params)

    def execute_query(self, query, params=None):
        return self.db.execute_query(query, params)

    # ==================== مزرعه ====================
    def save_farm(self, farm):
        return self.db.save_farm(farm.id, farm.name, farm.center_x, farm.center_y)

    def get_all_farms(self):
        rows = self.db.get_all_farms()
        from ..core.models import Farm, Mooring, Buoy, Anchor, Cage
        farms = []
        for row in rows:
            farm = Farm(row['id'], row['name'], row['center_x'], row['center_y'])
            mooring_rows = self.db.get_moorings_by_farm(farm.id)
            for m_row in mooring_rows:
                mooring = Mooring(m_row['id'], m_row['name'])
                for b_row in self.db.fetch_all("SELECT * FROM buoys WHERE mooring_id = %s", (mooring.id,)):
                    buoy = Buoy()
                    buoy.id = b_row['id']
                    buoy.mooring_id = b_row['mooring_id']
                    buoy.buoy_type = b_row['buoy_type']
                    buoy.utm_x = b_row['utm_x']
                    buoy.utm_y = b_row['utm_y']
                    buoy.color = b_row['color']
                    buoy.material = b_row['material']
                    buoy.volume = b_row['volume']
                    buoy.install_date = b_row['install_date'] or ''
                    buoy.has_light = bool(b_row['has_light'])
                    buoy.body_color = b_row['body_color']
                    buoy.status = b_row['status']
                    buoy.note = b_row['note'] or ''
                    mooring.buoys.append(buoy)
                for a_row in self.db.fetch_all("SELECT * FROM anchors WHERE mooring_id = %s", (mooring.id,)):
                    anchor = Anchor()
                    anchor.id = a_row['id']
                    anchor.mooring_id = a_row['mooring_id']
                    anchor.anchor_type = a_row['anchor_type']
                    anchor.utm_x = a_row['utm_x']
                    anchor.utm_y = a_row['utm_y']
                    anchor.weight = a_row['weight']
                    anchor.color = a_row['color']
                    anchor.material = a_row['material']
                    anchor.install_date = a_row['install_date'] or ''
                    anchor.install_depth = a_row['install_depth']
                    anchor.status = a_row['status']
                    anchor.note = a_row['note'] or ''
                    mooring.anchors.append(anchor)
                for c_row in self.db.fetch_all("SELECT * FROM cages WHERE mooring_id = %s", (mooring.id,)):
                    cage = Cage()
                    cage.id = c_row['id']
                    cage.mooring_id = c_row['mooring_id']
                    cage.diameter = c_row['diameter']
                    cage.material = c_row['material']
                    cage.utm_x = c_row['utm_x']
                    cage.utm_y = c_row['utm_y']
                    cage.color = c_row['color']
                    cage.install_date = c_row['install_date'] or ''
                    cage.status = c_row['status']
                    cage.note = c_row['note'] or ''
                    mooring.cages.append(cage)
                farm.moorings.append(mooring)
            farms.append(farm)
        return farms

    def delete_farm(self, farm_id):
        return self.db.delete_farm(farm_id)

    def save_mooring(self, mooring, farm_id):
        return self.db.save_mooring(mooring.id, farm_id, mooring.name)

    def delete_mooring(self, mooring_id):
        return self.db.delete_mooring(mooring_id)

    def save_cage(self, cage, mooring_id):
        return self.db.save_cage(cage.id, mooring_id, cage.diameter, cage.material,
                                 cage.utm_x, cage.utm_y, cage.color, cage.install_date,
                                 cage.status, cage.note)

    # ==================== تجهیزات ====================
    def save_buoy(self, buoy, mooring_id):
        return self.db.save_buoy(buoy.id, mooring_id, buoy.buoy_type, buoy.utm_x, buoy.utm_y,
                                 buoy.color, buoy.material, buoy.volume, buoy.install_date,
                                 1 if buoy.has_light else 0, buoy.body_color, buoy.status, buoy.note)

    def save_anchor(self, anchor, mooring_id):
        return self.db.save_anchor(anchor.id, mooring_id, anchor.anchor_type, anchor.utm_x, anchor.utm_y,
                                   anchor.weight, anchor.color, anchor.material, anchor.install_date,
                                   anchor.install_depth, anchor.status, anchor.note)

    def save_anchor_chain(self, chain, mooring_id):
        return self.db.save_anchor_chain(
            chain.id, mooring_id, chain.start_id, chain.end_id,
            chain.start_x, chain.start_y, chain.end_x, chain.end_y,
            chain.diameter, 1 if chain.use_manual_start else 0, 1 if chain.use_manual_end else 0,
            chain.color, chain.chain_type, chain.material,
            chain.install_date, chain.status, chain.note
        )

    def save_anchor_rope(self, rope, mooring_id):
        return self.db.save_anchor_rope(
            rope.id, mooring_id, rope.start_id, rope.end_id,
            rope.start_x, rope.start_y, rope.end_x, rope.end_y,
            rope.material, rope.diameter, 1 if rope.use_manual_start else 0, 1 if rope.use_manual_end else 0,
            rope.color, rope.strand_count, rope.length,
            rope.install_date, rope.status, rope.note
        )

    def save_buoy_chain(self, buoy_chain, mooring_id):
        return self.db.save_buoy_chain(
            buoy_chain.id, mooring_id, buoy_chain.buoy_id, buoy_chain.collector_id,
            buoy_chain.diameter, buoy_chain.length, buoy_chain.material,
            buoy_chain.chain_type, buoy_chain.install_date, buoy_chain.status, buoy_chain.note
        )

    def save_shackle(self, shackle, mooring_id):
        return self.db.save_shackle(
            shackle.id, mooring_id, shackle.shackle_type, shackle.quantity,
            shackle.size, shackle.capacity, shackle.material, shackle.connected_id,
            shackle.install_date, shackle.status, shackle.note
        )

    def save_bridle_rope(self, bridle, mooring_id):
        return self.db.save_bridle_rope(
            bridle.id, mooring_id, bridle.buoy_id, bridle.cage_x, bridle.cage_y,
            bridle.diameter, bridle.length, bridle.material, bridle.strand_count,
            bridle.install_date, bridle.status, bridle.color, bridle.note
        )

    def save_net(self, net, mooring_id):
        return self.db.save_net(
            net.id, mooring_id, net.cage_id, net.diameter, net.mesh_size,
            net.material, net.depth, net.install_date, net.status, net.note
        )

    def save_collector(self, collector, mooring_id):
        return self.db.save_collector(
            collector.id, mooring_id, collector.buoy_id, collector.diameter,
            collector.thickness, collector.depth, collector.material,
            collector.install_date, collector.status, collector.color, collector.note
        )

    # ==================== دوره پرورش ====================

    def get_active_cycle(self, cage_id):
        """دریافت دوره فعال پرورش"""
        row = self.fetch_one("""
            SELECT 
                cycle_id as id,
                cage_id, 
                start_date, 
                species, 
                initial_count, 
                initial_weight, 
                target_weight,
                is_active,
                note
            FROM production_cycles 
            WHERE cage_id = %s AND is_active = 1
            ORDER BY cycle_id DESC LIMIT 1
        """, (cage_id,))
        
        if not row:
            return None
        
        from ..core.models import ProductionCycle
        cycle = ProductionCycle()
        cycle.id = row['id']
        cycle.cage_id = row['cage_id']
        cycle.start_date = row['start_date']
        cycle.species = row['species'] or ''
        cycle.initial_count = row['initial_count'] or 0
        cycle.initial_weight = float(row['initial_weight']) if row['initial_weight'] else 0.0
        cycle.target_weight = float(row['target_weight']) if row['target_weight'] else 0.0
        cycle.is_active = row['is_active']
        cycle.note = row.get('note', '')
        return cycle

    def start_production_cycle(self, cage_id, start_date, species, initial_count, 
                               initial_weight, target_weight, target_fcr=1.5, note=""):
        """شروع دوره پرورش جدید"""
        result = self.execute_query("""
            INSERT INTO production_cycles 
            (cage_id, start_date, species, initial_count, initial_weight, target_weight, is_active, note)
            VALUES (%s, %s, %s, %s, %s, %s, 1, %s)
        """, (cage_id, start_date, species, initial_count, initial_weight, target_weight, note))
        
        if result:
            last_id = self.fetch_one("SELECT LAST_INSERT_ID() as id")
            return last_id['id'] if last_id else None
        return None

    def update_production_cycle(self, cycle_id, start_date, species, initial_count,
                                initial_weight, target_weight, note=""):
        """ویرایش دوره پرورش"""
        return self.execute_query("""
            UPDATE production_cycles 
            SET start_date = %s, 
                species = %s, 
                initial_count = %s, 
                initial_weight = %s, 
                target_weight = %s, 
                note = %s
            WHERE cycle_id = %s
        """, (start_date, species, initial_count, initial_weight, target_weight, note, cycle_id))

    def complete_cycle(self, cycle_id):
        """تکمیل دوره پرورش"""
        return self.execute_query("""
            UPDATE production_cycles 
            SET is_active = 0, is_completed = 1 
            WHERE cycle_id = %s
        """, (cycle_id,))

    def check_cycle_dependencies(self, cycle_id):
        """بررسی وابستگی‌های دوره"""
        biomass = self.fetch_one("SELECT COUNT(*) as cnt FROM biomasses WHERE cycle_id = %s", (cycle_id,))
        feed = self.fetch_one("SELECT COUNT(*) as cnt FROM feeds WHERE cycle_id = %s", (cycle_id,))
        mortality = self.fetch_one("SELECT COUNT(*) as cnt FROM mortalities WHERE cycle_id = %s", (cycle_id,))
        harvest = self.fetch_one("SELECT COUNT(*) as cnt FROM harvests WHERE cycle_id = %s", (cycle_id,))
        water = self.fetch_one("SELECT COUNT(*) as cnt FROM water_parameters WHERE cycle_id = %s", (cycle_id,))
        
        if biomass and biomass['cnt'] > 0:
            return False, "زیست توده"
        if feed and feed['cnt'] > 0:
            return False, "تغذیه"
        if mortality and mortality['cnt'] > 0:
            return False, "تلفات"
        if harvest and harvest['cnt'] > 0:
            return False, "برداشت"
        if water and water['cnt'] > 0:
            return False, "پارامترهای آب"
        return True, ""

    # ==================== تغذیه ====================

    def save_feed(self, cage_id, cycle_id, date, feed_type, feed_amount, feed_time, note=""):
        return self.execute_query("""
            INSERT INTO feeds (cage_id, cycle_id, date, feed_type, feed_amount, feed_time, note)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (cage_id, cycle_id, date, feed_type, feed_amount, feed_time, note))

    def get_feeds_by_cycle(self, cycle_id):
        rows = self.fetch_all("SELECT * FROM feeds WHERE cycle_id = %s ORDER BY date", (cycle_id,))
        result = []
        for row in rows:
            from ..core.models import DailyFeed
            f = DailyFeed()
            f.id = row.get('id')
            f.cage_id = row.get('cage_id')
            f.cycle_id = row.get('cycle_id')
            f.date = row.get('date')
            f.feed_type = row.get('feed_type')
            f.feed_amount = row.get('feed_amount', 0)
            f.feed_time = row.get('feed_time')
            f.note = row.get('note', '')
            result.append(f)
        return result

    # ==================== تلفات ====================

    def save_mortality(self, cage_id, cycle_id, date, count, cause, note=""):
        return self.execute_query("""
            INSERT INTO mortalities (cage_id, cycle_id, date, count, cause, note)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (cage_id, cycle_id, date, count, cause, note))

    def get_mortalities_by_cycle(self, cycle_id):
        rows = self.fetch_all("SELECT * FROM mortalities WHERE cycle_id = %s ORDER BY date", (cycle_id,))
        result = []
        for row in rows:
            from ..core.models import DailyMortality
            m = DailyMortality()
            m.id = row.get('id')
            m.cage_id = row.get('cage_id')
            m.cycle_id = row.get('cycle_id')
            m.date = row.get('date')
            m.count = row.get('count', 0)
            m.cause = row.get('cause')
            m.note = row.get('note', '')
            result.append(m)
        return result

    # ==================== زیست توده ====================

    def save_biomass(self, cage_id, cycle_id, date, estimated_weight, estimated_count, sample_size, note=""):
        return self.execute_query("""
            INSERT INTO biomasses 
            (cage_id, cycle_id, date, estimated_weight, estimated_count, sample_size, note)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (cage_id, cycle_id, date, estimated_weight, estimated_count, sample_size, note))

    def get_biomasses_by_cycle(self, cycle_id):
        rows = self.fetch_all("SELECT * FROM biomasses WHERE cycle_id = %s ORDER BY date", (cycle_id,))
        result = []
        for row in rows:
            from ..core.models import Biomass
            b = Biomass()
            b.id = row.get('id')
            b.cage_id = row.get('cage_id')
            b.cycle_id = row.get('cycle_id')
            b.date = row.get('date')
            b.estimated_weight = float(row.get('estimated_weight', 0))
            b.estimated_count = row.get('estimated_count', 0)
            b.sample_size = row.get('sample_size', 0)
            b.note = row.get('note', '')
            result.append(b)
        return result

    # ==================== برداشت ====================

    def save_harvest(self, cage_id, cycle_id, harvest_date, harvest_count, average_weight,
                     total_weight_kg, customer, price_per_kg, total_amount, is_final, note=""):
        return self.execute_query("""
            INSERT INTO harvests 
            (cage_id, cycle_id, harvest_date, harvest_count, average_weight, total_weight_kg,
             customer, price_per_kg, total_amount, is_final, note)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (cage_id, cycle_id, harvest_date, harvest_count, average_weight,
              total_weight_kg, customer, price_per_kg, total_amount, is_final, note))

    def get_harvests_by_cycle(self, cycle_id):
        rows = self.fetch_all("SELECT * FROM harvests WHERE cycle_id = %s ORDER BY harvest_date", (cycle_id,))
        result = []
        for row in rows:
            from ..core.models import HarvestRecord
            h = HarvestRecord()
            h.id = row.get('id')
            h.cage_id = row.get('cage_id')
            h.cycle_id = row.get('cycle_id')
            h.harvest_date = row.get('harvest_date')
            h.harvest_count = row.get('harvest_count', 0)
            h.average_weight = float(row.get('average_weight', 0))
            h.total_weight_kg = float(row.get('total_weight_kg', 0))
            h.customer = row.get('customer', '')
            h.price_per_kg = float(row.get('price_per_kg', 0))
            h.total_amount = float(row.get('total_amount', 0))
            h.is_final = row.get('is_final', False)
            h.note = row.get('note', '')
            result.append(h)
        return result

    # ==================== پارامترهای آب ====================

    def save_water_parameter(self, cage_id, cycle_id, date, time, temperature,
                             dissolved_oxygen, salinity, ph, note=""):
        return self.execute_query("""
            INSERT INTO water_parameters 
            (cage_id, cycle_id, date, time, temperature, dissolved_oxygen, salinity, ph, note)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (cage_id, cycle_id, date, time, temperature, dissolved_oxygen, salinity, ph, note))

    def get_water_parameters_by_cycle(self, cycle_id):
        rows = self.fetch_all("SELECT * FROM water_parameters WHERE cycle_id = %s ORDER BY date", (cycle_id,))
        result = []
        for row in rows:
            from ..core.models import WaterParameter
            w = WaterParameter()
            w.id = row.get('id')
            w.cage_id = row.get('cage_id')
            w.cycle_id = row.get('cycle_id')
            w.date = row.get('date')
            w.time = row.get('time')
            w.temperature = float(row.get('temperature', 0))
            w.dissolved_oxygen = float(row.get('dissolved_oxygen', 0))
            w.salinity = float(row.get('salinity', 0))
            w.ph = float(row.get('ph', 0))
            w.note = row.get('note', '')
            result.append(w)
        return result

    # ==================== گونه‌های ماهی ====================

    def get_all_species(self):
        return self.fetch_all("SELECT * FROM fish_species ORDER BY name")

    def get_species_by_id(self, species_id):
        return self.fetch_one("SELECT * FROM fish_species WHERE id = %s", (species_id,))

    # ==================== حذف ====================

    def delete_harvest(self, harvest_id):
        return self.execute_query("DELETE FROM harvests WHERE id = %s", (harvest_id,))

    def delete_biomass(self, biomass_id):
        return self.execute_query("DELETE FROM biomasses WHERE id = %s", (biomass_id,))

    def delete_water_parameter(self, param_id):
        return self.execute_query("DELETE FROM water_parameters WHERE id = %s", (param_id,))

    # ==================== وظایف روزانه (برای سازگاری) ====================

    def get_daily_tasks_by_date(self, task_date):
        return self.fetch_all("SELECT * FROM daily_tasks WHERE task_date = %s", (task_date,))

    def save_daily_task(self, plan_id, task_date, task_type, assigned_to, shift_time, notes=""):
        return self.execute_query("""
            INSERT INTO daily_tasks (task_date, task_type, assigned_to, shift_time, status, notes)
            VALUES (%s, %s, %s, %s, 'pending', %s)
        """, (task_date, task_type, assigned_to, shift_time, notes))

    def update_task_status(self, task_id, status):
        return self.execute_query("UPDATE daily_tasks SET status = %s WHERE id = %s", (status, task_id))

    def delete_task(self, task_id):
        return self.execute_query("DELETE FROM daily_tasks WHERE id = %s", (task_id,))

    # ==================== برنامه‌ریزی تولید ====================

    def get_all_production_plans(self, cage_id=None):
        if cage_id:
            return self.fetch_all("SELECT * FROM production_plans WHERE cage_id = %s ORDER BY start_date DESC", (cage_id,))
        return self.fetch_all("SELECT * FROM production_plans ORDER BY start_date DESC")

    def get_production_plan_by_id(self, plan_id):
        return self.fetch_one("SELECT * FROM production_plans WHERE id = %s", (plan_id,))

    def create_production_plan(self, plan_title, plan_type, start_date, end_date, cage_id, planned_by, notes=""):
        return self.execute_query("""
            INSERT INTO production_plans 
            (plan_title, plan_type, start_date, end_date, cage_id, plan_status, planned_by, notes)
            VALUES (%s, %s, %s, %s, %s, 'draft', %s, %s)
        """, (plan_title, plan_type, start_date, end_date, cage_id, planned_by, notes))

    def update_plan_status(self, plan_id, status):
        return self.execute_query("UPDATE production_plans SET plan_status = %s WHERE id = %s", (status, plan_id))

    def delete_production_plan(self, plan_id):
        return self.execute_query("DELETE FROM production_plans WHERE id = %s", (plan_id,))

    def get_plan_tasks(self, plan_id):
        return self.fetch_all("SELECT * FROM plan_tasks WHERE plan_id = %s ORDER BY scheduled_date", (plan_id,))

    def add_plan_task(self, plan_id, template_id, task_title, task_description, category,
                      scheduled_date, scheduled_start_time, estimated_duration_minutes,
                      assigned_to_personnel_id, assigned_to_unit, priority_level):
        return self.execute_query("""
            INSERT INTO plan_tasks 
            (plan_id, template_id, task_title, task_description, category,
             scheduled_date, scheduled_start_time, estimated_duration_minutes,
             assigned_to_personnel_id, assigned_to_unit, priority_level, execution_status)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 'pending')
        """, (plan_id, template_id, task_title, task_description, category,
              scheduled_date, scheduled_start_time, estimated_duration_minutes,
              assigned_to_personnel_id, assigned_to_unit, priority_level))

    # ==================== برنامه نت ====================

    def get_maintenance_plans(self, asset_type=None):
        if asset_type:
            return self.fetch_all("SELECT * FROM maintenance_plans WHERE asset_type = %s ORDER BY start_date DESC", (asset_type,))
        return self.fetch_all("SELECT * FROM maintenance_plans ORDER BY start_date DESC")

    def get_maintenance_plan_by_id(self, plan_id):
        return self.fetch_one("SELECT * FROM maintenance_plans WHERE id = %s", (plan_id,))

    def create_maintenance_plan(self, plan_title, plan_type, start_date, end_date, asset_type, asset_id, notes=""):
        return self.execute_query("""
            INSERT INTO maintenance_plans (plan_title, plan_type, start_date, end_date, asset_type, asset_id, plan_status, planned_by, notes)
            VALUES (%s, %s, %s, %s, %s, %s, 'draft', 1, %s)
        """, (plan_title, plan_type, start_date, end_date, asset_type, asset_id, notes))

    def delete_maintenance_plan(self, plan_id):
        return self.execute_query("DELETE FROM maintenance_plans WHERE id = %s", (plan_id,))

    def get_maintenance_tasks(self, plan_id):
        return self.fetch_all("SELECT * FROM maintenance_plan_tasks WHERE plan_id = %s ORDER BY scheduled_date", (plan_id,))

    def add_maintenance_task(self, plan_id, template_id, task_title, task_description, category,
                             scheduled_date, scheduled_start_time, estimated_duration_minutes, assigned_to_team, priority_level):
        return self.execute_query("""
            INSERT INTO maintenance_plan_tasks 
            (plan_id, template_id, task_title, task_description, category,
             scheduled_date, scheduled_start_time, estimated_duration_minutes, assigned_to_team, priority_level, execution_status)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 'pending')
        """, (plan_id, template_id, task_title, task_description, category,
              scheduled_date, scheduled_start_time, estimated_duration_minutes, assigned_to_team, priority_level))

    # ==================== پیشنهادات هوشمند ====================

    def get_ai_suggestions(self, status='pending'):
        """دریافت پیشنهادات هوشمند"""
        return self.fetch_all("""
            SELECT * FROM ai_suggestions 
            WHERE status = %s 
            ORDER BY priority, created_at DESC
        """, (status,))

    def get_all_ai_suggestions(self):
        """دریافت همه پیشنهادات هوشمند"""
        return self.fetch_all("SELECT * FROM ai_suggestions ORDER BY priority, created_at DESC")

    def add_ai_suggestion(self, suggestion_type, title, description, priority=2, suggested_date=None, reasoning=""):
        """افزودن پیشنهاد هوشمند جدید"""
        return self.execute_query("""
            INSERT INTO ai_suggestions (suggestion_type, title, description, priority, suggested_date, reasoning)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (suggestion_type, title, description, priority, suggested_date, reasoning))

    def accept_suggestion(self, suggestion_id):
        """پذیرش یک پیشنهاد هوشمند"""
        return self.execute_query("UPDATE ai_suggestions SET status = 'accepted' WHERE id = %s", (suggestion_id,))

    def reject_suggestion(self, suggestion_id):
        """رد یک پیشنهاد هوشمند"""
        return self.execute_query("UPDATE ai_suggestions SET status = 'rejected' WHERE id = %s", (suggestion_id,))

    def delete_suggestion(self, suggestion_id):
        """حذف یک پیشنهاد هوشمند"""
        return self.execute_query("DELETE FROM ai_suggestions WHERE id = %s", (suggestion_id,))

    # ==================== قوانین هوشمند ====================

    def get_rule_value(self, rule_name, default=None):
        result = self.fetch_one("SELECT rule_value FROM smart_rules_settings WHERE rule_name = %s", (rule_name,))
        if result:
            return float(result['rule_value'])
        return default

    def get_all_rules(self):
        return self.fetch_all("SELECT * FROM smart_rules_settings ORDER BY id")

    def update_rule_value(self, rule_name, rule_value, updated_by="admin"):
        return self.execute_query("""
            UPDATE smart_rules_settings 
            SET rule_value = %s, updated_by = %s, updated_at = NOW()
            WHERE rule_name = %s
        """, (rule_value, updated_by, rule_name))

    def update_multiple_rules(self, rules_dict, updated_by="admin"):
        for rule_name, rule_value in rules_dict.items():
            self.update_rule_value(rule_name, rule_value, updated_by)
        return True

    def reset_rules_to_default(self):
        default_values = {
            'temp_alert_high': 24,
            'temp_critical_high': 26,
            'o2_alert_low': 5,
            'o2_critical_low': 4,
            'salinity_min': 25,
            'salinity_max': 40,
            'mortality_threshold': 0.1,
            'net_clean_days': 30,
            'harvest_threshold': 0.9,
            'combined_temp_o2_alert': 2,
            'max_suggestions_per_day': 10
        }
        for rule_name, rule_value in default_values.items():
            self.execute_query("""
                UPDATE smart_rules_settings 
                SET rule_value = %s, updated_by = 'system_reset', updated_at = NOW()
                WHERE rule_name = %s
            """, (rule_value, rule_name))
        return True

    # ==================== جیره‌بندی ====================

    def save_diet_formulation(self, production_cycle_id, cage_id, formulation_date, species,
                              avg_weight_gram, water_temperature, daily_feed_rate,
                              calculated_feed_kg, feed_type, fcr_target, nutritionist_id, notes=""):
        return self.execute_query("""
            INSERT INTO diet_formulations 
            (production_cycle_id, cage_id, formulation_date, species, avg_weight_gram,
             water_temperature, daily_feed_rate, calculated_feed_kg, feed_type,
             fcr_target, nutritionist_id, notes)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (production_cycle_id, cage_id, formulation_date, species, avg_weight_gram,
              water_temperature, daily_feed_rate, calculated_feed_kg, feed_type,
              fcr_target, nutritionist_id, notes))

    def get_diet_formulations_by_cycle(self, production_cycle_id):
        return self.fetch_all("""
            SELECT * FROM diet_formulations 
            WHERE production_cycle_id = %s 
            ORDER BY formulation_date DESC
        """, (production_cycle_id,))

    def get_diet_formulation_by_id(self, formulation_id):
        return self.fetch_one("SELECT * FROM diet_formulations WHERE id = %s", (formulation_id,))

    def add_feeding_recommendation(self, diet_formulation_id, recommendation_date, 
                                   recommended_feed_kg, recommended_feed_time):
        return self.execute_query("""
            INSERT INTO feeding_recommendations 
            (diet_formulation_id, recommendation_date, recommended_feed_kg, recommended_feed_time)
            VALUES (%s, %s, %s, %s)
        """, (diet_formulation_id, recommendation_date, recommended_feed_kg, recommended_feed_time))

    def get_feeding_recommendations_by_formulation(self, diet_formulation_id):
        return self.fetch_all("""
            SELECT * FROM feeding_recommendations 
            WHERE diet_formulation_id = %s 
            ORDER BY recommendation_date
        """, (diet_formulation_id,))

    def update_feeding_recommendation_status(self, recommendation_id, status):
        return self.execute_query("UPDATE feeding_recommendations SET status = %s WHERE id = %s", (status, recommendation_id))

    def calculate_feed_rate(self, species, avg_weight_gram, water_temperature):
        if avg_weight_gram < 50:
            base_rate = 6.0
        elif avg_weight_gram < 200:
            base_rate = 4.0
        elif avg_weight_gram < 1000:
            base_rate = 2.5
        else:
            base_rate = 1.5
        
        if water_temperature < 12:
            temp_factor = 0.5
        elif water_temperature < 16:
            temp_factor = 0.7
        elif water_temperature < 22:
            temp_factor = 1.0
        elif water_temperature < 26:
            temp_factor = 0.8
        else:
            temp_factor = 0.5
        
        return round(base_rate * temp_factor, 1)

    def get_feed_type_by_weight(self, avg_weight_gram):
        if avg_weight_gram < 50:
            return 'شروع (0-20 گرم)'
        elif avg_weight_gram < 200:
            return 'رشد (20-100 گرم)'
        else:
            return 'پایانی (100+ گرم)'