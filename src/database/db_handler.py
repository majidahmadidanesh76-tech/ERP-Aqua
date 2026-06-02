"""
واسط بین برنامه و دیتابیس - جایگزین فایل JSON
نسخه کامل با پشتیبانی از همه اجزا (بویه، لنگر، قفس، زنجیر، طناب، ...)
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
                
                # بارگذاری بویه‌ها
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
                
                # بارگذاری لنگرها
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
                
                # بارگذاری قفس‌ها
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
    
    def get_moorings_by_farm(self, farm_id):
        rows = self.db.get_moorings_by_farm(farm_id)
        from ..core.models import Mooring
        moorings = []
        for row in rows:
            mooring = Mooring(row['id'], row['name'])
            moorings.append(mooring)
        return moorings
    
    def delete_mooring(self, mooring_id):
        return self.db.delete_mooring(mooring_id)
    
    # ==================== قفس ====================
    
    def save_cage(self, cage, mooring_id):
        query = """
            INSERT INTO cages (id, mooring_id, diameter, material, utm_x, utm_y,
                              color, install_date, status, note)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE
                diameter = VALUES(diameter), material = VALUES(material),
                utm_x = VALUES(utm_x), utm_y = VALUES(utm_y),
                color = VALUES(color), install_date = VALUES(install_date),
                status = VALUES(status), note = VALUES(note)
        """
        return self.db.execute_query(query, (
            cage.id, mooring_id, cage.diameter, cage.material,
            cage.utm_x, cage.utm_y, cage.color, cage.install_date,
            cage.status, cage.note
        ))
    
    def get_cages_by_mooring(self, mooring_id):
        rows = self.db.fetch_all("SELECT * FROM cages WHERE mooring_id = %s", (mooring_id,))
        from ..core.models import Cage
        cages = []
        for row in rows:
            cage = Cage()
            cage.id = row['id']
            cage.mooring_id = row['mooring_id']
            cage.diameter = row['diameter']
            cage.material = row['material']
            cage.utm_x = row['utm_x']
            cage.utm_y = row['utm_y']
            cage.color = row['color']
            cage.install_date = row['install_date'] or ''
            cage.status = row['status']
            cage.note = row['note'] or ''
            cages.append(cage)
        return cages
    
    def delete_cage(self, cage_id):
        return self.db.delete_cage(cage_id)
    
    # ==================== بویه ====================
    
    def save_buoy(self, buoy, mooring_id):
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
        return self.db.execute_query(query, (
            buoy.id, mooring_id, buoy.buoy_type, buoy.utm_x, buoy.utm_y,
            buoy.color, buoy.material, buoy.volume, buoy.install_date,
            1 if buoy.has_light else 0, buoy.body_color, buoy.status, buoy.note
        ))
    
    def get_buoys_by_mooring(self, mooring_id):
        rows = self.db.fetch_all("SELECT * FROM buoys WHERE mooring_id = %s", (mooring_id,))
        from ..core.models import Buoy
        buoys = []
        for row in rows:
            buoy = Buoy()
            buoy.id = row['id']
            buoy.mooring_id = row['mooring_id']
            buoy.buoy_type = row['buoy_type']
            buoy.utm_x = row['utm_x']
            buoy.utm_y = row['utm_y']
            buoy.color = row['color']
            buoy.material = row['material']
            buoy.volume = row['volume']
            buoy.install_date = row['install_date'] or ''
            buoy.has_light = bool(row['has_light'])
            buoy.body_color = row['body_color']
            buoy.status = row['status']
            buoy.note = row['note'] or ''
            buoys.append(buoy)
        return buoys
    
    # ==================== لنگر ====================
    
    def save_anchor(self, anchor, mooring_id):
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
        return self.db.execute_query(query, (
            anchor.id, mooring_id, anchor.anchor_type, anchor.utm_x, anchor.utm_y,
            anchor.weight, anchor.color, anchor.material, anchor.install_date,
            anchor.install_depth, anchor.status, anchor.note
        ))
    
    def get_anchors_by_mooring(self, mooring_id):
        rows = self.db.fetch_all("SELECT * FROM anchors WHERE mooring_id = %s", (mooring_id,))
        from ..core.models import Anchor
        anchors = []
        for row in rows:
            anchor = Anchor()
            anchor.id = row['id']
            anchor.mooring_id = row['mooring_id']
            anchor.anchor_type = row['anchor_type']
            anchor.utm_x = row['utm_x']
            anchor.utm_y = row['utm_y']
            anchor.weight = row['weight']
            anchor.color = row['color']
            anchor.material = row['material']
            anchor.install_date = row['install_date'] or ''
            anchor.install_depth = row['install_depth']
            anchor.status = row['status']
            anchor.note = row['note'] or ''
            anchors.append(anchor)
        return anchors
    
    # ==================== دوره پرورش ====================
    
    def start_production_cycle(self, cage_id, start_date, species, initial_count,
                               initial_weight, target_weight, target_fcr=1.5, note=""):
        return self.db.start_production_cycle(
            cage_id, start_date, species, initial_count,
            initial_weight, target_weight, target_fcr, note
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
    
    def complete_cycle(self, cycle_id):
        return self.db.complete_cycle(cycle_id)
    
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
    
    # ==================== زیست‌توده ====================
    
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
            b.sample_size = row['sample_size']
            b.note = row['note'] or ''
            biomasses.append(b)
        return biomasses
    
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
    
    def get_total_harvested_count(self, cycle_id):
        return self.db.get_total_harvested_count(cycle_id)
    
    def get_total_feed_by_cycle(self, cycle_id):
        return self.db.get_total_feed_by_cycle(cycle_id)