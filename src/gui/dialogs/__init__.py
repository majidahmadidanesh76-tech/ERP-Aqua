"""
مدیریت و صادرات دیالوگ‌های برنامه ERP-Aqua
این فایل باعث می‌شود همه دیالوگ‌ها با یک import قابل دسترسی باشند
"""

from .company_dialog import CompanyDialog
from .farm_dialog import AddFarmDialog, EditFarmDialog
from .mooring_dialog import AddMooringDialog, EditMooringDialog
from .buoy_dialog import BuoyDialog
from .anchor_dialog import AnchorDialog
from .chain_dialog import AddChainDialog
from .rope_dialog import AddRopeDialog
from .buoy_chain_dialog import AddBuoyChainDialog
from .shackle_dialog import AddShackleDialog
from .bridle_dialog import AddBridleRopeDialog
from .cage_dialog import AddCageDialog
from .net_dialog import AddNetDialog
from .collector_dialog import AddCollectorDialog
from .delete_confirm import DeleteConfirmDialog
from .final_list import FinalConfirmDialog

__all__ = [
    'CompanyDialog',
    'AddFarmDialog',
    'EditFarmDialog',
    'AddMooringDialog',
    'EditMooringDialog',
    'BuoyDialog',
    'AnchorDialog',
    'AddChainDialog',
    'AddRopeDialog',
    'AddBuoyChainDialog',
    'AddShackleDialog',
    'AddBridleRopeDialog',
    'AddCageDialog',
    'AddNetDialog',
    'AddCollectorDialog',
    'DeleteConfirmDialog',
    'FinalConfirmDialog'
]