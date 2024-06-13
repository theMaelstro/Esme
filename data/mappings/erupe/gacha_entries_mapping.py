"""Table mappings module"""
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column

from ..base_mapping import Base

class GachaEntries(Base):
    """Gacha Entries table object"""
    __tablename__ = "gacha_entries"
