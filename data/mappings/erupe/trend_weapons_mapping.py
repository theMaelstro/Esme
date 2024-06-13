"""Table mappings module"""
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column

from ..base_mapping import Base

class TrendWeapons(Base):
    """Trend Weapons table object"""
    __tablename__ = "trend_weapons"
