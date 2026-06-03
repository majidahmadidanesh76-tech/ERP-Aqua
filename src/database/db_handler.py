"""
واسط بین برنامه و دیتابیس - جایگزین فایل JSON
نسخه کامل با پشتیبانی از همه اجزا و برنامهریزی تولید
"""

from .db_manager import DatabaseManager

class DatabaseHandler:
    """مدیریت تمام عملیات دیتابیس برای برنامه"""

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.db = DatabaseManager()
        return cls._instance

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

                buoy_rows = self.db.fetch_all("SELECT * FROM buoys WHERE mooring_id = %s", (mooring.id,))
                for b_row in buoy_rows:
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

                anchor_rows = self.db.fetch_all("SELECT * FROM anchors WHERE mooring_id = %s", (mooring.id,))
                for a_row in anchor_rows:
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

                cage_rows = self.db.fetch_all("SELECT * FROM cages WHERE mooring_id = %s", (mooring.id,))
                for c_row in cage_rows:
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

    # ==================== مورینگ ====================

    def save_mooring(self, mooring, farm_id):
        return self.db.save_mooring(mooring.id, farm_id, mooring.name)

    def delete_mooring(self, mooring_id):
        return self.db.delete_mooring(mooring_id)

    # ==================== قفس ====================

    def save_cage(self, cage, mooring_id):
        return self.db.save_cage(cage.id, mooring_id, cage.diameter, cage.material,
                                 cage.utm_x, cage.utm_y, cage.color, cage.install_date,
                                 cage.status, cage.note)

    def delete_cage(self, cage_id):
        return self.db.delete_cage(cage_id)

    # ==================== بویه ====================

    def save_buoy(self, buoy, mooring_id):
        return self.db.save_buoy(buoy.id, mooring_id, buoy.buoy_type, buoy.utm_x, buoy.utm_y,
                                 buoy.color, buoy.material, buoy.volume, buoy.install_date,
                                 1 if buoy.has_light else 0, buoy.body_color, buoy.status, buoy.note)

    # ==================== لنگر ====================

    def save_anchor(self, anchor, mooring_id):
        return self.db.save_anchor(anchor.id, mooring_id, anchor.anchor_type, anchor.utm_x, anchor.utm_y,
                                   anchor.weight, anchor.color, anchor.material, anchor.install_date,
                                   anchor.install_depth, anchor.status, anchor.note)

    # ==================== زنجیر لنگر ====================

    def save_anchor_chain(self, chain, mooring_id):
        return self.db.save_anchor_chain(
            chain.id, mooring_id, chain.start_id, chain.end_id,
            chain.start_x, chain.start_y, chain.end_x, chain.end_y,
            chain.diameter, 1 if chain.use_manual_start else 0, 1 if chain.use_manual_end else 0,
            chain.color, chain.chain_type, chain.material,
            chain.install_date, chain.status, chain.note
        )

    # ==================== طناب لنگر ====================

    def save_anchor_rope(self, rope, mooring_id):
        return self.db.save_anchor_rope(
            rope.id, mooring_id, rope.start_id, rope.end_id,
            rope.start_x, rope.start_y, rope.end_x, rope.end_y,
            rope.material, rope.diameter, 1 if rope.use_manual_start else 0, 1 if rope.use_manual_end else 0,
            rope.color, rope.strand_count, rope.length,
            rope.install_date, rope.status, rope.note
        )

    # ==================== زنجیر بویه ====================

    def save_buoy_chain(self, buoy_chain, mooring_id):
        return self.db.save_buoy_chain(
            buoy_chain.id, mooring_id, buoy_chain.buoy_id, buoy_chain.collector_id,
            buoy_chain.diameter, buoy_chain.length, buoy_chain.material,
            buoy_chain.chain_type, buoy_chain.install_date, buoy_chain.status, buoy_chain.note
        )

    # ==================== شاکل ====================

    def save_shackle(self, shackle, mooring_id):
        return self.db.save_shackle(
            shackle.id, mooring_id, shackle.shackle_type, shackle.quantity,
            shackle.size, shackle.capacity, shackle.material, shackle.connected_id,
            shackle.install_date, shackle.status, shackle.note
        )

    # ==================== طناب برایدل ====================

    def save_bridle_rope(self, bridle, mooring_id):
        return self.db.save_bridle_rope(
            bridle.id, mooring_id, bridle.buoy_id, bridle.cage_x, bridle.cage_y,
            bridle.diameter, bridle.length, bridle.material, bridle.strand_count,
            bridle.install_date, bridle.status, bridle.color, bridle.note
        )

    # ==================== تور ====================

    def save_net(self, net, mooring_id):
        return self.db.save_net(
            net.id, mooring_id, net.cage_id, net.diameter, net.mesh_size,
            net.material, net.depth, net.install_date, net.status, net.note
        )

    # ==================== کلکتور ====================

    def save_collector(self, collector, mooring_id):
        return self.db.save_collector(
            collector.id, mooring_id, collector.buoy_id, collector.diameter,
            collector.thickness, collector.depth, collector.material,
            collector.install_date, collector.status, collector.color, collector.note
        )

    # ==================== دوره پرورش ====================

    def start_production_cycle(self, cage_id, start_date, species, initial_count,
                               initial_weight, target_weight, target_fcr=1.5, note=""):
        return self.db.start_production_cycle(
            cage_id, start_date, species, initial_count,
            initial_weight, target_weight, target_fcr, note
        )

    def update_production_cycle(self, cycle_id, start_date, species, initial_count,
                                initial_weight, target_weight, note=""):
        return self.db.update_production_cycle(
            cycle_id, start_date, species, initial_count,
            initial_weight, target_weight, note
        )

    def get_active_cycle(self, cage_id):
        row = self.db.get_active_cycle(cage_id)
        if not row:
            return None
        from ..core.models import ProductionCycle
        cycle = ProductionCycle()
        cycle.id = row['id']
        cycle.cage_id = row['cage_id']
        cycle.start_date = row['start_date']
        cycle.species = row['species'] or ''
        cycle.initial_count = row['initial_count']
        cycle.initial_weight = row['initial_weight']
        cycle.target_weight = row['target_weight']
        cycle.target_fcr = row['target_fcr'] if row['target_fcr'] else 1.5
        cycle.is_active = row['is_active']
        cycle.is_completed = row['is_completed']
        cycle.note = row['note'] or ''
        cycle.remaining_count = row['initial_count']
        cycle.total_harvested_count = 0
        cycle.total_harvested_kg = 0
        return cycle

    def get_archived_cycles(self, cage_id):
        rows = self.db.get_archived_cycles(cage_id)
        from ..core.models import ProductionCycle
        cycles = []
        for row in rows:
            cycle = ProductionCycle()
            cycle.id = row['id']
            cycle.cage_id = row['cage_id']
            cycle.start_date = row['start_date']
            cycle.species = row['species'] or ''
            cycle.initial_count = row['initial_count']
            cycle.initial_weight = row['initial_weight']
            cycle.target_weight = row['target_weight']
            cycle.target_fcr = row['target_fcr'] if row['target_fcr'] else 1.5
            cycle.is_active = row['is_active']
            cycle.is_completed = row['is_completed']
            cycle.note = row['note'] or ''
            cycles.append(cycle)
        return cycles

    def complete_cycle(self, cycle_id):
        return self.db.complete_cycle(cycle_id)

    def check_cycle_dependencies(self, cycle_id):
        return self.db.check_cycle_dependencies(cycle_id)

    # ==================== تغذیه ====================

    def save_feed(self, cage_id, cycle_id, date, feed_type, feed_amount, feed_time, note=""):
        return self.db.save_feed(cage_id, cycle_id, date, feed_type, feed_amount, feed_time, note)

    def get_feeds_by_cycle(self, cycle_id):
        rows = self.db.get_feeds_by_cage_and_cycle(None, cycle_id)
        from ..core.models import DailyFeed
        feeds = []
        for row in rows:
            feed = DailyFeed()
            feed.id = row['id']
            feed.cage_id = row['cage_id']
            feed.date = row['date']
            feed.feed_type = row['feed_type']
            feed.feed_amount = row['feed_amount']
            feed.feed_time = row['feed_time']
            feed.note = row['note'] or ''
            feeds.append(feed)
        return feeds

    # ==================== تلفات ====================

    def save_mortality(self, cage_id, cycle_id, date, count, cause, note=""):
        return self.db.save_mortality(cage_id, cycle_id, date, count, cause, note)

    def get_mortalities_by_cycle(self, cycle_id):
        rows = self.db.get_mortalities_by_cage_and_cycle(None, cycle_id)
        from ..core.models import DailyMortality
        mortalities = []
        for row in rows:
            m = DailyMortality()
            m.id = row['id']
            m.cage_id = row['cage_id']
            m.date = row['date']
            m.count = row['count']
            m.cause = row['cause']
            m.note = row['note'] or ''
            mortalities.append(m)
        return mortalities

    # ==================== پارامترهای آب ====================

    def save_water_parameter(self, cage_id, cycle_id, date, time, temperature,
                            dissolved_oxygen, salinity, ph, note=""):
        return self.db.save_water_parameter(
            cage_id, cycle_id, date, time, temperature,
            dissolved_oxygen, salinity, ph, note
        )

    def get_water_parameters_by_cycle(self, cycle_id):
        rows = self.db.get_water_parameters_by_cycle(cycle_id)
        from ..core.models import WaterParameter
        params = []
        for row in rows:
            p = WaterParameter()
            p.id = row['id']
            p.cage_id = row['cage_id']
            p.date = row['date']
            p.time = row['time'] if row['time'] else ''
            p.temperature = row['temperature']
            p.dissolved_oxygen = row['dissolved_oxygen']
            p.salinity = row['salinity'] if row['salinity'] else 0
            p.ph = row['ph']
            p.note = row['note'] or ''
            params.append(p)
        return params

    def delete_water_parameter(self, param_id):
        return self.db.execute_query("DELETE FROM water_parameters WHERE id = %s", (param_id,))

    # ==================== زیست توده ====================

    def save_biomass(self, cage_id, cycle_id, date, estimated_weight, estimated_count, sample_size, note=""):
        return self.db.save_biomass(cage_id, cycle_id, date, estimated_weight, estimated_count, sample_size, note)

    def get_biomasses_by_cycle(self, cycle_id):
        rows = self.db.get_biomasses_by_cage_and_cycle(None, cycle_id)
        from ..core.models import Biomass
        biomasses = []
        for row in rows:
            b = Biomass()
            b.id = row['id']
            b.cage_id = row['cage_id']
            b.date = row['date']
            b.estimated_weight = row['estimated_weight']
            b.estimated_count = row['estimated_count']
            b.sample_size = row['sample_size'] if row['sample_size'] else 0
            b.note = row['note'] or ''
            biomasses.append(b)
        return biomasses

    def delete_biomass(self, biomass_id):
        return self.db.execute_query("DELETE FROM biomasses WHERE id = %s", (biomass_id,))

    # ==================== برداشت ====================

    def save_harvest(self, cage_id, cycle_id, harvest_date, harvest_count, average_weight,
                    total_weight_kg, customer, price_per_kg, total_amount, is_final, note=""):
        return self.db.save_harvest(
            cage_id, cycle_id, harvest_date, harvest_count, average_weight,
            total_weight_kg, customer, price_per_kg, total_amount, is_final, note
        )

    def get_harvests_by_cycle(self, cycle_id):
        rows = self.db.get_harvests_by_cycle(cycle_id)
        from ..core.models import HarvestRecord
        harvests = []
        for row in rows:
            h = HarvestRecord()
            h.id = row['id']
            h.cage_id = row['cage_id']
            h.cycle_id = row['cycle_id']
            h.harvest_date = row['harvest_date']
            h.harvest_count = row['harvest_count']
            h.average_weight = row['average_weight']
            h.total_weight_kg = row['total_weight_kg']
            h.customer = row['customer'] or ''
            h.price_per_kg = row['price_per_kg']
            h.total_amount = row['total_amount']
            h.is_final = row['is_final']
            h.note = row['note'] or ''
            harvests.append(h)
        return harvests

    def delete_harvest(self, harvest_id):
        return self.db.execute_query("DELETE FROM harvests WHERE id = %s", (harvest_id,))

    def get_total_harvested_count(self, cycle_id):
        return self.db.get_total_harvested_count(cycle_id)

    def get_total_feed_by_cycle(self, cycle_id):
        return self.db.get_total_feed_by_cycle(cycle_id)

    # ==================== وظایف روزانه ====================

    def save_daily_task(self, plan_id, task_date, task_type, assigned_to, shift_time, notes=""):
        """ذخیره وظیفه روزانه - بدون plan_id"""
        query = """
            INSERT INTO daily_tasks (task_date, task_type, assigned_to, shift_time, status, notes)
            VALUES (%s, %s, %s, %s, 'pending', %s)
        """
        return self.db.execute_query(query, (task_date, task_type, assigned_to, shift_time, notes))

    def get_daily_tasks_by_date(self, task_date):
        """دریافت وظایف یک تاریخ مشخص"""
        return self.db.fetch_all(
            "SELECT * FROM daily_tasks WHERE task_date = %s ORDER BY shift_time",
            (task_date,)
        )

    def update_task_status(self, task_id, status):
        """بهروزرسانی وضعیت وظیفه"""
        return self.db.execute_query(
            "UPDATE daily_tasks SET status = %s WHERE id = %s",
            (status, task_id)
        )

    def delete_task(self, task_id):
        """حذف وظیفه"""
        return self.db.execute_query("DELETE FROM daily_tasks WHERE id = %s", (task_id,))

    # ==================== گونههای ماهی ====================

    def get_all_species(self):
        """دریافت لیست همه گونههای ماهی"""
        return self.db.fetch_all("SELECT * FROM fish_species ORDER BY name")

    def get_species_by_id(self, species_id):
        """دریافت اطلاعات یک گونه بر اساس ID"""
        return self.db.fetch_one("SELECT * FROM fish_species WHERE id = %s", (species_id,))

    def add_species(self, name, opt_temp_min, opt_temp_max, critical_temp, target_fcr, harvest_weight, daily_gain, description=""):
        """افزودن گونه جدید"""
        return self.db.add_species(name, opt_temp_min, opt_temp_max, critical_temp,
                                   target_fcr, harvest_weight, daily_gain, description)

    def update_species(self, species_id, name, opt_temp_min, opt_temp_max, critical_temp,
                       target_fcr, harvest_weight, daily_gain, description=""):
        """ویرایش گونه موجود"""
        return self.db.update_species(species_id, name, opt_temp_min, opt_temp_max, critical_temp,
                                      target_fcr, harvest_weight, daily_gain, description)

    def delete_species(self, species_id):
        """حذف گونه"""
        return self.db.delete_species(species_id)

    # ==================== برنامههای تولید ====================

    def save_production_plan(self, cage_id, species_id, stocking_date, harvest_date, feed_required):
        """ذخیره برنامه تولید جدید"""
        return self.db.save_production_plan(cage_id, species_id, stocking_date, harvest_date, feed_required)

    def get_production_plans_by_cage(self, cage_id):
        """دریافت برنامههای تولید برای یک قفس"""
        return self.db.get_production_plans_by_cage(cage_id)

    # ==================== متدهای کمکی ====================

    def fetch_all(self, query, params=None):
        """اجرای کوئری مستقیم و دریافت تمام نتایج"""
        return self.db.fetch_all(query, params)

    def fetch_one(self, query, params=None):
        """دریافت یک رکورد از دیتابیس"""
        return self.db.fetch_one(query, params)

    def execute_query(self, query, params=None):
        """اجرای مستقیم کوئری (DELETE, UPDATE, INSERT)"""
        return self.db.execute_query(query, params)